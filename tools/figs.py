"""Tiny SVG library for matrix-style practice items (Raven's style 3x3 grids, series).

A cell is a list of glyphs. Glyph tuples:
  ("shape", kind, x, y, r, fill, rot)   kind: circle square triangle diamond pentagon
                                         hexagon heptagon octagon star cross arrow dot
                                         x, y in [-1, 1] cell units; r radius in cell units
  ("seg", name)                          line inside the cell frame: top bottom left right
                                         hmid vmid d1 (top-left to bottom-right) d2
  ("frame",)                             square outline for overlay items
  ("ring", r)                            plain outline circle centred in the cell
fill: "white" (outline), "black", "grey", "hatch"

matrix_svg(cells9, options8, ...) draws the 3x3 grid (cell 8 shown as "?") and options A-H.
make_item(...) picks 7 unique distractors and shuffles with a fixed seed.
"""
import math
import random

CELL = 96
PAD = 14
STROKE = 2.4
INK = "#111"
GREY = "#9a9a9a"


def key(cell):
    out = []
    for g in cell:
        out.append(tuple(round(v, 3) if isinstance(v, float) else v for v in g))
    return tuple(sorted(out, key=repr))


def poly_points(n, cx, cy, r, rot):
    pts = []
    for i in range(n):
        a = math.radians(rot - 90 + 360 * i / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def fill_attr(fill):
    return {"white": "#fff", "black": INK, "grey": GREY, "hatch": "url(#hatch)"}[fill]


def render_glyph(g, ox, oy, s):
    """Return svg string for glyph in cell with top-left (ox, oy), size s."""
    h = s / 2
    if g[0] == "frame":
        m = s * 0.12
        return f'<rect x="{ox+m:.1f}" y="{oy+m:.1f}" width="{s-2*m:.1f}" height="{s-2*m:.1f}" fill="none" stroke="#b5b5b5" stroke-width="1.3" stroke-dasharray="3 3"/>'
    if g[0] == "ring":
        return f'<circle cx="{ox+h:.1f}" cy="{oy+h:.1f}" r="{g[1]*h:.1f}" fill="none" stroke="{INK}" stroke-width="{STROKE}"/>'
    if g[0] == "seg":
        m = s * 0.12
        x0, y0, x1, y1 = ox + m, oy + m, ox + s - m, oy + s - m
        xm, ym = ox + h, oy + h
        pts = {
            "top": (x0, y0, x1, y0), "bottom": (x0, y1, x1, y1),
            "left": (x0, y0, x0, y1), "right": (x1, y0, x1, y1),
            "hmid": (x0, ym, x1, ym), "vmid": (xm, y0, xm, y1),
            "d1": (x0, y0, x1, y1), "d2": (x1, y0, x0, y1),
        }[g[1]]
        return f'<line x1="{pts[0]:.1f}" y1="{pts[1]:.1f}" x2="{pts[2]:.1f}" y2="{pts[3]:.1f}" stroke="{INK}" stroke-width="{STROKE+1.4}" stroke-linecap="round"/>'
    _, kind, x, y, r, fill, rot = g
    cx, cy, rr = ox + h + x * h, oy + h + y * h, r * h
    f = fill_attr(fill)
    common = f'fill="{f}" stroke="{INK}" stroke-width="{STROKE}" stroke-linejoin="round"'
    if kind == "circle":
        return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rr:.1f}" {common}/>'
    if kind == "dot":
        return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rr:.1f}" fill="{INK if fill=="black" else f}" stroke="{INK}" stroke-width="{STROKE}"/>'
    if kind == "line":
        a = math.radians(rot)
        dx, dy = rr * math.sin(a), -rr * math.cos(a)
        return f'<line x1="{cx-dx:.1f}" y1="{cy-dy:.1f}" x2="{cx+dx:.1f}" y2="{cy+dy:.1f}" stroke="{INK}" stroke-width="{STROKE+0.8}" stroke-linecap="round"/>'
    if kind == "square":
        pts = poly_points(4, cx, cy, rr * 1.25, 45 + rot)
    elif kind == "diamond":
        pts = poly_points(4, cx, cy, rr * 1.2, rot)
    elif kind == "triangle":
        pts = [(px, py + rr * 0.18) for px, py in poly_points(3, cx, cy, rr * 1.15, rot)]
    elif kind in ("pentagon", "hexagon", "heptagon", "octagon"):
        n = {"pentagon": 5, "hexagon": 6, "heptagon": 7, "octagon": 8}[kind]
        pts = poly_points(n, cx, cy, rr * 1.08, rot)
    elif kind == "star":
        pts = []
        for i in range(10):
            rad = rr * 1.15 if i % 2 == 0 else rr * 0.5
            a = math.radians(rot - 90 + 36 * i)
            pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    elif kind == "cross":
        w = rr * 0.38
        base = [(-w, -rr), (w, -rr), (w, -w), (rr, -w), (rr, w), (w, w), (w, rr), (-w, rr), (-w, w), (-rr, w), (-rr, -w), (-w, -w)]
        a = math.radians(rot)
        pts = [(cx + px * math.cos(a) - py * math.sin(a), cy + px * math.sin(a) + py * math.cos(a)) for px, py in base]
    elif kind == "arrow":
        # points up at rot=0, rotates clockwise
        base = [(0, -rr), (rr * 0.75, -rr * 0.15), (rr * 0.28, -rr * 0.15), (rr * 0.28, rr), (-rr * 0.28, rr), (-rr * 0.28, -rr * 0.15), (-rr * 0.75, -rr * 0.15)]
        a = math.radians(rot)
        pts = [(cx + px * math.cos(a) - py * math.sin(a), cy + px * math.sin(a) + py * math.cos(a)) for px, py in base]
    else:
        raise ValueError(kind)
    return f'<polygon points="{" ".join(f"{px:.1f},{py:.1f}" for px, py in pts)}" {common}/>'


