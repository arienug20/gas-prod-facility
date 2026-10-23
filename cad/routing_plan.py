"""PIPING PLAN - SEPARATOR TO FLARE & STORAGE TANK.

GPF-00-PI-PLN-0002 Rev A0-A2 841x594, scale 1:200.
Rev A2: text converted to MTEXT per company standard (apply_text.py).
Plant (0..100, 0..60) m -> sheet: X = 40 + 5*E ; Y = 40 + 5*N.
Source: dokumen/01-design-basis.md + dokumen/03-plan-routing.md par.2.
"""

from __future__ import annotations

import math

from cadgen import build123d as bd
from cadgen import dxf

# ---- sheet & mapping constants -------------------------------------------
SW, SH = 841.0, 594.0                      # A1 paper
BX1, BY1, BX2, BY2 = 20.0, 10.0, 831.0, 584.0   # ISO 5457 border
PX0, PY0, SC = 40.0, 40.0, 5.0             # 1 m = 5 mm @ 1:200


def P(e: float, n: float):
    """Plant (E,N) meters -> sheet mm."""
    return (PX0 + SC * e, PY0 + SC * n)


# ---- verified idiom helpers (sheet mm) ------------------------------------
def line(x1, y1, x2, y2):
    return bd.Edge.make_line(bd.Vector(x1, y1, 0), bd.Vector(x2, y2, 0))


def circle(x, y, r):
    return bd.Location((x, y, 0)) * bd.Edge.make_circle(r)


def arc(x, y, r, a1, a2):
    return bd.Location((x, y, 0)) * bd.Edge.make_circle(
        r, start_angle=a1, end_angle=a2)


def dashed(x1, y1, x2, y2, dash=4.0, gap=1.6):
    dx, dy = x2 - x1, y2 - y1
    ln = math.hypot(dx, dy)
    ux, uy = dx / ln, dy / ln
    out, t = [], 0.0
    while t < ln:
        t2 = min(t + dash, ln)
        out.append(line(x1 + ux * t, y1 + uy * t, x1 + ux * t2, y1 + uy * t2))
        t = t2 + gap
    return out


def dashed_circle(x, y, r, dash=6.0, gap=2.0):
    step = math.degrees(dash / r)
    gapd = math.degrees(gap / r)
    out, a = [], 0.0
    while a < 360.0:
        out.append(arc(x, y, r, a, min(a + step, 359.999)))
        a += step + gapd
    return out


TEXTS = []  # company manifest: MTEXT written post-build by cad/apply_text.py


def text(t, x, y, size=2.5, rot=0.0, left=False):
    """Record one label into TEXTS (side effect only; returns no geometry)."""
    if t:  # skip empty strings
        TEXTS.append({"t": t, "x": x, "y": y, "h": size, "rot": rot,
                      "layer": "REF-TEXT", "att": 4 if left else 5})
    return []  # NEVER feed into the geometry return


def comp(items):
    return bd.Compound.make_composite(items)


def rect(x1, y1, x2, y2):
    return [line(x1, y1, x2, y1), line(x2, y1, x2, y2),
            line(x2, y2, x1, y2), line(x1, y2, x1, y1)]


def prect(e1, n1, e2, n2):
    return rect(*P(e1, n1), *P(e2, n2))


def arrow(x, y, ang):
    """Flow arrowhead, tip at (x,y), pointing along ang (deg)."""
    out = []
    for s in (1, -1):
        b = math.radians(ang + s * 25)
        out.append(line(x, y, x - 4 * math.cos(b), y - 4 * math.sin(b)))
    return out


def bl_arrow(x, y, d=1):
    """Battery-limit arrow glyph at sheet (x,y), pointing +/-X."""
    return [line(x, y - 3.5, x, y + 3.5),
            line(x, y - 3.5, x + 8 * d, y),
            line(x + 8 * d, y, x, y + 3.5)]


