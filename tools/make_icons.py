#!/usr/bin/env python3
"""
Generate the GrabBox extension icons - no Pillow needed, just zlib.

Two states per size, because the toolbar icon has to say something:
    icon-<n>.png         full colour  -> this page has things worth grabbing
    icon-faded-<n>.png   desaturated  -> nothing detected here

Run:  python3 tools/make_icons.py
"""

import os
import struct
import zlib

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "extension", "icons")
SIZES = (16, 32, 48, 128)

TOP = (79, 140, 255)      # #4f8cff
BOTTOM = (139, 92, 246)   # #8b5cf6
WHITE = (255, 255, 255)


def rounded(px, py, w, h, r):
    """Signed distance-ish test for a rounded rectangle mask."""
    if r <= 0:
        return True
    x = min(max(px, r), w - r)
    y = min(max(py, r), h - r)
    return (px - x) ** 2 + (py - y) ** 2 <= r * r


def arrow(px, py, cx, top, bottom, thickness):
    """Stem + chevron of a download arrow, plus the tray line under it."""
    half = thickness / 2.0
    stem_bottom = bottom - thickness * 2.2
    # vertical stem
    if abs(px - cx) <= half and top <= py <= stem_bottom:
        return True
    # chevron
    dy = py - stem_bottom
    if 0 <= dy <= thickness * 2.2:
        spread = dy * 0.95
        if abs(abs(px - cx) - spread) <= half:
            return True
    # tray
    tray_top = bottom - thickness * 0.5
    if tray_top <= py <= bottom and abs(px - cx) <= thickness * 2.6:
        return True
    return False


def pixel(size, x, y):
    r = max(2.0, size * 0.23)
    if not rounded(x + 0.5, y + 0.5, size, size, r):
        return (0, 0, 0, 0)
    t = y / max(1.0, size - 1)
    col = tuple(int(TOP[i] + (BOTTOM[i] - TOP[i]) * t) for i in range(3))
    cx = size / 2.0
    thick = max(1.2, size * 0.115)
    if arrow(x + 0.5, y + 0.5, cx, size * 0.24, size * 0.80, thick):
        return WHITE + (255,)
    return col + (255,)


def fade(rgba, amount=0.42):
    r, g, b, a = rgba
    grey = int(0.299 * r + 0.587 * g + 0.114 * b)
    mix = lambda c: int(c * amount + grey * (1 - amount))
    return (mix(r), mix(g), mix(b), max(90, int(a * 0.75)))


def png(size, faded):
    rows = []
    for y in range(size):
        row = bytearray([0])  # filter: none
        for x in range(size):
            px = pixel(size, x, y)
            if faded:
                px = fade(px)
            row += bytes(px)
        rows.append(bytes(row))
    raw = b"".join(rows)

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def main():
    os.makedirs(OUT, exist_ok=True)
    for size in SIZES:
        for faded in (False, True):
            name = "icon-faded-%d.png" % size if faded else "icon-%d.png" % size
            path = os.path.normpath(os.path.join(OUT, name))
            with open(path, "wb") as fh:
                fh.write(png(size, faded))
            print("wrote %s (%d bytes)" % (os.path.relpath(path), os.path.getsize(path)))


if __name__ == "__main__":
    main()
