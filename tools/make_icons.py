#!/usr/bin/env python3
"""
Generate the GrabBox extension icons - no Pillow needed, just zlib.

Two states per size, because the toolbar icon has to say something:
    icon-<n>.png         full colour  -> this page has things worth grabbing
    icon-faded-<n>.png   desaturated  -> nothing detected here

The toolbar composites the mark over its own surface, so these are the
transparent-background render, not the desktop tile. Below 32px the speed
sparks are dropped - at 16px they are a third of a pixel and just muddy the
shape.

Run:  python3 tools/make_icons.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brand  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "extension", "icons")
SIZES = (16, 32, 48, 128)
#: Below this the sparks are noise rather than detail.
SPARK_THRESHOLD = 48


def main():
    os.makedirs(OUT, exist_ok=True)
    for size in SIZES:
        canvas = brand.render(size, sparks=size >= SPARK_THRESHOLD)
        bright = brand.write_png(
            os.path.join(OUT, "icon-%d.png" % size), canvas.buf, size)
        faded = brand.write_png(
            os.path.join(OUT, "icon-faded-%d.png" % size),
            brand.desaturate(canvas.buf), size)
        print("wrote icon-%d.png (%d B) and icon-faded-%d.png (%d B)"
              % (size, bright, size, faded))
    print("done")


if __name__ == "__main__":
    main()
