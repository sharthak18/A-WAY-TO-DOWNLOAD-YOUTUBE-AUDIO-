#!/usr/bin/env python3
"""
The GrabBox mark, in one place.

An isometric box with a download arrow cut into its front corner, plus three
"speed" sparks off the top-right edge. Every surface - Android launcher,
notification shade, Tauri desktop, browser extension, web app, PyInstaller -
renders from the geometry and palette defined here, so the brand cannot drift
between them.

Design space is 100x100 with the origin top-left; callers map that onto
whatever canvas they need. Pure Python: no Pillow, zlib does the PNG work.

Consumers:
    tools/make_android_icons.py
    tools/make_app_icon.py       (Tauri desktop)
    tools/make_icons.py          (browser extension)
"""

import math
import os
import struct
import zlib

# --------------------------------------------------------------- palette --

#: Sampled off the brand artwork. Deep, saturated blue-violet rather than the
#: lighter tint the old rounded-square used.
BRAND_TOP = (0x46, 0x52, 0xF6)      # top face, lit from the upper left
BRAND_MID = (0x5B, 0x2B, 0xE4)      # right face
BRAND_DEEP = (0x63, 0x1F, 0xD8)     # bottom right, deepest
BRAND_ARROW = (0xFF, 0xFF, 0xFF)    # the arrow punched out of the front
ARROW_ALPHA = 0.88
SPARK_TOP = (0x4F, 0xAA, 0xFF)      # the three speed sparks
SPARK_BOTTOM = (0x1B, 0x7D, 0xE4)

#: Flat versions for callers that cannot do gradients (VectorDrawable paths,
#: the monochrome launcher layer, the status-bar icon).
FACE_TOP = (0x46, 0x52, 0xF6)
FACE_LEFT = (0x39, 0x2F, 0xEA)
FACE_RIGHT = (0x58, 0x24, 0xDE)
SPARK_FLAT = (0x2C, 0x8D, 0xF2)


# -------------------------------------------------------------- geometry --
# A cube seen from slightly above: the hexagon outline, plus the three faces
# that meet at the front-top corner (CENTRE).

TOP = (50.0, 12.0)
LEFT = (16.5, 26.8)
RIGHT = (83.5, 26.8)
CENTRE = (50.0, 41.6)
LEFT_BOTTOM = (16.5, 56.8)
RIGHT_BOTTOM = (83.5, 56.8)
BOTTOM = (50.0, 71.6)

FACE_TOP_POLY = [TOP, RIGHT, CENTRE, LEFT]
FACE_LEFT_POLY = [LEFT, CENTRE, BOTTOM, LEFT_BOTTOM]
FACE_RIGHT_POLY = [CENTRE, RIGHT, RIGHT_BOTTOM, BOTTOM]
#: Full silhouette, clockwise from the top vertex.
SILHOUETTE = [TOP, RIGHT, RIGHT_BOTTOM, BOTTOM, LEFT_BOTTOM, LEFT]

#: The download arrow, straddling the front corner edge.
ARROW_SHAFT = (46.2, 30.0, 53.8, 57.5)     # x0, y0, x1, y1
ARROW_SHAFT_R = 3.8
ARROW_HEAD = [(38.8, 54.0), (61.2, 54.0), (50.0, 70.0)]

#: Three sparks off the top-right edge: vertical, diagonal, horizontal. They
#: have to clear each other by a couple of units or they fuse into one blob at
#: small sizes, and the lowest one reaches past the cube's right vertex - the
#: asymmetry is in the original mark.
SPARK_R = 2.0
SPARKS = [
    ("rect", (62.0, 1.0, 66.4, 10.0)),
    ("line", (70.0, 7.5), (75.0, 12.5)),
    ("rect", (72.0, 16.0, 83.0, 20.4)),
]

#: Axis-aligned bounds of the whole mark (cube + sparks).
BBOX = (16.5, 1.0, 83.0, 71.6)


# --------------------------------------------------------- polygon utils --