# ---- REF-FRAME: paper edge, border, sheet grid refs, boxes ----------------
def frame_items():
    it = rect(0.0, 0.0, SW, SH) + rect(BX1, BY1, BX2, BY2)
    # border zone references: columns 1-8, rows A-F (as Plan A)
    for i in range(8):
        cx = BX1 + (BX2 - BX1) / 8.0 * (i + 0.5)
        t = str(i + 1)
        it.extend(text(t, cx, 589.0, 2.5) + text(t, cx, 5.0, 2.5))
    for j in range(6):
        cy = BY1 + (BY2 - BY1) / 6.0 * (j + 0.5)
        t = chr(65 + j)
        it.extend(text(t, 15.0, cy, 2.5) + text(t, 836.0, cy, 2.5))
    # legend + line index boxes
    it += rect(555.0, 150.0, 821.0, 470.0)
    it += rect(555.0, 480.0, 821.0, 580.0)
    for x in (600.0, 616.0, 736.0):
        it.append(line(x, 480.0, x, 580.0))
    it.append(line(555.0, 562.0, 821.0, 562.0))
    return it


# ---- REF-TITLE: title block ISO 7200 + rev table --------------------------
def title_items():
    it = rect(651.0, 15.0, 827.0, 105.0)
    # rev table reuses the shared edge y=105 (no duplicate); A2 adds row 120-125
    it += [line(651.0, 105.0, 651.0, 125.0), line(651.0, 120.0, 827.0, 120.0),
           line(651.0, 125.0, 827.0, 125.0), line(827.0, 105.0, 827.0, 125.0),
           line(700.0, 120.0, 700.0, 125.0), line(770.0, 120.0, 770.0, 125.0)]
    for y in (88.0, 71.0, 57.25, 43.5, 29.75):
        it.append(line(651.0, y, 827.0, y))
    for x in (700.0, 770.0):
        it.append(line(x, 105.0, x, 120.0))
    it.extend(text("GAS PRODUCTION FACILITY — ONSHORE FIELD",
                   739.0, 96.5, 3.0))
    it.extend(text("PIPING PLAN — SEPARATOR TO FLARE & STORAGE TANK",
                   739.0, 79.5, 3.0))
    fields = [
        (64.1, "DOC NO: GPF-00-PI-PLN-0002"),
        (50.4, "REV: A2 (ISSUED FOR REVIEW)    SCALE: 1:200 @ A1"),
        (36.6, "DATE: 12 OCT 2026    UNITS: mm    SHEET: 1 OF 1"),
        (22.4, "DRAWN: GLM-5.3-FLASH    CHECKED: PM (AI)    APPROVED: —"),
    ]
    for y, s in fields:
        it.extend(text(s, 655.0, y, 2.5, left=True))
    it.extend(text("REV", 675.5, 117.3, 2.0))
    it.extend(text("DESCRIPTION", 735.0, 117.3, 2.0))
    it.extend(text("DATE", 798.5, 117.3, 2.0))
    it.extend(text("A0", 675.5, 112.6, 1.8))
    it.extend(text("ISSUED FOR REVIEW", 735.0, 112.6, 1.8))
    it.extend(text("09 OCT 26", 798.5, 112.6, 1.8))
    it.extend(text("A1", 675.5, 107.6, 1.8))
    it.extend(text("REVISED PER COMPANY DRAFTING STANDARD", 735.0, 107.6, 1.8))
    it.extend(text("09 OCT 26", 798.5, 107.6, 1.8))
    it.extend(text("A2", 675.5, 122.5, 1.8))
    it.extend(text("TEXT CONVERTED TO MTEXT PER COMPANY STANDARD",
                   735.0, 122.5, 1.8))
    it.extend(text("12 OCT 26", 798.5, 122.5, 1.8))
    return it


# ---- REF-GRID: plant grid ticks + labels (10 m) ---------------------------
def grid_items():
    it = []
    for i in range(11):                     # A..K at E = 0..100
        x, _ = P(10.0 * i, 0.0)
        _, y2 = P(0.0, -0.6)
        it.append(line(x, PY0, x, y2))
        it.extend(text(chr(65 + i), x, 34.0, 2.5))
    for j in range(6):                      # 1..6 at N = 10..60
        x1, y = P(-0.6, 10.0 * (j + 1))
        it.append(line(x1, y, PX0, y))
        it.extend(text(str(j + 1), 34.0, y, 2.5))
    return it


