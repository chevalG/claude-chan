"""Claude-Chan 校服版：用 1 秒余弦交叉溶解连接枢纽 A 与各状态。

    .venv\\Scripts\\python.exe scripts\\make_uniform_transitions.py [状态...]

输出 resources/assets-uniform/videos/transitions/claude-girl-uniform-<状态>-<方向>-transparent-9x16.webm。
idle 和 waiting 共用 idle；error 用关键帧。
"""

from __future__ import annotations

import sys
from pathlib import Path

import av
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / "resources" / "assets-uniform"
LOOPS = A / "videos" / "loops"
OUT = A / "videos" / "transitions"
KF = A / "keyframes"
W, H = 774, 1376
CW, CH, PX, PY = 768, 1344, 3, 16
FRAMES = 24
STATES = tuple(sys.argv[1:]) or ("thinking", "reading", "writing", "complete", "confirmation", "drowsy", "error")


def image_frame(im: Image.Image) -> np.ndarray:
    im = im.convert("RGBA").resize((CW, CH), Image.LANCZOS)
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    c.paste(im, (PX, PY))
    return np.asarray(c, dtype=np.float32)


def first_frame(path: Path) -> np.ndarray:
    if path.suffix == ".png":
        return image_frame(Image.open(path))
    with av.open(str(path)) as c:
        dec = av.CodecContext.create("libvpx-vp9", "r")
        for p in c.demux(c.streams.video[0]):
            for f in dec.decode(p):
                return np.asarray(Image.fromarray(f.to_ndarray(format="rgba"), "RGBA").resize((W, H), Image.LANCZOS), dtype=np.float32)
    raise RuntimeError(f"读不到帧：{path}")


def encode(frames: list[np.ndarray], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with av.open(str(path), "w", format="webm") as out:
        s = out.add_stream("libvpx-vp9", rate=24)
        s.width, s.height = W, H
        s.pix_fmt = "yuva420p"
        s.options = {"crf": "28", "b:v": "0", "auto-alt-ref": "0", "row-mt": "1", "deadline": "good", "cpu-used": "2"}
        for f in frames:
            for p in s.encode(av.VideoFrame.from_ndarray(np.clip(f, 0, 255).round().astype(np.uint8), format="rgba")):
                out.mux(p)
        for p in s.encode():
            out.mux(p)


def crossfade(a: np.ndarray, b: np.ndarray) -> list[np.ndarray]:
    out = []
    for i in range(FRAMES):
        t = i / (FRAMES - 1)
        w = 0.5 - 0.5 * np.cos(np.pi * t)
        out.append(np.clip(a * (1 - w) + b * w, 0, 255).round().astype(np.uint8))
    return out


def state_frame(state: str) -> np.ndarray:
    if state == "error":
        return first_frame(KF / "claude-girl-uniform-error-transparent-9x16.png")
    loop = LOOPS / f"claude-girl-loop-uniform-{state}-sway-transparent-9x16.webm"
    if loop.exists():
        return first_frame(loop)
    return first_frame(KF / f"claude-girl-uniform-{state}-transparent-9x16.png")


def main() -> None:
    idle = first_frame(LOOPS / "claude-girl-loop-uniform-idle-sway-transparent-9x16.webm")
    OUT.mkdir(parents=True, exist_ok=True)
    for state in STATES:
        try:
            target = state_frame(state)
        except Exception as exc:
            print(f"跳过 {state}：{exc}")
            continue
        for direction, a, b in (
            ("hub-to-state", idle, target),
            ("state-to-hub", target, idle),
        ):
            name = f"claude-girl-uniform-{state}-{direction}-transparent-9x16.webm"
            encode(crossfade(a, b), OUT / name)
            print(f"{name}: {FRAMES} 帧")


if __name__ == "__main__":
    main()