def rounded_rect(x0, y0, x1, y1, r, steps=10):
    """Polygon for a rectangle with rounded corners, clockwise from top-left."""
    r = max(0.0, min(r, (x1 - x0) / 2.0, (y1 - y0) / 2.0))
    if r <= 0.01:
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    pts = []
    for cx, cy, a0 in (
        (x1 - r, y0 + r, -90.0),      # top-right
        (x1 - r, y1 - r, 0.0),        # bottom-right
        (x0 + r, y1 - r, 90.0),       # bottom-left
        (x0 + r, y0 + r, 180.0),      # top-left
    ):
        for i in range(steps + 1):
            a = math.radians(a0 + 90.0 * i / steps)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def round_segment(p0, p1, r, steps=10):
    """Polygon for a thick line between p0 and p1 with round caps."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dy) or 1.0
    ux, uy = dx / length, dy / length
    nx, ny = -uy, ux
    pts = []
    for i in range(steps + 1):                       # cap at p1
        a = math.atan2(uy, ux) - math.pi / 2 + math.pi * i / steps
        pts.append((p1[0] + r * math.cos(a), p1[1] + r * math.sin(a)))
    for i in range(steps + 1):                       # cap at p0
        a = math.atan2(uy, ux) + math.pi / 2 + math.pi * i / steps
        pts.append((p0[0] + r * math.cos(a), p0[1] + r * math.sin(a)))
    return pts


def spark_polys():
    """The three speed sparks, as polygons."""
    out = []
    for shape, *rest in SPARKS:
        if shape == "rect":
            x0, y0, x1, y1 = rest[0]
            out.append(rounded_rect(x0, y0, x1, y1, SPARK_R))
        else:
            out.append(round_segment(rest[0], rest[1], SPARK_R))
    return out


def arrow_polys():
    """Shaft and head of the download arrow, as polygons."""
    x0, y0, x1, y1 = ARROW_SHAFT
    return [rounded_rect(x0, y0, x1, y1, ARROW_SHAFT_R), list(ARROW_HEAD)]


def fit(box, into, scale_to=None):
    """Map design space into a square canvas of side `into`.

    Returns ``(scale, offset_x, offset_y)`` for
    ``design -> device: d * scale + offset``.
    """
    bx0, by0, bx1, by1 = box
    w, h = bx1 - bx0, by1 - by0
    s = ((scale_to or into) / max(w, h)) if into else 1.0
    return s, (into - w * s) / 2.0 - bx0 * s, (into - h * s) / 2.0 - by0 * s


# ------------------------------------------------------------- gradients --

def _lerp(c0, c1, t):
    t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
    return tuple(int(round(c0[i] + (c1[i] - c0[i]) * t)) for i in range(3))


def _rgba(colour, alpha=255):
    return (colour[0], colour[1], colour[2], alpha)


def gradient(p0, p1, c0, c1):
    """Colour function of (x, y) along the p0 -> p1 axis, in design space."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length_sq = dx * dx + dy * dy or 1.0

    def colour(x, y):
        t = ((x - p0[0]) * dx + (y - p0[1]) * dy) / length_sq
        return _lerp(c0, c1, t)
    return colour


# --------------------------------------------------------------- canvas ---

