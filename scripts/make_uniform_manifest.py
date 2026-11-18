"""生成 resources/assets-uniform/manifest.json（只登记已经生成的片段）。

    .venv\\Scripts\\python.exe scripts\\make_uniform_manifest.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "resources" / "assets-uniform"
KF = "keyframes/claude-girl-uniform-{}-transparent-9x16.png"
LOOP = "videos/loops/claude-girl-loop-uniform-{}-sway-transparent-9x16.avif"
TRANS = "videos/transitions/claude-girl-uniform-{}-{}-transparent-9x16.avif"

states = {
    "idle": {"hub": "A", "kind": "loop", "atHub": True, "keyframe": KF.format("idle")},
    "waiting": {"hub": "A", "kind": "loop", "atHub": True, "keyframe": KF.format("idle")},
    "thinking": {"hub": "A", "kind": "loop", "keyframe": KF.format("thinking")},
    "confirmation": {"hub": "A", "kind": "loop", "keyframe": KF.format("confirmation")},
    "complete": {"hub": "A", "kind": "loop", "keyframe": KF.format("complete")},
    "error": {"hub": "A", "kind": "oneshot", "keyframe": KF.format("error")},
    "drowsy": {"hub": "A", "kind": "loop", "keyframe": KF.format("drowsy")},
    "reading": {"hub": "A", "kind": "loop", "keyframe": KF.format("reading")},
    "writing": {"hub": "A", "kind": "loop", "keyframe": KF.format("writing")},
}

clips = []
loop_files = {
    "idle": "idle",
    "waiting": "idle",
    "thinking": "thinking",
    "confirmation": "confirmation",
    "complete": "complete",
    "drowsy": "drowsy",
    "reading": "reading",
    "writing": "writing",
}
for state, source in loop_files.items():
    f = LOOP.format(source)
    if (ASSETS / f).with_suffix(".webm").exists():
        clips.append({"id": f"{state}-loop", "type": "loop", "state": state, "file": f})
for state in ("thinking", "confirmation", "complete", "drowsy", "reading", "writing", "error"):
    intro = TRANS.format(state, "hub-to-state")
    outro = TRANS.format(state, "state-to-hub")
    if (ASSETS / intro).with_suffix(".webm").exists():
        clips.append({"id": f"{state}-intro", "type": "intro", "state": state, "from": "A", "file": intro})
    if (ASSETS / outro).with_suffix(".webm").exists():
        clips.append({"id": f"{state}-outro", "type": "outro", "state": state, "to": "A", "file": outro})

manifest = {
    "fps": 24,
    "width": 774,
    "height": 1376,
    "hubs": {"A": {"keyframe": KF.format("idle")}},
    "states": states,
    "clips": clips,
}
(ASSETS / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"uniform manifest：{len(clips)} 个片段")
for c in clips:
    print(" ", c["id"], c["file"])