# ---- REF-FENCE: plot fence (0,0)-(100,60) dashed --------------------------
def fence_items():
    it = dashed(*P(0, 0), *P(100, 0), 6.0, 2.0)
    it += dashed(*P(100, 0), *P(100, 60), 6.0, 2.0)
    it += dashed(*P(100, 60), *P(0, 60), 6.0, 2.0)
    it += dashed(*P(0, 60), *P(0, 0), 6.0, 2.0)
    return it


# ---- REF-ROAD: access road y 40..43 ---------------------------------------
def road_items():
    it = [line(*P(8, 40), *P(92, 40))]
    it.append(line(*P(8, 43), *P(92, 43)))
    cx1, cy = P(8, 41.5)
    cxm, _ = P(42, 41.5)
    cx2, _ = P(58, 41.5)
    cx3, _ = P(92, 41.5)
    it += dashed(cx1, cy, cxm, cy, 3.0, 2.0)
    it += dashed(cx2, cy, cx3, cy, 3.0, 2.0)
    return it


# ---- REF-EQUIP: V-101, P-101, rack, V-102, T-101 + bund -------------------
def equip_items():
    it = []
    # V-101 shell + heads + skid
    it += prect(10.2, 32.85, 17.8, 35.15)
    hx1, hy = P(10.2, 34.0)
    hx2, _ = P(17.8, 34.0)
    it.append(arc(hx1, hy, 5.75, 90, 270))
    it.append(arc(hx2, hy, 5.75, 270, 450))
    it += dashed(*P(9.5, 32.0), *P(18.5, 32.0), 4.0, 1.6)
    it += dashed(*P(18.5, 32.0), *P(18.5, 36.5), 4.0, 1.6)
    it += dashed(*P(18.5, 36.5), *P(9.5, 36.5), 4.0, 1.6)
    it += dashed(*P(9.5, 36.5), *P(9.5, 32.0), 4.0, 1.6)
    # P-101 pump box + discharge triangle
    it += prect(21.4, 30.2, 22.6, 30.8)
    tx, ty = P(22.6, 30.5)
    it.append(line(tx, ty - 0.75, P(23.2, 30.5)[0], ty))
    it.append(line(P(23.2, 30.5)[0], ty, tx, ty + 0.75))
    # pipe rack: 2 rails + alternating braces per 6 m bay
    it.append(line(*P(19, 34), *P(58, 34)))
    it.append(line(*P(19, 36), *P(58, 36)))
    xs = [22.0, 28.0, 34.0, 40.0, 46.0, 52.0, 58.0]
    for k in range(6):
        if k % 2 == 0:
            it.append(line(*P(xs[k], 34), *P(xs[k + 1], 36)))
        else:
            it.append(line(*P(xs[k], 36), *P(xs[k + 1], 34)))
    # V-102 KO drum + heads
    it += prect(70.0, 45.2, 72.5, 46.8)
    vx1, vy = P(70.0, 46.0)
    vx2, _ = P(72.5, 46.0)
    it.append(arc(vx1, vy, 4.0, 90, 270))
    it.append(arc(vx2, vy, 4.0, 270, 450))
    # T-101 tank + bund (double wall)
    tcx, tcy = P(69.0, 14.0)
    it.append(circle(tcx, tcy, 15.0))
    it += prect(62.0, 8.0, 76.0, 20.0)
    it += prect(62.3, 8.3, 75.7, 19.7)
    return it


# ---- REF-HATCH: bund wall poche (45 deg ticks) ----------------------------
def hatch_items():
    it = []
    bx1, by1 = P(62.0, 8.0)
    bx2, by2 = P(76.0, 20.0)
    x = bx1 + 2.0
    while x < bx2 - 1.5:
        it.append(line(x, by1, min(x + 1.5, bx2), by1 + 1.5))
        it.append(line(x, by2, min(x + 1.5, bx2), by2 - 1.5))
        x += 4.0
    y = by1 + 2.0
    while y < by2 - 1.5:
        it.append(line(bx1, y, bx1 + 1.5, min(y + 1.5, by2)))
        it.append(line(bx2, y, bx2 - 1.5, min(y + 1.5, by2)))
        y += 4.0
    return it