class Canvas(object):
    """An RGBA raster with analytic anti-aliasing. Straight alpha, 0..255."""

    def __init__(self, size, xform=None, background=(0, 0, 0, 0)):
        self.size = size
        self.buf = bytearray(size * size * 4)
        if background and background[3]:
            r, g, b, a = background
            self.buf[0::4] = bytes([r]) * (size * size)
            self.buf[1::4] = bytes([g]) * (size * size)
            self.buf[2::4] = bytes([b]) * (size * size)
            self.buf[3::4] = bytes([a]) * (size * size)
        # (scale, offset_x, offset_y) mapping design space -> device pixels
        self.xform = xform or (size / 100.0, 0.0, 0.0)

    def fill_poly(self, poly, colour, alpha=1.0, samples=4):
        """Fill `poly` (design space) with a solid colour or a colour fn."""
        if alpha <= 0.0:
            return
        s, ox, oy = self.xform
        pts = [(x * s + ox, y * s + oy) for x, y in poly]
        size = self.size
        if len(pts) < 3:
            return
        y0 = max(0, int(math.floor(min(p[1] for p in pts))))
        y1 = min(size - 1, int(math.ceil(max(p[1] for p in pts))))
        x_lo = max(0, int(math.floor(min(p[0] for p in pts))))
        x_hi = min(size - 1, int(math.ceil(max(p[0] for p in pts))))
        if y1 < y0 or x_hi < x_lo:
            return
        n = len(pts)
        buf = self.buf
        inv_s = 1.0 / s
        solid = colour if not callable(colour) else None
        cov = [0.0] * (x_hi - x_lo + 2)
        row_bytes = size * 4
        for y in range(y0, y1 + 1):
            for i in range(len(cov)):
                cov[i] = 0.0
            for k in range(samples):
                sy = y + (k + 0.5) / samples
                xs = []
                for i in range(n):
                    ax, ay = pts[i]
                    bx, by = pts[(i + 1) % n]
                    if (ay <= sy < by) or (by <= sy < ay):
                        t = (sy - ay) / (by - ay)
                        xs.append(ax + t * (bx - ax))
                if not xs:
                    continue
                xs.sort()
                for j in range(0, len(xs) - 1, 2):
                    xa, xb = xs[j], xs[j + 1]
                    if xb <= x_lo or xa >= x_hi + 1:
                        continue
                    xa = max(xa, x_lo)
                    xb = min(xb, x_hi + 1)
                    i0 = int(xa)
                    i1 = min(int(xb), x_hi + 1)
                    if i1 == i0 and xb <= i0:
                        i1 = i0 + 1
                    for px in range(i0, min(i1, x_hi + 1)):
                        left = px if px > xa else xa
                        right = px + 1 if (px + 1) < xb else xb
                        if right > left:
                            cov[px - x_lo] += (right - left) / samples
            base = y * row_bytes
            dy = (y + 0.5 - oy) * inv_s
            for px in range(x_lo, x_hi + 1):
                c = cov[px - x_lo]
                if c <= 0.0:
                    continue
                if c > 1.0:
                    c = 1.0
                a = c * alpha
                if solid is not None:
                    r, g, b = solid
                else:
                    r, g, b = colour((px + 0.5 - ox) * inv_s, dy)
                o = base + px * 4
                da = buf[o + 3] / 255.0
                out_a = a + da * (1.0 - a)
                if out_a <= 0.0:
                    continue
                for ch, sc in ((0, r), (1, g), (2, b)):
                    buf[o + ch] = int(
                        round((sc * a + buf[o + ch] * da * (1.0 - a)) / out_a))
                buf[o + 3] = int(round(out_a * 255))

    def to_png(self):
        return png_encode(self.buf, self.size)


# ------------------------------------------------------------- encoders ---

def png_encode(px, size):
    """RGBA bytearray -> PNG bytes."""
    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))
    stride = size * 4
    raw = bytearray()
    for y in range(size):
        raw.append(0)                       # filter: none
        raw += px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def write_png(path, px, size):
    with open(path, "wb") as fh:
        fh.write(png_encode(px, size))
    return os.path.getsize(path)


def write_ico(path, pngs):
    """pngs: list of (size, png_bytes), ascending."""
    header = struct.pack("<HHH", 0, 1, len(pngs))
    entries = b""
    offset = 6 + 16 * len(pngs)
    body = b""
    for size, data in pngs:
        entries += struct.pack("<BBBBHHII",
                               size if size < 256 else 0,
                               size if size < 256 else 0,
                               0, 0, 1, 32, len(data), offset)
        body += data
        offset += len(data)
    with open(path, "wb") as fh:
        fh.write(header + entries + body)


def write_icns(path, entries):
    """entries: list of (ostype, png_bytes)."""
    body = b""
    for ostype, data in entries:
        body += ostype + struct.pack(">I", len(data) + 8) + data
    with open(path, "wb") as fh:
        fh.write(b"icns" + struct.pack(">I", len(body) + 8) + body)


# -------------------------------------------------------------- renderers --

#: The rounded tile behind the mark, for the desktop and pre-Android-26
#: launcher icons. A bare transparent mark vanishes on a light desktop.
TILE_TOP = (0x6E, 0x74, 0xFF)
TILE_BOTTOM = (0x8E, 0x5E, 0xF4)
TILE_RADIUS = 22.0
#: How much of the tile the mark fills.
TILE_MARK_SPAN = 76.0


def _draw_mark(canvas, samples, sparks=True):
    """Paint the cube, the sparks and the arrow using canvas.xform."""
    # Faces, lit from the upper left so the cube reads as a solid object.
    canvas.fill_poly(FACE_TOP_POLY,
                     gradient(LEFT, RIGHT, BRAND_TOP, BRAND_MID), samples=samples)
    canvas.fill_poly(FACE_LEFT_POLY,
                     gradient(LEFT, BOTTOM, FACE_LEFT, BRAND_MID),
                     samples=samples)
    canvas.fill_poly(FACE_RIGHT_POLY,
                     gradient(CENTRE, BOTTOM, BRAND_MID, BRAND_DEEP),
                     samples=samples)
    if sparks:                          # they blur into nothing below ~32px
        for poly in spark_polys():
            canvas.fill_poly(poly,
                             gradient((64, 1), (86, 20), SPARK_TOP, SPARK_BOTTOM),
                             samples=samples)
    for poly in arrow_polys():
        canvas.fill_poly(poly, BRAND_ARROW, alpha=ARROW_ALPHA, samples=samples)


