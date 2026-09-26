#!/usr/bin/env python3
"""
Generate the GrabBox desktop app icons.

Renders the brand mark at the sizes Tauri wants, then packs them into icon.ico
and icon.icns. Geometry and palette live in tools/brand.py; this file is only
the packaging.

Run:  python3 tools/make_app_icon.py
Out:  desktop/src-tauri/icons/{32x32,128x128,128x128@2x,icon}.png, icon.ico, icon.icns
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brand  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "desktop", "src-tauri", "icons")

PNG_SIZES = (("32x32.png", 32), ("128x128.png", 128),
             ("128x128@2x.png", 256), ("icon.png", 1024))
ICO_SIZES = (16, 24, 32, 48, 64, 256)
ICNS_SIZES = ((b"ic07", 128), (b"ic08", 256), (b"ic09", 512), (b"ic10", 1024))

_memo = {}


def at(size):
    """Encoded PNG at `size`, rendered once."""
    if size not in _memo:
        canvas = brand.render_tile(size)
        _memo[size] = brand.png_encode(canvas.buf, size)
    return _memo[size]


def main():
    os.makedirs(OUT, exist_ok=True)
    print("rendering GrabBox desktop icons ->", os.path.abspath(OUT))

    for name, size in PNG_SIZES:
        path = os.path.normpath(os.path.join(OUT, name))
        data = brand.write_png(path, brand.render_tile(size).buf, size)
        print("  wrote %s (%dx%d, %d bytes)" % (name, size, size, data))

    brand.write_ico(os.path.join(OUT, "icon.ico"),
                    [(s, at(s)) for s in ICO_SIZES])
    print("  wrote icon.ico (%d sizes)" % len(ICO_SIZES))
    brand.write_icns(os.path.join(OUT, "icon.icns"),
                     [(t, at(s)) for t, s in ICNS_SIZES])
    print("  wrote icon.icns (%d sizes)" % len(ICNS_SIZES))
    print("done")


if __name__ == "__main__":
    main()
