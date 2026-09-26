#!/usr/bin/env python3
"""
Generate the GrabBox web assets: the favicon and the logo in the app's header.

Both come from the same mark as every other surface (tools/brand.py). The
header logo is inlined into grabbox/web/index.html because that page already
keeps its whole icon set in one hidden <svg> block and references it with
<use href="#i-logo">; pulling in an external file there would add a request
for one glyph.

Run:  python3 tools/make_web_icons.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brand  # noqa: E402

WEB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "grabbox", "web")

#: The page rounds the corners itself (.logo has a border-radius), so the
#: symbol is full-bleed rather than a rounded tile.
LOGO_SYMBOL = '  <symbol id="i-logo" viewBox="0 0 100 100">'


def _body(tile, view_size):
    """The mark's SVG, minus the <svg> wrapper, for embedding in a <symbol>."""
    doc = brand.svg(view_size, tile=tile)
    return doc.split("\n", 1)[1].rsplit("</svg>", 1)[0].rstrip()


def write_favicon():
    path = os.path.join(WEB, "icon.svg")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(brand.svg(64, tile=True))
    print("  wrote %s" % os.path.relpath(path, WEB))


def patch_header_logo():
    path = os.path.join(WEB, "index.html")
    html = open(path, encoding="utf-8").read()
    inner = "\n".join("    " + l if l.strip() else l
                      for l in _body(True, 100).split("\n"))
    symbol = "%s\n%s\n  </symbol>" % (LOGO_SYMBOL, inner)
    new, n = re.subn(r'  <symbol id="i-logo".*?</symbol>',
                     lambda _: symbol, html, count=1, flags=re.S)
    if n != 1:
        print("  WARNING: no #i-logo symbol in index.html - left it alone")
        return
    # The old rounded-square logo carried its own <defs>; drop it if the new
    # one did not reintroduce it, so we do not leave dead gradients behind.
    if 'id="gb-grad"' not in symbol and "gb-grad" not in new.replace(symbol, ""):
        new = re.sub(r"  <defs>.*?</defs>\n", "", new, count=1, flags=re.S)
    open(path, "w", encoding="utf-8").write(new)
    print("  wrote %s (#i-logo)" % os.path.relpath(path, WEB))


def main():
    print("rendering GrabBox web assets ->", os.path.abspath(WEB))
    write_favicon()
    patch_header_logo()
    print("done")


if __name__ == "__main__":
    main()