# ---- REF-PROC: routes (design basis par.4) + flow arrows ------------------
def proc_items():
    it = []
    # 100-PF-1001 DN150: BL W -> V-101 N1
    it.append(line(*P(0, 34), *P(10.2, 34)))
    # 100-GO-1002 DN100: N2 riser + east header to tee
    it.append(line(*P(15, 35.15), *P(15, 35)))
    it.append(line(*P(15, 35), *P(50, 35)))
    # 100-FL-1005 DN150: header (shared leg 15-50 drawn once by GO-1002)
    it.append(line(*P(13, 35), *P(15, 35)))
    it.append(line(*P(50, 35), *P(58, 35)))
    it.append(line(*P(58, 35), *P(58, 46)))
    it.append(line(*P(58, 46), *P(70, 46)))
    # 080-CO-1003 DN80: N3 -> P-101 suction
    it.append(line(*P(17.8, 33.2), *P(22, 33.2)))
    it.append(line(*P(22, 33.2), *P(22, 30.9)))
    # 080-CO-1004 DN80: discharge -> rack -> tank N1
    it.append(line(*P(22.8, 30.5), *P(24, 30.5)))
    it.append(line(*P(24, 30.5), *P(24, 34)))
    it.append(line(*P(24, 34), *P(44, 34)))
    it.append(line(*P(44, 34), *P(44, 16)))
    it.append(line(*P(44, 16), *P(67, 16)))
    it.append(line(*P(67, 16), *P(67, 17.5)))
    it.append(line(*P(67, 17.5), *P(67, 15.8)))
    # 050-PW-1006 DN50 (minor): BREAK gap 3 mm sheet at (44,22) where it
    # crosses 080-CO-1004 DN80 (major stays intact)
    it.append(line(*P(26, 32.85), *P(26, 22)))
    it.append(line(*P(26, 22), *P(43.7, 22)))
    it.append(line(*P(44.3, 22), *P(100, 22)))
    # 050-CD-1007 DN50 (minor): BREAK gaps 3 mm at (44.5,22) [vs PW-1006,
    # same DN50 tie -> CD breaks] and (44.5,16) [vs 080-CO-1004 major]
    it.append(line(*P(44.5, 32.85), *P(44.5, 22.3)))
    it.append(line(*P(44.5, 21.7), *P(44.5, 16.3)))
    it.append(line(*P(44.5, 15.7), *P(44.5, 6)))
    it.append(line(*P(44.5, 6), *P(100, 6)))
    # T-101 N3 loading (by others)
    it.append(line(*P(69, 11), *P(69, 9.7)))
    it.append(line(*P(69, 9.7), *P(100, 9.7)))
    # PSV-101 tail DN150: N5 -> rack top -> tee (50,35)
    it.append(line(*P(13, 35.15), *P(13, 36)))
    it.append(line(*P(13, 36), *P(50, 36)))
    it.append(line(*P(50, 36), *P(50, 35)))
    # flow arrows (every ~15 m + at boundaries)
    flows = [
        (6, 34, 0),                                    # PF-1001 (1)
        (18, 35, 0), (33, 35, 0),                      # GO-1002 (2)
        (45, 35, 0), (54, 35, 0), (58, 40, 90),
        (64, 46, 0),                                   # FL-1005 (4)
        (19.5, 33.2, 0), (22, 32, 270),                # CO-1003 (2)
        (24, 32.5, 90), (30, 34, 0), (40, 34, 0),
        (44, 28, 270), (50, 16, 0), (60, 16, 0),
        (67, 16.9, 90),                                # CO-1004 (7)
        (26, 27, 270), (40, 22, 0), (55, 22, 0),
        (70, 22, 0), (85, 22, 0),                      # PW-1006 (5)
        (44.5, 20, 270), (60, 6, 0), (75, 6, 0), (90, 6, 0),   # CD-1007 (4)
        (69, 10.3, 270), (80, 9.7, 0), (92, 9.7, 0),   # loading (3)
        (25, 36, 0), (40, 36, 0), (50, 35.5, 270),     # PSV tail (3)
    ]
    for e, n, a in flows:
        x, y = P(e, n)
        it += arrow(x, y, a)
    return it


