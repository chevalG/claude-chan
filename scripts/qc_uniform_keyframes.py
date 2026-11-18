"""校服版关键帧一致性检查：并排全身图 + 深/浅背景 Alpha 边缘 + 腿/鞋局部。

    .venv\\Scripts\\python.exe scripts\\qc_uniform_keyframes.py

输出 qc/keyframes-contact.png、qc/alpha-dark.png、qc/alpha-light.png、qc/legs.png。
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
KF = ROOT / "resources" / "assets-uniform" / "keyframes"
QC = ROOT / "qc"
QC.mkdir(exist_ok=True)
STATES = ["idle", "thinking", "reading", "writing", "complete", "confirmation", "drowsy", "error"]

ims = {}
for state in STATES:
    p = KF / f"claude-girl-uniform-{state}-transparent-9x16.png"
    if p.exists():
        ims[state] = Image.open(p).convert("RGBA")
if not ims:
    raise SystemExit("还没有关键帧")

H = 900
tiles = []
for state, im in ims.items():
    tiles.append(im.resize((round(im.width * H / im.height), H), Image.LANCZOS))
sheet = Image.new("RGBA", (sum(t.width for t in tiles) + 8 * (len(tiles) - 1), H), (255, 255, 255, 255))
x = 0
for tile in tiles:
    sheet.paste(tile, (x, 0), tile)
    x += tile.width + 8
sheet.convert("RGB").save(QC / "keyframes-contact.png")

for name, bg in (("dark", (30, 30, 40)), ("light", (245, 245, 245))):
    rows = []
    for state, im in ims.items():
        small = im.resize((im.width // 3, im.height // 3), Image.LANCZOS)
        canvas = Image.new("RGBA", small.size, bg + (255,))
        canvas.alpha_composite(small)
        head = im.crop((250, 80, 800, 630)).resize((300, 300), Image.LANCZOS)
        hc = Image.new("RGBA", head.size, bg + (255,))
        hc.alpha_composite(head)
        row = Image.new("RGBA", (canvas.width + 310, canvas.height), bg + (255,))
        row.paste(canvas, (0, 0))
        row.paste(hc, (canvas.width + 5, 0))
        rows.append(row)
    W = max(r.width for r in rows)
    out = Image.new("RGBA", (W, sum(r.height for r in rows) + 5 * (len(rows) - 1)), bg + (255,))
    y = 0
    for row in rows:
        out.paste(row, (0, y))
        y += row.height + 5
    out.convert("RGB").save(QC / f"alpha-{name}.png")

# 腿和鞋：每个状态底部 45% 的并排局部图
leg_tiles = []
for state, im in ims.items():
    crop = im.crop((int(im.width * 0.15), int(im.height * 0.55), int(im.width * 0.9), im.height))
    leg_tiles.append(crop.resize((round(crop.width * 500 / crop.height), 500), Image.LANCZOS))
legs = Image.new("RGB", (sum(t.width for t in leg_tiles) + 6 * (len(leg_tiles) - 1), 500), (245, 245, 245))
x = 0
for tile in leg_tiles:
    bg = Image.new("RGBA", tile.size, (245, 245, 245, 255))
    bg.alpha_composite(tile)
    legs.paste(bg.convert("RGB"), (x, 0))
    x += tile.width + 6
legs.save(QC / "legs.png")
print(f"已输出 {len(ims)} 个状态的关键帧检查图")
