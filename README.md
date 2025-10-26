# Poly
---

## 🚀 Recent Milestones

| Date | Milestone | Description |
|------|------------|-------------|
| **2025-10-26** | [✨ Poly Tutor MVP Achieved](logs/2025-10-26.md) | First successful interactive teaching loop between Poly and Blender 2.79 — Poly gave voice instructions, detected success, and responded verbally using SSML. |
| **2025-10-25** | Hook v0.4b Verified | JSON command fallback resolved; plaintext `get loc` validated; PowerShell `Send-Poly` helper operational. |
| **2025-10-19** | CLI & Hook Integration | Confirmed socket communication, PowerShell relay, and Blender event response baseline. |
| **2025-10-01** | GrantAI Readiness Checklist Complete | Repository docs, roadmap, and CI badge verified for upcoming grant submission. |
| **2025-09-13** | Shipwright → Poly Handoff | Core observability pipeline validated; Poly Phase 1 groundwork established. |

> 🧭 *Next up:* Record the OBS demo, share milestone posts, and begin grant-video prep for the Poly Tutor MVP showcase.

![CI](https://github.com/ladym0d/Poly/actions/workflows/ci.yml/badge.svg)

> An open, pirate-themed AI collaboration assistant...

## Highlights
- Shipwright → Poly handoff (Phase 1 → Phase 2)
- Blender event hooks + OBS overlay relay
- Programming Mentor mode (MVP)

## Repo Map
See /docs/REPO_MAP.md

## 🧩 Poly Tutor MVP (v0.4b)

The first functional teaching loop between Poly and Blender 2.79 — completed **October 26 2025**.

**Core Components**
- **Hook:** [`poly_hook.py`](poly_hook.py) — Blender socket listener and verifier.
- **Teaching Script:** [`teach_step_1.ps1`](demo/teach_step_1.ps1) — PowerShell loop that runs “teach add cube” → verify → “teach move cube”.
- **Demo Video:** `video/poly_mvp_demo_2025-10-26.mp4` — recorded proof-of-concept of Poly teaching Blender live.
- **Hardware:** Surface Pro 7 (Windows 11) using Windows TTS.

> 🎉 *This marks the first time Poly issued spoken instructions, detected success in Blender, and responded using SSML — the birth of interactive tutoring.*


## License
MIT
=======
Poly: Your AI First-Mate is Phase 2 of the Shipwright project, where I am developing a virtual mentor that can coach someone through new tasks and complex workflows in real-time.
>>>>>>> 9d16c327cab3d07dfe6304f44e0a86df840ccbdb
