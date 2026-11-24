"""Item specs for the Raven's-style practice matrices in this repo.

Run `python3 tools/items.py` from the repo root. It writes every picture to docs/img/
and the practice-item blocks into the section pages between
<!-- items:start --> and <!-- items:end --> markers, so the picture, the answer key and
the explanation always come from the same spec.

Every item is original, made for these notes.
"""
import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from figs import group, key, make_item, matrix_svg, one  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMS = []
POSITIONS = {}

# ---------- cell builders ----------
CORNER = [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)]  # TL TR BR BL, clockwise
MID = [(0, -0.62), (0.62, 0), (0, 0.62), (-0.62, 0)]  # top right bottom left, clockwise
GRID9 = [(x, y) for y in (-0.55, 0, 0.55) for x in (-0.55, 0, 0.55)]
SIZE3 = [0.26, 0.42, 0.62]


def frame(*segs):
    return [("frame",)] + [("seg", s) for s in segs]


def dots(on, fill="black"):
    return [("shape", "dot", x, y, 0.15, fill if i in on else "white", 0) for i, (x, y) in enumerate(GRID9)]


def corner_dot(i, fill="black", r=0.2):
    x, y = CORNER[i % 4]
    return [("frame",), ("shape", "dot", x, y, r, fill, 0)]


def ring_dot(i, fill="black"):
    x, y = MID[i % 4]
    return [("ring", 0.82), ("shape", "dot", x * 0.95, y * 0.95, 0.17, fill, 0)]


def vstack(n, x, fill="black", kind="square"):
    ys = {1: [0], 2: [-0.3, 0.3], 3: [-0.55, 0, 0.55], 4: [-0.66, -0.22, 0.22, 0.66]}[n]
    return [("shape", kind, x, y, 0.17, fill, 0) for y in ys]


def slots(i, fill="black", n=3):
    xs = [-0.55, 0, 0.55]
    return [("shape", "circle", x, 0, 0.2, fill if j == i else "white", 0) for j, x in enumerate(xs[:n])]


def slots_multi(on, fill="black"):
    xs = [-0.55, 0, 0.55]
    return [("shape", "circle", x, 0, 0.2, fill if j in on else "white", 0) for j, x in enumerate(xs)]


def corner_arrow(i, rot, fill="black"):
    x, y = CORNER[i % 4] if i is not None else (0, 0)
    return [("frame",), ("shape", "arrow", x * 0.96, y * 0.96, 0.27, fill, rot % 360)]


def two_arrows(a, b, fill="white"):
    return [("shape", "arrow", -0.45, 0, 0.36, fill, a % 360), ("shape", "arrow", 0.45, 0, 0.36, fill, b % 360)]


def outer_inner(outer, inner, inner_fill="black", n=1):
    o = [("shape", outer, 0, 0, 0.68, "white", 0)]
    if inner is None:
        return o
    if n == 1:
        return o + [("shape", inner, 0, 0.02, 0.24, inner_fill, 0)]
    return o + [("shape", inner, x * 0.55, y * 0.4, 0.15, inner_fill, 0) for x, y in [(-0.5, 0), (0.5, 0)]]


def top_bottom(t, b, fill="black"):
    out = []
    if t:
        out.append(("shape", t, 0, -0.42, 0.3, fill, 0))
    if b:
        out.append(("shape", b, 0, 0.45, 0.3, fill, 0))
    return out


def shape_line(kind, line_rot, fill="white", extra=None):
    out = [("shape", kind, 0, 0, 0.6, fill, 0)]
    if line_rot is not None:
        out.append(("shape", "line", 0, 0, 0.75, "black", line_rot % 180))
    if extra is not None:
        out.append(("shape", "line", 0, 0, 0.75, "black", extra % 180))
    return out


def grid(f):
    return [f(r, c) for r in range(3) for c in range(3)]


def item(iid, section, cells, distractors, rule, why):
    ITEMS.append(dict(id=iid, section=section, cells=cells, distractors=distractors, rule=rule, why=why))


POLY = {3: "triangle", 4: "square", 5: "pentagon", 6: "hexagon", 7: "heptagon", 8: "octagon"}

# =====================================================================
# Section 1: progression
# =====================================================================
S = "progression"
item("prog-01", S, grid(lambda r, c: group(r + c + 1)),
     [group(4), group(6), group(5, "circle", "white"), group(3), group(5, "circle", "grey"), group(5, "square"), group(7)],
     "Each row adds one dot from left to right, and each row starts with one more dot than the row above. Row 3 runs 3, 4, so the missing cell holds **5 black dots**.",
     "{d0} has 4 dots, which repeats the cell to its left instead of adding one. {d2} has the right number but white circles, and every cell in the grid uses black dots.")

item("prog-02", S, grid(lambda r, c: one(["circle", "square", "triangle"][r], r=SIZE3[c])),
     [one("triangle", r=SIZE3[1]), one("triangle", r=SIZE3[0]), one("square", r=SIZE3[2]), one("circle", r=SIZE3[2]),
      one("triangle", "black", SIZE3[2]), one("triangle", "grey", SIZE3[2]), one("pentagon", r=SIZE3[2])],
     "Each row keeps one shape (circles, squares, triangles) and the shape grows from small to medium to large across the row. The gap is in row 3, column 3: a **large white triangle**.",
     "{d0} is a triangle but medium, the size of column 2. {d2} is large but a square, which belongs to row 2.")

item("prog-03", S, grid(lambda r, c: one(POLY[3 + r + c], r=0.55)),
     [one("hexagon", r=0.55), one("octagon", r=0.55), one("pentagon", r=0.55), one("heptagon", "black", 0.55),
      one("star", r=0.55), one("circle", r=0.55), group(2, "heptagon", "white")],
     "Count the sides. Each step to the right adds one side, and each row starts one side higher than the row above. Row 3 runs pentagon (5), hexagon (6), so the gap is a **heptagon, 7 sides**.",
     "{d0} is the hexagon again, 6 sides. {d1} is an octagon, 8 sides, which is two steps on. Count carefully: these shapes look alike at a glance.")

item("prog-04", S, grid(lambda r, c: group(1 + 2 * c + r, "square", "white")),
     [group(6, "square", "white"), group(8, "square", "white"), group(5, "square", "white"), group(7, "square", "black"),
      group(7, "circle", "white"), group(9, "square", "white"), group(4, "square", "white")],
     "The count rises by **two** across each row: 1, 3, 5 in row 1, then 2, 4, 6, then 3, 5 and the gap. Add two to 5: **7 white squares**.",
     "{d0} has 6, which is what you get if you assume the step is one. {d1} has 8. Always check the step size on a complete row before you trust it.")

item("prog-05", S, grid(lambda r, c: group(r + 1, "circle", ["white", "grey", "black"][c])),
     [group(3, "circle", "grey"), group(3, "circle", "white"), group(2, "circle", "black"), group(3, "square", "black"),
      group(3, "circle", "hatch"), group(1, "circle", "black"), group(4, "circle", "black")],
     "Two rules. The number of circles is set by the row (1, 2, 3). The shading darkens across each row: white, grey, black. Row 3, column 3 is **three black circles**.",
     "{d0} has three circles but grey, the shading of column 2. {d2} is black but has only two circles, the count for row 2.")