# ---- REF-SYM: north, supports, F-101, exclusion, crossing, hop, BL --------
def sym_items():
    it = []
    # north arrow (plant NE area, per manifest)
    it.append(line(*P(88, 52), *P(92, 52)))
    it.append(line(*P(92, 52), *P(90, 55)))
    it.append(line(*P(90, 55), *P(88, 52)))
    # pipe supports: 0.4 m boxes on rack bents
    for e in (22.0, 28.0, 34.0, 40.0, 46.0, 52.0, 58.0):
        it += prect(e - 0.2, 34.0, e + 0.2, 36.0)
    # leader to one support (x=58)
    it.append(line(288.0, 226.0, P(58, 36)[0] - 1.0, P(58, 36)[1] + 0.8))
    # F-101 flare stack + exclusion radius
    fx, fy = P(84, 46)
    it.append(circle(fx, fy, 1.5))
    it.append(circle(fx, fy, 0.75))
    it.append(line(*P(84, 45.5), *P(84, 46.5)))
    it += dashed_circle(fx, fy, 65.0, 6.0, 2.0)
    # overhead road crossing box (1 x 3 m)
    it += prect(57.5, 40.0, 58.5, 43.0)
    # battery limit arrows
    for e, n in ((100, 22), (100, 6), (100, 9.7)):
        x, y = P(e, n)
        it += bl_arrow(x, y, 1)
    x0, y0 = P(0, 34)
    it += bl_arrow(x0, y0, -1)
    return it


# ---- REF-DIM: elevation label leaders -------------------------------------
def dim_items():
    return [
        line(190.0, 220.3, 190.0, 220.85),      # rack CL +5.000
        line(200.0, 150.4, 200.0, 151.6),       # PW-1006 CL +1.200
        line(290.0, 70.4, 290.0, 71.6),         # CD-1007 CL +1.200
        line(318.0, 235.0, 328.0, 239.5),       # crossing EL +6.500
        line(375.0, 131.2, 375.0, 127.8),       # rise to +6.7
    ]


