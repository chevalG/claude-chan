"""把 Qwen 编辑出的校服状态候选放进素材，并按 idle 的椅子/脚部区域做小幅对齐。

    .venv\\Scripts\\python.exe scripts\\place_uniform_keyframe.py thinking <候选.png> [--no-align]

- 输出 resources/assets-uniform/keyframes/claude-girl-uniform-<状态>-transparent-9x16.png
- 同时写 ComfyUI input 的 claude-chan-cu-<状态>-transparent-9x16.png（后续编辑用）
  和 gpt-chan-cu-<状态>-cyan-9x16.png（H3 生成用）
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "resources" / "assets-uniform"
INPUT = Path("D:/Comfyui-WF-2026.8.8/ComfyUI/input")
SIZE = (1026, 1824)
KEY = (0, 184, 212)


def small(im: Image.Image) -> np.ndarray:
    return np.asarray(im.convert("RGBA").resize((256, 456), Image.LANCZOS), dtype=np.float32)


def align_to_idle(im: Image.Image, ref: Image.Image) -> Image.Image:
    """在画面下部（椅子腿/鞋）比较，找候选相对 idle 的最佳平移。"""
    a = small(im)
    b = small(ref)
    y0, y1 = 330, 440
    best = (1e18, 0, 0)
    for dy in range(-24, 25, 2):
        for dx in range(-24, 25, 2):
            ay0, ay1 = y0 + dy, y1 + dy
            ax0, ax1 = 40 + dx, 216 + dx
            if ay0 < 0 or ay1 > a.shape[0] or ax0 < 0 or ax1 > a.shape[1]:
                continue
            sa = a[ay0:ay1, ax0:ax1, :3]
            sb = b[y0:y1, 40:216, :3]
            ma = a[ay0:ay1, ax0:ax1, 3] > 20
            mb = b[y0:y1, 40:216, 3] > 20
            mask = ma & mb
            if mask.sum() < 1000:
                continue
            err = float(np.abs(sa[mask] - sb[mask]).mean())
            if err < best[0]:
                best = (err, dx, dy)
    err, dx, dy = best
    print(f"对齐：平移 ({dx:+d}, {dy:+d})，下部残差 {err:.1f}")
    out = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    out.alpha_composite(im, ((SIZE[0] - im.width) // 2 + dx, (SIZE[1] - im.height) // 2 + dy))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("state")
    ap.add_argument("candidate")
    ap.add_argument("--no-align", action="store_true")
    args = ap.parse_args()
    im = Image.open(args.candidate).convert("RGBA").resize(SIZE, Image.LANCZOS)
    idle_path = ASSETS / "keyframes" / "claude-girl-uniform-idle-transparent-9x16.png"
    if not args.no_align and idle_path.exists():
        im = align_to_idle(im, Image.open(idle_path).convert("RGBA"))
    kf = ASSETS / "keyframes" / f"claude-girl-uniform-{args.state}-transparent-9x16.png"
    kf.parent.mkdir(parents=True, exist_ok=True)
    im.save(kf)
    im.save(INPUT / f"claude-chan-cu-{args.state}-transparent-9x16.png")
    cyan = Image.new("RGB", SIZE, KEY)
    cyan.paste(im, (0, 0), im)
    cyan.save(INPUT / f"gpt-chan-cu-{args.state}-cyan-9x16.png")
    print(f"已写入 {kf.relative_to(ROOT)} 和 ComfyUI input")


if __name__ == "__main__":
    main()
