#!/usr/bin/env python3
"""
Generate the GrabBox desktop app icons - pure python, no Pillow (zlib only).

Renders the brand mark (rounded-square gradient + download arrow) at the sizes
Tauri wants, then packs them into icon.ico and icon.icns.

Run:  python3 tools/make_app_icon.py
Out:  desktop/src-tauri/icons/{32x32,128x128,128x128@2x,icon}.png, icon.ico, icon.icns
"""

import os
import struct
import zlib

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "desktop", "src-tauri", "icons")

TOP = (79, 140, 255)      # #4f8cff
BOTTOM = (139, 92, 246)   # #8b5cf6


def dist_to_segment(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / length_sq))
    cx, cy = x1 + t * dx, y1 + t * dy
    return ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5


def render(size):
    """RGBA bytearray of the icon at `size` px (drawn in 64-unit space)."""
    s = size / 64.0
    radius = 14.0 * s
    px = bytearray(size * size * 4)
    stem_half = 2.75 * s
    chevron_w = 2.75 * s
    tray_half = 2.75 * s
    for y in range(size):
        row = y * size * 4
        gy = y / size
        for x in range(size):
            i = row + x * 4
            # outside the rounded rect -> transparent
            cx = min(max(x, radius), size - radius)
            cy = min(max(y, radius), size - radius)
            if (x - cx) ** 2 + (y - cy) ** 2 > radius * radius:
                continue
            # gradient (diagonal)
            t = (x * 0.3 + y * 0.7) / size
            r = TOP[0] + (BOTTOM[0] - TOP[0]) * t
            g = TOP[1] + (BOTTOM[1] - TOP[1]) * t
            b = TOP[2] + (BOTTOM[2] - TOP[2]) * t
            a = 255
            # download arrow, white
            if abs(x - 32 * s) <= stem_half and 14 * s <= y <= 36 * s:
                r = g = b = 255
            d1 = dist_to_segment(x, y, 21.5 * s, 29.5 * s, 32 * s, 40 * s)
            d2 = dist_to_segment(x, y, 42.5 * s, 29.5 * s, 32 * s, 40 * s)
            if min(d1, d2) <= chevron_w:
                r, g, b = 245, 245, 255
            if abs(y - 48 * s) <= tray_half and 18 * s <= x <= 46 * s:
                r, g, b = 240, 240, 250
            px[i] = int(r)
            px[i + 1] = int(g)
            px[i + 2] = int(b)
            px[i + 3] = a
    return px


def downscale(src, size, factor):
    """Box-average `src` (size*factor) down to `size`."""
    big = size * factor
    out = bytearray(size * size * 4)
    for y in range(size):
        for x in range(size):
            acc = [0, 0, 0, 0]
            for dy in range(factor):
                base = ((y * factor + dy) * big + x * factor) * 4
                for dx in range(factor):
                    o = base + dx * 4
                    for c in range(4):
                        acc[c] += src[o + c]
            o = (y * size + x) * 4
            n = factor * factor
            for c in range(4):
                out[o + c] = acc[c] // n
    return out


def png_encode(px, size):
    def chunk(typ, data):
        return (struct.pack(">I", len(data)) + typ + data
                + struct.pack(">I", zlib.crc32(typ + data) & 0xffffffff))

    raw = bytearray()
    stride = size * 4
    for y in range(size):
        raw.append(0)
        raw += px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def write_png(name, size):
    # supersample small icons 4x for smooth edges; big ones drawn directly
    if size <= 256:
        data = downscale(render(size * 4), size, 4)
    else:
        data = render(size)
    path = os.path.join(OUT, name)
    with open(path, "wb") as fh:
        fh.write(png_encode(data, size))
    print("  wrote %s (%dx%d)" % (name, size, size))


def write_ico(pngs):
    """pngs: list of (size, png_bytes)."""
    header = struct.pack("<HHH", 0, 1, len(pngs))
    entries = b""
    offset = 6 + 16 * len(pngs)
    body = b""
    for size, data in pngs:
        entries += struct.pack("<BBBBHHII",
                               size if size < 256 else 0, size if size < 256 else 0,
                               0, 0, 1, 32, len(data), offset)
        body += data
        offset += len(data)
    with open(os.path.join(OUT, "icon.ico"), "wb") as fh:
        fh.write(header + entries + body)
    print("  wrote icon.ico (%d sizes)" % len(pngs))


def write_icns(entries):
    """entries: list of (ostype, png_bytes)."""
    body = b""
    for ostype, data in entries:
        body += ostype + struct.pack(">I", len(data) + 8) + data
    with open(os.path.join(OUT, "icon.icns"), "wb") as fh:
        fh.write(b"icns" + struct.pack(">I", len(body) + 8) + body)
    print("  wrote icon.icns (%d sizes)" % len(entries))


def encode_in_memory(size):
    if size <= 256:
        return png_encode(downscale(render(size * 4), size, 4), size)
    return png_encode(render(size), size)


def main():
    os.makedirs(OUT, exist_ok=True)
    print("rendering GrabBox icons ->", os.path.abspath(OUT))
    write_png("32x32.png", 32)
    write_png("128x128.png", 128)
    write_png("128x128@2x.png", 256)
    write_png("icon.png", 1024)
    write_ico([(16, encode_in_memory(16)), (24, encode_in_memory(24)),
               (32, encode_in_memory(32)), (48, encode_in_memory(48)),
               (64, encode_in_memory(64)), (256, encode_in_memory(256))])
    write_icns([(b"ic07", encode_in_memory(128)), (b"ic08", encode_in_memory(256)),
                (b"ic09", encode_in_memory(512)), (b"ic10", encode_in_memory(1024))])
    print("done")


if __name__ == "__main__":
    main()
