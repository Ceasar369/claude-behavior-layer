#!/usr/bin/env python3
"""Generate icon.png — the app icon, drawn from code. No dependencies.

A macOS-style squircle holding two offset bars: one going out, one coming back.
Orange is a question waiting; green is an answer waiting. The same two colours
the status page uses, so the icon and the page read as one thing.

Drawn analytically with a signed-distance field, so every edge is antialiased
and the file is reproducible — there is no binary art to keep in sync.

    python3 make-icon.py [output.png]

build-app.sh calls this, then converts the result to icon.icns.
"""
import math
import struct
import sys
import zlib

SIZE = 1024

# macOS Big Sur proportions: the squircle fills ~80% of the canvas, centred,
# leaving transparent margin for the system's own shadow.
BOX = 824.0
BOX_R = BOX * 0.2237

BG_TOP = (0x22, 0x27, 0x31)
BG_BOTTOM = (0x0F, 0x11, 0x15)
ORANGE = (0xEF, 0x7F, 0x37)
GREEN = (0x46, 0xC4, 0x6A)

BAR_H = 122.0
BAR_GAP = 70.0
# Different widths and opposite offsets, so the pair reads as an exchange
# rather than an equals sign. The question goes out long; the answer comes
# back short, because an answer is shorter than the question that earned it.
TOP_W = 470.0
TOP_DX = -80.0
BOT_W = 330.0
BOT_DX = 130.0


def rounded_rect_sdf(px, py, cx, cy, hw, hh, r):
    """Signed distance to a rounded rectangle. Negative inside."""
    dx = abs(px - cx) - (hw - r)
    dy = abs(py - cy) - (hh - r)
    outside = math.hypot(max(dx, 0.0), max(dy, 0.0))
    inside = min(max(dx, dy), 0.0)
    return outside + inside - r


def coverage(d):
    """Antialiased coverage from a distance, one pixel of falloff."""
    return min(max(0.5 - d, 0.0), 1.0)


def build():
    c = SIZE / 2.0
    box_h = BOX / 2.0
    top_hw = TOP_W / 2.0
    bot_hw = BOT_W / 2.0
    bar_hh = BAR_H / 2.0
    bar_r = bar_hh
    offset = (BAR_H + BAR_GAP) / 2.0

    top_cx = c + TOP_DX
    top_cy = c - offset
    bot_cx = c + BOT_DX
    bot_cy = c + offset

    # Quick-reject bounds. Everything outside the squircle is transparent.
    lo = int(c - box_h) - 2
    hi = int(c + box_h) + 2

    rows = []
    for y in range(SIZE):
        row = bytearray(SIZE * 4)
        if y < lo or y > hi:
            rows.append(bytes(row))
            continue
        py = y + 0.5
        # Vertical gradient across the squircle only.
        t = min(max((py - (c - box_h)) / BOX, 0.0), 1.0)
        br = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t)
        bg = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t)
        bb = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t)

        for x in range(lo if lo > 0 else 0, hi + 1 if hi < SIZE else SIZE):
            px = x + 0.5
            a_box = coverage(rounded_rect_sdf(px, py, c, c, box_h, box_h, BOX_R))
            if a_box <= 0.0:
                continue

            r, g, b = br, bg, bb

            a_top = coverage(rounded_rect_sdf(px, py, top_cx, top_cy, top_hw, bar_hh, bar_r))
            if a_top > 0.0:
                r = int(r + (ORANGE[0] - r) * a_top)
                g = int(g + (ORANGE[1] - g) * a_top)
                b = int(b + (ORANGE[2] - b) * a_top)

            a_bot = coverage(rounded_rect_sdf(px, py, bot_cx, bot_cy, bot_hw, bar_hh, bar_r))
            if a_bot > 0.0:
                r = int(r + (GREEN[0] - r) * a_bot)
                g = int(g + (GREEN[1] - g) * a_bot)
                b = int(b + (GREEN[2] - b) * a_bot)

            i = x * 4
            row[i] = r
            row[i + 1] = g
            row[i + 2] = b
            row[i + 3] = int(a_box * 255)

        rows.append(bytes(row))
    return rows


def write_png(path, rows):
    raw = b"".join(b"\x00" + r for r in rows)

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "icon.png"
    write_png(out, build())
    print(f"ICON_PNG={out} {SIZE}x{SIZE}")