# ---- REF-TEXT: all labels --------------------------------------------------
def txt_items():
    it = []
    # route labels (skill §1: line no 2.0; from/to 2.0, split two lines)
    it.extend(text("100-PF-1001 DN150", *P(5, 35.4), 2.0))
    it.extend(text("FROM PRODUCTION HEADER", *P(5, 34.6), 2.0))
    it.extend(text("100-GO-1002 DN100 SLOPE 1:500", *P(46, 35.6), 2.0))
    it.extend(text("100-FL-1005 DN150 FLARE HEADER", *P(52, 44.4), 2.0))
    it.extend(text("PSV TAIL + GO-1002 — SLOPE 1:500 TO KO DRUM",
                   *P(52, 43.6), 2.0))
    it.extend(text("080-CO-1003 DN80", *P(19, 32.6), 2.0))
    it.extend(text("080-CO-1004 DN80", *P(30, 32.0), 2.0))
    it.extend(text("TO TANK", *P(30, 31.2), 2.0))
    it.extend(text("080-CO-1004 DN80", *P(55, 16.8), 2.0))
    it.extend(text("TO TANK", *P(55, 16.0), 2.0))
    it.extend(text("050-PW-1006 DN50", *P(60, 23.4), 2.0))
    it.extend(text("TO PW TREATMENT", *P(60, 22.6), 2.0))
    it.extend(text("050-CD-1007 DN50", *P(60, 7.4), 2.0))
    it.extend(text("TO CLOSED DRAIN", *P(60, 6.6), 2.0))
    it.extend(text("T-101 N3 DN80", *P(80, 11.2), 2.0))
    it.extend(text("TO TRUCK LOADING (BY OTHERS)", *P(80, 10.4), 2.0))
    it.extend(text("PSV-101 TAIL DN150", *P(46, 36.7), 2.0))
    # equipment labels (2.5-3.0)
    it.extend(text("V-101 3-PHASE SEPARATOR", *P(14, 30.5), 2.5))
    it.extend(text("P-101", *P(22, 29.5), 2.5))
    it.extend(text("PIPE RACK TOP +4.5", *P(38, 37), 2.5))
    it.extend(text("TYP. PIPE SUPPORT", *P(50, 37.5), 2.2))
    it.extend(text("V-102 FLARE KO DRUM", *P(66, 48), 2.5))
    it.extend(text("F-101 FLARE STACK H=12 m", *P(84, 49.5), 2.5))
    it.extend(text("T-101 API 650 D6.0 X H6.0", *P(69, 6.5), 2.5))
    it.extend(text("EXCLUSION R=13 m (API 521 — ASSUMED, CONFIRM BY CALC)",
                   *P(84, 32.6), 2.0))
    it.extend(text("ACCESS ROAD 6 m", *P(50, 41.5), 2.5))
    it.extend(text("OVHD CROSSING EL +6.5", *P(63, 42), 2.2))
    it.extend(text("N", *P(90, 56.5), 2.5))
    # elevation labels (plan par.2.4)
    it.extend(text("CL +5.000", 190.0, 222.0, 2.2))
    it.extend(text("CL +1.200", 200.0, 152.8, 2.2))
    it.extend(text("CL +1.200", 290.0, 73.0, 2.2))
    it.extend(text("EL +6.500 CROSSING", 306.0, 233.5, 2.2))
    it.extend(text("RISE TO +6.7 → T-101 N1", 375.0, 132.5, 2.2))
    # legend content
    it.extend(text("LEGEND", 688.0, 462.0, 3.0))
    leg = [
        (440.0, "PROCESS LINE (SEE LINE INDEX)", 2.5),
        (414.0, "FENCE - PLOT BOUNDARY", 2.5),
        (388.0, "ACCESS ROAD 6 m", 2.5),
        (362.0, "PIPE RACK 1 LEVEL (TOP +4.5)", 2.5),
        (336.0, "PIPE SUPPORT TYP. EVERY 6 m", 2.5),
        (310.0, "OVHD CROSSING (ELEV. AS NOTED)", 2.5),
        (284.0, "LINE HOP / BREAK", 2.5),
        (258.0, "EXCLUSION RADIUS (API 521)", 2.5),
        (232.0, "BATTERY LIMIT", 2.5),
        (206.0, "ELEVATIONS CL/EL IN m FROM PLANT GRADE", 2.2),
        (192.0, "ALL COORDINATES IN PLANT METERS (E,N)", 2.2),
        (178.0, "PIPE SPEC A1A — ASME B31.3-2022", 2.2),
    ]
    for y, s, sz in leg:
        it.extend(text(s, 722.0, y, sz))
    # line index table
    it.extend(text("LINE INDEX", 688.0, 574.0, 3.0))
    hdr = [(560.0, "LINE NO"), (608.0, "DN"), (620.0, "FROM — TO"),
           (740.0, "VALVES / REMARKS")]
    for x, s in hdr:
        it.extend(text(s, x, 567.0, 2.0, left=True))
    rows = [
        ("100-PF-1001", "150", "PROD. HEADER BL W — V-101 N1",
         "SDV-101 ESD, FC"),
        ("100-GO-1002", "100", "V-101 N2 — TEE (50,35) CL +5.0",
         "PV-101 GV-141 FE/FT-141; 1:500"),
        ("100-FL-1005", "150", "TEE (50,35) — V-102 — F-101",
         "PSV-101 TAIL JOIN; SLOPE 1:500"),
        ("080-CO-1003", "80", "V-101 N3 — P-101 SUCTION", "GV-101, ST-101"),
        ("080-CO-1004", "80", "P-101 DISCH. — T-101 N1",
         "CV-101 GV-102 LV-121 FE/FT-142 GV-103"),
        ("050-PW-1006", "50", "V-101 N4 — BL E (PW TREAT.)",
         "LV-131 FE/FT-143; CL +1.2"),
        ("050-CD-1007", "50", "V-101 N6 — BL E (CLOS. DRAIN)",
         "GV-104 NC; CL +1.2"),
        ("BY OTHERS", "80", "T-101 N3 — TRUCK LOADING",
         "NOT IN SCOPE (LDG)"),
    ]
    y = 554.0
    for r in rows:
        it.extend(text(r[0], 560.0, y, 2.2, left=True))
        it.extend(text(r[1], 608.0, y, 2.2))
        it.extend(text(r[2], 620.0, y, 2.2, left=True))
        it.extend(text(r[3], 740.0, y, 2.2, left=True))
        y -= 9.0
    # notes (plan par.2.6)
    it.extend(text("NOTES:", 52.0, 36.5, 2.5, left=True))
    notes = [
        "1. PLAN SCALE 1:200 @ A1. PLANT GRID 10 m. COORDINATES IN METERS.",
        "2. ELEVATIONS IN METERS FROM PLANT GRADE DATUM +0.00.",
        "3. PIPING PER ASME B31.3-2022. FLARE PER API STD 521 (7th ed. 2020)"
        " & API STD 537 (4th ed. 2024). TANK PER API 650 (13th ed. 2020)."
        " SEPARATOR PER API RP 12J (9th ed. 2024).",
        "4. FLARE HEADER SLOPE 1:500 TO KO DRUM — NO POCKETS.",
        "5. EXCLUSION RADIUS 13 m ASSUMED — CONFIRM BY FLARE RADIATION CALC"
        " (API 521).",
        "6. TANK BUND CAPACITY >= 110% TANK VOLUME.",
        "7. ROUTE SURVEY & PIPE SUPPORT DESIGN BY OTHERS.",
        "8. SEE P&ID GPF-00-PI-PID-0001 FOR INSTRUMENTATION.",
    ]
    y = 32.8
    for s in notes:
        it.extend(text(s, 56.0, y, 2.2, left=True))
        y -= 3.0
    return it


