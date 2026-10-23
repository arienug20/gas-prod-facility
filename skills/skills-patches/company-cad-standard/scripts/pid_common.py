"""Reusable P&ID Symbol, Auto-Trimming, Level Bridle, Equipment Catalog & A1 Sheet Furniture Library.

Versi 2.0.0 (Process & Piping Advanced CAD Suite).

Standar acuan:
  - ANSI/ISA-5.1-2024 (Instrumentation Symbols and Identification)
  - ISO 10628-2:2012 (Diagrams for chemical and petrochemical industry — Graphical symbols)
  - API RP 12J (Specification for Oil and Gas Separators)
  - API STD 521 (Pressure-relieving and Depressurizing Systems)
  - API STD 650 (Welded Tanks for Oil Storage)
  - TEMA Standards / ASME Sec VIII (Shell & Tube Heat Exchangers)
  - ASME B31.3 / B31.4 / B31.8 (Process Piping & Pipeline Systems)
  - Referensi Perusahaan: SSY-PRO-PID-002 & SSY-PRO-PID-003

Wajib di-import oleh semua script P&ID / PFD proyek agar simbol katup, aktuator,
instrumen, bejana, tangki, heat exchanger, kompresor, level bridle tertutup,
macro assembly, auto-trimming, dan auto-schedule MTO 100% konsisten.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from cadgen import build123d as bd

BUBBLE_R = 6.0


# =============================================================================
# PRIMITIF GEOMETRI DASAR (2D EDGE MURNI — DILARANG POLYFACE)
# =============================================================================
def line(x1: float, y1: float, x2: float, y2: float) -> bd.Edge:
    return bd.Edge.make_line(bd.Vector(x1, y1, 0), bd.Vector(x2, y2, 0))


def circle(x: float, y: float, r: float) -> bd.Edge:
    return bd.Location((x, y, 0)) * bd.Edge.make_circle(r)


def arc(x: float, y: float, r: float, a1: float, a2: float) -> bd.Edge:
    return bd.Location((x, y, 0)) * bd.Edge.make_circle(r, start_angle=a1, end_angle=a2)


def rect(x0: float, y0: float, x1: float, y1: float) -> list[bd.Edge]:
    return [
        line(x0, y0, x1, y0),
        line(x1, y0, x1, y1),
        line(x1, y1, x0, y1),
        line(x0, y1, x0, y0),
    ]


def dashed(
    x1: float, y1: float, x2: float, y2: float, dash: float = 4.0, gap: float = 1.6
) -> list[bd.Edge]:
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 1e-6:
        return []
    ux, uy = dx / L, dy / L
    out, t = [], 0.0
    while t < L - 1e-9:
        t2 = min(t + dash, L)
        if t2 - t > 1e-6:
            out.append(line(x1 + ux * t, y1 + uy * t, x1 + ux * t2, y1 + uy * t2))
        t = t2 + gap
    return out


def dashed_brk(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    brk: tuple | list = (),
    dash: float = 4.0,
    gap: float = 1.6,
    half: float = 1.5,
) -> list[bd.Edge]:
    """Garis putus-putus (sinyal elektrik) dengan celah break 3 mm (half=1.5) pada titik potong."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 1e-6:
        return []
    ux, uy = dx / L, dy / L
    cs = sorted(c for c in brk if half + 0.2 < c < L - half - 0.2)
    runs, a = [], 0.0
    for c in cs:
        runs.append((a, c - half))
        a = c + half
    runs.append((a, L))
    out = []
    for ra, rb in runs:
        if rb - ra >= 0.3:
            out += dashed(x1 + ux * ra, y1 + uy * ra, x1 + ux * rb, y1 + uy * rb, dash, gap)
    return out


def arc3(p1: tuple[float, float], pm: tuple[float, float], p2: tuple[float, float]) -> bd.Edge:
    """Arc melalui 3 titik (untuk ellipsoidal head bejana tekan)."""
    ax, ay = p1
    bx, by = pm
    cx, cy = p2
    d1x, d1y = bx - ax, by - ay
    d2x, d2y = cx - ax, cy - ay
    e1 = (bx * bx + by * by) - (ax * ax + ay * ay)
    e2 = (cx * cx + cy * cy) - (ax * ax + ay * ay)
    det = d1x * d2y - d2x * d1y
    if abs(det) < 1e-9:
        return line(ax, ay, cx, cy)
    ux = (e1 * d2y - e2 * d1y) / (2.0 * det)
    uy = (d1x * e2 - d2x * e1) / (2.0 * det)
    r = math.hypot(ax - ux, ay - uy)
    aa = math.degrees(math.atan2(ay - uy, ax - ux))
    am = math.degrees(math.atan2(by - uy, bx - ux))
    ac = math.degrees(math.atan2(cy - uy, cx - ux))
    if (am - aa) % 360.0 < (ac - aa) % 360.0:
        return arc(ux, uy, r, aa, ac)
    return arc(ux, uy, r, ac, aa)