def render(size, sparks=True, background=None, samples=None):
    """The mark alone, on transparency. Android's foreground layer, the
    extension toolbar icon and anything that composites over its own surface."""
    if samples is None:
        samples = 4 if size <= 256 else 3
    canvas = Canvas(size, fit(BBOX, size), background)
    _draw_mark(canvas, samples, sparks)
    return canvas


def mask_circle(canvas):
    """Knock out everything outside the inscribed circle."""
    size = canvas.size
    r = size / 2.0
    c = size / 2.0
    for y in range(size):
        dy = y + 0.5 - c
        for x in range(size):
            dx = x + 0.5 - c
            if dx * dx + dy * dy > r * r:
                o = (y * size + x) * 4
                canvas.buf[o:o + 4] = b"\0\0\0\0"
    return canvas


def render_tile(size, samples=None, corner=True, round_mask=False):
    """A brand tile with the mark centred on it.

    ``corner`` gives the rounded square the desktop icon wants; ``round_mask``
    clips to a circle for Android's pre-API-26 round launcher icon.
    """
    if samples is None:
        samples = 4 if size <= 256 else 3
    if corner:
        canvas = Canvas(size, (size / 100.0, 0.0, 0.0))
        canvas.fill_poly(rounded_rect(0, 0, 100, 100, TILE_RADIUS),
                         gradient((0, 0), (100, 100), TILE_TOP, TILE_BOTTOM),
                         samples=samples)
    else:
        canvas = Canvas(size, (size / 100.0, 0.0, 0.0),
                        _rgba(gradient((0, 0), (100, 100),
                                       TILE_TOP, TILE_BOTTOM)(50, 50), 255))
    canvas.xform = xform(BBOX, 100.0, TILE_MARK_SPAN)
    _draw_mark(canvas, samples)
    if round_mask:
        mask_circle(canvas)
    return canvas


def desaturate(px):
    """The toolbar's "nothing here" state: same shape, colours drained."""
    out = bytearray(px)
    for i in range(0, len(out), 4):
        r, g, b, a = out[i], out[i + 1], out[i + 2], out[i + 3]
        grey = 0.299 * r + 0.587 * g + 0.114 * b
        for ch, val in ((0, r), (1, g), (2, b)):
            out[i + ch] = int(val * 0.45 + grey * 0.55)
        out[i + 3] = max(0, int(a * 0.72))
    return out


# ------------------------------------------------------------------ SVG ---

def _pts(poly, fmt="%.2f"):
    return " ".join((fmt % x) + "," + (fmt % y) for x, y in poly)


def _grad_xml(gid, p0, p1, c0, c1, bbox):
    x0, y0, x1, y1 = bbox
    return (
        '  <linearGradient id="%s" x1="%g" y1="%g" x2="%g" y2="%g">\n'
        '    <stop offset="0" stop-color="%s"/>\n'
        '    <stop offset="1" stop-color="%s"/>\n'
        '  </linearGradient>\n' % (
            gid, p0[0], p0[1], p1[0], p1[1],
            "#%02x%02x%02x" % c0, "#%02x%02x%02x" % c1))


def svg(size=64, tile=False):
    """The mark as an SVG document. Same geometry as the raster path.

    ``tile=True`` puts it on the full-bleed brand background, for callers that
    round the corners in CSS (the web app header does).
    """
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" '
           'width="%d" height="%d">' % (size, size)]
    out.append(_grad_xml("gt", LEFT, RIGHT, BRAND_TOP, BRAND_MID, BBOX))
    out.append(_grad_xml("gl", LEFT, BOTTOM, FACE_LEFT, BRAND_MID, BBOX))
    out.append(_grad_xml("gr", CENTRE, BOTTOM, BRAND_MID, BRAND_DEEP, BBOX))
    out.append(_grad_xml("gs", (64, 1), (86, 20), SPARK_TOP, SPARK_BOTTOM, BBOX))
    xf = xform(BBOX, 100.0, TILE_MARK_SPAN)

    def at(poly):
        return " ".join("%g,%g" % xf(x, y) for x, y in poly)

    if tile:
        out.append(_grad_xml("gb", (0, 0), (100, 100),
                             TILE_TOP, TILE_BOTTOM, (0, 0, 100, 100)))
        out.append('  <rect x="0" y="0" width="100" height="100" fill="url(#gb)"/>')
    out.append('  <path d="M%s Z" fill="url(#gt)"/>' % _pts(FACE_TOP_POLY))
    out.append('  <path d="M%s Z" fill="url(#gl)"/>' % _pts(FACE_LEFT_POLY))
    out.append('  <path d="M%s Z" fill="url(#gr)"/>' % _pts(FACE_RIGHT_POLY))
    for poly in spark_polys():
        out.append('  <path d="M%s Z" fill="url(#gs)" opacity="0.95"/>'
                   % _pts(poly))
    arrow = " ".join("M%s Z" % _pts(p) for p in arrow_polys())
    out.append('  <path d="%s" fill="#fff" fill-opacity="%g"/>'
               % (arrow, ARROW_ALPHA))
    out.append("</svg>")
    return "\n".join(out) + "\n"