# ---- legend symbol samples on REF-SYM / REF-PROC / REF-EQUIP --------------
def legend_sample_items():
    sym, proc, eqp, fen, roadi = [], [], [], [], []
    proc.append(line(570.0, 440.0, 610.0, 440.0))
    proc += arrow(604.0, 440.0, 0)
    fen += dashed(570.0, 414.0, 610.0, 414.0, 6.0, 2.0)
    roadi += [line(570.0, 386.0, 610.0, 386.0),
              line(570.0, 390.0, 610.0, 390.0)]
    roadi += dashed(570.0, 388.0, 610.0, 388.0, 3.0, 2.0)
    eqp += [line(570.0, 360.0, 610.0, 360.0),
            line(570.0, 364.0, 610.0, 364.0),
            line(578.0, 360.0, 588.0, 364.0)]
    sym += rect(583.0, 333.0, 589.0, 339.0)
    sym += rect(581.0, 307.0, 589.0, 313.0)
    sym += [line(570.0, 284.0, 582.0, 284.0), line(586.0, 284.0, 598.0, 284.0),
            arc(584.0, 284.0, 2.0, 0, 180)]
    sym += dashed_circle(590.0, 258.0, 5.0, 2.5, 1.5)
    sym += bl_arrow(578.0, 232.0, 1)
    return sym, proc, eqp, fen, roadi


@dxf
def routing_plan():
    sym, proc, eqp, fen, roadi = legend_sample_items()
    txt_items()  # company: labels -> TEXTS manifest only, never geometry
    return {
        "REF-FRAME": comp(frame_items()),
        "REF-TITLE": comp(title_items()),
        "REF-GRID": comp(grid_items()),
        "REF-FENCE": comp(fence_items() + fen),
        "REF-ROAD": comp(road_items() + roadi),
        "REF-EQUIP": comp(equip_items() + eqp),
        "REF-HATCH": comp(hatch_items()),
        "REF-PROC": comp(proc_items() + proc),
        "REF-SYM": comp(sym_items() + sym),
        "REF-DIM": comp(dim_items()),
    }


if __name__ == "__main__":
    routing_plan()  # build: the daemon worker runs the body in ITS process
    # harvest the manifest in THIS process: re-run the raw body (pure side
    # effect, writes nothing) so module-level TEXTS is populated here
    routing_plan.__cadgen_model__.func()
    if TEXTS:  # never overwrite a good manifest with an empty one
        import json
        json.dump(TEXTS, open("cad/routing_plan.texts.json", "w"))