item("prog-06", S, grid(lambda r, c: corner_dot(r + c)),
     [corner_dot(1), corner_dot(2), corner_dot(3), [("frame",), ("shape", "dot", 0, 0, 0.2, "black", 0)],
      [("frame",), ("shape", "dot", -0.5, -0.5, 0.2, "black", 0), ("shape", "dot", 0.5, 0.5, 0.2, "black", 0)],
      corner_dot(0, "white"), corner_dot(0, r=0.32)],
     "The dot moves one corner clockwise with each step to the right, and each row starts one corner further on than the row above. Row 3 has the dot bottom right, then bottom left, so next it moves to **the top-left corner**.",
     "{d0} puts the dot top right, which is two steps on. {d2} leaves it bottom left, where it already is in the cell before the gap.")

item("prog-07", S, grid(lambda r, c: group((r + 1) * (c + 1), "star", "black")),
     [group(8, "star"), group(7, "star"), group(6, "star"), group(9, "circle"), group(9, "star", "white"),
      group(5, "star"), group(9, "star", "grey")],
     "Column 1 counts 1, 2, 3. Each row then goes up in steps of its first number: row 1 in ones (1, 2, 3), row 2 in twos (2, 4, 6), row 3 in threes (3, 6, and the gap). That gives **9 black stars**.",
     "{d0} has 8 and {d1} has 7: both come from guessing a fixed step instead of reading the step from the row's first cell.")

item("prog-08", S, grid(lambda r, c: group(c + 1, ["hexagon", "diamond", "circle"][r], "white", [0.55, 0.32, 0.22][c])),
     [group(3, "circle", "white", 0.32), group(2, "circle", "white", 0.22), group(1, "circle", "white", 0.55),
      group(3, "diamond", "white", 0.22), group(3, "circle", "black", 0.22), group(4, "circle", "white", 0.22), group(3, "hexagon", "white", 0.22)],
     "Across each row the shapes multiply and shrink: one large, two medium, three small. The shape stays the same within a row. Row 3 is circles, so the gap is **three small white circles**.",
     "{d0} has three circles but medium sized, so it breaks the size rule. {d3} has the right count and size but uses diamonds from row 2.")

item("prog-09", S, grid(lambda r, c: group(6 - r - c, "triangle", "black")),
     [group(1, "triangle"), group(3, "triangle"), group(2, "triangle", "white"), group(2, "circle"), group(4, "triangle"),
      group(2, "triangle", "grey"), group(5, "triangle")],
     "The count falls by one across each row, and each row starts one lower than the row above: 6, 5, 4, then 5, 4, 3, then 4, 3 and the gap. The answer is **two black triangles**.",
     "{d0} has one triangle, a drop of two. {d1} has three, which repeats the previous cell. {d2} has the right count but white triangles.")

item("prog-10", S, grid(lambda r, c: one(POLY[8 - r - c], ["white", "grey", "black"][r], 0.55)),
     [one("pentagon", "black", 0.55), one("square", "grey", 0.55), one("square", "white", 0.55), one("triangle", "black", 0.55),
      one("hexagon", "black", 0.55), one("square", "hatch", 0.55), one("circle", "black", 0.55)],
     "Each step to the right loses one side, and each row starts one side lower than the row above. The shading is fixed by the row: white, grey, black. Row 3 runs hexagon, pentagon, so the gap is a **black square**.",
     "{d0} is black but a pentagon, the cell before the gap. {d1} is a square but grey, the shading of row 2.")

# =====================================================================
# Section 2: rotation and movement
# =====================================================================
S = "rotation"
item("rot-01", S, grid(lambda r, c: one("arrow", "white", 0.62, 90 * (r + c) % 360)),
     [one("arrow", "white", 0.62, 90), one("arrow", "white", 0.62, 270), one("arrow", "white", 0.62, 180),
      one("arrow", "white", 0.62, 45), one("arrow", "grey", 0.62, 0), group(2, "arrow", "white", None, 0), one("arrow", "black", 0.62, 0)],
     "The arrow turns a quarter turn (90 degrees) clockwise with each step to the right. Each row starts a quarter turn on from the row above. Row 3 points down, then left, so next it points **up**.",
     "{d0} points right, which is a quarter turn too far. {d1} points left, the same as the cell before the gap, which means no turn at all.")

item("rot-02", S, grid(lambda r, c: one("line", "black", 0.8, (45 * (r + c)) % 180)),
     [one("line", "black", 0.8, 135), one("line", "black", 0.8, 45), one("line", "black", 0.8, 90),
      group(2, "line", "black", 0.6, 0), [("shape", "line", 0, 0, 0.8, "black", 0), ("shape", "line", 0, 0, 0.8, "black", 90)],
      one("line", "black", 0.4, 0), [("shape", "line", 0, 0, 0.8, "black", 45), ("shape", "line", 0, 0, 0.8, "black", 135)]],
     "The line turns 45 degrees clockwise with each step: vertical, sloping, horizontal, sloping the other way, then vertical again. Row 3 goes horizontal, then sloping down to the right, so the gap is a **vertical line**.",
     "{d0} repeats the cell before the gap. {d2} is horizontal, which is a step backwards. A line looks the same after half a turn, so after four 45 degree steps it is back to vertical.")

item("rot-03", S, grid(lambda r, c: one("triangle", ["white", "grey", "black"][r], 0.55, 90 * (r + c) % 360)),
     [one("triangle", "black", 0.55, 90), one("triangle", "black", 0.55, 180), one("triangle", "black", 0.55, 270),
      one("triangle", "grey", 0.55, 0), one("triangle", "white", 0.55, 0), one("triangle", "black", 0.36, 0), one("diamond", "black", 0.55, 0)],
     "Two rules. The triangle turns a quarter turn clockwise with each step to the right, and the shading is set by the row (white, grey, black). Row 3 points down, then left, so the gap is a **black triangle pointing up**.",
     "{d0} is black but points right, one quarter turn too far. {d3} points up but is grey, the shading of row 2.")

item("rot-04", S, grid(lambda r, c: ring_dot(r - c)),
     [ring_dot(1), ring_dot(2), ring_dot(3), [("ring", 0.82), ("shape", "dot", 0, 0, 0.17, "black", 0)], ring_dot(0, "white"),
      [("ring", 0.82), ("shape", "dot", 0, -0.59, 0.17, "black", 0), ("shape", "dot", 0, 0.59, 0.17, "black", 0)],
      [("ring", 0.82), ("shape", "dot", 0.42, -0.42, 0.17, "black", 0)]],
     "The dot moves a quarter of the way round the circle **anticlockwise** with each step to the right. Each row starts a quarter turn clockwise from the row above. Row 3 has the dot at the bottom, then on the right, so next it moves to **the top**.",
     "{d1} puts the dot at the bottom, the result of moving clockwise. Spotting the direction is the whole item: check it on row 1 first.")

