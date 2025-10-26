# poly_hook.py — Blender 2.79b-safe main-thread executor (v0.4b)
# Launch: blender.exe --python C:\PolyDemo\poly_hook.py

import bpy, socket, threading, json, time
from collections import deque
from threading import Event, Lock

HOST = "127.0.0.1"
PORT = 8765
VERSION = "POLY_HOOK v0.4b-main"

# ---------- main-thread task queue ----------
_queue = deque()
_q_lock = Lock()
_pump_started = False  # sentinel

def enqueue(opname, args=None):
    item = {"op": opname, "args": args or {}, "result": None, "evt": Event()}
    with _q_lock:
        _queue.append(item)
    item["evt"].wait(2.0)
    return item.get("result") or {"op":"error","msg":"timeout"}

# ---- actions (main thread) ----
def _do_add_cube():
    try:
        bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 0.0))
        return {"op":"ok","msg":"cube added"}
    except Exception as e:
        return {"op":"error","msg":"add_cube: {}".format(e)}

def _do_move(axis, val):
    obj = bpy.context.active_object
    if not obj:
        return {"op":"error","msg":"no active object"}
    try:
        val = float(val)
    except:
        return {"op":"error","msg":"bad value"}
    a = (axis or "").lower()
    if   a == "x": obj.location.x += val
    elif a == "y": obj.location.y += val
    elif a == "z": obj.location.z += val
    else:          return {"op":"error","msg":"bad axis"}
    return {"op":"ok","msg":"moved {}".format(a)}

def _do_get_active_loc():
    obj = bpy.context.active_object
    if not obj:
        return {"op":"error","msg":"no active object"}
    loc = obj.location
    return {"op":"ok","loc":[float(loc.x), float(loc.y), float(loc.z)]}

# ---- read-only checks (coach mode) ----
def _do_get_mode():
    try:
        return {"op":"ok","mode": bpy.context.mode}
    except Exception as e:
        return {"op":"error","msg":"mode: {}".format(e)}

def _do_active_exists():
    return {"op":"ok","exists": bpy.context.active_object is not None}

def _do_active_is_cube():
    obj = bpy.context.active_object
    if not obj:
        return {"op":"ok","is_cube": False}
    name = (obj.name or "").lower()
    data_name = (getattr(getattr(obj, "data", None), "name", "") or "").lower()
    is_cubeish = (obj.type == 'MESH') and (name.startswith("cube") or data_name.startswith("cube"))
    return {"op":"ok","is_cube": is_cubeish}

def _do_scene_cube_count():
    scn = bpy.context.scene
    n = sum(1 for o in scn.objects if getattr(o, "type", None) == 'MESH' and (o.name or "").lower().startswith("cube"))
    return {"op":"ok","count": int(n)}

def _run_on_main(opname, args):
    if   opname == "ping":              return {"op":"pong","msg":VERSION}
    elif opname == "add_cube":          return _do_add_cube()
    elif opname == "move":              return _do_move(args.get("axis"), args.get("val"))
    elif opname == "get_active_loc":    return _do_get_active_loc()
    elif opname == "get_mode":          return _do_get_mode()
    elif opname == "active_exists":     return _do_active_exists()
    elif opname == "active_is_cube":    return _do_active_is_cube()
    elif opname == "scene_cube_count":  return _do_scene_cube_count()
    elif opname == "ops":
        return {"op":"ok","ops":["ping","add_cube","move","get_active_loc","get_mode","active_exists","active_is_cube","scene_cube_count"]}
    return {"op":"error","msg":"unknown op: {}".format(opname)}

class POLY_OT_MainThreadPump(bpy.types.Operator):
    bl_idname = "poly.main_thread_pump"
    bl_label = "Poly Main Thread Pump"
    _timer = None
    def modal(self, context, event):
        if event.type == 'TIMER':
            item = None
            with _q_lock:
                if _queue:
                    item = _queue.popleft()
            if item:
                try:
                    res = _run_on_main(item["op"], item["args"])
                except Exception as e:
                    res = {"op":"error","msg":"exec: {}".format(e)}
                item["result"] = res
                item["evt"].set()
        return {'PASS_THROUGH'}
    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, context.window)
        wm.modal_handler_add(self)
        print("{} main-thread pump started.".format(VERSION))
        return {'RUNNING_MODAL'}

def ensure_pump_running():
    global _pump_started
    if not _pump_started:
        try:
            bpy.ops.poly.main_thread_pump()
            _pump_started = True
        except Exception as e:
            print("[{}] pump start failed: {}".format(VERSION, e))

# ---------- protocol handler ----------
def handle(raw):
    raw = (raw or "").strip()
    print("[{}] RAW: {}".format(VERSION, repr(raw)))
    if "{" in raw and "}" in raw:
        try:
            start = raw.find("{"); end = raw.rfind("}")+1
            msg = json.loads(raw[start:end])
            op = (msg.get("op") or "").strip()
            print("[{}] OP: {}".format(VERSION, repr(op)))
            res = enqueue(op, msg)
            return json.dumps(res) + "\n"
        except Exception as e:
            print("[{}] JSON parse error: {}".format(VERSION, e))
    cmd = raw.lower()
    if cmd == "add cube":      return json.dumps(enqueue("add_cube")) + "\n"
    if cmd.startswith("move "):
        parts = cmd.split()
        if len(parts) == 3:    return json.dumps(enqueue("move", {"axis":parts[1], "val":parts[2]})) + "\n"
    if cmd == "get loc":       return json.dumps(enqueue("get_active_loc")) + "\n"
    return json.dumps({"op":"error","msg":"unknown command"}) + "\n"

# ---------- socket server ----------
def server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(4)
    print("{} listening on {}:{} at {}".format(VERSION, HOST, PORT, time.strftime("%H:%M:%S")))
    while True:
        conn, addr = s.accept()
        try:
            with conn:
                data = conn.recv(4096).decode("utf-8", errors="replace")
                if not data:
                    continue
                reply = handle(data)
                conn.sendall(reply.encode("utf-8"))
        except Exception as e:
            print("[{}] Server error: {}".format(VERSION, e))

def _start():
    ensure_pump_running()
    t = threading.Thread(target=server)
    t.daemon = True
    t.start()
    print("{} started.".format(VERSION))

def register():
    bpy.utils.register_class(POLY_OT_MainThreadPump)
    _start()

def unregister():
    try:
        bpy.utils.unregister_class(POLY_OT_MainThreadPump)
    except Exception:
        pass

if __name__ == "__main__":
    register()