def pneu(x1: float, y1: float, x2: float, y2: float, spacing: float = 8.0) -> list[bd.Edge]:
    """Sinyal pneumatic (ANSI/ISA-5.1): garis utuh dengan tanda slash ganda '//'."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < 1e-6:
        return []
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    sx, sy = ux * 0.5 + px * 0.866, uy * 0.5 + py * 0.866
    n = math.hypot(sx, sy)
    sx, sy = sx / n, sy / n
    out = [line(x1, y1, x2, y2)]
    hl, t = 1.5, spacing / 2.0
    while t < L:
        mx, my = x1 + ux * t, y1 + uy * t
        for off in (-0.7, 0.7):
            ax, ay = mx + ux * off, my + uy * off
            out.append(line(ax - sx * hl, ay - sy * hl, ax + sx * hl, ay + sy * hl))
        t += spacing
    return out


def hatch45(x0: float, y0: float, x1: float, y1: float, spacing: float = 3.0) -> list[bd.Edge]:
    """Arsiran 45 derajat untuk internals bejana (coalescer pack, demister pad)."""
    out = []
    c = x0 - y1
    while c <= x1 - y0:
        xs = max(x0, c + y0)
        xe = min(x1, c + y1)
        if xe - xs > 0.1:
            out.append(line(xs, xs - c, xe, xe - c))
        c += spacing
    return out


def comp(items: list) -> bd.Compound:
    flat = []
    for item in items:
        if isinstance(item, list):
            flat.extend(item)
        elif item is not None:
            flat.append(item)
    return bd.Compound.make_composite(flat)


# =============================================================================
# HELPER AUTO-TRIMMING PIPA (DILARANG MENEMBUS SIMBOL ATAU PERSILANGAN)
# =============================================================================
def pipe_run_h(
    y: float, x0: float, x1: float, gaps: list[tuple[float, float]] | None = None
) -> list[bd.Edge]:
    """Garis pipa horizontal dengan celah (gaps=[(center_x, half_width), ...]) otomatis terpotong."""
    if gaps is None:
        gaps = []
    x_min, x_max = min(x0, x1), max(x0, x1)
    intervals = []
    for c, hw in gaps:
        ia = max(x_min, c - hw)
        ib = min(x_max, c + hw)
        if ib > ia:
            intervals.append((ia, ib))
    intervals.sort()
    merged = []
    for ia, ib in intervals:
        if not merged:
            merged.append([ia, ib])
        else:
            if ia <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], ib)
            else:
                merged.append([ia, ib])
    out = []
    curr = x_min
    for ia, ib in merged:
        if ia - curr > 0.1:
            out.append(line(curr, y, ia, y))
        curr = max(curr, ib)
    if x_max - curr > 0.1:
        out.append(line(curr, y, x_max, y))
    return out


def pipe_run_v(
    x: float, y0: float, y1: float, gaps: list[tuple[float, float]] | None = None
) -> list[bd.Edge]:
    """Garis pipa vertikal dengan celah (gaps=[(center_y, half_height), ...]) otomatis terpotong."""
    if gaps is None:
        gaps = []
    y_min, y_max = min(y0, y1), max(y0, y1)
    intervals = []
    for c, hh in gaps:
        ia = max(y_min, c - hh)
        ib = min(y_max, c + hh)
        if ib > ia:
            intervals.append((ia, ib))
    intervals.sort()
    merged = []
    for ia, ib in intervals:
        if not merged:
            merged.append([ia, ib])
        else:
            if ia <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], ib)
            else:
                merged.append([ia, ib])
    out = []
    curr = y_min
    for ia, ib in merged:
        if ia - curr > 0.1:
            out.append(line(x, curr, x, ia))
        curr = max(curr, ib)
    if y_max - curr > 0.1:
        out.append(line(x, curr, x, y_max))
    return out


# =============================================================================
# KELAS UTAMA KONTEKS P&ID (PIDContext)
# =============================================================================
class PIDContext:
    """Konteks pembuat P&ID / PFD standar perusahaan (A1 841x594 mm, ISO 10628-2 & ANSI/ISA-5.1)."""

    def __init__(self) -> None:
        self.frame: list[bd.Edge] = []
        self.title: list[bd.Edge] = []
        self.equip: list[bd.Edge] = []
        self.proc: list[bd.Edge] = []
        self.sym: list[bd.Edge] = []
        self.sig: list[bd.Edge] = []
        self.sigp: list[bd.Edge] = []
        self.hatch: list[bd.Edge] = []
        self.texts: list[dict] = []
        self.solids: list[dict] = []

        # Auto-Registry Schedules (Equipment List, Valve MTO, Instrument Index, Line List)
        self.schedule_valves: list[dict] = []
        self.schedule_instruments: list[dict] = []
        self.schedule_equipment: list[dict] = []
        self.schedule_lines: list[dict] = []

    def text(
        self,
        t: str,
        x: float,
        y: float,
        size: float = 2.0,
        rot: float = 0.0,
        left: bool = False,
        layer: str = "REF-TEXT",
    ) -> list:
        """Catat entitas MTEXT (font ARIAL, tinggi 0.5..3.0 mm, att=4 bila left=True, att=5 bila tengah)."""
        if not t:
            return []
        h = max(0.5, min(3.0, float(size)))
        att = 4 if left else 5
        self.texts.append(
            {
                "t": str(t),
                "x": round(float(x), 3),
                "y": round(float(y), 3),
                "h": round(h, 2),
                "rot": round(float(rot), 1),
                "layer": layer,
                "att": att,
            }
        )
        return []

    def solid_triangle(
        self,
        p1: tuple[float, float],
        p2: tuple[float, float],
        p3: tuple[float, float],
        layer: str = "REF-PROC",
    ) -> None:
        self.solids.append(
            {
                "pts": [
                    [round(p1[0], 3), round(p1[1], 3)],
                    [round(p2[0], 3), round(p2[1], 3)],
                    [round(p3[0], 3), round(p3[1], 3)],
                ],
                "layer": layer,
            }
        )

    def solid_dot(self, cx: float, cy: float, r: float = 1.3, layer: str = "REF-PROC") -> None:
        """Lingkaran penuh SOLID via 8-segitiga fan (untuk globe valve & check valve hinge)."""
        n = 8
        pts = [
            (cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n))
            for i in range(n)
        ]
        for i in range(n):
            self.solid_triangle((cx, cy), pts[i], pts[(i + 1) % n], layer=layer)

    # -------------------------------------------------------------------------
    # SIMBOL PANAH ALIRAN & KATUP (ISO 10628-2)
    # -------------------------------------------------------------------------
    def flow_arrow_h(
        self, x: float, y: float, direction: int = 1, size: float = 3.2, layer: str = "REF-PROC"
    ) -> list[bd.Edge]:
        if direction >= 0:
            self.solid_triangle(
                (x, y), (x - size * 1.5, y + size * 0.5), (x - size * 1.5, y - size * 0.5), layer=layer
            )
        else:
            self.solid_triangle(
                (x, y), (x + size * 1.5, y + size * 0.5), (x + size * 1.5, y - size * 0.5), layer=layer
            )
        return []

    def flow_arrow_v(
        self, x: float, y: float, direction: int = 1, size: float = 3.2, layer: str = "REF-PROC"
    ) -> list[bd.Edge]:
        if direction >= 0:
            self.solid_triangle(
                (x, y), (x - size * 0.5, y - size * 1.5), (x + size * 0.5, y - size * 1.5), layer=layer
            )
        else:
            self.solid_triangle(
                (x, y), (x - size * 0.5, y + size * 1.5), (x + size * 0.5, y + size * 1.5), layer=layer
            )
        return []

    def valve_gate_h(
        self,
        cx: float,
        cy: float,
        w: float = 10.0,
        h: float = 6.0,
        nc: bool = False,
        flanged: bool = True,
        tag: str = "",
    ) -> list[bd.Edge]:
        hw, hh = w / 2.0, h / 2.0
        out = [
            line(cx - hw, cy - hh, cx, cy),
            line(cx, cy, cx - hw, cy + hh),
            line(cx - hw, cy - hh, cx - hw, cy + hh),
            line(cx + hw, cy - hh, cx, cy),
            line(cx, cy, cx + hw, cy + hh),
            line(cx + hw, cy - hh, cx + hw, cy + hh),
            line(cx, cy, cx, cy + hh + 2.5),
            line(cx - 2.5, cy + hh + 2.5, cx + 2.5, cy + hh + 2.5),
        ]
        if flanged:
            out += [
                line(cx - hw - 1.2, cy - hh - 1.0, cx - hw - 1.2, cy + hh + 1.0),
                line(cx + hw + 1.2, cy - hh - 1.0, cx + hw + 1.2, cy + hh + 1.0),
            ]
        if nc:
            self.solid_triangle((cx - hw, cy - hh), (cx, cy), (cx - hw, cy + hh), layer="REF-PROC")
            self.solid_triangle((cx + hw, cy - hh), (cx, cy), (cx + hw, cy + hh), layer="REF-PROC")
        if tag:
            self.schedule_valves.append({
                "tag": tag,
                "type": "GATE VALVE (NC)" if nc else "GATE VALVE",
                "orientation": "H",
                "x": round(cx, 3),
                "y": round(cy, 3),
                "flanged": flanged,
            })
        return out

    def valve_gate_v(
        self,
        cx: float,
        cy: float,
        w: float = 6.0,
        h: float = 10.0,
        nc: bool = False,
        flanged: bool = True,
        tag: str = "",
    ) -> list[bd.Edge]:
        hw, hh = w / 2.0, h / 2.0
        out = [
            line(cx - hw, cy - hh, cx, cy),
            line(cx + hw, cy - hh, cx, cy),
            line(cx - hw, cy - hh, cx + hw, cy - hh),
            line(cx - hw, cy + hh, cx, cy),
            line(cx + hw, cy + hh, cx, cy),
            line(cx - hw, cy + hh, cx + hw, cy + hh),
            line(cx, cy, cx + hw + 2.5, cy),
            line(cx + hw + 2.5, cy - 2.5, cx + hw + 2.5, cy + 2.5),
        ]
        if flanged:
            out += [
                line(cx - hw - 0.8, cy - hh - 1.2, cx + hw + 0.8, cy - hh - 1.2),
                line(cx - hw - 0.8, cy + hh + 1.2, cx + hw + 0.8, cy + hh + 1.2),
            ]
        if nc:
            self.solid_triangle((cx - hw, cy - hh), (cx, cy), (cx + hw, cy - hh), layer="REF-PROC")
            self.solid_triangle((cx - hw, cy + hh), (cx, cy), (cx + hw, cy + hh), layer="REF-PROC")
        if tag:
            self.schedule_valves.append({
                "tag": tag,
                "type": "GATE VALVE (NC)" if nc else "GATE VALVE",
                "orientation": "V",
                "x": round(cx, 3),
                "y": round(cy, 3),
                "flanged": flanged,
            })
        return out

    def valve_globe_h(
        self,
        cx: float,
        cy: float,
        w: float = 10.0,
        h: float = 6.0,
        flanged: bool = True,
        tag: str = "",
        nc: bool = False,
    ) -> list[bd.Edge]:
        out = self.valve_gate_h(cx, cy, w, h, nc=nc, flanged=flanged)
        self.solid_dot(cx, cy, r=1.3, layer="REF-PROC")
        if tag:
            self.schedule_valves.append({
                "tag": tag,
                "type": "GLOBE VALVE (NC)" if nc else "GLOBE VALVE",
                "orientation": "H",
                "x": round(cx, 3),
                "y": round(cy, 3),
                "flanged": flanged,
            })
        return out

    def control_valve_h(
        self,
        cx: float,
        cy: float,
        w: float = 10.0,
        h: float = 6.0,
        tag: str = "",
        fail: str = "",
    ) -> list[bd.Edge]:
        """Control valve (globe body + diaphragm dome actuator ISA-5.1, TANPA handwheel T-bar)."""
        hw, hh = w / 2.0, h / 2.0
        stem_top = cy + hh + 5.0
        out = [
            line(cx - hw, cy - hh, cx, cy),
            line(cx, cy, cx - hw, cy + hh),
            line(cx - hw, cy - hh, cx - hw, cy + hh),
            line(cx + hw, cy - hh, cx, cy),
            line(cx, cy, cx + hw, cy + hh),
            line(cx + hw, cy - hh, cx + hw, cy + hh),
            line(cx - hw - 1.2, cy - hh - 1.0, cx - hw - 1.2, cy + hh + 1.0),
            line(cx + hw + 1.2, cy - hh - 1.0, cx + hw + 1.2, cy + hh + 1.0),
            line(cx, cy, cx, stem_top),
            arc(cx, stem_top, 4.5, 0, 180),
            line(cx - 4.5, stem_top, cx + 4.5, stem_top),
        ]
        self.solid_dot(cx, cy, r=1.3, layer="REF-PROC")
        if tag:
            self.schedule_valves.append({
                "tag": tag,
                "type": "CONTROL VALVE",
                "orientation": "H",
                "x": round(cx, 3),
                "y": round(cy, 3),
                "fail": fail,
            })
        return out

    def sdv_h(
        self, cx: float, cy: float, tag: str = "SDV-101", fail: str = "FC"
    ) -> list[bd.Edge]:
        """Shutdown valve: flanged gate valve + diaphragm actuator + solenoid S (TANPA T-bar)."""
        w, h = 10.0, 6.0
        hw, hh = w / 2.0, h / 2.0
        stem_top = cy + hh + 5.0
        out = [
            line(cx - hw, cy - hh, cx, cy),
            line(cx, cy, cx - hw, cy + hh),
            line(cx - hw, cy - hh, cx - hw, cy + hh),
            line(cx + hw, cy - hh, cx, cy),
            line(cx, cy, cx + hw, cy + hh),
            line(cx + hw, cy - hh, cx + hw, cy + hh),
            line(cx - hw - 1.2, cy - hh - 1.0, cx - hw - 1.2, cy + hh + 1.0),
            line(cx + hw + 1.2, cy - hh - 1.0, cx + hw + 1.2, cy + hh + 1.0),
            line(cx, cy, cx, stem_top),
            arc(cx, stem_top, 4.5, 0, 180),
            line(cx - 4.5, stem_top, cx + 4.5, stem_top),
        ]
        out += rect(cx + 6.0, stem_top - 2.5, cx + 11.0, stem_top + 2.5)
        self.text("S", cx + 8.5, stem_top, size=1.8)
        out += pneu(cx + 6.0, stem_top, cx + 4.5, stem_top, spacing=3.0)
        if tag:
            self.text(tag, cx, cy - 7.0, size=2.2)
            self.schedule_valves.append({
                "tag": tag,
                "type": "SHUTDOWN VALVE (SDV)",
                "orientation": "H",
                "x": round(cx, 3),
                "y": round(cy, 3),
                "fail": fail,
            })
        if fail:
            self.text(fail, cx, cy - 11.5, size=1.8)
        return out

    def valve_check_h(
        self, cx: float, cy: float, w: float = 10.0, h: float = 6.0, tag: str = ""
    ) -> list[bd.Edge]:
        """Check valve (ISO 10628-2): 2 garis tegak + diagonal flapper + engsel solid + panah solid (TANPA garis kotak atas/bawah)."""
        hw, hh = w / 2.0, h / 2.0
        out = [
            line(cx - hw, cy - hh, cx - hw, cy + hh),
            line(cx + hw, cy - hh, cx + hw, cy + hh),
            line(cx - hw, cy + hh, cx + hw, cy - hh),
            line(cx - hw - 1.2, cy - hh - 1.0, cx - hw - 1.2, cy + hh + 1.0),
            line(cx + hw + 1.2, cy - hh - 1.0, cx + hw + 1.2, cy + hh + 1.0),
        ]
        self.solid_dot(cx - hw, cy + hh, r=0.9, layer="REF-PROC")
        self.solid_triangle(
            (cx + hw, cy - hh), (cx + hw - 3.0, cy - hh), (cx + hw, cy - hh + 3.0), layer="REF-PROC"
        )
        if tag:
            self.schedule_valves.append({
                "tag": tag,
                "type": "CHECK VALVE",
                "orientation": "H",
                "x": round(cx, 3),
                "y": round(cy, 3),
            })
        return out

    def psv_angle(
        self,
        cx: float,
        cy: float,
        tag: str = "PSV-101",
        size_str: str = "DN100x150",
        set_press: str = "SET 17.2 BARG",
    ) -> list[bd.Edge]:
        """Spring-Loaded Angle PSV (ISO 10628-2)."""
        out = [
            line(cx - 4.0, cy - 8.0, cx, cy),
            line(cx + 4.0, cy - 8.0, cx, cy),
            line(cx - 4.0, cy - 8.0, cx + 4.0, cy - 8.0),
            line(cx - 5.2, cy - 9.2, cx + 5.2, cy - 9.2),
            line(cx, cy, cx + 8.0, cy - 4.0),
            line(cx, cy, cx + 8.0, cy + 4.0),
            line(cx + 8.0, cy - 4.0, cx + 8.0, cy + 4.0),
            line(cx + 9.2, cy - 5.2, cx + 9.2, cy + 5.2),
            line(cx, cy, cx, cy + 5.0),
            line(cx - 3.0, cy + 5.0, cx + 3.0, cy + 8.0),
            line(cx + 3.0, cy + 8.0, cx - 3.0, cy + 11.0),
            line(cx - 3.0, cy + 11.0, cx + 3.0, cy + 14.0),
            line(cx + 3.0, cy + 14.0, cx, cy + 16.0),
            line(cx - 3.0, cy + 16.0, cx + 3.0, cy + 16.0),
        ]
        self.text(tag, cx - 12.0, cy + 12.0, size=2.2)
        self.text(size_str, cx - 12.0, cy + 7.5, size=1.8)
        self.text(set_press, cx - 12.0, cy + 3.0, size=1.8)
        if tag:
            self.schedule_valves.append({
                "tag": tag,
                "type": "PRESSURE SAFETY VALVE (PSV)",
                "orientation": "ANGLE",
                "x": round(cx, 3),
                "y": round(cy, 3),
                "size": size_str,
                "set_press": set_press,
            })
        return out

    def reducer_h(
        self,
        cx: float,
        cy: float,
        w: float = 8.0,
        h1: float = 5.0,
        h2: float = 8.0,
        label: str = "DN100x150",
    ) -> list[bd.Edge]:
        hw = w / 2.0
        hh1, hh2 = h1 / 2.0, h2 / 2.0
        out = [
            line(cx - hw, cy - hh1, cx - hw, cy + hh1),
            line(cx - hw, cy + hh1, cx + hw, cy + hh2),
            line(cx + hw, cy + hh2, cx + hw, cy - hh2),
            line(cx + hw, cy - hh2, cx - hw, cy - hh1),
        ]
        if label:
            self.text(label, cx, cy + hh2 + 3.0, size=1.8)
        return out

    def orifice_h(self, cx: float, cy: float, tag_fe: str = "") -> list[bd.Edge]:
        out = [
            line(cx - 1.2, cy - 6.0, cx - 1.2, cy + 6.0),
            line(cx + 1.2, cy - 6.0, cx + 1.2, cy + 6.0),
            line(cx - 2.5, cy - 6.0, cx - 2.5, cy + 6.0),
            line(cx + 2.5, cy - 6.0, cx + 2.5, cy + 6.0),
        ]
        if tag_fe:
            self.text(tag_fe, cx - 8.0, cy + 3.0, size=1.8)
            self.schedule_instruments.append({
                "tag": tag_fe,
                "type": "FLOW ORIFICE (FE)",
                "x": round(cx, 3),
                "y": round(cy, 3),
            })
        return out

    def strainer_v(self, cx: float, cy: float, tag: str = "ST-101") -> list[bd.Edge]:
        out = [
            line(cx - 3.5, cy - 6.0, cx + 3.5, cy - 6.0),
            line(cx - 3.5, cy + 6.0, cx + 3.5, cy + 6.0),
            line(cx - 3.5, cy - 6.0, cx - 3.5, cy + 6.0),
            line(cx + 3.5, cy - 6.0, cx + 3.5, cy + 6.0),
            line(cx, cy, cx + 6.0, cy - 6.0),
            line(cx + 3.5, cy - 2.5, cx + 8.5, cy - 7.5),
            line(cx + 6.0, cy - 6.0, cx + 8.5, cy - 7.5),
        ]
        if tag:
            self.text(tag, cx + 11.0, cy, size=2.0)
            self.schedule_equipment.append({
                "tag": tag,
                "type": "STRAINER (BASKET/Y-TYPE)",
                "x": round(cx, 3),
                "y": round(cy, 3),
            })
        return out

    def pump_centrifugal(
        self, cx: float, cy: float, r: float = 7.0, tag: str = ""
    ) -> list[bd.Edge]:
        out = [
            circle(cx, cy, r),
            line(cx - 4.5, cy - r, cx - 6.5, cy - r - 3.5),
            line(cx + 4.5, cy - r, cx + 6.5, cy - r - 3.5),
            line(cx - 7.5, cy - r - 3.5, cx + 7.5, cy - r - 3.5),
            line(cx - 4.0, cy + r + 2.0, cx + 4.0, cy + r + 2.0),
            line(cx - 4.0, cy + r + 3.2, cx + 4.0, cy + r + 3.2),
            line(cx, cy + r, cx, cy + r + 2.0),
        ]
        if tag:
            self.schedule_equipment.append({
                "tag": tag,
                "type": "CENTRIFUGAL PUMP",
                "x": round(cx, 3),
                "y": round(cy, 3),
                "radius": round(r, 3),
            })
        return out

    def electric_motor(
        self, cx: float, cy: float, r: float = 5.0, tag: str = "M"
    ) -> list[bd.Edge]:
        out = [
            circle(cx, cy, r),
            line(cx - 3.5, cy - r, cx - 5.0, cy - r - 5.5),
            line(cx + 3.5, cy - r, cx + 5.0, cy - r - 5.5),
            line(cx - 6.0, cy - r - 5.5, cx + 6.0, cy - r - 5.5),
        ]
        self.text(tag, cx, cy, size=2.5)
        if tag and tag != "M":
            self.schedule_equipment.append({
                "tag": tag,
                "type": "ELECTRIC MOTOR",
                "x": round(cx, 3),
                "y": round(cy, 3),
                "radius": round(r, 3),
            })
        return out

    # -------------------------------------------------------------------------
    # KATALOG PERALATAN PROSES TAMBAHAN (ISO 10628-2, API 12J, API 650, TEMA)
    # -------------------------------------------------------------------------
    def vessel_vertical_ko(
        self,
        cx: float,
        y_bot: float,
        y_top: float,
        r: float = 18.0,
        tag: str = "V-102",
        demister: bool = True,
    ) -> list[bd.Edge]:
        """Bejana vertikal (Knock-Out Drum / Gas Scrubber) sesuai ISO 10628-2 & API RP 12J.

        Dilengkapi:
          - Dinding silinder kiri & kanan (cx - r, cx + r)
          - Head 2:1 ellipsoidal atas & bawah via arc3
          - Garis seam las (tangent line) putus-putus
          - Skirt support di bawah y_bot lengkap dengan base ring
          - Demister pad berarsir 45 derajat (self.hatch += hatch45(...)) di bagian atas
          - Vortex breaker baffle di dasar head bawah (simbol ISO plat silang cruciform)
          - Nozzle drain / outlet dasar dengan flensa
          - Label tag & auto-registration ke schedule_equipment
        """
        h_head = r * 0.5  # 2:1 ellipsoidal head depth
        out = [
            # Dinding silinder vertikal
            line(cx - r, y_bot, cx - r, y_top),
            line(cx + r, y_bot, cx + r, y_top),
            # Head atas & bawah (arc3)
            arc3((cx - r, y_top), (cx, y_top + h_head), (cx + r, y_top)),
            arc3((cx - r, y_bot), (cx, y_bot - h_head), (cx + r, y_bot)),
        ]
        # Seam / tangent lines (putus-putus)
        out += dashed(cx - r, y_top, cx + r, y_top, dash=3.0, gap=1.5)
        out += dashed(cx - r, y_bot, cx + r, y_bot, dash=3.0, gap=1.5)

        # Skirt support di bawah y_bot dengan clearance untuk nozzle dasar
        skirt_h = max(14.0, h_head + 7.0)
        y_skirt_base = y_bot - skirt_h
        out += [
            line(cx - r, y_bot, cx - r, y_skirt_base),
            line(cx + r, y_bot, cx + r, y_skirt_base),
            # Base plate ring
            line(cx - r - 2.5, y_skirt_base, cx + r + 2.5, y_skirt_base),
            line(cx - r - 2.5, y_skirt_base - 1.2, cx + r + 2.5, y_skirt_base - 1.2),
            line(cx - r - 2.5, y_skirt_base - 1.2, cx - r - 2.5, y_skirt_base),
            line(cx + r + 2.5, y_skirt_base - 1.2, cx + r + 2.5, y_skirt_base),
        ]

        # Demister pad di bagian atas
        if demister:
            y_d_top = y_top - 3.0
            y_d_bot = y_top - 9.0
            w_d = r - 1.2
            out += [
                line(cx - w_d, y_d_top, cx + w_d, y_d_top),
                line(cx - w_d, y_d_bot, cx + w_d, y_d_bot),
                line(cx - w_d, y_d_bot, cx - w_d, y_d_top),
                line(cx + w_d, y_d_bot, cx + w_d, y_d_top),
            ]
            self.hatch += hatch45(cx - w_d, y_d_bot, cx + w_d, y_d_top, spacing=2.5)

        # Nozzle drain / outlet di apex head bawah
        y_v = y_bot - h_head
        out += [
            line(cx - 2.0, y_v, cx - 2.0, y_v - 4.5),
            line(cx + 2.0, y_v, cx + 2.0, y_v - 4.5),
            line(cx - 3.5, y_v - 4.5, cx + 3.5, y_v - 4.5),
        ]

        # Vortex breaker di dasar head bawah (simbol ISO plat silang cruciform)
        out += [
            line(cx - 3.5, y_v + 2.0, cx + 3.5, y_v + 2.0),
            line(cx, y_v + 0.5, cx, y_v + 4.5),
            line(cx - 2.5, y_v + 0.8, cx + 2.5, y_v + 4.0),
            line(cx - 2.5, y_v + 4.0, cx + 2.5, y_v + 0.8),
        ]

        if tag:
            self.text(tag, cx, (y_bot + y_top) / 2.0, size=2.5)
            self.schedule_equipment.append({
                "tag": tag,
                "type": "VERTICAL KO DRUM / SCRUBBER",
                "x": round(cx, 3),
                "y": round((y_bot + y_top) / 2.0, 3),
                "y_bot": round(y_bot, 3),
                "y_top": round(y_top, 3),
                "radius": round(r, 3),
                "demister": demister,
            })
        return out

    def storage_tank_atm(
        self,
        cx: float,
        y_bot: float,
        w: float = 48.0,
        h_shell: float = 36.0,
        h_roof: float = 8.0,
        tag: str = "T-101",
        bund: bool = False,
    ) -> list[bd.Edge]:
        """Tangki timbun atmosferik cone roof (API STD 650).

        Dilengkapi:
          - Dinding shell silinder & dasar tangki
          - Atap kerucut segitiga (cone roof)
          - Conservation vent / breather valve di puncak atap
          - Liquid level dashed line dengan penunjuk segitiga
          - Tanggul bundwall opsi parametrik (bund=True untuk Plot Plan, bund=False default untuk P&ID)
          - Label tag & auto-registration ke schedule_equipment
        """
        hw = w / 2.0
        y_top_shell = y_bot + h_shell
        y_apex = y_top_shell + h_roof
        out = [
            # Shell persegi panjang (dasar, dinding kiri/kanan, curb angle atas)
            line(cx - hw, y_bot, cx + hw, y_bot),
            line(cx - hw, y_bot, cx - hw, y_top_shell),
            line(cx + hw, y_bot, cx + hw, y_top_shell),
            line(cx - hw, y_top_shell, cx + hw, y_top_shell),
            # Atap kerucut (cone roof)
            line(cx - hw, y_top_shell, cx, y_apex),
            line(cx, y_apex, cx + hw, y_top_shell),
            # Conservation vent / breather valve di puncak atap
            line(cx, y_apex, cx, y_apex + 3.0),
            line(cx - 1.8, y_apex + 3.0, cx + 1.8, y_apex + 3.0),
            line(cx, y_apex + 3.0, cx, y_apex + 5.5),
            line(cx - 3.5, y_apex + 5.5, cx + 3.5, y_apex + 5.5),
            line(cx - 3.5, y_apex + 5.5, cx, y_apex + 7.5),
            line(cx, y_apex + 7.5, cx + 3.5, y_apex + 5.5),
        ]

        # Liquid level line (garis putus-putus permukaan cairan normal ~75% h_shell)
        y_level = y_bot + 0.75 * h_shell
        out += dashed(cx - hw + 2.0, y_level, cx + hw - 2.0, y_level, dash=3.0, gap=1.5)
        self.solid_triangle(
            (cx - hw + 8.0, y_level),
            (cx - hw + 6.0, y_level + 3.0),
            (cx - hw + 10.0, y_level + 3.0),
            layer="REF-EQUIP",
        )
        out.append(line(cx - hw + 5.0, y_level + 3.0, cx - hw + 11.0, y_level + 3.0))

        # Pondasi dasar tangki
        out += [
            line(cx - hw - 3.0, y_bot, cx + hw + 3.0, y_bot),
            line(cx - hw - 3.0, y_bot - 1.2, cx + hw + 3.0, y_bot - 1.2),
            line(cx - hw - 3.0, y_bot - 1.2, cx - hw - 3.0, y_bot),
            line(cx + hw + 3.0, y_bot - 1.2, cx + hw + 3.0, y_bot),
        ]

        # Bundwall / containment dike opsional (default False untuk P&ID)
        if bund:
            # Garis tanggul: dua garis horizontal sejajar di kaki tangki kiri/kanan dengan tick arsir kecil
            # Tanggul kiri
            x_l1, x_l2 = cx - hw - 18.0, cx - hw - 3.0
            out += [
                line(x_l1, y_bot, x_l2, y_bot),
                line(x_l1, y_bot + 2.0, x_l2, y_bot + 2.0),
                line(x_l1, y_bot, x_l1, y_bot + 2.0),
                line(x_l2, y_bot, x_l2, y_bot + 2.0),
            ]
            for xt in [x_l1 + 3.0, x_l1 + 6.0, x_l1 + 9.0, x_l1 + 12.0]:
                out.append(line(xt, y_bot, xt + 1.2, y_bot + 2.0))
            # Tanggul kanan
            x_r1, x_r2 = cx + hw + 3.0, cx + hw + 18.0
            out += [
                line(x_r1, y_bot, x_r2, y_bot),
                line(x_r1, y_bot + 2.0, x_r2, y_bot + 2.0),
                line(x_r1, y_bot, x_r1, y_bot + 2.0),
                line(x_r2, y_bot, x_r2, y_bot + 2.0),
            ]
            for xt in [x_r1 + 3.0, x_r1 + 6.0, x_r1 + 9.0, x_r1 + 12.0]:
                out.append(line(xt, y_bot, xt + 1.2, y_bot + 2.0))

        if tag:
            self.text(tag, cx, y_bot + h_shell * 0.42, size=2.5)
            self.schedule_equipment.append({
                "tag": tag,
                "type": "ATMOSPHERIC CONE ROOF TANK (API 650)",
                "x": round(cx, 3),
                "y": round(y_bot + h_shell * 0.42, 3),
                "y_bot": round(y_bot, 3),
                "w": round(w, 3),
                "h_shell": round(h_shell, 3),
                "h_roof": round(h_roof, 3),
                "bund": bund,
            })
        return out

    def heat_exchanger_st(
        self,
        cx: float,
        cy: float,
        length: float = 44.0,
        r: float = 10.0,
        tag: str = "E-101",
    ) -> list[bd.Edge]:
        """Shell & Tube Heat Exchanger horizontal (ISO 10628-2 & TEMA).

        Dilengkapi:
          - Shell silinder horizontal
          - Tubesheet flange lines ganda
          - Channel spool silinder di ujung kiri lengkap dengan 2 nozzle tube vertikal (inlet & outlet)
          - Bonnet channel head kiri & return head kanan elipsoidal via arc3
          - Pass partition plate horizontal
          - Internal tube bundle dashed lines
          - 2 Nozzle shell vertikal (inlet atas & outlet bawah) berjarak aman dari saddles
          - Support saddles ganda
          - Label tag & auto-registration ke schedule_equipment
        """
        hw = length / 2.0
        x_l = cx - hw
        x_r = cx + hw
        w_chan = 8.0
        x_chan = x_l - w_chan

        out = [
            # Dinding shell silinder horizontal
            line(x_l, cy + r, x_r, cy + r),
            line(x_l, cy - r, x_r, cy - r),
            # Tubesheet flange lines ganda di x_l dan x_r (terhubung utuh ke shell & head)
            line(x_l, cy - r, x_l, cy + r),
            line(x_l - 1.5, cy - r, x_l - 1.5, cy + r),
            line(x_r, cy - r, x_r, cy + r),
            line(x_r + 1.5, cy - r, x_r + 1.5, cy + r),
            # Channel spool silinder kiri (antara tubesheet x_l dan bonnet head x_chan)
            line(x_chan, cy + r, x_l - 1.5, cy + r),
            line(x_chan, cy - r, x_l - 1.5, cy - r),
            # Channel bonnet head kiri & return head kanan (setengah lingkaran mulus tanpa sudut tajam)
            arc(x_chan, cy, r, 90, 270),
            arc(x_r + 1.5, cy, r, 270, 90),
            # Pass partition plate di channel head kiri
            line(x_chan - r, cy, x_l, cy),
        ]
        # Internal tube bundle dashed lines
        out += dashed(x_l + 2.0, cy + r * 0.38, x_r - 2.0, cy + r * 0.38, dash=3.0, gap=1.5)
        out += dashed(x_l + 2.0, cy - r * 0.38, x_r - 2.0, cy - r * 0.38, dash=3.0, gap=1.5)

        # 4 Nozzles:
        # 1. Shell inlet (atas)
        x_s_in = cx - length * 0.15
        out += [
            line(x_s_in - 2.0, cy + r, x_s_in - 2.0, cy + r + 4.0),
            line(x_s_in + 2.0, cy + r, x_s_in + 2.0, cy + r + 4.0),
            line(x_s_in - 3.5, cy + r + 4.0, x_s_in + 3.5, cy + r + 4.0),
        ]
        # 2. Shell outlet (bawah) - diposisikan aman bebas tabrakan dari saddle penopang
        x_s_out = cx + length * 0.08
        out += [
            line(x_s_out - 2.0, cy - r, x_s_out - 2.0, cy - r - 4.0),
            line(x_s_out + 2.0, cy - r, x_s_out + 2.0, cy - r - 4.0),
            line(x_s_out - 3.5, cy - r - 4.0, x_s_out + 3.5, cy - r - 4.0),
        ]
        # 3. Tube inlet (channel spool kiri bawah)
        x_t_in = x_chan + w_chan / 2.0
        out += [
            line(x_t_in - 1.8, cy - r, x_t_in - 1.8, cy - r - 4.0),
            line(x_t_in + 1.8, cy - r, x_t_in + 1.8, cy - r - 4.0),
            line(x_t_in - 3.2, cy - r - 4.0, x_t_in + 3.2, cy - r - 4.0),
        ]
        # 4. Tube outlet (channel spool kiri atas)
        x_t_out = x_chan + w_chan / 2.0
        out += [
            line(x_t_out - 1.8, cy + r, x_t_out - 1.8, cy + r + 4.0),
            line(x_t_out + 1.8, cy + r, x_t_out + 1.8, cy + r + 4.0),
            line(x_t_out - 3.2, cy + r + 4.0, x_t_out + 3.2, cy + r + 4.0),
        ]

        # Support saddles ganda di cx ± length * 0.35 (bebas tabrakan dari shell outlet)
        for xs in (cx - length * 0.35, cx + length * 0.35):
            out += [
                line(xs - 3.0, cy - r, xs - 4.2, cy - r - 4.0),
                line(xs + 3.0, cy - r, xs + 4.2, cy - r - 4.0),
                line(xs - 5.5, cy - r - 4.0, xs + 5.5, cy - r - 4.0),
            ]

        if tag:
            self.text(tag, cx, cy, size=2.5)
            self.schedule_equipment.append({
                "tag": tag,
                "type": "SHELL & TUBE HEAT EXCHANGER (TEMA)",
                "x": round(cx, 3),
                "y": round(cy, 3),
                "length": round(length, 3),
                "radius": round(r, 3),
            })
        return out

    def compressor_centrifugal(
        self,
        cx: float,
        cy: float,
        r_in: float = 6.0,
        r_out: float = 9.0,
        tag: str = "K-101",
    ) -> list[bd.Edge]:
        """Kompresor sentrifugal / ekspander gas dinamis sesuai ISO 10628-2.

        Dilengkapi:
          - Casing trapesium tirus ISO 10628-2 (suction besar r_out, discharge menyempit r_in)
          - Nozzle suction flanged vertikal ke atas di sisi suction (kiri)
          - Nozzle discharge flanged vertikal ke atas di sisi discharge (kanan)
          - Driver motor listrik 'M' & poros kopel
          - Skid baseplate penopang
          - Label tag & auto-registration ke schedule_equipment
        """
        w_casing = 16.0
        hw = w_casing / 2.0
        # Casing trapesium: suction di kiri (r_out), discharge di kanan (r_in)
        slope = (r_in - r_out) / w_casing  # kemiringan garis atas casing terhadap x dari kiri

        # Nozzle suction vertikal di sisi kiri (suction)
        x_suc_l = cx - hw + 1.5
        x_suc_r = cx - hw + 4.5
        y_suc_l = cy + r_out + slope * 1.5
        y_suc_r = cy + r_out + slope * 4.5
        y_suc_flange = cy + r_out + 4.5

        # Nozzle discharge vertikal di sisi kanan (discharge)
        x_dis_l = cx + hw - 4.5
        x_dis_r = cx + hw - 1.5
        y_dis_l = cy + r_out + slope * (w_casing - 4.5)
        y_dis_r = cy + r_out + slope * (w_casing - 1.5)
        y_dis_flange = cy + r_in + 4.5

        out = [
            # Dinding casing
            line(cx - hw, cy - r_out, cx - hw, cy + r_out),
            line(cx + hw, cy - r_in, cx + hw, cy + r_in),
            line(cx - hw, cy + r_out, cx + hw, cy + r_in),
            line(cx - hw, cy - r_out, cx + hw, cy - r_in),
            # Suction nozzle flanged (atas sisi kiri)
            line(x_suc_l, y_suc_l, x_suc_l, y_suc_flange),
            line(x_suc_r, y_suc_r, x_suc_r, y_suc_flange),
            line(x_suc_l - 1.0, y_suc_flange, x_suc_r + 1.0, y_suc_flange),
            # Discharge nozzle flanged (atas sisi kanan)
            line(x_dis_l, y_dis_l, x_dis_l, y_dis_flange),
            line(x_dis_r, y_dis_r, x_dis_r, y_dis_flange),
            line(x_dis_l - 1.0, y_dis_flange, x_dis_r + 1.0, y_dis_flange),
        ]

        # Driver motor listrik "M" & poros kopel di sisi kiri
        x_coupling = cx - hw - 3.5
        x_motor = cx - hw - 15.0
        r_motor = 6.0
        y_base = cy - max(r_in, r_out) - 4.0

        out += [
            # Poros kopel
            line(cx - hw, cy, x_coupling, cy),
            line(x_coupling, cy - 2.5, x_coupling, cy + 2.5),
            line(x_coupling, cy, x_motor + r_motor, cy),
            # Lingkaran motor M
            circle(x_motor, cy, r_motor),
            # Kaki motor ke baseplate
            line(x_motor - 3.5, cy - r_motor, x_motor - 3.5, y_base),
            line(x_motor + 3.5, cy - r_motor, x_motor + 3.5, y_base),
            # Kaki kompresor ke baseplate
            line(cx - 3.5, cy - r_out - slope * (hw - 3.5), cx - 3.5, y_base),
            line(cx + 3.5, cy - r_in + slope * (hw - 3.5), cx + 3.5, y_base),
            # Baseplate skid
            line(x_motor - r_motor - 3.0, y_base, cx + hw + 3.0, y_base),
            line(x_motor - r_motor - 3.0, y_base - 1.2, cx + hw + 3.0, y_base - 1.2),
            line(x_motor - r_motor - 3.0, y_base - 1.2, x_motor - r_motor - 3.0, y_base),
            line(cx + hw + 3.0, y_base - 1.2, cx + hw + 3.0, y_base),
        ]
        self.text("M", x_motor, cy, size=2.5)

        if tag:
            self.text(tag, cx, y_base - 5.5, size=2.5)
            self.schedule_equipment.append({
                "tag": tag,
                "type": "CENTRIFUGAL COMPRESSOR",
                "x": round(cx, 3),
                "y": round(cy, 3),
                "r_in": round(r_in, 3),
                "r_out": round(r_out, 3),
            })
        return out

    def pig_trap(
        self,
        cx: float,
        cy: float,
        length: float = 36.0,
        h_minor: float = 6.0,
        h_major: float = 10.0,
        direction: int = 1,
        tag: str = "PL-101",
    ) -> list[bd.Edge]:
        """Pig Launcher / Receiver sesuai ISO 10628-2 & ASME B31.8 / B31.4.

        Dilengkapi:
          - Quick-opening closure door berengsel (convex head + hinge flange)
          - Major barrel (diameter besar untuk loading/retrieving)
          - Eccentric bottom-flat reducer (garis dasar rata horizontal agar pig tidak tersangkut)
          - Minor barrel (ukuran pipa nominal)
          - Kicker line nozzle & Pig passage signaller (XI)
          - Support saddles
          - Label tag & auto-registration ke schedule_equipment
        """
        hw = length / 2.0
        x_left = cx - hw
        x_right = cx + hw
        r_min = h_minor / 2.0
        y_bot = cy - r_min  # Garis dasar rata horizontal (bottom-flat)

        out = []
        if direction >= 0:
            # Launcher: Closure di kiri, aliran ke kanan
            x_maj_end = x_left + length * 0.45
            x_min_start = x_left + length * 0.65
            y_top_maj = y_bot + h_major
            y_top_min = y_bot + h_minor
            out += [
                # Garis dasar bawah rata (bottom-flat)
                line(x_left, y_bot, x_right, y_bot),
                # Major barrel atas
                line(x_left, y_top_maj, x_maj_end, y_top_maj),
                # Eccentric reducer atas miring
                line(x_maj_end, y_top_maj, x_min_start, y_top_min),
                # Minor barrel atas
                line(x_min_start, y_top_min, x_right, y_top_min),
                # Minor barrel outlet flange di x_right
                line(x_right, y_bot - 1.2, x_right, y_top_min + 1.2),
                line(x_right + 1.2, y_bot - 1.2, x_right + 1.2, y_top_min + 1.2),
                # Quick-Opening Closure door cembung di x_left
                arc3((x_left, y_bot), (x_left - 3.2, (y_bot + y_top_maj) / 2.0), (x_left, y_top_maj)),
                line(x_left, y_bot - 1.5, x_left, y_top_maj + 1.5),
                line(x_left - 1.2, y_bot - 1.5, x_left - 1.2, y_top_maj + 1.5),
            ]
            # Kicker line nozzle di major barrel (atas)
            x_kick = x_left + length * 0.22
            out += [
                line(x_kick - 1.8, y_top_maj, x_kick - 1.8, y_top_maj + 3.5),
                line(x_kick + 1.8, y_top_maj, x_kick + 1.8, y_top_maj + 3.5),
                line(x_kick - 3.0, y_top_maj + 3.5, x_kick + 3.0, y_top_maj + 3.5),
            ]
            # Pig passage signaller (XI) di minor barrel
            x_xi = x_left + length * 0.82
            out += [
                line(x_xi, y_top_min, x_xi, y_top_min + 3.0),
                line(x_xi - 2.0, y_top_min + 3.0, x_xi + 2.0, y_top_min + 5.0),
                line(x_xi + 2.0, y_top_min + 5.0, x_xi - 2.0, y_top_min + 5.0),
            ]
            self.text("XI", x_xi, y_top_min + 8.0, size=1.8)
            if tag:
                self.schedule_instruments.append({
                    "tag": f"{tag}-XI",
                    "type": "PIG SIGNALLER",
                    "x": round(x_xi, 3),
                    "y": round(y_top_min + 8.0, 3),
                })
        else:
            # Receiver: Closure di kanan, aliran dari kiri
            x_min_end = x_left + length * 0.35
            x_maj_start = x_left + length * 0.55
            y_top_min = y_bot + h_minor
            y_top_maj = y_bot + h_major
            out += [
                line(x_left, y_bot, x_right, y_bot),
                line(x_left, y_top_min, x_min_end, y_top_min),
                line(x_min_end, y_top_min, x_maj_start, y_top_maj),
                line(x_maj_start, y_top_maj, x_right, y_top_maj),
                line(x_left, y_bot - 1.2, x_left, y_top_min + 1.2),
                line(x_left - 1.2, y_bot - 1.2, x_left - 1.2, y_top_min + 1.2),
                arc3((x_right, y_top_maj), (x_right + 3.2, (y_bot + y_top_maj) / 2.0), (x_right, y_bot)),
                line(x_right, y_bot - 1.5, x_right, y_top_maj + 1.5),
                line(x_right + 1.2, y_bot - 1.5, x_right + 1.2, y_top_maj + 1.5),
            ]
            x_xi = x_left + length * 0.18
            out += [
                line(x_xi, y_top_min, x_xi, y_top_min + 3.0),
                line(x_xi - 2.0, y_top_min + 3.0, x_xi + 2.0, y_top_min + 5.0),
                line(x_xi + 2.0, y_top_min + 5.0, x_xi - 2.0, y_top_min + 5.0),
            ]
            self.text("XI", x_xi, y_top_min + 8.0, size=1.8)
            if tag:
                self.schedule_instruments.append({
                    "tag": f"{tag}-XI",
                    "type": "PIG SIGNALLER",
                    "x": round(x_xi, 3),
                    "y": round(y_top_min + 8.0, 3),
                })

        # Support saddles
        for xs in (x_left + length * 0.25, x_left + length * 0.75):
            out += [
                line(xs - 2.5, y_bot, xs - 3.5, y_bot - 3.5),
                line(xs + 2.5, y_bot, xs + 3.5, y_bot - 3.5),
                line(xs - 4.5, y_bot - 3.5, xs + 4.5, y_bot - 3.5),
            ]

        if tag:
            self.text(tag, cx, y_bot - 7.5, size=2.5)
            self.schedule_equipment.append({
                "tag": tag,
                "type": "PIG LAUNCHER" if direction >= 0 else "PIG RECEIVER",
                "x": round(cx, 3),
                "y": round(cy, 3),
                "length": round(length, 3),
                "direction": direction,
            })
        return out

    # -------------------------------------------------------------------------
    # INSTRUMEN, LEVEL BRIDLE TERTUTUP & CONTINUITY BOX (ANSI/ISA-5.1)
    # -------------------------------------------------------------------------
    def bubble(self, cx: float, cy: float, tag1: str = "", tag2: str = "") -> list[bd.Edge]:
        out = [circle(cx, cy, BUBBLE_R)]
        if tag1 and tag2:
            out.append(line(cx - BUBBLE_R, cy, cx + BUBBLE_R, cy))
            self.text(tag1, cx, cy + 2.2, size=2.0)
            self.text(tag2, cx, cy - 2.2, size=2.0)
        elif tag1:
            self.text(tag1, cx, cy, size=2.0)
        full_tag = f"{tag1}-{tag2}".strip("-") if (tag1 or tag2) else ""
        if full_tag:
            self.schedule_instruments.append({
                "tag": full_tag,
                "tag1": tag1,
                "tag2": tag2,
                "type": "FIELD INSTRUMENT",
                "x": round(cx, 3),
                "y": round(cy, 3),
            })
        return out

    def dcs(self, cx: float, cy: float, tag1: str = "", tag2: str = "") -> list[bd.Edge]:
        out = [
            line(cx - 7.5, cy - 7.5, cx + 7.5, cy - 7.5),
            line(cx + 7.5, cy - 7.5, cx + 7.5, cy + 7.5),
            line(cx + 7.5, cy + 7.5, cx - 7.5, cy + 7.5),
            line(cx - 7.5, cy + 7.5, cx - 7.5, cy - 7.5),
            circle(cx, cy, BUBBLE_R),
            line(cx - 7.5, cy, cx + 7.5, cy),
        ]
        if tag1:
            self.text(tag1, cx, cy + 2.2, size=2.0)
        if tag2:
            self.text(tag2, cx, cy - 2.2, size=2.0)
        full_tag = f"{tag1}-{tag2}".strip("-") if (tag1 or tag2) else ""
        if full_tag:
            self.schedule_instruments.append({
                "tag": full_tag,
                "tag1": tag1,
                "tag2": tag2,
                "type": "DCS SHARED DISPLAY",
                "x": round(cx, 3),
                "y": round(cy, 3),
            })
        return out

    def sis_box(self, cx: float, cy: float, tag1: str = "", tag2: str = "") -> list[bd.Edge]:
        out = [
            line(cx - 8.0, cy - 8.0, cx + 8.0, cy - 8.0),
            line(cx + 8.0, cy - 8.0, cx + 8.0, cy + 8.0),
            line(cx + 8.0, cy + 8.0, cx - 8.0, cy + 8.0),
            line(cx - 8.0, cy + 8.0, cx - 8.0, cy - 8.0),
            line(cx - 6.0, cy, cx, cy + 6.0),
            line(cx, cy + 6.0, cx + 6.0, cy),
            line(cx + 6.0, cy, cx, cy - 6.0),
            line(cx, cy - 6.0, cx - 6.0, cy),
        ]
        if tag1:
            self.text(tag1, cx, cy + 1.8, size=1.8)
        if tag2:
            self.text(tag2, cx, cy - 1.8, size=1.8)
        full_tag = f"{tag1}/{tag2}".strip("/") if (tag1 or tag2) else ""
        if full_tag:
            self.schedule_instruments.append({
                "tag": full_tag,
                "tag1": tag1,
                "tag2": tag2,
                "type": "SIS LOGIC SOLVER",
                "x": round(cx, 3),
                "y": round(cy, 3),
            })
        return out

    def interlock_diamond(
        self, cx: float, cy: float, tag: str = "ESD-1", r: float = 5.0
    ) -> list[bd.Edge]:
        out = [
            line(cx - r, cy, cx, cy + r),
            line(cx, cy + r, cx + r, cy),
            line(cx + r, cy, cx, cy - r),
            line(cx, cy - r, cx - r, cy),
        ]
        if tag:
            self.text(tag, cx, cy, size=1.8)
            self.schedule_instruments.append({
                "tag": tag,
                "type": "INTERLOCK LOGIC",
                "x": round(cx, 3),
                "y": round(cy, 3),
            })
        return out

    def level_bridle(
        self,
        x_pipe: float,
        y_shell_bot: float,
        y_tap_bot: float,
        y_tap_top: float,
        lg_tag: str,
        lt_bpcs: tuple[str, str],
        lt_sis: tuple[str, str],
    ) -> None:
        """Gambar closed-loop level bridle lengkap (standpipe + 2 isolation valve + drain valve + LG + 2 LT + SIS box)
        tanpa satu pun garis putus/menggantung (zero floating stubs).
        """
        x_lg_l = x_pipe + 12.0
        x_lg_r = x_pipe + 15.0
        x_lt = x_pipe + 26.0
        x_sis = x_pipe + 44.0

        self.equip += [
            line(x_pipe, y_shell_bot, x_pipe, y_tap_top),
            # Tap atas + isolation valve ke LG
            line(x_pipe, y_tap_top, x_pipe + 3.5, y_tap_top),
            self.valve_gate_h(x_pipe + 6.0, y_tap_top, w=5.0, h=3.2, flanged=False),
            line(x_pipe + 8.5, y_tap_top, x_lg_l, y_tap_top),
            # Tap bawah + isolation valve ke LG
            line(x_pipe, y_tap_bot, x_pipe + 3.5, y_tap_bot),
            self.valve_gate_h(x_pipe + 6.0, y_tap_bot, w=5.0, h=3.2, flanged=False),
            line(x_pipe + 8.5, y_tap_bot, x_lg_l, y_tap_bot),
            # Drain valve di bawah shell bejana
            line(x_pipe, y_shell_bot, x_pipe, y_shell_bot - 4.5),
            self.valve_gate_v(x_pipe, y_shell_bot - 7.0, w=3.2, h=5.0, flanged=False),
            line(x_pipe, y_shell_bot - 9.5, x_pipe, y_shell_bot - 14.0),
            line(x_pipe - 2.0, y_shell_bot - 14.0, x_pipe + 2.0, y_shell_bot - 14.0),
        ]
        self.sym += [
            line(x_lg_l, y_tap_bot, x_lg_l, y_tap_top),
            line(x_lg_r, y_tap_bot, x_lg_r, y_tap_top),
            line(x_lg_l, y_tap_bot, x_lg_r, y_tap_bot),
            line(x_lg_l, y_tap_top, x_lg_r, y_tap_top),
        ]
        self.text(lg_tag, (x_lg_l + x_lg_r) / 2.0, y_tap_top + 5.0, size=2.0)
        if lg_tag:
            self.schedule_instruments.append({
                "tag": lg_tag,
                "type": "LEVEL GAUGE (GLASS)",
                "x": round((x_lg_l + x_lg_r) / 2.0, 3),
                "y": round(y_tap_top + 5.0, 3),
            })

        y_lt_bpcs = y_tap_bot + 13.0
        y_lt_sis = y_tap_top - 11.0
        self.sym += self.bubble(x_lt, y_lt_bpcs, lt_bpcs[0], lt_bpcs[1])
        self.sig += dashed(x_lg_r, y_lt_bpcs, x_lt - BUBBLE_R, y_lt_bpcs, dash=2.0, gap=1.2)

        self.sym += self.bubble(x_lt, y_lt_sis, lt_sis[0], lt_sis[1])
        self.sig += dashed(x_lg_r, y_lt_sis, x_lt - BUBBLE_R, y_lt_sis, dash=2.0, gap=1.2)
        self.sym += self.sis_box(x_sis, y_lt_sis, "LAHH", "LALL")
        self.sig += dashed(x_lt + BUBBLE_R, y_lt_sis, x_sis - 8.0, y_lt_sis, dash=2.5, gap=1.2)
        self.text("TO ESD-1", x_sis, y_lt_sis + 11.0, size=1.8)

    def continuity_box_left(self, y: float, tag: str, desc: str, dwg: str) -> list[bd.Edge]:
        x0, x1 = 25.0, 68.0
        tip_x = x1 + 4.5
        hh = 5.0
        out = [
            line(x0, y - hh, x1, y - hh),
            line(x1, y - hh, tip_x, y),
            line(tip_x, y, x1, y + hh),
            line(x1, y + hh, x0, y + hh),
            line(x0, y + hh, x0, y - hh),
        ]
        mid_x = (x0 + x1) / 2.0
        self.text(dwg, mid_x, y, size=1.8)
        self.text(desc, mid_x, y + hh + 2.5, size=2.0)
        self.text(tag, mid_x, y - hh - 2.5, size=1.8)
        return out

    def continuity_box_right(self, y: float, tag: str, desc: str, dwg: str) -> list[bd.Edge]:
        x0, x1 = 585.0, 628.0
        tip_x = x1 + 5.0
        hh = 5.0
        out = [
            line(x0, y - hh, x1, y - hh),
            line(x1, y - hh, tip_x, y),
            line(tip_x, y, x1, y + hh),
            line(x1, y + hh, x0, y + hh),
            line(x0, y + hh, x0, y - hh),
        ]
        mid_x = (x0 + x1) / 2.0
        self.text(dwg, mid_x, y, size=1.8)
        self.text(desc, mid_x, y + hh + 2.5, size=2.0)
        self.text(tag, mid_x, y - hh - 2.5, size=1.8)
        return out

    # -------------------------------------------------------------------------
    # MACRO ASSEMBLIES PERPIPAAN & PFD SIMBOL (ISO 10628-2 & ASME B31.3)
    # -------------------------------------------------------------------------
    def spec_break_h(
        self,
        x: float,
        y: float,
        left_spec: str = "150# A1A",
        right_spec: str = "300# B1A",
    ) -> list[bd.Edge]:
        """Piping Class / Specification Break horizontal (ASME B31.3 / ISO 10628-2).

        Garis batas vertikal setinggi ±5.5 mm melintasi pipa, disertai bendera segitiga
        solid di kedua sisi dan anotasi spesifikasi kelas perpipaan di kiri dan kanan.
        """
        out = [line(x, y, x, y + 5.5), line(x, y, x, y - 5.5)]
        self.solid_triangle((x, y + 5.5), (x - 2.8, y + 5.5), (x, y + 2.8), layer="REF-PROC")
        self.solid_triangle((x, y - 5.5), (x + 2.8, y - 5.5), (x, y - 2.8), layer="REF-PROC")
        if left_spec:
            dx_text = len(left_spec) * 1.8 * 0.3 + 2.0
            self.text(left_spec, x - dx_text, y + 8.0, size=1.8, left=False)
        if right_spec:
            dx_text = len(right_spec) * 1.8 * 0.3 + 2.0
            self.text(right_spec, x + dx_text, y - 8.0, size=1.8, left=False)
        return out

    def spec_break_v(
        self,
        x: float,
        y: float,
        bot_spec: str = "150# A1A",
        top_spec: str = "300# B1A",
    ) -> list[bd.Edge]:
        """Piping Class / Specification Break vertikal (ASME B31.3 / ISO 10628-2)."""
        out = [line(x, y, x + 5.5, y), line(x, y, x - 5.5, y)]
        self.solid_triangle((x + 5.5, y), (x + 5.5, y + 2.8), (x + 2.8, y), layer="REF-PROC")
        self.solid_triangle((x - 5.5, y), (x - 5.5, y - 2.8), (x - 2.8, y), layer="REF-PROC")
        if top_spec:
            self.text(top_spec, x + 8.5, y + 4.5, size=1.8, left=True)
        if bot_spec:
            self.text(bot_spec, x + 8.5, y - 4.5, size=1.8, left=True)
        return out

    def control_valve_station_h(
        self,
        cx: float,
        cy: float,
        cv_tag: str = "PV-101",
        gv_up_tag: str = "GV-101A",
        gv_dn_tag: str = "GV-101B",
        bp_tag: str = "BV-101",
        fail: str = "FC",
        span: float = 56.0,
        bypass_dy: float = 18.0,
    ) -> tuple[float, float]:
        """Control Valve Bypass Station lengkap sesuai standar Process & Piping.

        Menggambar rakitan lengkap langsung pada self.proc:
          - Di jalur utama cy:
              * Upstream Block Gate Valve di cx - dx_v (dx_v >= 20 mm)
              * Control Valve (diafragma actuator) di cx
              * Downstream Block Gate Valve di cx + dx_v
              * Segmen pipa penghubung nyata di antara ketiga katup (jarak >= 20 mm antar katup)
          - Di jalur bypass cy + bypass_dy:
              * Riser vertikal di cx - hw_station dan cx + hw_station (default cx ± 28)
              * Bypass Valve (Normally Closed Solid) TANPA kubah aktuator
              * Teks "NC" di posisi bebas di sisi kanan katup bypass (bebas dari kubah aktuator CV)
              * Segmen pipa horizontal bypass utuh terhubung ke riser tanpa ujung menggantung
          - Menambahkan seluruh elemen ke self.proc dan mendaftarkan katup ke schedule_valves.

        Returns:
          tuple (cx, span / 2.0) yang dapat langsung dimasukkan ke argumen gaps pada pipe_run_h.
        """
        hw_station = span / 2.0  # Default 28.0 mm
        x_up_tee = cx - hw_station
        x_dn_tee = cx + hw_station

        # Jarak katup upstream/downstream dari center: >= 20 mm
        dx_v = 20.0 if span == 56.0 else max(20.0, hw_station - 8.0)
        flg_hw = 6.2  # w=10.0 flanged: half width 5.0 + 1.2

        # 1. Jalur Utama (cy)
        # Upstream Block Gate Valve di cx - dx_v
        self.proc += self.valve_gate_h(cx - dx_v, cy, w=10.0, h=6.0, flanged=True, tag=gv_up_tag)
        if gv_up_tag:
            self.text(gv_up_tag, cx - dx_v, cy - 7.0, size=1.8)

        # Control Valve di cx (kubah diafragma di atas sumbu cy)
        self.proc += self.control_valve_h(cx, cy, w=10.0, h=6.0, tag=cv_tag, fail=fail)
        if cv_tag:
            self.text(cv_tag, cx, cy - 7.0, size=2.2)
        if fail:
            self.text(fail, cx, cy - 11.5, size=1.8)

        # Downstream Block Gate Valve di cx + dx_v
        self.proc += self.valve_gate_h(cx + dx_v, cy, w=10.0, h=6.0, flanged=True, tag=gv_dn_tag)
        if gv_dn_tag:
            self.text(gv_dn_tag, cx + dx_v, cy - 7.0, size=1.8)

        # Pipa penghubung pada sumbu utama cy (segmen pipa antar katup nyata)
        self.proc += [
            line(x_up_tee, cy, cx - dx_v - flg_hw, cy),
            line(cx - dx_v + flg_hw, cy, cx - flg_hw, cy),
            line(cx + flg_hw, cy, cx + dx_v - flg_hw, cy),
            line(cx + dx_v + flg_hw, cy, x_dn_tee, cy),
        ]

        # 2. Jalur Bypass (cy + bypass_dy)
        y_bp = cy + bypass_dy
        # Riser vertikal kiri & kanan
        self.proc += [
            line(x_up_tee, cy, x_up_tee, y_bp),
            line(x_dn_tee, cy, x_dn_tee, y_bp),
        ]
        # Bypass Valve (Normally Closed Solid, TANPA kubah aktuator)
        self.proc += self.valve_globe_h(cx, y_bp, w=10.0, h=6.0, flanged=True, tag=bp_tag, nc=True)

        # Pipa horizontal bypass utuh terhubung ke riser
        self.proc += [
            line(x_up_tee, y_bp, cx - flg_hw, y_bp),
            line(cx + flg_hw, y_bp, x_dn_tee, y_bp),
        ]
        if bp_tag:
            self.text(bp_tag, cx, y_bp + 8.5, size=1.8)
        # Label NC di samping katup bypass pada posisi bebas (bebas dari kubah aktuator PV di bawah)
        self.text("NC", cx + 10.0, y_bp + 3.5, size=1.8)

        return (cx, hw_station)

        return (cx, hw_station)

    def stream_flag_h(
        self,
        x: float,
        y: float,
        stream_no: str = "1",
        p_barg: str = "10.0",
        t_degc: str = "40",
        flow_kgh: str = "12500",
    ) -> list[bd.Edge]:
        """Stream Diamond Flag & Mini Parameter Table untuk PFD (ISO 10628-2).

        Dilengkapi:
          - Belah ketupat penomoran aliran pada garis pipa (r = 4.0 mm)
          - Kotak parameter mini (Tekanan, Temperatur, Mass Flow Rate)
          - Label teks terformat rapi
        """
        r_dia = 4.0
        out = [
            line(x - r_dia, y, x, y + r_dia),
            line(x, y + r_dia, x + r_dia, y),
            line(x + r_dia, y, x, y - r_dia),
            line(x, y - r_dia, x - r_dia, y),
        ]
        self.text(str(stream_no), x, y, size=2.0)

        # Leader kecil dari puncak diamond ke dasar tabel mini
        y0 = y + r_dia + 3.0
        out.append(line(x, y + r_dia, x, y0))

        # Kotak parameter mini 3 baris
        box_w = 28.0
        row_h = 4.0
        box_h = row_h * 3.0
        x0 = x - box_w / 2.0
        x1 = x + box_w / 2.0
        y1 = y0 + box_h

        out += rect(x0, y0, x1, y1)
        out.append(line(x0, y0 + row_h, x1, y0 + row_h))
        out.append(line(x0, y0 + row_h * 2.0, x1, y0 + row_h * 2.0))

        # Format teks parameter
        p_str = p_barg if ("bar" in str(p_barg).lower()) else f"P: {p_barg} barg"
        t_str = t_degc if ("c" in str(t_degc).lower() or "°" in str(t_degc)) else f"T: {t_degc} \u00b0C"
        w_str = flow_kgh if ("kg" in str(flow_kgh).lower() or "t/h" in str(flow_kgh).lower()) else f"W: {flow_kgh} kg/h"

        self.text(p_str, x, y0 + row_h * 2.5, size=1.8)
        self.text(t_str, x, y0 + row_h * 1.5, size=1.8)
        self.text(w_str, x, y0 + row_h * 0.5, size=1.8)

        return out

    # -------------------------------------------------------------------------
    # REGISTRY PIPA & EXPORTER JADWAL (MTO, EQUIPMENT LIST, INSTRUMENT INDEX)
    # -------------------------------------------------------------------------
    def register_line(
        self,
        line_no: str,
        spec: str = "",
        service: str = "",
        dn: int = 0,
    ) -> None:
        """Catat nomor line pipa ke schedule_lines untuk pelacakan dan cross-check QA."""
        if line_no:
            self.schedule_lines.append({
                "line_no": line_no,
                "spec": spec,
                "service": service,
                "dn": dn,
            })

    def export_schedules(self, out_json_path: Path | str) -> dict:
        """Ekspor daftar peralatan, katup, dan instrumen ke format JSON terstruktur.

        Output terstruktur untuk draf deliverable:
          - Equipment List
          - Valve MTO / Schedule
          - Instrument Index
          - Line List
        """
        path = Path(out_json_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "equipment": self.schedule_equipment,
            "valves": self.schedule_valves,
            "instruments": self.schedule_instruments,
            "lines": self.schedule_lines,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return data

    def get_layers(self) -> dict[str, bd.Compound]:
        """Kembalikan hanya layer non-kosong sebagai dictionary compound.

        Mencegah error cadgen: 'layer contains no geometry'.
        """
        mapping = {
            "REF-FRAME": self.frame,
            "REF-TITLE": self.title,
            "REF-EQUIP": self.equip,
            "REF-PROC": self.proc,
            "REF-SYM": self.sym,
            "REF-SIG": self.sig,
            "REF-SIGP": self.sigp,
            "REF-HATCH": self.hatch,
        }
        return {name: comp(items) for name, items in mapping.items() if items}

    def export_manifest(self, json_path: Path | str) -> dict[str, bd.Compound]:
        path = Path(json_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        manifest = {
            "texts": self.texts,
            "dims": [],
            "solids": self.solids,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        return self.get_layers()