item("rot-05", S, grid(lambda r, c: [("frame",), ("shape", "dot", *CORNER[(r + c) % 4], 0.2, "black", 0),
                                     ("shape", "dot", *CORNER[(1 - r - c) % 4], 0.2, "white", 0)]),
     [[("frame",), ("shape", "dot", *CORNER[1], 0.2, "black", 0), ("shape", "dot", *CORNER[0], 0.2, "white", 0)],
      [("frame",), ("shape", "dot", *CORNER[0], 0.2, "black", 0), ("shape", "dot", *CORNER[3], 0.2, "white", 0)],
      [("frame",), ("shape", "dot", *CORNER[1], 0.2, "black", 0), ("shape", "dot", *CORNER[2], 0.2, "white", 0)],
      [("frame",), ("shape", "dot", *CORNER[2], 0.2, "black", 0), ("shape", "dot", *CORNER[1], 0.2, "white", 0)],
      [("frame",), ("shape", "dot", *CORNER[0], 0.2, "black", 0), ("shape", "dot", *CORNER[1], 0.2, "black", 0)],
      [("frame",), ("shape", "dot", *CORNER[0], 0.2, "black", 0)],
      [("frame",), ("shape", "dot", *CORNER[0], 0.2, "black", 0), ("shape", "dot", *CORNER[2], 0.2, "white", 0)]],
     "Track each dot on its own. The black dot moves one corner **clockwise** per step. The white dot moves one corner **anticlockwise** per step. In row 3 the black dot goes bottom right, bottom left, so next top left. The white dot goes bottom left, bottom right, so next top right. The answer has **black top left, white top right**.",
     "{d0} swaps the colours: the positions are right but the dots are the wrong way round. Items with two moving parts are solved one part at a time.")

item("rot-06", S, grid(lambda r, c: group(r + 1, "arrow", "white", None, 45 * c + 90 * r)),
     [group(3, "arrow", "white", None, 0), group(3, "arrow", "white", None, 225), group(2, "arrow", "white", None, 270),
      group(3, "arrow", "white", None, 90), group(3, "arrow", "black", None, 270), group(3, "arrow", "white", None, 315), group(1, "arrow", "white", None, 270)],
     "Two rules. The number of arrows is set by the row (1, 2, 3). The arrows turn 45 degrees clockwise with each step to the right. Row 3 points down, then down-left, so the gap is **three arrows pointing left**.",
     "{d1} repeats the down-left direction of the cell before. {d2} points left but has only two arrows, the count for row 2.")

item("rot-07", S, grid(lambda r, c: slots((r + c) % 3)),
     [slots(0), slots(2), slots_multi({0, 1}), slots_multi(set()), slots(1, "grey"),
      [("shape", "circle", 0, y, 0.2, "black" if j == 1 else "white", 0) for j, y in enumerate([-0.55, 0, 0.55])], slots_multi({0, 1, 2})],
     "The black circle moves one slot to the right with each step and wraps round to the left end after the last slot. Each row starts one slot further right than the row above. Row 3 has it on the right, then on the left, so next it is **in the middle**.",
     "{d0} keeps it on the left. {d1} jumps it back to the right. The wrap-around is the step people miss: after the right-hand slot, the next position is the left-hand one.")

item("rot-08", S, grid(lambda r, c: one("arrow", "black", 0.62, 45 * r - 90 * c)),
     [one("arrow", "black", 0.62, 90), one("arrow", "black", 0.62, 0), one("arrow", "black", 0.62, 180),
      one("arrow", "black", 0.62, 315), one("arrow", "black", 0.62, 225), one("arrow", "white", 0.62, 270), group(2, "arrow", "black", None, 270)],
     "Within each row the arrow turns a quarter turn **anticlockwise** per step. The rows start at up, up-right and right: each start is 45 degrees clockwise from the one above. Row 3 points right, then up, so next it points **left**.",
     "{d0} points right, which is what you get turning clockwise. {d3} points up-left, the result of applying the 45 degree row step inside the row.")

item("rot-09", S, grid(lambda r, c: one("arrow", "white", 0.62, (135 * c + 90 * r) % 360)),
     [one("arrow", "white", 0.62, 0), one("arrow", "white", 0.62, 45), one("arrow", "white", 0.62, 135),
      one("arrow", "white", 0.62, 270), one("arrow", "white", 0.62, 180), one("arrow", "black", 0.62, 90), group(2, "arrow", "white", None, 90)],
     "The arrow turns 135 degrees clockwise (a quarter turn plus an eighth) with each step to the right. Check it on row 1: up, then down-right, then left. Row 3 starts down, then up-left, so add 135 degrees once more: it points **right**.",
     "{d2} points down-right, the result of a 90 degree step. When a quarter turn does not fit row 1, measure the actual angle between two cells instead of assuming.")

item("rot-10", S, grid(lambda r, c: two_arrows(90 * (r + c), 90 * (r - c))),
     [two_arrows(0, 180), two_arrows(180, 0), two_arrows(180, 180), two_arrows(90, 270), two_arrows(270, 90),
      two_arrows(0, 0, "black"), one("arrow", "white", 0.5, 0)],
     "Each cell has two arrows. The left arrow turns a quarter turn **clockwise** per step; the right arrow turns a quarter turn **anticlockwise** per step. Both start pointing the same way in column 1. In row 3, the left arrow goes down, left, so next up. The right arrow goes down, right, so next up. The answer has **both arrows pointing up**.",
     "{d0} turns the right arrow the wrong way. Treat each arrow as its own small puzzle: work out its rule on row 1, then apply it.")

# =====================================================================
# Section 3: distribution of three
# =====================================================================
S = "distribution"
SH3 = ["circle", "square", "triangle"]
item("dist-01", S, grid(lambda r, c: one(SH3[(c + r) % 3])),
     [one("circle"), one("triangle"), one("square", "black"), group(2, "square", "white"), one("square", r=0.3),
      one("pentagon"), one("hexagon")],
     "Every row holds the same three shapes, a circle, a square and a triangle, each once, in a different order. Row 3 has a triangle and a circle, so the gap is a **white square** of the same size.",
     "{d0} is a circle, which row 3 already has. {d2} is a square but black, and nothing in the grid is shaded.")

item("dist-02", S, grid(lambda r, c: one(SH3[(c + r) % 3], ["white", "grey", "black"][(c - r) % 3])),
     [one("square", "grey"), one("square", "black"), one("triangle", "white"), one("circle", "white"), one("square", "hatch"),
      group(2, "square", "white"), one("pentagon", "white")],
     "Shape and shading each follow their own distribution of three. Each row has one circle, one square and one triangle, and also one white, one grey and one black shape. Row 3 is missing the square and the white shading: a **white square**.",
     "{d0} is a square but grey, and row 3 already has a grey shape. {d2} is white but a triangle, which row 3 already has.")

item("dist-03", S, grid(lambda r, c: group((c + r) % 3 + 1, ["star", "hexagon", "cross"][(c + 2 * r) % 3], "black")),
     [group(1, "star"), group(3, "star"), group(2, "hexagon"), group(2, "cross"), group(2, "star", "white"),
      group(4, "star"), group(2, "star", "grey")],
     "Each row has one, two and three shapes, and also one set of stars, one of hexagons and one of crosses. Row 3 has three hexagons and one cross, so the gap needs the missing count (2) and the missing shape (star): **two black stars**.",
     "{d1} has three stars, but row 3 already has a cell with three. {d2} has two shapes but they are hexagons, already used in row 3.")

item("dist-04", S, grid(lambda r, c: outer_inner(["circle", "square", "hexagon"][(c + r) % 3], ["dot", "triangle", "cross"][(c - r) % 3])),
     [outer_inner("square", "triangle"), outer_inner("square", "cross"), outer_inner("circle", "dot"), outer_inner("hexagon", "dot"),
      outer_inner("square", None), outer_inner("square", "dot", "white"), outer_inner("square", "dot", n=2)],
     "Outer and inner shapes are separate distributions. Each row has a circle, a square and a hexagon outside, and a dot, a triangle and a cross inside. Row 3 is missing the square outside and the dot inside: a **square with a black dot**.",
     "{d0} pairs the square with a triangle, but row 3 already has an inner triangle. {d2} has the dot but in a circle, which row 3 already uses.")

