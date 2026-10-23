"""Shared true piping isometric library and FNKT-10 3-column furniture layout.

Standard: FNKT-10-L0-DWG-007 & Company CAD Standard §7.
Axes:
  EX  (+30 deg)  : (+0.8660254, +0.5)   East / rising right
  WX  (-150 deg) : (-0.8660254, -0.5)   West / falling left
  NX  (+150 deg) : (-0.8660254, +0.5)   North / rising left
  SX  (-30 deg)  : (+0.8660254, -0.5)   South / falling right
  UX  (+90 deg)  : (0.0, +1.0)          Up / vertical
  DNX (-90 deg)  : (0.0, -1.0)          Down / vertical
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

from cadgen import build123d as bd

# True Piping Isometric Direction Vectors (30° / 150° / 90°)
EX: Tuple[float, float] = (+0.8660254037844386, +0.5)
WX: Tuple[float, float] = (-0.8660254037844386, -0.5)
NX: Tuple[float, float] = (-0.8660254037844386, +0.5)
SX: Tuple[float, float] = (+0.8660254037844386, -0.5)
UX: Tuple[float, float] = (0.0, +1.0)
DNX: Tuple[float, float] = (0.0, -1.0)


# Vector Math Utilities
def addp(p: Tuple[float, float], d: Tuple[float, float]) -> Tuple[float, float]:
    return (p[0] + d[0], p[1] + d[1])


def subp(p: Tuple[float, float], d: Tuple[float, float]) -> Tuple[float, float]:
    return (p[0] - d[0], p[1] - d[1])


def mulp(d: Tuple[float, float], s: float) -> Tuple[float, float]:
    return (d[0] * s, d[1] * s)


def unit(p: Tuple[float, float], q: Tuple[float, float]) -> Tuple[float, float]:
    dx, dy = q[0] - p[0], q[1] - p[1]
    ln = math.hypot(dx, dy)
    if ln == 0:
        return (1.0, 0.0)
    return (dx / ln, dy / ln)


def perp(d: Tuple[float, float]) -> Tuple[float, float]:
    return (-d[1], d[0])


def rot(px: float, py: float, cx: float, cy: float, ang: float) -> Tuple[float, float]:
    a = math.radians(ang)
    dx, dy = px - cx, py - cy
    return (cx + dx * math.cos(a) - dy * math.sin(a),
            cy + dx * math.sin(a) + dy * math.cos(a))


def hdg(d: Tuple[float, float]) -> float:
    return math.degrees(math.atan2(d[1], d[0]))


# Geometry Helpers
def line(x1: float, y1: float, x2: float, y2: float) -> bd.Edge:
    return bd.Edge.make_line(bd.Vector(x1, y1, 0), bd.Vector(x2, y2, 0))


def circle(x: float, y: float, r: float) -> bd.Edge:
    return bd.Location((x, y, 0)) * bd.Edge.make_circle(r)


def arc(x: float, y: float, r: float, a1: float, a2: float) -> bd.Edge:
    return bd.Location((x, y, 0)) * bd.Edge.make_circle(r, start_angle=a1, end_angle=a2)


def rect(x1: float, y1: float, x2: float, y2: float) -> List[bd.Edge]:
    return [line(x1, y1, x2, y1), line(x2, y1, x2, y2),
            line(x2, y2, x1, y2), line(x1, y2, x1, y1)]


def dashed_line(p1: Tuple[float, float], p2: Tuple[float, float],
                dash: float = 2.2, gap: float = 1.2) -> List[bd.Edge]:
    u = unit(p1, p2)
    tot = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
    edges: List[bd.Edge] = []
    curr = 0.0
    while curr < tot:
        end = min(curr + dash, tot)
        p_a = addp(p1, mulp(u, curr))
        p_b = addp(p1, mulp(u, end))
        edges.append(line(p_a[0], p_a[1], p_b[0], p_b[1]))
        curr += dash + gap
    return edges


def comp(items: List[Any]) -> bd.Compound:
    return bd.Compound.make_composite(items)


class IsoContext:
    """Manages drawing layers and manifest entities (MTEXT, DIMENSION, SOLID)."""

    def __init__(self):
        self.texts: List[Dict[str, Any]] = []
        self.dims: List[Dict[str, Any]] = []
        self.solids: List[Dict[str, Any]] = []

        self.proc_edges: List[bd.Edge] = []
        self.sym_edges: List[bd.Edge] = []
        self.furn_edges: List[bd.Edge] = []
        self.frame_edges: List[bd.Edge] = []
        self.road_edges: List[bd.Edge] = []
        self.equip_edges: List[bd.Edge] = []

    def text(self, t: str, x: float, y: float, size: float = 1.8,
             rot: float = 0.0, left: bool = False, layer: str = "REF-TEXT",
             att: Optional[int] = None) -> None:
        if not t:
            return
        if att is None:
            att = 4 if left else 5
        self.texts.append({
            "t": t, "x": round(x, 3), "y": round(y, 3), "h": round(size, 2),
            "rot": round(rot, 1), "layer": layer, "att": att
        })

    def dimrec(self, p1: Tuple[float, float], p2: Tuple[float, float],
               txt: str, angle: float, base: Tuple[float, float],
               oblique: Optional[float] = None) -> None:
        d: Dict[str, Any] = {
            "p1": [round(p1[0], 3), round(p1[1], 3)],
            "p2": [round(p2[0], 3), round(p2[1], 3)],
            "base": [round(base[0], 3), round(base[1], 3)],
            "angle": round(angle, 1),
            "text": str(txt)
        }
        if oblique is not None:
            d["oblique"] = round(oblique, 1)
        self.dims.append(d)

    def solidrec(self, pts: List[Tuple[float, float]], layer: str = "REF-SYM") -> None:
        self.solids.append({
            "pts": [[round(p[0], 3), round(p[1], 3)] for p in pts],
            "layer": layer
        })

    def add_pipe_run(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> None:
        self.proc_edges.append(line(p1[0], p1[1], p2[0], p2[1]))

    def flange(self, P: Tuple[float, float], u: Tuple[float, float],
               half: float = 1.6, offs: Tuple[float, ...] = (0.45, -0.45)) -> None:
        n = perp(u)
        for s in offs:
            q = addp(P, mulp(u, s))
            p_a = subp(q, mulp(n, half))
            p_b = addp(q, mulp(n, half))
            self.sym_edges.append(line(p_a[0], p_a[1], p_b[0], p_b[1]))

    def filled_dot(self, cx: float, cy: float, r: float = 0.75,
                   layer: str = "REF-SYM", add_ring: bool = True) -> None:
        if add_ring:
            self.sym_edges.append(circle(cx, cy, r))
        c45 = r * 0.7071
        # Approximate filled circle with two overlapping solid quads (8-point star/octagon)
        self.solidrec([(cx - r, cy), (cx, cy - r), (cx, cy + r), (cx + r, cy)], layer=layer)
        self.solidrec([(cx - c45, cy - c45), (cx + c45, cy - c45),
                       (cx - c45, cy + c45), (cx + c45, cy + c45)], layer=layer)

    def gate(self, P: Tuple[float, float], u: Tuple[float, float],
             L: float = 3.4, W: float = 1.8, tl: float = 0.4, tw: float = 2.0) -> None:
        ang = hdg(u)
        hL, hW = L / 2.0, W / 2.0
        def rp(lx: float, ly: float) -> Tuple[float, float]:
            return rot(P[0] + lx, P[1] + ly, P[0], P[1], ang)

        # ISO 10628-2 / FNKT-10 Bowtie (no top/bottom horizontal box edges)
        a1, a2 = rp(-hL, -hW), rp(-hL, hW)
        b1, b2 = rp(hL, -hW), rp(hL, hW)
        self.sym_edges += [line(*a1, *a2), line(*b1, *b2),
                           line(*a1, *b2), line(*a2, *b1)]
        for s in (-1.0, 1.0):
            qx = s * (hL + tl / 2.0)
            self.solidrec([rp(qx - tl / 2.0, -tw / 2.0), rp(qx + tl / 2.0, -tw / 2.0),
                           rp(qx - tl / 2.0, tw / 2.0), rp(qx + tl / 2.0, tw / 2.0)])

    def globe(self, P: Tuple[float, float], u: Tuple[float, float],
              L: float = 3.6, W: float = 2.0, tl: float = 0.4, tw: float = 2.2,
              has_actuator: bool = False, act_tag: Optional[str] = None) -> None:
        ang = hdg(u)
        hL, hW = L / 2.0, W / 2.0
        def rp(lx: float, ly: float) -> Tuple[float, float]:
            return rot(P[0] + lx, P[1] + ly, P[0], P[1], ang)

        # Body: bowtie + ISO 10628-2 filled globe dot at center
        a1, a2 = rp(-hL, -hW), rp(-hL, hW)
        b1, b2 = rp(hL, -hW), rp(hL, hW)
        self.sym_edges += [line(*a1, *a2), line(*a1, *P), line(*P, *a2),
                           line(*b1, *b2), line(*b1, *P), line(*P, *b2)]
        self.filled_dot(P[0], P[1], r=0.65)
        for s in (-1.0, 1.0):
            qx = s * (hL + tl / 2.0)
            self.solidrec([rp(qx - tl / 2.0, -tw / 2.0), rp(qx + tl / 2.0, -tw / 2.0),
                           rp(qx - tl / 2.0, tw / 2.0), rp(qx + tl / 2.0, tw / 2.0)])
        if has_actuator:
            # Stem and diaphragm
            s_top = rp(0.0, 5.0)
            self.sym_edges.append(line(*P, *s_top))
            # Diaphragm dome
            d1 = rp(-2.2, 5.0)
            d2 = rp(2.2, 5.0)
            self.sym_edges.append(line(*d1, *d2))
            self.sym_edges.append(arc(s_top[0], s_top[1], 2.2, ang, ang + 180.0))
            if act_tag:
                t_pos = rp(5.5, 8.5)
                self.text(act_tag, t_pos[0], t_pos[1], size=1.5, att=5)

    def check_valve(self, P: Tuple[float, float], u: Tuple[float, float],
                    L: float = 3.4, W: float = 1.8, tl: float = 0.4, tw: float = 2.0) -> None:
        ang = hdg(u)
        hL, hW = L / 2.0, W / 2.0
        def rp(lx: float, ly: float) -> Tuple[float, float]:
            return rot(P[0] + lx, P[1] + ly, P[0], P[1], ang)

        # ISO 10628-2 / Piping Iso Check Valve: two vertical end bars + diagonal flapper + hinge dot + arrow tip
        a1, a2 = rp(-hL, -hW), rp(-hL, hW)
        b1, b2 = rp(hL, -hW), rp(hL, hW)
        self.sym_edges += [line(*a1, *a2), line(*b1, *b2), line(*a2, *b1)]
        # Filled hinge dot at upstream top corner a2
        self.filled_dot(a2[0], a2[1], r=0.45)
        # Arrowhead at downstream bottom corner b1 along diagonal a2 -> b1
        u_diag = unit(a2, b1)
        n_diag = perp(u_diag)
        p_barb1 = addp(subp(b1, mulp(u_diag, 1.2)), mulp(n_diag, 0.55))
        p_barb2 = subp(subp(b1, mulp(u_diag, 1.2)), mulp(n_diag, 0.55))
        self.solidrec([b1, p_barb1, p_barb2])
        for s in (-1.0, 1.0):
            qx = s * (hL + tl / 2.0)
            self.solidrec([rp(qx - tl / 2.0, -tw / 2.0), rp(qx + tl / 2.0, -tw / 2.0),
                           rp(qx - tl / 2.0, tw / 2.0), rp(qx + tl / 2.0, tw / 2.0)])

    def reducer(self, P: Tuple[float, float], u: Tuple[float, float],
                L: float = 2.6, W1: float = 1.2, W2: float = 2.2) -> None:
        ang = hdg(u)
        hL = L / 2.0
        hW1, hW2 = W1 / 2.0, W2 / 2.0
        def rp(lx: float, ly: float) -> Tuple[float, float]:
            return rot(P[0] + lx, P[1] + ly, P[0], P[1], ang)

        # Closed concentric trapezoid per ISO 6412-2
        p1, p2 = rp(-hL, -hW1), rp(-hL, hW1)
        p3, p4 = rp(hL, hW2), rp(hL, -hW2)
        self.sym_edges += [line(*p1, *p2), line(*p2, *p3),
                           line(*p3, *p4), line(*p4, *p1)]

    def strainer(self, P: Tuple[float, float], u: Tuple[float, float],
                 L: float = 3.6, W: float = 2.0, tl: float = 0.4, tw: float = 2.2) -> None:
        ang = hdg(u)
        hL, hW = L / 2.0, W / 2.0
        def rp(lx: float, ly: float) -> Tuple[float, float]:
            return rot(P[0] + lx, P[1] + ly, P[0], P[1], ang)

        # Main body
        self.sym_edges += [line(*rp(-hL, -hW), *rp(hL, -hW)),
                           line(*rp(hL, -hW), *rp(hL, hW)),
                           line(*rp(hL, hW), *rp(-hL, hW)),
                           line(*rp(-hL, hW), *rp(-hL, -hW))]
        # Y-branch strainer pocket + internal mesh line
        p_leg_tip = rp(0.8, -3.2)
        p_leg_cap = rp(2.0, -2.6)
        self.sym_edges.append(line(*rp(-0.2, -hW), *p_leg_tip))
        self.sym_edges.append(line(*rp(1.2, -hW), *p_leg_cap))
        self.sym_edges.append(line(*p_leg_tip, *p_leg_cap))
        self.sym_edges.append(line(*rp(0.5, -hW), *rp(1.4, -2.9)))
        for s in (-1.0, 1.0):
            qx = s * (hL + tl / 2.0)
            self.solidrec([rp(qx - tl / 2.0, -tw / 2.0), rp(qx + tl / 2.0, -tw / 2.0),
                           rp(qx - tl / 2.0, tw / 2.0), rp(qx + tl / 2.0, tw / 2.0)])

    def orifice(self, P: Tuple[float, float], u: Tuple[float, float],
                half: float = 4.0, tag: Optional[str] = None,
                lead_dir: Tuple[float, float] = (0.0, 1.0)) -> None:
        n = perp(u)
        q1 = addp(P, mulp(u, 0.8))
        q2 = subp(P, mulp(u, 0.8))
        self.sym_edges.append(line(*subp(q1, mulp(n, half)), *addp(q1, mulp(n, half))))
        self.sym_edges.append(line(*subp(q2, mulp(n, half)), *addp(q2, mulp(n, half))))
        if tag:
            # Instrument lead line to transmitter bubble (start from q1 edge, stop at circle radius)
            r_bub = 3.6
            p_bub = addp(P, mulp(lead_dir, 14.0))
            u_ld = unit(P, p_bub)
            p_start = addp(P, mulp(u_ld, half))
            p_end = subp(p_bub, mulp(u_ld, r_bub))
            self.sym_edges.append(line(*p_start, *p_end))
            self.sym_edges.append(circle(p_bub[0], p_bub[1], r_bub))
            self.text(tag, p_bub[0], p_bub[1], size=1.35, att=5)

    def sw(self, P: Tuple[float, float], u: Tuple[float, float],
           txtoff: Tuple[float, float] = (0.0, 3.2)) -> None:
        # ISO 6412-2 / FNKT-10 filled weld dot (circle + solid fill)
        self.filled_dot(P[0], P[1], r=0.8)
        self.text("SW", P[0] + txtoff[0], P[1] + txtoff[1], size=1.5, att=5)

    def flow_arrow(self, P: Tuple[float, float], u: Tuple[float, float]) -> None:
        n = perp(u)
        apex = addp(P, mulp(u, 2.2))
        b1 = addp(subp(P, mulp(u, 1.8)), mulp(n, 1.4))
        b2 = subp(subp(P, mulp(u, 1.8)), mulp(n, 1.4))
        self.solidrec([apex, b1, b2])

    def pipe_support(self, P: Tuple[float, float], u: Tuple[float, float],
                     tag: str, stype: str,
                     leader_vec: Tuple[float, float] = (0.0, -12.0),
                     shelf_len: float = 16.0) -> None:
        ang = hdg(u)
        L, W = 3.6, 1.4
        hL, hW = L / 2.0, W / 2.0
        def rp(lx: float, ly: float) -> Tuple[float, float]:
            return rot(P[0] + lx, P[1] + ly, P[0], P[1], ang)

        # Tilted cross box
        box = [(-hL, -hW), (hL, -hW), (hL, hW), (-hL, hW)]
        for i in range(4):
            self.sym_edges.append(line(*rp(*box[i]), *rp(*box[(i + 1) % 4])))
        self.sym_edges.append(line(*rp(-hL, -hW), *rp(hL, hW)))
        self.sym_edges.append(line(*rp(hL, -hW), *rp(-hL, hW)))

        # Leader to shelf
        p_shelf = addp(P, leader_vec)
        self.sym_edges.append(line(P[0], P[1], p_shelf[0], p_shelf[1]))
        dx = shelf_len if shelf_len >= 0 else shelf_len
        p_end = addp(p_shelf, (dx, 0.0))
        self.sym_edges.append(line(p_shelf[0], p_shelf[1], p_end[0], p_end[1]))

        # Two-line text above shelf
        tx = p_shelf[0] + 1.0 if dx > 0 else p_end[0] + 1.0
        self.text(tag, tx, p_shelf[1] + 3.8, size=1.5, left=True, att=4)
        self.text(stype, tx, p_shelf[1] + 1.2, size=1.4, left=True, att=4)

    def part_bubble(self, P_center: Tuple[float, float],
                    target_pt: Tuple[float, float], item_no: int,
                    r: float = 1.85) -> None:
        self.sym_edges.append(circle(P_center[0], P_center[1], r))
        self.text(str(item_no), P_center[0], P_center[1], size=1.45, att=5)
        # Leader line from target_pt to edge of circle
        u_tgt = unit(P_center, target_pt)
        p_edge = addp(P_center, mulp(u_tgt, r))
        self.sym_edges.append(line(target_pt[0], target_pt[1], p_edge[0], p_edge[1]))

    def stacked_bubbles(self, target_pt: Tuple[float, float],
                        dir_vec: Tuple[float, float],
                        item_nos: List[int], r: float = 1.85,
                        dist_first: float = 6.0) -> None:
        u_dir = unit((0, 0), dir_vec)
        for i, no in enumerate(item_nos):
            c = addp(target_pt, mulp(u_dir, dist_first + i * (2.0 * r + 0.3)))
            self.sym_edges.append(circle(c[0], c[1], r))
            self.text(str(no), c[0], c[1], size=1.4, att=5)
            if i == 0:
                p_edge = subp(c, mulp(u_dir, r))
                self.sym_edges.append(line(target_pt[0], target_pt[1], p_edge[0], p_edge[1]))

    def line_callout(self, P_pipe: Tuple[float, float],
                     P_elbow: Tuple[float, float],
                     line_str: str, bop_str: str,
                     shelf_len: float = 24.0) -> None:
        # Arrowhead touching pipe
        u_lead = unit(P_pipe, P_elbow)
        n_lead = perp(u_lead)
        a_barb1 = addp(addp(P_pipe, mulp(u_lead, 2.0)), mulp(n_lead, 0.8))
        a_barb2 = subp(addp(P_pipe, mulp(u_lead, 2.0)), mulp(n_lead, 0.8))
        self.solidrec([P_pipe, a_barb1, a_barb2])

        # Leader line to elbow and shelf
        self.sym_edges.append(line(P_pipe[0], P_pipe[1], P_elbow[0], P_elbow[1]))
        p_end = addp(P_elbow, (shelf_len, 0.0))
        self.sym_edges.append(line(P_elbow[0], P_elbow[1], p_end[0], p_end[1]))

        # Two line label
        self.text(line_str, P_elbow[0] + 1.5, P_elbow[1] + 3.8, size=1.75, left=True, att=4)
        self.text(bop_str, P_elbow[0] + 1.5, P_elbow[1] + 1.2, size=1.75, left=True, att=4)

    def continuation(self, P_end: Tuple[float, float],
                     u_dir: Tuple[float, float],
                     lines_text: List[str], length: float = 14.0) -> None:
        p_term = addp(P_end, mulp(u_dir, length))
        self.sym_edges += dashed_line(P_end, p_term)
        # Multi line label
        tx = p_term[0] + u_dir[0] * 2.0
        ty = p_term[1] + u_dir[1] * 2.0
        for i, t in enumerate(lines_text):
            self.text(t, tx, ty - i * 3.4, size=1.4, left=True, att=4)

    def build_furniture(self, sheet_no: int, total_sheets: int,
                        drw_no: str, line_no: str, service: str,
                        code: str, pipe_class: str,
                        design_temp: str, design_press: str,
                        op_temp: str, op_press: str,
                        bom_items: List[Tuple[Optional[int], str, str, str, str]],
                        notes: List[str]) -> None:
        """Construct FNKT-10 3-column furniture layout."""
        # 1. Outer and Inner Borders
        self.frame_edges += rect(2.0, 1.3, 418.0, 295.7)
        self.frame_edges += rect(7.0, 6.3, 413.0, 290.7)

        # 2. Grid Ticks & Labels (1..12 horizontal, A..H vertical)
        step_x = (413.0 - 7.0) / 12.0
        for i in range(1, 12):
            gx = 7.0 + i * step_x
            self.furn_edges.append(line(gx, 290.7, gx, 295.7))
            self.furn_edges.append(line(gx, 1.3, gx, 6.3))
        for i in range(12):
            gxc = 7.0 + (i + 0.5) * step_x
            self.text(str(i + 1), gxc, 293.2, size=1.6, att=5)
            self.text(str(i + 1), gxc, 3.8, size=1.6, att=5)

        step_y = (290.7 - 6.3) / 8.0
        for j in range(1, 8):
            gy = 6.3 + j * step_y
            self.furn_edges.append(line(2.0, gy, 7.0, gy))
            self.furn_edges.append(line(413.0, gy, 418.0, gy))
        for j in range(8):
            gyc = 290.7 - (j + 0.5) * step_y
            letter = "ABCDEFGH"[j]
            self.text(letter, 4.5, gyc, size=1.6, att=5)
            self.text(letter, 415.5, gyc, size=1.6, att=5)

        # 3. Isometric Star Compass at (cx=25.3, cy=271.2)
        # 4 Tips along NX, SX, EX, WX and 4 Valleys in between
        cx, cy = 25.3, 271.2
        p_c = (cx, cy)
        tip_N = addp(p_c, mulp(NX, 12.0))
        tip_S = addp(p_c, mulp(SX, 6.0))
        tip_E = addp(p_c, mulp(EX, 6.0))
        tip_W = addp(p_c, mulp(WX, 6.0))

        v_NE = addp(p_c, (0.0, 2.0))             # NX + EX = (0, 1.0)
        v_SE = addp(p_c, (1.732, 0.0))           # SX + EX = (1.732, 0)
        v_SW = addp(p_c, (0.0, -2.0))            # SX + WX = (0, -1.0)
        v_NW = addp(p_c, (-1.732, 0.0))          # NX + WX = (-1.732, 0)

        # 4 Spines from center to tips
        self.furn_edges += [line(*p_c, *tip_N), line(*p_c, *tip_S),
                            line(*p_c, *tip_E), line(*p_c, *tip_W)]
        # 8 Outer contour lines
        self.furn_edges += [
            line(*tip_N, *v_NE), line(*v_NE, *tip_E),
            line(*tip_E, *v_SE), line(*v_SE, *tip_S),
            line(*tip_S, *v_SW), line(*v_SW, *tip_W),
            line(*tip_W, *v_NW), line(*v_NW, *tip_N),
        ]
        # 4 Solid fills on one side of each spine
        self.solidrec([p_c, tip_N, v_NE])
        self.solidrec([p_c, tip_E, v_SE])
        self.solidrec([p_c, tip_S, v_SW])
        self.solidrec([p_c, tip_W, v_NW])

        # Text N
        p_ntxt = addp(tip_N, mulp(NX, 3.2))
        self.text("N", p_ntxt[0], p_ntxt[1], size=2.5, att=5)

        # 4. Column 1 Top: NDT & Line Data Table (x = 195.4..271.5, y = 236.4..290.7)
        # Note: x=271.5 boundary is shared with Col 2, so only draw left, top, bottom
        self.furn_edges += [
            line(195.4, 236.4, 195.4, 290.7),  # left edge
            line(195.4, 290.7, 271.5, 290.7),  # top edge
            line(195.4, 236.4, 271.5, 236.4),  # bottom edge
        ]
        self.furn_edges.append(line(235.1, 236.4, 235.1, 290.7))
        row_h = (290.7 - 236.4) / 12.0
        for i in range(1, 12):
            ry = 290.7 - i * row_h
            self.furn_edges.append(line(195.4, ry, 271.5, ry))

        ndt_rows = [
            ("NDT :", ""),
            ("RADIOGRAPHY TEST (RT)", "100%"),
            ("ULTRASONOGRAPHY (UT)", "100%"),
            ("MAGNETIC PARTICLE TEST (MT)", "NOTE 3"),
            ("DYE PENETRANT TEST (PT)", "NOTE 3"),
            ("SERVICE LINE", service),
            ("CODE", code),
            ("LINE NUMBER", line_no),
            ("PIPING CLASS", pipe_class),
            ("DESIGN TEMPERATURE", design_temp),
            ("DESIGN PRESSURE", design_press),
            ("OPERATING TEMP / PRESS", f"{op_temp} / {op_press}"),
        ]
        for i, (k, v) in enumerate(ndt_rows):
            ryc = 290.7 - (i + 0.5) * row_h
            self.text(k, 196.8, ryc, size=1.35, left=True, att=4)
            self.text(v, 253.3, ryc, size=1.35, att=5)

        # 5. Column 2: Full Vertical BOM (x = 271.5..349.5, y = 6.3..290.7)
        self.furn_edges += rect(271.5, 6.3, 349.5, 290.7)
        # Header 1
        self.text("BILL OF MATERIALS", 310.5, 288.6, size=1.6, att=5)
        self.furn_edges.append(line(271.5, 286.5, 349.5, 286.5))
        # Header 2
        self.text("NO", 274.0, 284.0, size=1.4, att=5)
        self.text("DESCRIPTION", 278.0, 284.0, size=1.4, left=True, att=4)
        self.text("SIZE", 336.0, 284.0, size=1.4, att=5)
        self.text("QUANT", 345.0, 284.0, size=1.4, att=5)
        self.furn_edges.append(line(271.5, 281.5, 349.5, 281.5))

        # Vertical divider lines
        self.furn_edges.append(line(276.5, 6.3, 276.5, 286.5))
        self.furn_edges.append(line(331.5, 6.3, 331.5, 286.5))
        self.furn_edges.append(line(340.5, 6.3, 340.5, 286.5))

        # Horizontal grid rows every 5.5 mm
        n_bom_grid = int((281.5 - 6.3) / 5.5)
        for i in range(1, n_bom_grid + 1):
            by = 281.5 - i * 5.5
            self.furn_edges.append(line(271.5, by, 349.5, by))

        # Populate BOM items
        # bom_items is list of (item_no, category, description, size, quant)
        curr_row = 0
        last_cat = None
        for item_no, cat, desc, sz, qty in bom_items:
            if cat != last_cat:
                # Category Header row
                byc = 281.5 - (curr_row + 0.5) * 5.5
                self.text(cat, 278.0, byc, size=1.35, left=True, att=4)
                last_cat = cat
                curr_row += 1

            byc = 281.5 - (curr_row + 0.5) * 5.5
            if item_no is not None:
                self.text(str(item_no), 274.0, byc, size=1.35, att=5)
            self.text(desc, 278.0, byc, size=1.28, left=True, att=4)
            self.text(sz, 336.0, byc, size=1.3, att=5)
            self.text(qty, 345.0, byc, size=1.3, att=5)
            curr_row += 1

        # 6. Column 3: NOTE, LEGEND, REF DOC, REV TABLE, TITLE BLOCK (x = 349.5..413.0, y = 6.3..290.7)
        # Note: x=349.5 is already drawn by Col 2, so draw top, bottom, right edges only
        self.furn_edges += [
            line(349.5, 290.7, 413.0, 290.7),  # top edge
            line(413.0, 6.3, 413.0, 290.7),    # right edge
            line(349.5, 6.3, 413.0, 6.3),      # bottom edge
        ]

        # Section A: NOTE Box (y = 231.7..290.7)
        self.furn_edges.append(line(349.5, 231.7, 413.0, 231.7))
        self.text("NOTE", 381.25, 288.2, size=1.6, att=5)
        self.furn_edges.append(line(349.5, 285.5, 413.0, 285.5))
        ny = 281.5
        for note in notes:
            self.text(note, 351.5, ny, size=1.3, left=True, att=4)
            ny -= 5.4

        # Section B: LEGEND Box (y = 144.7..231.7)
        self.furn_edges.append(line(349.5, 144.7, 413.0, 144.7))
        self.text("LEGEND", 381.25, 228.7, size=1.6, att=5)
        self.furn_edges.append(line(349.5, 226.0, 413.0, 226.0))

        # Legend 1: Pipe Support
        ly = 217.0
        self.furn_edges += [line(356.0, ly - 0.8, 360.0, ly - 0.8),
                            line(360.0, ly - 0.8, 360.0, ly + 0.8),
                            line(360.0, ly + 0.8, 356.0, ly + 0.8),
                            line(356.0, ly + 0.8, 356.0, ly - 0.8),
                            line(356.0, ly - 0.8, 360.0, ly + 0.8),
                            line(356.0, ly + 0.8, 360.0, ly - 0.8)]
        self.text("PIPE SUPPORT", 366.0, ly, size=1.35, left=True, att=4)

        # Legend 2: Shop Weld (pipe line + filled weld dot per ISO 6412-2 & FNKT-10)
        ly = 203.0
        self.furn_edges.append(line(355.0, ly, 361.0, ly))
        self.furn_edges.append(circle(358.0, ly, 0.8))
        self.filled_dot(358.0, ly, r=0.8, add_ring=False)
        self.text("SHOP WELD / SW", 366.0, ly, size=1.35, left=True, att=4)

        # Legend 3: Flange
        ly = 189.0
        self.furn_edges += [line(355.0, ly, 361.0, ly),
                            line(357.5, ly - 1.5, 357.5, ly + 1.5),
                            line(358.5, ly - 1.5, 358.5, ly + 1.5)]
        self.text("FLANGE CONNECTION", 366.0, ly, size=1.35, left=True, att=4)

        # Legend 4: Valve (ISO 10628-2 / FNKT-10 bowtie + solid flange ticks)
        ly = 175.0
        self.furn_edges += [line(356.0, ly - 1.0, 356.0, ly + 1.0),
                            line(360.0, ly - 1.0, 360.0, ly + 1.0),
                            line(356.0, ly - 1.0, 360.0, ly + 1.0),
                            line(356.0, ly + 1.0, 360.0, ly - 1.0)]
        self.solidrec([(355.5, ly - 1.2), (356.0, ly - 1.2), (355.5, ly + 1.2), (356.0, ly + 1.2)])
        self.solidrec([(360.0, ly - 1.2), (360.5, ly - 1.2), (360.0, ly + 1.2), (360.5, ly + 1.2)])
        self.text("VALVE", 366.0, ly, size=1.35, left=True, att=4)

        # Legend 5: Flow Arrow
        ly = 161.0
        self.solidrec([(360.0, ly), (356.0, ly + 1.2), (356.0, ly - 1.2)])
        self.text("FLOW ARROW", 366.0, ly, size=1.35, left=True, att=4)

        # Legend 6: Continuation Line
        ly = 149.0
        self.furn_edges += dashed_line((355.0, ly), (361.0, ly))
        self.text("CONTINUATION LINE", 366.0, ly, size=1.35, left=True, att=4)

        # Section C: REFERENCE DOCUMENT (y = 121.3..144.7)
        self.furn_edges.append(line(349.5, 121.3, 413.0, 121.3))
        self.text("REFERENCE DOCUMENT", 381.25, 142.2, size=1.4, att=5)
        self.furn_edges.append(line(349.5, 139.5, 413.0, 139.5))
        self.furn_edges.append(line(379.0, 121.3, 379.0, 139.5))

        ref_docs = [
            ("GPF-00-PI-PID-0001", "P&ID SEPARATOR V-101"),
            ("GPF-00-PI-PLN-0002", "PIPING PLAN"),
            ("GPF-00-DB-0001", "DESIGN BASIS"),
        ]
        for i, (dno, dtit) in enumerate(ref_docs):
            ry = 135.5 - i * 5.6
            self.text(dno, 351.0, ry, size=1.25, left=True, att=4)
            self.text(dtit, 381.0, ry, size=1.25, left=True, att=4)

        # Section D: REVISION TABLE (y = 96.4..121.3)
        self.furn_edges.append(line(349.5, 96.4, 413.0, 96.4))
        # Revision Table Header at bottom y = 96.4..100.0
        self.furn_edges.append(line(349.5, 100.0, 413.0, 100.0))
        self.furn_edges.append(line(354.5, 96.4, 354.5, 121.3))
        self.furn_edges.append(line(361.5, 96.4, 361.5, 121.3))
        self.furn_edges.append(line(391.5, 96.4, 391.5, 121.3))
        self.furn_edges.append(line(404.0, 96.4, 404.0, 121.3))

        self.text("NO", 352.0, 98.2, size=1.25, att=5)
        self.text("REV", 358.0, 98.2, size=1.25, att=5)
        self.text("DESCRIPTION", 376.5, 98.2, size=1.25, att=5)
        self.text("DATE", 397.75, 98.2, size=1.25, att=5)
        self.text("REM", 408.5, 98.2, size=1.25, att=5)

        # Rev rows A0 to A5 (bottom to top)
        revs = [
            ("1", "A0", "ISSUED FOR REVIEW", "09 OCT 26", "IFR"),
            ("2", "A1", "REVISED PER CAD STANDARD", "10 OCT 26", "REV"),
            ("3", "A2", "CONVERTED TO MTEXT", "12 OCT 26", "REV"),
            ("4", "A3", "RESTYLED PER FNKT-10", "13 OCT 26", "REV"),
            ("5", "A4", "ISO ORIENTATION UPDATE", "15 OCT 26", "REV"),
            ("6", "A5", "TRUE PIPING ISO & FNKT-10", "22 OCT 26", "REV"),
        ]
        rev_h = (121.3 - 100.0) / 6.0
        for i, (r_no, r_rev, r_desc, r_date, r_rem) in enumerate(revs):
            ry = 100.0 + i * rev_h
            if i > 0:
                self.furn_edges.append(line(349.5, ry, 413.0, ry))
            ryc = ry + 0.5 * rev_h
            self.text(r_no, 352.0, ryc, size=1.25, att=5)
            self.text(r_rev, 358.0, ryc, size=1.25, att=5)
            self.text(r_desc, 363.0, ryc, size=1.2, left=True, att=4)
            self.text(r_date, 397.75, ryc, size=1.2, att=5)
            self.text(r_rem, 408.5, ryc, size=1.2, att=5)

        # Section E: PROJECT / COMPANY / CONSULTANT (y = 53.3..96.4)
        self.furn_edges.append(line(349.5, 85.1, 413.0, 85.1))
        self.furn_edges.append(line(349.5, 68.3, 413.0, 68.3))
        self.furn_edges.append(line(349.5, 53.3, 413.0, 53.3))

        self.text("PROJECT:", 351.5, 93.5, size=1.35, left=True, att=4)
        self.text("GAS PRODUCTION FACILITY", 351.5, 89.8, size=1.5, left=True, att=4)
        self.text("ONSHORE FIELD", 351.5, 86.8, size=1.5, left=True, att=4)

        self.text("COMPANY:", 351.5, 81.8, size=1.35, left=True, att=4)
        self.text("PM OIL & GAS SURFACE FACILITY", 351.5, 76.5, size=1.5, left=True, att=4)

        self.text("CONSULTANT:", 351.5, 65.0, size=1.35, left=True, att=4)
        self.text("REKAYASA ENGINEERING", 351.5, 59.5, size=1.5, left=True, att=4)

        # Section F: APPROVAL GRID (y = 30.7..53.3)
        self.furn_edges.append(line(349.5, 30.7, 413.0, 30.7))
        self.furn_edges.append(line(349.5, 49.5, 413.0, 49.5))
        self.furn_edges.append(line(349.5, 44.0, 413.0, 44.0))
        self.furn_edges.append(line(349.5, 37.0, 413.0, 37.0))
        self.furn_edges.append(line(370.6, 30.7, 370.6, 49.5))
        self.furn_edges.append(line(391.8, 30.7, 391.8, 49.5))

        self.text("APPROVAL", 381.25, 51.4, size=1.4, att=5)
        self.text("DRAWN", 360.0, 46.8, size=1.3, att=5)
        self.text("CHECKED", 381.2, 46.8, size=1.3, att=5)
        self.text("APPROVED", 402.4, 46.8, size=1.3, att=5)

        self.text("GLM-5.3-FLASH", 360.0, 40.5, size=1.3, att=5)
        self.text("PM (AI)", 381.2, 40.5, size=1.3, att=5)
        self.text("REKAYASA", 402.4, 40.5, size=1.3, att=5)

        self.text("22 OCT 26", 360.0, 33.8, size=1.3, att=5)
        self.text("22 OCT 26", 381.2, 33.8, size=1.3, att=5)
        self.text("22 OCT 26", 402.4, 33.8, size=1.3, att=5)

        # Section G: TITLE (y = 16.7..30.7)
        self.furn_edges.append(line(349.5, 16.7, 413.0, 16.7))
        self.text("ISOMETRIC DRAWING", 381.25, 26.5, size=1.8, att=5)
        self.text(line_no, 381.25, 22.5, size=1.6, att=5)
        self.text(service, 381.25, 19.0, size=1.4, att=5)

        # Section H: DRAWING NUMBER / SHEET / REV / SCALE (y = 6.3..16.7)
        self.furn_edges.append(line(349.5, 11.5, 413.0, 11.5))
        self.furn_edges.append(line(386.0, 6.3, 386.0, 16.7))
        self.furn_edges.append(line(395.0, 6.3, 395.0, 16.7))
        self.furn_edges.append(line(404.0, 6.3, 404.0, 16.7))

        self.text("DRAWING NUMBER", 351.5, 14.3, size=1.3, left=True, att=4)
        self.text(drw_no, 351.5, 8.8, size=1.75, left=True, att=4)

        self.text("SHT", 390.5, 14.3, size=1.2, att=5)
        self.text(f"{sheet_no:02d}/{total_sheets:02d}", 390.5, 8.8, size=1.4, att=5)

        self.text("REV", 399.5, 14.3, size=1.2, att=5)
        # Revision triangle around A5
        self.furn_edges += [line(396.5, 6.8, 402.5, 6.8),
                            line(402.5, 6.8, 399.5, 11.0),
                            line(399.5, 11.0, 396.5, 6.8)]
        self.text("A5", 399.5, 8.5, size=1.35, att=5)

        self.text("SCALE", 408.5, 14.3, size=1.2, att=5)
        self.text("NTS", 408.5, 8.8, size=1.35, att=5)

    def get_layers(self) -> Dict[str, bd.Compound]:
        layers: Dict[str, bd.Compound] = {}
        if self.frame_edges:
            layers["REF-FRAME"] = comp(self.frame_edges)
        if self.furn_edges:
            layers["REF-TITLE"] = comp(self.furn_edges)
        if self.proc_edges:
            layers["REF-PROC"] = comp(self.proc_edges)
        if self.sym_edges:
            layers["REF-SYM"] = comp(self.sym_edges)
        if self.equip_edges:
            layers["REF-EQUIP"] = comp(self.equip_edges)
        if self.road_edges:
            layers["REF-ROAD"] = comp(self.road_edges)
        return layers

    def save_manifest(self, filepath: str) -> None:
        import json
        manifest = {
            "texts": self.texts,
            "dims": self.dims,
            "solids": self.solids
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