# --------------------------------------------------- Android vector paths --

def _d(poly, xf, nd=2):
    """One closed subpath of Android path data, in design -> viewport space."""
    parts = []
    for i, (x, y) in enumerate(poly):
        dx, dy = xf(x, y)
        parts.append(("M" if i == 0 else "L") + ("%.*f,%.*f" % (nd, dx, nd, dy)))
    return " ".join(parts) + " Z"


def xform(box, viewport, span):
    """``(scale, offset_x, offset_y)`` fitting `box` into the centre of a
    `viewport`x`viewport` canvas at `span` units across its longest side."""
    bx0, by0, bx1, by1 = box
    w, h = bx1 - bx0, by1 - by0
    s = span / max(w, h)
    return (s,
            viewport / 2.0 - (bx0 + w / 2.0) * s,
            viewport / 2.0 - (by0 + h / 2.0) * s)


def _xf(box, viewport, span):
    """Design -> viewport point mapping, for emitting path data."""
    s, ox, oy = xform(box, viewport, span)

    def fn(x, y):
        return x * s + ox, y * s + oy
    return fn


def adaptive_foreground(viewport=108.0, span=70.0):
    """
    Solid-fill layers for the adaptive icon foreground.

    VectorDrawable gradients need the aapt namespace and an AGP that is happy
    to inline them; flat per-face colours are boring but cannot fail to build,
    and the three faces still read as a lit cube. The gradient version is what
    the raster mipmaps use.
    """
    xf = _xf(BBOX, viewport, span)
    layers = [
        (_d(FACE_TOP_POLY, xf), "#%02x%02x%02x" % FACE_TOP, None),
        (_d(FACE_LEFT_POLY, xf), "#%02x%02x%02x" % FACE_LEFT, None),
        (_d(FACE_RIGHT_POLY, xf), "#%02x%02x%02x" % FACE_RIGHT, None),
    ]
    for poly in spark_polys():
        layers.append((_d(poly, xf), "#%02x%02x%02x" % SPARK_FLAT, None))
    for poly in arrow_polys():
        layers.append((_d(poly, xf), "#FFFFFF", int(ARROW_ALPHA * 255)))
    return layers


def silhouette_even_odd(viewport, span, box=None):
    """
    Cube with the arrow knocked out, as one even-odd path.

    Used for the themed launcher layer and the notification icon, both of
    which take a single colour and must not lose the arrow to it.
    """
    xf = _xf(box or BBOX, viewport, span)
    body = _d(SILHOUETTE, xf)
    holes = " ".join(_d(p, xf) for p in arrow_polys())
    return body + " " + holes


def vector_drawable(paths, width, height, viewport):
    out = ['<?xml version="1.0" encoding="utf-8"?>',
           "<!-- Generated by tools/brand.py - do not edit by hand. -->",
           '<vector xmlns:android="http://schemas.android.com/apk/res/android"',
           '    android:width="%sdp"' % width,
           '    android:height="%sdp"' % height,
           '    android:viewportWidth="%g"' % viewport,
           '    android:viewportHeight="%g">' % viewport]
    for d, colour, alpha in paths:
        out.append('    <path')
        out.append('        android:pathData="%s"' % d)
        out.append('        android:fillColor="%s"' % colour)
        if alpha is not None:
            out.append('        android:fillAlpha="%g"' % (alpha / 255.0))
        if " " in d and d.count("M") > 1:
            out.append('        android:fillType="evenOdd"')
        out.append('        />')
    out.append("</vector>")
    return "\n".join(out) + "\n"