item("dist-05", S, grid(lambda r, c: group((c - r) % 3 + 1, ["circle", "triangle", "diamond"][(c + r) % 3], ["white", "grey", "black"][(c + 2 * r) % 3])),
     [group(1, "triangle", "grey"), group(1, "triangle", "black"), group(2, "triangle", "white"), group(3, "triangle", "white"),
      group(1, "circle", "white"), group(1, "diamond", "white"), group(2, "triangle", "grey")],
     "Three distributions at once: shape (circle, triangle, diamond), shading (white, grey, black) and count (one, two, three). Take them one at a time for row 3. Shapes present: diamond, circle, so the gap is a triangle. Shading present: grey, black, so it is white. Counts present: two, three, so it is one. The answer is **one white triangle**.",
     "{d0} gets shape and count right but repeats grey. {d2} gets shape and shading right but repeats the count of two.")

item("dist-06", S, grid(lambda r, c: shape_line(SH3[c], [0, 90, 45][(c + r) % 3])),
     [shape_line("triangle", 0), shape_line("triangle", 45), shape_line("square", 90), shape_line("circle", 90),
      shape_line("triangle", None), shape_line("triangle", 0, extra=90), shape_line("triangle", 90, "grey")],
     "The shape is fixed by the column: circles in column 1, squares in column 2, triangles in column 3. The line through the shape follows a distribution of three: vertical, horizontal and sloping, once each per row. Row 3 has a sloping line in column 1 and a vertical line in column 2, so the gap is **a triangle with a horizontal line**.",
     "{d0} uses the vertical line, already in row 3. {d2} has the horizontal line but in a square, and column 3 is all triangles.")

item("dist-07", S, grid(lambda r, c: [("shape", ["square", "circle", "triangle"][(c + r) % 3], [-0.52, 0, 0.52][(c - r) % 3], 0, 0.24, "black", 0)]),
     [[("shape", "circle", 0, 0, 0.24, "black", 0)], [("shape", "circle", 0.52, 0, 0.24, "black", 0)], [("shape", "square", -0.52, 0, 0.24, "black", 0)],
      [("shape", "triangle", -0.52, 0, 0.24, "black", 0)], [("shape", "circle", -0.52, 0, 0.24, "white", 0)],
      [("shape", "circle", -0.52, 0, 0.24, "black", 0), ("shape", "circle", 0.52, 0, 0.24, "black", 0)], [("shape", "circle", -0.52, -0.52, 0.24, "black", 0)]],
     "Each row uses a square, a circle and a triangle once, and puts the shape on the left, in the centre and on the right once each. Row 3 has a triangle in the centre and a square on the right, so the gap is a **black circle on the left**.",
     "{d0} is a circle but in the centre, a position row 3 already uses. {d2} is on the left but a square, already in row 3.")

item("dist-08", S, grid(lambda r, c: one("pentagon", ["white", "hatch", "black"][(c + r) % 3], SIZE3[(c + 2 * r) % 3])),
     [one("pentagon", "hatch", SIZE3[1]), one("pentagon", "hatch", SIZE3[2]), one("pentagon", "black", SIZE3[0]),
      one("pentagon", "white", SIZE3[0]), one("pentagon", "grey", SIZE3[0]), one("hexagon", "hatch", SIZE3[0]), group(2, "pentagon", "hatch", 0.26)],
     "All the shapes are pentagons, so look at what changes: size and fill. Each row has one small, one medium and one large pentagon, and one white, one striped and one black. Row 3 has a large black one and a medium white one, so the gap is a **small striped pentagon**.",
     "{d0} is striped but medium, a size row 3 already has. {d2} is small but black, a fill row 3 already has.")

item("dist-09", S, grid(lambda r, c: one("arrow", ["white", "black", "grey"][(2 * c + r) % 3], 0.6, [0, 90, 180][(c + r) % 3])),
     [one("arrow", "black", 0.6, 90), one("arrow", "grey", 0.6, 90), one("arrow", "white", 0.6, 0), one("arrow", "white", 0.6, 180),
      one("arrow", "white", 0.6, 270), group(2, "arrow", "white", None, 90), one("arrow", "white", 0.35, 90)],
     "This is not a rotation item, even though it uses arrows. The arrows only ever point up, right or down, and each row has each direction once. Shading is also a distribution: white, black and grey once per row. Row 3 has down-grey and up-black, so the gap is a **white arrow pointing right**.",
     "{d4} points left, a direction that never appears in the grid, which is a sign a turning rule is the wrong idea here. {d0} points right but is black, already in row 3.")

item("dist-10", S, grid(lambda r, c: top_bottom(SH3[(c + r) % 3], SH3[(c + 2 * r) % 3])),
     [top_bottom("circle", "square"), top_bottom("square", "square"), top_bottom("circle", "circle"), top_bottom("square", "triangle"),
      top_bottom("triangle", "circle"), top_bottom("square", None), top_bottom("square", "circle", "white")],
     "Each cell has a top shape and a bottom shape, and each follows its own distribution of circle, square and triangle. Row 3 tops: triangle, circle, so the top of the gap is a square. Row 3 bottoms: square, triangle, so the bottom is a circle. The answer is a **square above a circle**.",
     "{d0} has the right two shapes but the wrong way round. That swap is the most common miss on two-part cells: solve the top and the bottom separately, then check both.")

# =====================================================================
# Section 4: addition and subtraction (overlay)
# =====================================================================
S = "overlay"
R1 = [({"top"}, {"left"}), ({"d1"}, {"hmid"}), ({"vmid", "bottom"}, {"d2"})]
item("add-01", S, grid(lambda r, c: frame(*sorted([R1[r][0], R1[r][1], R1[r][0] | R1[r][1]][c]))),
     [frame("vmid", "bottom"), frame("d2"), frame("vmid", "d2"), frame("bottom", "d2"), frame("vmid", "bottom", "d1"),
      frame("vmid", "bottom", "d2", "hmid"), frame("vmid", "hmid", "d2")],
     "The third cell in each row is the first two laid on top of each other. Row 3 combines the vertical middle line and the bottom edge with the diagonal from top right to bottom left: **all three lines together**.",
     "{d2} drops the bottom edge. {d4} uses the other diagonal. With overlay items, check every line in the answer against the two source cells.")

R2 = [({"top", "left", "d1"}, {"left", "right"}), ({"hmid", "vmid"}, {"vmid", "bottom"}), ({"d1", "d2", "top"}, {"d2", "right", "top"})]
item("add-02", S, grid(lambda r, c: frame(*sorted([R2[r][0], R2[r][1], R2[r][0] ^ R2[r][1]][c]))),
     [frame("d1", "d2", "top", "right"), frame("d2", "top"), frame("d1"), frame("right"), frame("d1", "right", "d2"),
      frame("d1", "top", "right"), frame("d2", "right")],
     "Lines that appear in both of the first two cells cancel out; lines that appear in only one of them are kept. Check row 1: the left edge is in both and is gone from cell 3. In row 3, the top edge and the diagonal from top right are shared, so they cancel. What is left is **the diagonal from top left and the right edge**.",
     "{d0} keeps every line, which is plain addition and does not fit row 1. {d1} keeps only the shared lines, the opposite rule.")

