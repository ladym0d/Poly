# teach_step_1.ps1 — Poly Tutor (coach mode): you act, Poly verifies

# --- Speak() using Windows TTS (nicer defaults) ---
Add-Type -AssemblyName System.Speech
$spk = New-Object System.Speech.Synthesis.SpeechSynthesizer
$spk.Rate = -1   # a bit slower = more natural
$spk.Volume = 100
# try preferred voices in order; silently skip missing ones
$preferred = @("Microsoft Zira Desktop","Microsoft Hazel Desktop","Microsoft David Desktop")
foreach($v in $preferred){ try { $spk.SelectVoice($v); break } catch {} }
function Speak([string]$text) { $spk.Speak($text) }
function SpeakSSML([string]$ssml) { $spk.SpeakSsml($ssml) }  # optional SSML

# --- Send-Poly helper (connect -> send -> read -> close) ---
function Send-Poly {
  param([Parameter(Mandatory=$true)][string]$msg)
  $port = 8765
  $client = New-Object System.Net.Sockets.TcpClient("127.0.0.1",$port)
  $stream = $client.GetStream()
  $w = New-Object System.IO.StreamWriter($stream); $w.AutoFlush = $true
  $r = New-Object System.IO.StreamReader($stream)
  $w.Write($msg+"`n")
  $reply = $r.ReadLine()
  $client.Close()
  $reply
}
function J($s){ if(-not $s){return $null}; return ConvertFrom-Json -InputObject $s }

# --- Small polling helper ---
function Wait-Until($scriptblock, $timeoutSec=30, $intervalMs=500){
  $deadline = (Get-Date).AddSeconds($timeoutSec)
  while((Get-Date) -lt $deadline){
    if(& $scriptblock){ return $true }
    Start-Sleep -Milliseconds $intervalMs
  }
  return $false
}

# --- Sanity ping
$ping = J (Send-Poly '{"op":"ops"}')

# --- Step A: Add a cube (you do it)
SpeakSSML @"
<speak version='1.0' xml:lang='en-US'>
  <p>Step one.</p>
  <p>Add a cube.
     <break time='300ms'/> Press <emphasis level='moderate'>Shift + A</emphasis>,
     then Mesh, <break time='120ms'/> then Cube.</p>
</speak>
"@
$ok = Wait-Until {
  $m = J (Send-Poly '{"op":"get_mode"}')
  $a = J (Send-Poly '{"op":"active_exists"}')
  $c = J (Send-Poly '{"op":"active_is_cube"}')
  ($m -and $m.mode -eq 'OBJECT') -and ($a.exists) -and ($c.is_cube)
}
if(-not $ok){ Speak "Not seeing a cube selected. Try again."; throw "Cube not detected." }
Speak "Great. I see a cube selected."

# snapshot baseline X
$loc = J (Send-Poly '{"op":"get_active_loc"}')
$baseX = $loc.loc[0]

# --- Step B: Move +X by 1 (you do it)
SpeakSSML @"
<speak version='1.0' xml:lang='en-US'>
  <p>Now move the cube one unit along X.</p>
  <p>Press <emphasis>G</emphasis>, <break time='120ms'/> X,
     <break time='120ms'/> one, <break time='120ms'/> Enter.</p>
</speak>
"@
$passed = Wait-Until {
  $m = J (Send-Poly '{"op":"get_mode"}')
  $cur = J (Send-Poly '{"op":"get_active_loc"}')
  if(-not $m -or -not $cur){ return $false }
  ($m.mode -eq 'OBJECT') -and (($cur.loc[0] - $baseX) -ge 0.95)
}
if($passed){
  Speak "Nice move. Plus one on X. Step complete."
  Write-Host "✅ Teach Step 1 passed." -ForegroundColor Green
}else{
  Speak "I'm not seeing movement along X. Try again with G, X, one, then Enter."
  throw "Move verification failed."
}