def render_cell(cell, ox, oy, s=CELL):
    return "".join(render_glyph(g, ox, oy, s) for g in cell)


DEFS = (
    '<defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
    f'<rect width="6" height="6" fill="#fff"/><line x1="0" y1="0" x2="0" y2="6" stroke="{INK}" stroke-width="2.2"/></pattern></defs>'
)


def matrix_svg(cells, options, title, rows=3, cols=3):
    """cells: rows*cols lists (last one is ignored and shown as '?'). options: 8 cells."""
    s = CELL
    opt_w = 4 * s + 5 * PAD
    grid_w = cols * s
    W = max(opt_w, grid_w + 2 * PAD) + 2 * PAD
    gx = (W - grid_w) / 2
    gy = PAD * 2
    oy0 = gy + rows * s + 44
    H = oy0 + 2 * (s + 26) + PAD
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="{title}">',
           f"<title>{title}</title>", DEFS,
           f'<rect x="0" y="0" width="{W:.0f}" height="{H:.0f}" fill="#fff"/>']
    for i in range(rows * cols):
        r, c = divmod(i, cols)
        x, y = gx + c * s, gy + r * s
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{s}" height="{s}" fill="#fff" stroke="#444" stroke-width="1.4"/>')
        if i == rows * cols - 1:
            out.append(f'<text x="{x+s/2:.1f}" y="{y+s/2+14:.1f}" font-family="Arial, Helvetica, sans-serif" font-size="40" font-weight="bold" text-anchor="middle" fill="#555">?</text>')
        else:
            out.append(render_cell(cells[i], x, y))
    out.append(f'<line x1="{PAD}" y1="{oy0-22:.1f}" x2="{W-PAD}" y2="{oy0-22:.1f}" stroke="#bbb" stroke-width="1" stroke-dasharray="4 4"/>')
    ox0 = (W - (4 * s + 3 * PAD)) / 2
    for i, cell in enumerate(options):
        r, c = divmod(i, 4)
        x, y = ox0 + c * (s + PAD), oy0 + r * (s + 26)
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{s}" height="{s}" fill="#fff" stroke="#444" stroke-width="1.4"/>')
        out.append(render_cell(cell, x, y))
        out.append(f'<text x="{x+s/2:.1f}" y="{y+s+19:.1f}" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="bold" text-anchor="middle" fill="#111">{"ABCDEFGH"[i]}</text>')
    out.append("</svg>")
    return "\n".join(out)


def make_item(item_id, cells, candidates, pos=None):
    """cells: 9 cells, cells[8] is the correct answer. candidates: list of distractor cells
    (more than 7 is fine). Returns (options8, answer_letter)."""
    correct = cells[8]
    seen = {key(correct)}
    picked = []
    for c in candidates:
        k = key(c)
        if k in seen or not c:
            continue
        seen.add(k)
        picked.append(c)
        if len(picked) == 7:
            break
    if len(picked) < 7:
        raise ValueError(f"{item_id}: only {len(picked)} unique distractors")
    if pos is None:
        pos = random.Random("opts-" + item_id).randrange(8)
    opts = picked[:pos] + [correct] + picked[pos:]
    return opts, "ABCDEFGH"[pos]


# ---------- layout helpers ----------
LAYOUT = {
    1: [(0, 0)],
    2: [(-0.45, 0), (0.45, 0)],
    3: [(-0.5, 0.42), (0, -0.42), (0.5, 0.42)],
    4: [(-0.42, -0.42), (0.42, -0.42), (-0.42, 0.42), (0.42, 0.42)],
    5: [(-0.5, -0.5), (0.5, -0.5), (0, 0), (-0.5, 0.5), (0.5, 0.5)],
    6: [(-0.42, -0.55), (0.42, -0.55), (-0.42, 0), (0.42, 0), (-0.42, 0.55), (0.42, 0.55)],
    7: [(-0.55, -0.55), (0, -0.55), (0.55, -0.55), (-0.27, 0), (0.27, 0), (-0.27, 0.55), (0.27, 0.55)],
    8: [(-0.55, -0.55), (0, -0.55), (0.55, -0.55), (-0.27, 0), (0.27, 0), (-0.55, 0.55), (0, 0.55), (0.55, 0.55)],
    9: [(x, y) for y in (-0.55, 0, 0.55) for x in (-0.55, 0, 0.55)],
}


def group(n, kind="circle", fill="black", r=None, rot=0):
    if n == 0:
        return []
    if r is None:
        r = {1: 0.42, 2: 0.3, 3: 0.27, 4: 0.26}.get(n, 0.17)
    return [("shape", kind, x, y, r, fill, rot) for x, y in LAYOUT[n]]


def one(kind, fill="white", r=0.55, rot=0, x=0.0, y=0.0):
    return [("shape", kind, x, y, r, fill, rot)]