R3 = [({"top", "left", "d1"}, {"top", "d1", "right"}), ({"hmid", "vmid", "bottom"}, {"vmid", "left", "bottom"}), ({"d2", "right", "hmid", "top"}, {"left", "right", "top", "d1"})]
item("add-03", S, grid(lambda r, c: frame(*sorted([R3[r][0], R3[r][1], R3[r][0] & R3[r][1]][c]))),
     [frame("d2", "hmid", "left", "d1"), frame("d2", "right", "hmid", "top", "left", "d1"), frame("right"), frame("top"),
      frame("right", "top", "d2"), frame("right", "top", "left"), frame("top", "left")],
     "Only the lines that the first two cells **share** survive into the third. In row 3, the two cells share the right edge and the top edge, so the gap shows **the top and right edges only**.",
     "{d0} keeps the lines that are not shared, which is the opposite rule. {d4} adds a diagonal that only the first cell has.")

R4 = [({0, 1, 2, 4}, {1, 4}), ({3, 4, 5, 7, 8}, {4, 8}), ({0, 2, 4, 6, 8}, {0, 8})]
item("add-04", S, grid(lambda r, c: dots([R4[r][0], R4[r][1], R4[r][0] - R4[r][1]][c])),
     [dots({0, 8}), dots({2, 6}), dots({2, 4, 6, 8}), dots({0, 4, 8}), dots({2, 4}), dots({4, 6}), dots({0, 2, 4, 6, 8, 1})],
     "Each cell is a 3 by 3 grid of positions. The third cell is the first cell **minus** the dots shown in the second. In row 3, the first cell has an X of five dots and the second has the top-left and bottom-right dots, so remove those two: the answer is **the other diagonal, top right, centre and bottom left**.",
     "{d1} removes the centre too. {d0} is the dots that were removed, not the ones that are left.")

C5 = [(1, 1), (2, 3), (3, 1)]
item("add-05", S, grid(lambda r, c: group([C5[r][0], C5[r][1], sum(C5[r])][c], "star", "black")),
     [group(3, "star"), group(2, "star"), group(5, "star"), group(6, "star"), group(4, "star", "white"), group(4, "circle"), group(4, "star", "grey")],
     "Count the stars. The third cell in each row holds as many stars as the first two together: 1 + 1 = 2, 2 + 3 = 5. Row 3 has 3 and 1, so the gap holds **four black stars**.",
     "{d0} has three, which copies the first cell. {d2} has five, which only fits if you assume the third cell copies row 2.")

C6 = [(5, 2), (6, 4), (4, 3)]
item("add-06", S, grid(lambda r, c: group([C6[r][0], C6[r][1], C6[r][0] - C6[r][1]][c], "circle", "white")),
     [group(2, "circle", "white"), group(7, "circle", "white"), group(3, "circle", "white"), group(1, "circle", "black"),
      group(1, "square", "white"), group(4, "circle", "white"), group(5, "circle", "white")],
     "The third cell holds the first cell's count **minus** the second's: 5 - 2 = 3, 6 - 4 = 2. Row 3 has 4 and 3, so the gap holds **one white circle**.",
     "{d1} has seven, which adds instead of subtracting. Always test whether row 1 adds or subtracts before you use it.")

R7 = [({0, 1, 3}, {1, 2, 5}), ({4, 6, 7}, {4, 8}), ({0, 4, 8}, {2, 4, 6})]
item("add-07", S, grid(lambda r, c: dots([R7[r][0], R7[r][1], R7[r][0] ^ R7[r][1]][c])),
     [dots({0, 2, 4, 6, 8}), dots({4}), dots({0, 8}), dots({2, 6}), dots({0, 2, 6}), dots({0, 4, 8, 1}), dots({2, 4, 6, 3})],
     "A dot that appears in both of the first two cells disappears; a dot in only one of them stays. In row 1, the shared top-middle dot is gone. In row 3, both cells share the centre dot, so it cancels and the four corners stay: **a dot in each corner, centre empty**.",
     "{d0} keeps the centre, which is plain addition. {d1} keeps only the centre, which is the shared part.")

C8 = [({"top"}, {"left"}, {"hmid"}), ({"bottom"}, {"d1"}, {"vmid"})]
item("add-08", S, grid(lambda r, c: frame(*sorted(C8[0][c] if r == 0 else C8[1][c] if r == 1 else C8[0][c] | C8[1][c]))),
     [frame("hmid"), frame("vmid"), frame("hmid", "vmid", "d1"), frame("hmid", "d1"), frame("left", "d1", "hmid", "vmid"),
      frame("top", "bottom", "hmid", "vmid"), frame("d1", "d2")],
     "This one works **down the columns**, not along the rows. Row 1 does not combine into anything, so test the columns: in column 1, the top edge (row 1) and the bottom edge (row 2) together give row 3. Column 3 has the horizontal middle line and the vertical middle line, so the gap is **a plus sign, both middle lines**.",
     "{d0} and {d1} each keep only one of the two lines. If a row rule fails on row 1, always try the columns before guessing.")

item("add-09", S, grid(lambda r, c: [[("shape", "circle", 0, 0, 0.62, "white", 0)], [("shape", "line", 0, 0, 0.8, "black", 0)],
                                     [("shape", "circle", 0, 0, 0.62, "white", 0), ("shape", "line", 0, 0, 0.8, "black", 0)]][c] if r == 0 else
                [[("shape", "square", 0, 0, 0.55, "white", 0)], [("shape", "line", 0, 0, 0.8, "black", 90)],
                 [("shape", "square", 0, 0, 0.55, "white", 0), ("shape", "line", 0, 0, 0.8, "black", 90)]][c] if r == 1 else
                [[("shape", "triangle", 0, 0, 0.6, "white", 0)], [("shape", "dot", 0, 0.08, 0.16, "black", 0)],
                 [("shape", "triangle", 0, 0, 0.6, "white", 0), ("shape", "dot", 0, 0.08, 0.16, "black", 0)]][c]),
     [[("shape", "triangle", 0, 0, 0.6, "white", 0)], [("shape", "dot", 0, 0.08, 0.16, "black", 0)],
      [("shape", "circle", 0, 0, 0.62, "white", 0), ("shape", "dot", 0, 0.08, 0.16, "black", 0)],
      [("shape", "square", 0, 0, 0.55, "white", 0), ("shape", "dot", 0, 0.08, 0.16, "black", 0)],
      [("shape", "triangle", 0, 0, 0.6, "black", 0)],
      [("shape", "triangle", 0, 0, 0.6, "white", 0), ("shape", "dot", -0.2, 0.25, 0.14, "black", 0), ("shape", "dot", 0.2, 0.25, 0.14, "black", 0)],
      [("shape", "triangle", 0, 0, 0.6, "white", 0), ("shape", "dot", 0, 0.08, 0.16, "black", 0), ("shape", "line", 0, 0, 0.8, "black", 0)]],
     "The third cell is simply the first two drawn on top of each other: circle plus line, square plus line. Row 3 gives **a white triangle with a black dot in the middle**.",
     "{d0} is the triangle alone and {d1} is the dot alone: each copies one source cell. A warm-up item, but the same check applies to the hardest overlays.")

