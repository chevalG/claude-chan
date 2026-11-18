"""校服版：为 complete / confirmation / drowsy 生成程序化呼吸 loop（固定关键帧 + 极轻微缩放）。

    .venv\\Scripts\\python.exe scripts\\make_uniform_loops.py

输出 resources/assets-uniform/videos/loops/claude-girl-loop-uniform-<状态>-sway-transparent-9x16.webm。
这些状态没有大幅动作，保持关键帧不变可以避免书页、手指和椅子变形。
"""

import sys
from pathlib import Path

import av
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
KF = ROOT / "resources" / "assets-uniform" / "keyframes"
OUT = ROOT / "resources" / "assets-uniform" / "videos" / "loops"
W, H = 774, 1376
CW, CH, PAD_X, PAD_Y = 768, 1344, 3, 16
FRAMES = 138
STATES = tuple(sys.argv[1:]) or ("complete", "confirmation", "drowsy")


def load(state: str) -> Image.Image:
    im = Image.open(KF / f"claude-girl-uniform-{state}-transparent-9x16.png").convert("RGBA")
    im = im.resize((CW, CH), Image.LANCZOS)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    canvas.paste(im, (PAD_X, PAD_Y))
    return canvas


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for state in STATES:
        base = load(state)
        frames = []
        for i in range(FRAMES):
            t = i / FRAMES
            s = 1.0 + 0.0015 * np.sin(2 * np.pi * t)
            nw, nh = round(W * s), round(H * s)
            scaled = base.resize((nw, nh), Image.LANCZOS)
            canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            canvas.paste(scaled, ((W - nw) // 2, (H - nh) // 2))
            frames.append(np.asarray(canvas, dtype=np.uint8))
        path = OUT / f"claude-girl-loop-uniform-{state}-sway-transparent-9x16.webm"
        with av.open(str(path), "w", format="webm") as out:
            stream = out.add_stream("libvpx-vp9", rate=24)
            stream.width, stream.height = W, H
            stream.pix_fmt = "yuva420p"
            stream.options = {"crf": "28", "b:v": "0", "auto-alt-ref": "0", "row-mt": "1", "deadline": "good", "cpu-used": "2"}
            for f in frames:
                for packet in stream.encode(av.VideoFrame.from_ndarray(f, format="rgba")):
                    out.mux(packet)
            for packet in stream.encode():
                out.mux(packet)
        print(f"{state}: {FRAMES} 帧 -> {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