R10 = [({0, 2, 4, 6}, {0, 1, 2, 8}), ({3, 4, 5}, {1, 4, 7}), ({0, 1, 2, 3}, {1, 3, 5, 7})]
item("add-10", S, grid(lambda r, c: dots([R10[r][0], R10[r][1], R10[r][0] & R10[r][1]][c])),
     [dots({0, 2, 5, 7}), dots({0, 1, 2, 3, 5, 7}), dots({1}), dots({3}), dots({1, 3, 5}), dots({0, 1, 3}), dots({1, 3, 7})],
     "Only dots that appear in **both** of the first two cells survive. Row 2 shows it clearly: a horizontal line and a vertical line share only the centre. In row 3, the cells share the top-middle and middle-left dots, so the answer is **those two dots only**.",
     "{d0} keeps the unshared dots instead. {d2} keeps only one of the two shared dots.")

# =====================================================================
# Section 5: combined rules
# =====================================================================
S = "combined"
item("comb-01", S, grid(lambda r, c: group(c + 1, SH3[(c + r) % 3], "black")),
     [group(3, "circle"), group(3, "triangle"), group(2, "square"), group(1, "square"), group(3, "square", "white"),
      group(4, "square"), group(3, "square", "grey")],
     "The count follows the column (one, two, three). The shape follows a distribution of three across each row. Row 3 has triangles and circles, so the gap is squares, and column 3 means three of them: **three black squares**.",
     "{d0} has the right count but repeats the circle. {d2} has squares but only two.")

item("comb-02", S, grid(lambda r, c: one("arrow", ["white", "grey", "black"][(c + r) % 3], 0.6, 90 * (r + c))),
     [one("arrow", "white", 0.6, 0), one("arrow", "black", 0.6, 0), one("arrow", "grey", 0.6, 180), one("arrow", "grey", 0.6, 90),
      one("arrow", "grey", 0.6, 270), group(2, "arrow", "grey", None, 0), one("arrow", "grey", 0.6, 45)],
     "Two rules. The arrow turns a quarter turn clockwise per step, each row starting a quarter turn on. The shading is a distribution of three: white, grey and black once per row. Row 3 goes down-black, left-white, so the gap is **a grey arrow pointing up**.",
     "{d0} points up but is white, already used in row 3. {d2} is grey but points down, half a turn off.")

F3 = ["black", "hatch", "grey"]
R13 = [({0, 4, 5}, {4, 8}), ({1, 2, 7}, {2, 3}), ({0, 2, 6}, {2, 4, 8})]
item("comb-03", S, grid(lambda r, c: dots([R13[r][0], R13[r][1], R13[r][0] ^ R13[r][1]][c], F3[r])),
     [dots({0, 4, 6, 8}, "black"), dots({0, 4, 6, 8}, "hatch"), dots({0, 2, 4, 6, 8}, "grey"), dots({2}, "grey"),
      dots({0, 6}, "grey"), dots({4, 8}, "grey"), dots({0, 4, 6}, "grey")],
     "The dots follow the cancel-out rule: a dot in both of the first two cells disappears, a dot in only one stays. The shading of the dots is set by the row (black, striped, grey). In row 3, the shared top-right dot cancels, leaving top left, bottom left, centre and bottom right, all **grey**.",
     "{d0} has the right dots but black, the shading of row 1. {d2} keeps the shared dot, which is plain addition.")

item("comb-04", S, grid(lambda r, c: one(["hexagon", "star", "circle"][(c + 2 * r) % 3], ["white", "black", "grey"][r], SIZE3[c])),
     [one("hexagon", "grey", SIZE3[1]), one("hexagon", "grey", SIZE3[0]), one("hexagon", "white", SIZE3[2]), one("hexagon", "black", SIZE3[2]),
      one("star", "grey", SIZE3[2]), one("circle", "grey", SIZE3[2]), one("hexagon", "hatch", SIZE3[2])],
     "Three rules. Size grows across each row (small, medium, large). Shading is set by the row (white, black, grey). The shape follows a distribution of three. Row 3 has a star and a circle, so the gap is a hexagon, large and grey: **a large grey hexagon**.",
     "{d0} is a grey hexagon but medium. {d4} is large and grey but a star, already in row 3.")

item("comb-05", S, grid(lambda r, c: vstack(r + 1, [-0.55, 0, 0.55][c])),
     [vstack(3, 0), vstack(3, -0.55), vstack(2, 0.55), vstack(4, 0.55), vstack(3, 0.55, "white"), vstack(1, 0.55), vstack(3, 0.55, kind="circle")],
     "The row sets how many squares are stacked (one, two, three). The column sets where the stack sits (left, centre, right). Row 3, column 3: **three black squares stacked on the right**.",
     "{d0} has three squares but in the centre, the column 2 position. {d2} is on the right but has only two.")

item("comb-06", S, grid(lambda r, c: outer_inner(["circle", "square", "hexagon"][r], ["triangle", "cross", "star"][(c + r) % 3], ["white", "grey", "black"][c])),
     [outer_inner("hexagon", "cross", "grey"), outer_inner("hexagon", "cross", "white"), outer_inner("hexagon", "star", "black"),
      outer_inner("hexagon", "triangle", "black"), outer_inner("square", "cross", "black"), outer_inner("circle", "cross", "black"),
      outer_inner("hexagon", "cross", "black", n=2)],
     "Three rules. The outer shape is set by the row (circle, square, hexagon). The inner shape follows a distribution of three (triangle, cross, star). The inner shading darkens across the row (white, grey, black). Row 3 has an inner star and triangle, so the gap is **a hexagon with a black cross inside**.",
     "{d0} has the cross but grey, the shading of column 2. {d2} is black but a star, already in row 3.")

C7 = [("circle", 1, 2), ("square", 3, 1), ("triangle", 2, 3)]
item("comb-07", S, grid(lambda r, c: group(C7[r][1], C7[r][0], "white") if c == 0 else group(C7[r][2], C7[r][0], "white") if c == 1 else group(C7[r][1] + C7[r][2], C7[r][0], "black")),
     [group(5, "triangle", "white"), group(4, "triangle", "black"), group(6, "triangle", "black"), group(5, "square", "black"),
      group(5, "circle", "black"), group(1, "triangle", "black"), group(5, "triangle", "grey")],
     "Two rules on the third cell. Its count is the first two cells added together (1 + 2 = 3, 3 + 1 = 4), and its shapes turn black. The shape type stays the same along each row. Row 3: 2 + 3 = 5, so the gap is **five black triangles**.",
     "{d0} has five triangles but white: it misses the colour change. {d1} has four, which is a counting slip.")

item("comb-08", S, grid(lambda r, c: group((c + r) % 3 + 1, "arrow", ["white", "grey", "black"][r], None, 90 * c)),
     [group(2, "arrow", "black", None, 0), group(2, "arrow", "black", None, 90), group(2, "arrow", "black", None, 270),
      group(1, "arrow", "black", None, 180), group(3, "arrow", "black", None, 180), group(2, "arrow", "grey", None, 180), group(2, "arrow", "white", None, 180)],
     "Three rules. Direction follows the column: up in column 1, right in column 2, down in column 3. Shading follows the row: white, grey, black. The count is a distribution of three (one, two and three arrows once per row). Row 3 has three and one, so the gap has two: **two black arrows pointing down**.",
     "{d0} has two black arrows but pointing up, the column 1 direction. {d5} points down but is grey, the row 2 shading.")

item("comb-09", S, grid(lambda r, c: one(POLY[3 + r + c], ["white", "black", "hatch"][(c + r) % 3], 0.55)),
     [one("heptagon", "hatch", 0.55), one("heptagon", "white", 0.55), one("hexagon", "black", 0.55), one("octagon", "black", 0.55),
      one("heptagon", "black", 0.3), one("heptagon", "grey", 0.55), one("pentagon", "black", 0.55)],
     "Two rules. The number of sides goes up by one per step, each row starting one higher. The fill is a distribution of three (white, black, striped). Row 3 runs pentagon (striped), hexagon (white), so the gap is a 7-sided shape and the missing fill is black: **a black heptagon**.",
     "{d0} is a heptagon but striped, already in row 3. {d2} is black but has 6 sides.")

item("comb-10", S, grid(lambda r, c: corner_arrow(r + c, 90 * (r + c))),
     [corner_arrow(0, 90), corner_arrow(0, 180), corner_arrow(0, 270), corner_arrow(1, 0), corner_arrow(2, 0), corner_arrow(3, 0),
      [("frame",), ("shape", "arrow", 0, 0, 0.3, "black", 0)]],
     "The arrow does two things at each step: it moves one corner clockwise and it turns a quarter turn clockwise. Row 3 has it bottom right pointing down, then bottom left pointing left. Next it moves to **the top-left corner and points up**.",
     "{d0} is in the right corner but still points right, so it skipped the turn. {d3} points up but is in the top-right corner, so it skipped the move.")

# =====================================================================
# Diagnostic: 3 per section
# =====================================================================
S = "diagnostic"
item("diag-01", S, grid(lambda r, c: group(r + c + 2, "circle", "white")),
     [group(5, "circle", "white"), group(7, "circle", "white"), group(6, "circle", "black"), group(4, "circle", "white"),
      group(6, "square", "white"), group(8, "circle", "white"), group(6, "circle", "grey")],
     "Progression. Each step to the right adds one circle and each row starts one higher: 4, 5, so the gap has **six white circles**.",
     "{d0} has five, a copy of the cell before.")
item("diag-02", S, grid(lambda r, c: one(["star", "hexagon", "cross"][r], "black", SIZE3[c])),
     [one("cross", "black", SIZE3[1]), one("hexagon", "black", SIZE3[2]), one("cross", "white", SIZE3[2]), one("cross", "black", SIZE3[0]),
      one("star", "black", SIZE3[2]), one("cross", "grey", SIZE3[2]), group(2, "cross", "black")],
     "Progression. The shape is set by the row and grows across it, so the gap is **a large black cross**.",
     "{d0} is the medium cross from column 2.")
item("diag-03", S, grid(lambda r, c: group(1 + c + 2 * r, "square", "black")),
     [group(6, "square"), group(8, "square"), group(7, "square", "white"), group(5, "square"), group(7, "circle"), group(9, "square"), group(3, "square")],
     "Progression. Across each row the count rises by one; down each column it rises by two. Row 3 runs 5, 6, so the gap has **seven black squares**.",
     "{d0} has six, a copy of the cell before.")
item("diag-04", S, grid(lambda r, c: one("triangle", "white", 0.55, [0, 270, 90][r] + 90 * c)),
     [one("triangle", "white", 0.55, 90), one("triangle", "white", 0.55, 0), one("triangle", "white", 0.55, 180), one("triangle", "black", 0.55, 270),
      one("triangle", "white", 0.32, 270), group(2, "triangle", "white", None, 270), one("arrow", "white", 0.55, 270)],
     "Rotation. Within each row the triangle turns a quarter turn clockwise per step. Row 3 points right, then down, so the gap points **left**.",
     "{d0} points right, which is no turn from the start of the row and two turns back from the cell before.")
item("diag-05", S, grid(lambda r, c: ring_dot(c + 2 * r)),
     [ring_dot(1), ring_dot(0), ring_dot(3), ring_dot(2, "white"), [("ring", 0.82), ("shape", "dot", 0, 0, 0.17, "black", 0)],
      [("ring", 0.82), ("shape", "dot", -0.42, 0.42, 0.17, "black", 0)], [("ring", 0.82), ("shape", "dot", 0, 0.59, 0.17, "black", 0), ("shape", "dot", 0, -0.59, 0.17, "black", 0)]],
     "Rotation. The dot moves a quarter of the way round clockwise with each step. Row 3 has it at the top, then on the right, so next it is at **the bottom**.",
     "{d0} leaves it on the right, a copy of the cell before.")
item("diag-06", S, grid(lambda r, c: one("arrow", "black", 0.6, [0, 90, 180][r] - 45 * c)),
     [one("arrow", "black", 0.6, 135), one("arrow", "black", 0.6, 180), one("arrow", "black", 0.6, 45), one("arrow", "white", 0.6, 90),
      one("arrow", "black", 0.6, 0), one("arrow", "black", 0.6, 270), group(2, "arrow", "black", None, 90)],
     "Rotation. The arrow turns 45 degrees **anticlockwise** per step. Row 3 points down, then down-right, so next it points **right**.",
     "{d0} points down-right, a copy of the cell before. {d1} points down, the start of the row.")
item("diag-07", S, grid(lambda r, c: one(["hexagon", "circle", "star"][(c + 2 * r) % 3], "black")),
     [one("circle", "black"), one("star", "black"), one("hexagon", "white"), one("pentagon", "black"), group(2, "hexagon", "black"),
      one("hexagon", "grey"), one("hexagon", "black", 0.3)],
     "Distribution of three. Each row has a hexagon, a circle and a star once. Row 3 has a circle and a star, so the gap is **a black hexagon**.",
     "{d0} and {d1} repeat shapes row 3 already has.")
item("diag-08", S, grid(lambda r, c: one(["triangle", "circle", "square"][(c + r) % 3], ["black", "white", "grey"][(c + 2 * r) % 3])),
     [one("circle", "white"), one("circle", "grey"), one("triangle", "black"), one("square", "black"), one("circle", "hatch"),
      group(2, "circle", "black"), one("hexagon", "black")],
     "Distribution of three, twice. Shapes: row 3 has a square and a triangle, so a circle. Shading: row 3 has grey and white, so black. The answer is **a black circle**.",
     "{d0} is a circle but white, already in row 3.")
item("diag-09", S, grid(lambda r, c: group((c + r) % 3 + 1, ["square", "triangle", "cross"][(c + 2 * r) % 3], "grey")),
     [group(1, "square", "grey"), group(3, "square", "grey"), group(2, "triangle", "grey"), group(2, "cross", "grey"),
      group(2, "square", "black"), group(4, "square", "grey"), group(2, "square", "white")],
     "Distribution of three, twice. Counts in row 3: three and one, so two. Shapes: triangle and cross, so square. The answer is **two grey squares**.",
     "{d1} has squares but three of them, a count row 3 already has.")
R19 = [({"top"}, {"bottom"}), ({"left"}, {"d2"}), ({"hmid"}, {"vmid", "d1"})]
item("diag-10", S, grid(lambda r, c: frame(*sorted([R19[r][0], R19[r][1], R19[r][0] | R19[r][1]][c]))),
     [frame("hmid"), frame("vmid", "d1"), frame("hmid", "vmid"), frame("hmid", "d1"), frame("hmid", "vmid", "d2"),
      frame("hmid", "vmid", "d1", "right"), frame("vmid", "right", "d1")],
     "Addition. The third cell is the first two laid on top of each other, so the gap has **the horizontal middle line, the vertical middle line and the diagonal from top left to bottom right**.",
     "{d2} drops the diagonal. {d4} uses the other diagonal.")
R20 = [({0, 1, 4}, {1, 2, 4}), ({3, 6}, {6, 7, 8}), ({1, 3, 4}, {4, 5, 7})]
item("diag-11", S, grid(lambda r, c: dots([R20[r][0], R20[r][1], R20[r][0] ^ R20[r][1]][c])),
     [dots({1, 3, 4, 5, 7}), dots({4}), dots({1, 3}), dots({5, 7}), dots({1, 3, 5}), dots({1, 4, 7}), dots({3, 4, 5})],
     "Addition with cancelling. A dot in both of the first two cells disappears. Row 3 shares only the centre, so the gap is **a diamond of four dots: top, left, right and bottom middle**.",
     "{d0} keeps the shared centre dot.")
C21 = [(2, 1), (1, 3), (4, 2)]
item("diag-12", S, grid(lambda r, c: group([C21[r][0], C21[r][1], sum(C21[r])][c], "triangle", "black")),
     [group(5, "triangle"), group(2, "triangle"), group(7, "triangle"), group(6, "triangle", "white"), group(4, "triangle"), group(6, "circle"), group(8, "triangle")],
     "Addition. The third cell's count is the first two added: 4 + 2 = **six black triangles**.",
     "{d0} has five and {d2} has seven: off by one in each direction.")
item("diag-13", S, grid(lambda r, c: group(r + 1, ["star", "circle", "hexagon"][(c + 2 * r) % 3], "black")),
     [group(3, "circle"), group(3, "hexagon"), group(2, "star"), group(3, "star", "white"), group(4, "star"), group(1, "star"), group(3, "star", "grey")],
     "Combined. The row sets the count (one, two, three) and the shape follows a distribution of three. Row 3 has circles and hexagons, so the gap is **three black stars**.",
     "{d0} has three but circles, already in row 3.")
item("diag-14", S, grid(lambda r, c: one("triangle", ["white", "black", "grey"][(c + 2 * r) % 3], 0.55, 90 * c)),
     [one("triangle", "white", 0.55, 0), one("triangle", "black", 0.55, 180), one("triangle", "grey", 0.55, 180), one("triangle", "white", 0.55, 90),
      one("triangle", "white", 0.55, 270), one("triangle", "hatch", 0.55, 180), one("triangle", "white", 0.32, 180)],
     "Combined. Each row turns the triangle a quarter turn clockwise per step, starting from up. Shading follows a distribution of three. Row 3 has black and grey, so the gap is **a white triangle pointing down**.",
     "{d0} is white but points up, the column 1 direction. {d1} points down but is black, already in row 3.")
R23 = [({1, 4}, {4, 7}), ({0, 2}, {2, 8}), ({3, 4, 5}, {5, 8})]
item("diag-15", S, grid(lambda r, c: dots([R23[r][0], R23[r][1], R23[r][0] ^ R23[r][1]][c], ["black", "grey", "hatch"][r])),
     [dots({3, 4, 8}, "black"), dots({3, 4, 8}, "grey"), dots({3, 4, 5, 8}, "hatch"), dots({5}, "hatch"), dots({3, 4}, "hatch"),
      dots({4, 8}, "hatch"), dots({3, 8}, "hatch")],
     "Combined. Shared dots cancel, and the row sets the shading (black, grey, striped). Row 3 shares the middle-right dot, so the gap keeps **middle left, centre and bottom right, striped**.",
     "{d1} has the right dots but grey, the row 2 shading.")


# ---------- build ----------
def main():
    img = os.path.join(ROOT, "docs", "img")
    os.makedirs(img, exist_ok=True)
    key_out = {}
    blocks = {}
    num = {}
    for it in ITEMS:
        sec = it["section"]
        num[sec] = num.get(sec, 0) + 1
        n = num[sec]
        cells = it["cells"]
        if sec not in POSITIONS:
            seq = []
            rng = random.Random("balance-" + sec)
            for _ in range(3):
                block = list(range(8))
                rng.shuffle(block)
                seq += block
            POSITIONS[sec] = seq
        opts, ans = make_item(it["id"], cells, it["distractors"], POSITIONS[sec][n - 1])
        letters = {}
        # letter of each distractor in the shuffled options
        for di, d in enumerate(it["distractors"]):
            for oi, o in enumerate(opts):
                if key(o) == key(d):
                    letters[f"d{di}"] = f"Option {'ABCDEFGH'[oi]}"
        for di in range(len(it["distractors"])):
            letters.setdefault(f"d{di}", "A wrong option")
        sec_title = {"progression": "Progression", "rotation": "Rotation and movement", "distribution": "Distribution of three",
                     "overlay": "Addition and subtraction", "combined": "Combined rules", "diagnostic": "Diagnostic"}[sec]
        title = f"{sec_title} practice item {n}: a 3 by 3 matrix with the bottom-right cell missing, and eight answer options labelled A to H"
        fn = f"{it['id']}.svg"
        with open(os.path.join(img, fn), "w") as f:
            f.write(matrix_svg(cells, opts, title))
        key_out[it["id"]] = ans
        why = it["why"].format(**letters)
        src = f"img/{fn}" if sec == "diagnostic" else f"../img/{fn}"
        md = (f"### Item {n}\n\n![{title}]({src})\n\n"
              f"<details>\n<summary>Answer and explanation, item {n}</summary>\n\n"
              f"**Answer: {ans}.** {it['rule']}\n\n*Why not the others:* {why}\n\n</details>\n")
        blocks.setdefault(sec, []).append((n, ans, md))
    with open(os.path.join(ROOT, "tools", "answer-key.json"), "w") as f:
        json.dump(key_out, f, indent=1)
    # write into pages
    for sec, items in blocks.items():
        page = os.path.join(ROOT, "docs", "diagnostic.md" if sec == "diagnostic" else f"sections/{sec}.md")
        if not os.path.exists(page):
            print("missing page", page)
            continue
        text = open(page, encoding="utf-8").read()
        if sec == "diagnostic":
            parts = {}
            for n, ans, md in items:
                parts.setdefault((n - 1) // 3, []).append(md)
            for p, mds in parts.items():
                text = re.sub(rf"<!-- items:{p}:start -->.*?<!-- items:{p}:end -->",
                              lambda _: f"<!-- items:{p}:start -->\n\n" + "\n".join(mds) + f"\n<!-- items:{p}:end -->", text, flags=re.S)
            table = "| Item | " + " | ".join(str(n) for n, _, _ in items) + " |\n|---|" + "---|" * len(items) + "\n| Answer | " + " | ".join(a for _, a, _ in items) + " |"
        else:
            body = "\n".join(md for _, _, md in items)
            text = re.sub(r"<!-- items:start -->.*?<!-- items:end -->", lambda _: "<!-- items:start -->\n\n" + body + "\n<!-- items:end -->", text, flags=re.S)
            table = "| Item | " + " | ".join(str(n) for n, _, _ in items) + " |\n|---|" + "---|" * len(items) + "\n| Answer | " + " | ".join(a for _, a, _ in items) + " |"
        text = re.sub(r"<!-- key:start -->.*?<!-- key:end -->", lambda _: "<!-- key:start -->\n\n" + table + "\n\n<!-- key:end -->", text, flags=re.S)
        with open(page, "w", encoding="utf-8") as f:
            f.write(text)
    print(f"{len(ITEMS)} items, key in tools/answer-key.json")


if __name__ == "__main__":
    main()
