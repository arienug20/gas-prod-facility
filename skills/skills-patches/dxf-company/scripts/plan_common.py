"""Reusable 2D Piping Plan & Plot Plan Standard Library.

Standard: ASME B31.3-2022, API STD 650 13th Ed. 2020, API RP 12J 8th Ed. 2014, API STD 521 7th Ed. 2020, ISO 5457:1999, ISO 7200:2004 & Company CAD Standard.
Coordinates:
  Plant Coordinate System (Easting, Northing) in METERS -> Sheet (X, Y) in MILLIMETERS.
  Default mapping for A1 sheet (841 x 594 mm) at scale 1:200:
    X_sheet = px0 + scale * Easting   (default px0 = 40.0 mm, scale = 5.0 mm/m)
    Y_sheet = py0 + scale * Northing  (default py0 = 40.0 mm, scale = 5.0 mm/m)
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from cadgen import build123d as bd

# =============================================================================
# GEOMETRY PRIMITIVES (PURE 2D EDGES - ZERO 3D / ZERO POLYFACE)
# =============================================================================
def line(x1: float, y1: float, x2: float, y2: float) -> bd.Edge:
    """Create a 2D line edge between (x1, y1) and (x2, y2)."""
    return bd.Edge.make_line(bd.Vector(x1, y1, 0), bd.Vector(x2, y2, 0))


def circle(x: float, y: float, r: float) -> bd.Edge:
    """Create a 2D circle edge centered at (x, y) with radius r."""
    return bd.Location((x, y, 0)) * bd.Edge.make_circle(r)


def arc(x: float, y: float, r: float, a1: float, a2: float) -> bd.Edge:
    """Create a 2D circular arc edge centered at (x, y) with radius r from a1 to a2 deg."""
    return bd.Location((x, y, 0)) * bd.Edge.make_circle(r, start_angle=a1, end_angle=a2)


def rect(x0: float, y0: float, x1: float, y1: float) -> List[bd.Edge]:
    """Create 4 edges forming an axis-aligned rectangle (x0, y0) to (x1, y1)."""
    return [
        line(x0, y0, x1, y0),
        line(x1, y0, x1, y1),
        line(x1, y1, x0, y1),
        line(x0, y1, x0, y0),
    ]


def dashed(
    x1: float, y1: float, x2: float, y2: float, dash: float = 4.0, gap: float = 1.6
) -> List[bd.Edge]:
    """Create dashed line segments between (x1, y1) and (x2, y2)."""
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length < 1e-6:
        return []
    ux, uy = dx / length, dy / length
    out: List[bd.Edge] = []
    t = 0.0
    while t < length - 1e-9:
        t2 = min(t + dash, length)
        if t2 - t > 1e-6:
            out.append(line(x1 + ux * t, y1 + uy * t, x1 + ux * t2, y1 + uy * t2))
        t = t2 + gap
    return out


def dashed_circle(
    x: float, y: float, r: float, dash: float = 6.0, gap: float = 2.0
) -> List[bd.Edge]:
    """Create dashed circular arc segments along circle (x, y, r)."""
    if r < 1e-6:
        return []
    step = math.degrees(dash / r)
    gapd = math.degrees(gap / r)
    out: List[bd.Edge] = []
    a = 0.0
    while a < 360.0:
        a_end = min(a + step, 359.999)
        if a_end > a:
            out.append(arc(x, y, r, a, a_end))
        a += step + gapd
    return out


def comp(items: List[Any]) -> bd.Compound:
    """Flatten nested lists of edges and compose into a single bd.Compound."""
    flat: List[bd.Edge] = []

    def _collect(obj: Any) -> None:
        if isinstance(obj, list):
            for child in obj:
                _collect(child)
        elif obj is not None:
            flat.append(obj)

    _collect(items)
    return bd.Compound.make_composite(flat)


# =============================================================================
# PIPING PLAN & PLOT PLAN CONTEXT (PlanContext)
# =============================================================================
class PlanContext:
    """Framework standar untuk Piping Plan & Plot Plan (A1 841 x 594 mm).

    Fitur utama:
      - Transformasi koordinat Plant (Easting, Northing) meter -> Sheet (X, Y) mm.
      - Auto-trimming pipa horizontal & vertikal dengan gap break standar (3.0 mm).
      - Simbol tampak atas: Elbow UP/DN, Tee UP/DN, Gate Valve, Pipe Support, Pipe Rack.
      - Kompas Utara 2D (North Arrow), Matchline, Coordinate Callout.
      - Manifest exporter untuk post-processor apply_text.py (MTEXT, DIMENSION, SOLID).
    """

    def __init__(self, px0: float = 40.0, py0: float = 40.0, scale: float = 5.0) -> None:
        """Inisialisasi context Piping Plan.

        Args:
            px0: Sheet X offset (mm) untuk Easting = 0.0 m.
            py0: Sheet Y offset (mm) untuk Northing = 0.0 m.
            scale: Rasio skala mm per meter plant (5.0 mm/m = 1:200).
        """
        self.px0 = float(px0)
        self.py0 = float(py0)
        self.scale = float(scale)

        # Koleksi layer standar drawing
        self.frame: List[bd.Edge] = []
        self.title: List[bd.Edge] = []
        self.grid: List[bd.Edge] = []
        self.fence: List[bd.Edge] = []
        self.road: List[bd.Edge] = []
        self.equip: List[bd.Edge] = []
        self.proc: List[bd.Edge] = []
        self.sym: List[bd.Edge] = []
        self.dim: List[bd.Edge] = []
        self.hatch: List[bd.Edge] = []

        # Manifest koleksi entitas pasca-build (MTEXT, SOLID, DIMENSION)
        self.texts: List[Dict[str, Any]] = []
        self.solids: List[Dict[str, Any]] = []
        self.dims: List[Dict[str, Any]] = []

    # -------------------------------------------------------------------------
    # TRANSFORMASI KOORDINAT
    # -------------------------------------------------------------------------
    def P(self, e: float, n: float) -> Tuple[float, float]:
        """Konversi koordinat Plant (Easting, Northing) meter -> Sheet (X, Y) mm."""
        return (self.px0 + self.scale * float(e), self.py0 + self.scale * float(n))

    def inv_P(self, x: float, y: float) -> Tuple[float, float]:
        """Konversi koordinat Sheet (X, Y) mm -> Plant (Easting, Northing) meter."""
        return ((float(x) - self.px0) / self.scale, (float(y) - self.py0) / self.scale)

    def m2mm(self, dist_m: float) -> float:
        """Konversi jarak plant (meter) ke jarak kertas (mm)."""
        return float(dist_m) * self.scale

    def mm2m(self, dist_mm: float) -> float:
        """Konversi jarak kertas (mm) ke jarak plant (meter)."""
        return float(dist_mm) / self.scale

    # -------------------------------------------------------------------------
    # MANIFEST ENTITIES (MTEXT, SOLID, DIMENSION)
    # -------------------------------------------------------------------------
    def text(
        self,
        t: str,
        x: float,
        y: float,
        size: float = 2.0,
        rot: float = 0.0,
        left: bool = False,
        layer: str = "REF-TEXT",
        att: Optional[int] = None,
    ) -> List[Any]:
        """Catat entitas MTEXT ke manifest (tidak menghasilkan geometri edge).

        Sesuai Company Standard §1:
          - Tinggi karakter dibatasi 0.5 <= size <= 3.0 mm.
          - att: 4 = Middle-Left (jika left=True), 5 = Middle-Center (default).
        """
        if not t:
            return []
        h = max(0.5, min(3.0, float(size)))
        if att is None:
            att = 4 if left else 5
        self.texts.append({
            "t": str(t),
            "x": round(float(x), 3),
            "y": round(float(y), 3),
            "h": round(h, 2),
            "rot": round(float(rot), 1),
            "layer": layer,
            "att": int(att),
        })
        return []

    def solid_triangle(
        self,
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        p3: Tuple[float, float],
        layer: str = "REF-PROC",
    ) -> None:
        """Catat entitas SOLID segitiga (3 titik) ke manifest."""
        self.solids.append({
            "pts": [
                [round(float(p1[0]), 3), round(float(p1[1]), 3)],
                [round(float(p2[0]), 3), round(float(p2[1]), 3)],
                [round(float(p3[0]), 3), round(float(p3[1]), 3)],
            ],
            "layer": layer,
        })

    def solid_quad(
        self,
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        p3: Tuple[float, float],
        p4: Tuple[float, float],
        layer: str = "REF-PROC",
    ) -> None:
        """Catat entitas SOLID segiempat (dipecah menjadi 2 segitiga bebas konflik)."""
        self.solid_triangle(p1, p2, p3, layer=layer)
        self.solid_triangle(p1, p3, p4, layer=layer)

    def solid_dot(
        self, cx: float, cy: float, r: float = 0.5, layer: str = "REF-PROC"
    ) -> None:
        """Lingkaran penuh SOLID via 8-segitiga fan (untuk simbol elbow/tee/weld)."""
        n = 8
        pts = [
            (
                cx + r * math.cos(2 * math.pi * i / n),
                cy + r * math.sin(2 * math.pi * i / n),
            )
            for i in range(n)
        ]
        for i in range(n):
            self.solid_triangle((cx, cy), pts[i], pts[(i + 1) % n], layer=layer)

    def dimrec(
        self,
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        txt: str,
        angle: float = 0.0,
        base: Optional[Tuple[float, float]] = None,
        oblique: Optional[float] = None,
    ) -> None:
        """Catat entitas DIMENSION ke manifest untuk post-processor apply_text.py."""
        d: Dict[str, Any] = {
            "p1": [round(float(p1[0]), 3), round(float(p1[1]), 3)],
            "p2": [round(float(p2[0]), 3), round(float(p2[1]), 3)],
            "angle": round(float(angle), 1),
            "text": str(txt),
        }
        if base is not None:
            d["base"] = [round(float(base[0]), 3), round(float(base[1]), 3)]
        if oblique is not None:
            d["oblique"] = round(float(oblique), 1)
        self.dims.append(d)

    # -------------------------------------------------------------------------
    # AUTO-TRIMMING RUTE PIPA PLAN (plan_pipe_h, plan_pipe_v)
    # -------------------------------------------------------------------------
    def plan_pipe_h(
        self,
        n: float,
        e0: float,
        e1: float,
        breaks_e: Optional[List[Union[float, Tuple[float, float]]]] = None,
        break_mm: float = 3.0,
        gaps: Optional[List[Tuple[float, float]]] = None,
        layer: str = "REF-PROC",
    ) -> List[bd.Edge]:
        """Menggambar pipa horizontal sepanjang Northing `n` dari `e0` ke `e1` (Plant meters).

        Secara otomatis membuat celah line break sebesar `break_mm` (default 3.0 mm di atas kertas
        = break_mm / scale meter pada plant) pada setiap titik potong `breaks_e`.

        Args:
            n: Northing pipa dalam meter plant.
            e0: Easting awal pipa dalam meter plant.
            e1: Easting akhir pipa dalam meter plant.
            breaks_e: Daftar titik Easting (meter) yang dipotong, atau tuple (center_e, half_w_m).
            break_mm: Lebar celah pemotongan pada ukuran kertas A1 (default 3.0 mm).
            gaps: Parameter alternatif untuk tuple (center_e, half_w_m).
            layer: Layer target (default "REF-PROC").

        Returns:
            Daftar segmen bd.Edge yang digambar.
        """
        e_min, e_max = min(e0, e1), max(e0, e1)
        half_gap_m = (float(break_mm) / 2.0) / self.scale

        raw_intervals: List[Tuple[float, float]] = []
        if breaks_e:
            for item in breaks_e:
                if isinstance(item, (int, float)):
                    raw_intervals.append((float(item) - half_gap_m, float(item) + half_gap_m))
                elif isinstance(item, (tuple, list)) and len(item) == 2:
                    c, hw = float(item[0]), float(item[1])
                    raw_intervals.append((c - hw, c + hw))

        if gaps:
            for item in gaps:
                if isinstance(item, (tuple, list)) and len(item) == 2:
                    c, hw = float(item[0]), float(item[1])
                    raw_intervals.append((c - hw, c + hw))

        # Clamp interval ke rentang pipa
        clamped: List[Tuple[float, float]] = []
        for a, b in raw_intervals:
            ia = max(e_min, min(a, b))
            ib = min(e_max, max(a, b))
            if ib > ia + 1e-6:
                clamped.append((ia, ib))
        clamped.sort()

        # Gabungkan interval yang saling beririsan
        merged: List[List[float]] = []
        for ia, ib in clamped:
            if not merged:
                merged.append([ia, ib])
            else:
                if ia <= merged[-1][1] + 1e-6:
                    merged[-1][1] = max(merged[-1][1], ib)
                else:
                    merged.append([ia, ib])

        # Buat segmen garis yang tidak terpotong
        edges: List[bd.Edge] = []
        curr = e_min
        for ia, ib in merged:
            if ia - curr > 1e-4:
                x1, y1 = self.P(curr, n)
                x2, y2 = self.P(ia, n)
                edges.append(line(x1, y1, x2, y2))
            curr = max(curr, ib)

        if e_max - curr > 1e-4:
            x1, y1 = self.P(curr, n)
            x2, y2 = self.P(e_max, n)
            edges.append(line(x1, y1, x2, y2))

        # Tambahkan ke layer yang sesuai
        if layer == "REF-PROC":
            self.proc.extend(edges)
        elif layer == "REF-EQUIP":
            self.equip.extend(edges)
        elif layer == "REF-SYM":
            self.sym.extend(edges)
        else:
            self.proc.extend(edges)

        return edges

    def plan_pipe_v(
        self,
        e: float,
        n0: float,
        n1: float,
        breaks_n: Optional[List[Union[float, Tuple[float, float]]]] = None,
        break_mm: float = 3.0,
        gaps: Optional[List[Tuple[float, float]]] = None,
        layer: str = "REF-PROC",
    ) -> List[bd.Edge]:
        """Menggambar pipa vertikal sepanjang Easting `e` dari `n0` ke `n1` (Plant meters).

        Secara otomatis membuat celah line break sebesar `break_mm` pada setiap titik potong `breaks_n`.
        """
        n_min, n_max = min(n0, n1), max(n0, n1)
        half_gap_m = (float(break_mm) / 2.0) / self.scale

        raw_intervals: List[Tuple[float, float]] = []
        if breaks_n:
            for item in breaks_n:
                if isinstance(item, (int, float)):
                    raw_intervals.append((float(item) - half_gap_m, float(item) + half_gap_m))
                elif isinstance(item, (tuple, list)) and len(item) == 2:
                    c, hh = float(item[0]), float(item[1])
                    raw_intervals.append((c - hh, c + hh))

        if gaps:
            for item in gaps:
                if isinstance(item, (tuple, list)) and len(item) == 2:
                    c, hh = float(item[0]), float(item[1])
                    raw_intervals.append((c - hh, c + hh))

        clamped: List[Tuple[float, float]] = []
        for a, b in raw_intervals:
            ia = max(n_min, min(a, b))
            ib = min(n_max, max(a, b))
            if ib > ia + 1e-6:
                clamped.append((ia, ib))
        clamped.sort()

        merged: List[List[float]] = []
        for ia, ib in clamped:
            if not merged:
                merged.append([ia, ib])
            else:
                if ia <= merged[-1][1] + 1e-6:
                    merged[-1][1] = max(merged[-1][1], ib)
                else:
                    merged.append([ia, ib])

        edges: List[bd.Edge] = []
        curr = n_min
        for ia, ib in merged:
            if ia - curr > 1e-4:
                x1, y1 = self.P(e, curr)
                x2, y2 = self.P(e, ia)
                edges.append(line(x1, y1, x2, y2))
            curr = max(curr, ib)

        if n_max - curr > 1e-4:
            x1, y1 = self.P(e, curr)
            x2, y2 = self.P(e, n_max)
            edges.append(line(x1, y1, x2, y2))

        if layer == "REF-PROC":
            self.proc.extend(edges)
        elif layer == "REF-EQUIP":
            self.equip.extend(edges)
        elif layer == "REF-SYM":
            self.sym.extend(edges)
        else:
            self.proc.extend(edges)

        return edges

    # -------------------------------------------------------------------------
    # SIMBOL TAMPAK ATAS PERPIPAAN (PIPING PLAN SYMBOLS)
    # -------------------------------------------------------------------------
    def flow_arrow_plan(
        self,
        e: float,
        n: float,
        ang_deg: float,
        size_mm: float = 3.2,
        layer: str = "REF-PROC",
    ) -> List[bd.Edge]:
        """Kepala panah aliran SOLID pada koordinat Plant (e, n).

        Args:
            e: Easting dalam meter plant.
            n: Northing dalam meter plant.
            ang_deg: Sudut arah aliran dalam derajat (0 = East, 90 = North, 180 = West, 270 = South).
            size_mm: Ukuran dasar panah dalam mm (panjang = 1.5 * size_mm).
            layer: Layer target (default "REF-PROC").
        """
        cx, cy = self.P(e, n)
        rad = math.radians(ang_deg)
        ux, uy = math.cos(rad), math.sin(rad)
        nx, ny = -uy, ux

        length = size_mm * 1.5
        half_w = size_mm * 0.55

        p_tip = (cx, cy)
        p_left = (cx - length * ux + half_w * nx, cy - length * uy + half_w * ny)
        p_right = (cx - length * ux - half_w * nx, cy - length * uy - half_w * ny)

        # Rekam SOLID terisi penuh ke manifest
        self.solid_triangle(p_tip, p_left, p_right, layer=layer)

        # Garis outline panah
        edges = [
            line(*p_tip, *p_left),
            line(*p_tip, *p_right),
            line(*p_left, *p_right),
        ]
        if layer == "REF-PROC":
            self.proc.extend(edges)
        elif layer == "REF-SYM":
            self.sym.extend(edges)
        elif layer == "REF-EQUIP":
            self.equip.extend(edges)
        else:
            self.proc.extend(edges)
        return edges

    def elbow_up(
        self, e: float, n: float, r_mm: float = 1.8, layer: str = "REF-PROC"
    ) -> List[bd.Edge]:
        """Simbol 90° Elbow Turning UP tampak atas (lingkaran r_mm + titik tengah SOLID r=0.5 mm)."""
        cx, cy = self.P(e, n)
        c = circle(cx, cy, r_mm)
        self.solid_dot(cx, cy, r=0.5, layer=layer)
        self.proc.append(c)
        return [c]

    # Alias sesuai blueprint Bab 4
    elbow_90_up = elbow_up

    def elbow_dn(
        self,
        e: float,
        n: float,
        r_mm: float = 1.8,
        orient_deg: float = 0.0,
        layer: str = "REF-PROC",
    ) -> List[bd.Edge]:
        """Simbol 90° Elbow Turning DOWN tampak atas (busur arc 240° + titik tengah SOLID).

        Opening celah 120° menghadap arah orient_deg (arah masuknya pipa horizontal).
        """
        cx, cy = self.P(e, n)
        a1 = (orient_deg + 60.0) % 360.0
        a2 = (orient_deg + 300.0) % 360.0
        a = arc(cx, cy, r_mm, a1, a2)
        self.solid_dot(cx, cy, r=0.5, layer=layer)
        self.proc.append(a)
        return [a]

    # Alias sesuai blueprint Bab 4
    elbow_90_dn = elbow_dn

    def tee_up(
        self, e: float, n: float, r_mm: float = 1.8, layer: str = "REF-PROC"
    ) -> List[bd.Edge]:
        """Simbol Tee dengan cabang vertikal belok UP (+Z)."""
        cx, cy = self.P(e, n)
        c = circle(cx, cy, r_mm)
        self.solid_dot(cx, cy, r=0.5, layer=layer)
        self.proc.append(c)
        return [c]

    def tee_dn(
        self,
        e: float,
        n: float,
        r_mm: float = 1.8,
        orient_deg: float = 0.0,
        layer: str = "REF-PROC",
    ) -> List[bd.Edge]:
        """Simbol Tee dengan cabang vertikal belok DOWN (-Z)."""
        cx, cy = self.P(e, n)
        a1 = (orient_deg + 60.0) % 360.0
        a2 = (orient_deg + 300.0) % 360.0
        a = arc(cx, cy, r_mm, a1, a2)
        self.solid_dot(cx, cy, r=0.5, layer=layer)
        self.proc.append(a)
        return [a]

    def plan_valve_gate(
        self,
        e: float,
        n: float,
        orient: Union[str, float] = "H",
        w_mm: float = 7.0,
        h_mm: float = 4.2,
        tag: str = "",
        tag_offset: Optional[Tuple[float, float]] = None,
        layer: str = "REF-SYM",
    ) -> List[bd.Edge]:
        """Simbol Gate Valve tampak atas dengan bowtie + tick flange + label tag."""
        cx, cy = self.P(e, n)
        if isinstance(orient, str):
            orient_clean = orient.strip().upper()
            ang = 0.0 if orient_clean == "H" else (90.0 if orient_clean == "V" else float(orient_clean))
        else:
            ang = float(orient)

        rad = math.radians(ang)
        cos_a, sin_a = math.cos(rad), math.sin(rad)

        def rot_pt(lx: float, ly: float) -> Tuple[float, float]:
            return (cx + lx * cos_a - ly * sin_a, cy + lx * sin_a + ly * cos_a)

        hw = w_mm / 2.0
        hh = h_mm / 2.0

        pt_lt = rot_pt(-hw, hh)
        pt_lb = rot_pt(-hw, -hh)
        pt_rt = rot_pt(hw, hh)
        pt_rb = rot_pt(hw, -hh)

        edges = [
            line(*pt_lt, *pt_lb),
            line(*pt_rt, *pt_rb),
            line(*pt_lt, *pt_rb),
            line(*pt_lb, *pt_rt),
        ]

        # Tick flange di kedua ujung
        hf = hh * 1.15
        edges.append(line(*rot_pt(-hw, -hf), *rot_pt(-hw, hf)))
        edges.append(line(*rot_pt(hw, -hf), *rot_pt(hw, hf)))

        if tag:
            if tag_offset is not None:
                tx = cx + float(tag_offset[0])
                ty = cy + float(tag_offset[1])
                self.text(tag, tx, ty, size=2.0, layer="REF-TEXT", att=5)
            else:
                # Tempatkan label tag di sisi katup dengan jarak bebas aman (menghindari tabrakan dengan flange tick)
                clearance = max(hh + 2.5, hf + 2.0)
                tx, ty = rot_pt(0.0, clearance)
                if abs(sin_a) > 0.5:
                    # Orientasi V: tempatkan teks horizontal di kiri katup dengan attachment Middle-Right
                    self.text(tag, cx - (hf + 2.0), cy, size=2.0, layer="REF-TEXT", att=6)
                else:
                    self.text(tag, tx, ty, size=2.0, layer="REF-TEXT", att=5)

        self.sym.extend(edges)
        return edges

    def pipe_support_plan(
        self,
        e: float,
        n: float,
        orient: Union[str, float] = "H",
        tag: str = "PS-01",
        stype: str = "ANCHOR",
        dx_mm: float = 8.0,
        dy_mm: float = 8.0,
        shelf_len: float = 14.0,
        layer: str = "REF-SYM",
    ) -> List[bd.Edge]:
        """Simbol Pipe Support / Anchor / Guide tampak atas beserta garis leader & callout."""
        cx, cy = self.P(e, n)
        if isinstance(orient, str):
            orient_clean = orient.strip().upper()
            ang = 0.0 if orient_clean == "H" else (90.0 if orient_clean == "V" else float(orient_clean))
        else:
            ang = float(orient)

        rad = math.radians(ang)
        cos_a, sin_a = math.cos(rad), math.sin(rad)

        def rot_pt(lx: float, ly: float) -> Tuple[float, float]:
            return (cx + lx * cos_a - ly * sin_a, cy + lx * sin_a + ly * cos_a)

        w_box, h_box = 4.2, 2.6
        hw, hh = w_box / 2.0, h_box / 2.0

        p1 = rot_pt(-hw, -hh)
        p2 = rot_pt(hw, -hh)
        p3 = rot_pt(hw, hh)
        p4 = rot_pt(-hw, hh)

        edges = [
            line(*p1, *p2),
            line(*p2, *p3),
            line(*p3, *p4),
            line(*p4, *p1),
        ]

        stype_upper = stype.strip().upper()
        if "ANCHOR" in stype_upper:
            # Diagonal cross X di dalam kotak shoe
            edges.append(line(*p1, *p3))
            edges.append(line(*p2, *p4))
        elif "GUIDE" in stype_upper:
            # Plat pemandu di kedua sisi
            edges.append(line(*rot_pt(-hw - 0.6, -hh), *rot_pt(-hw - 0.6, hh)))
            edges.append(line(*rot_pt(hw + 0.6, -hh), *rot_pt(hw + 0.6, hh)))

        # Garis penunjuk (leader) ke rak teks horizontal
        p_start = rot_pt(0.0, hh)
        p_elbow = (p_start[0] + dx_mm, p_start[1] + dy_mm)
        s_dir = 1.0 if dx_mm >= 0 else -1.0
        p_shelf = (p_elbow[0] + s_dir * shelf_len, p_elbow[1])

        edges.append(line(*p_start, *p_elbow))
        edges.append(line(*p_elbow, *p_shelf))

        # Teks callout dua baris
        mid_x = (p_elbow[0] + p_shelf[0]) / 2.0
        self.text(tag, mid_x, p_elbow[1] + 1.8, size=1.8, att=5)
        self.text(stype_upper, mid_x, p_elbow[1] - 1.8, size=1.6, att=5)

        self.sym.extend(edges)
        return edges

    def pipe_rack(
        self,
        e0: float,
        e1: float,
        n0: float,
        n1: float,
        bay_m: float = 6.0,
        layer: str = "REF-EQUIP",
    ) -> List[bd.Edge]:
        """Menggambar 2 rel pipe rack beserta ikatan angin diagonal (alternating plan bracing).

        Mendukung rack yang membujur Timur-Barat maupun Utara-Selatan.
        """
        e_min, e_max = min(e0, e1), max(e0, e1)
        n_min, n_max = min(n0, n1), max(n0, n1)

        edges: List[bd.Edge] = []
        if (e_max - e_min) >= (n_max - n_min):
            # Rack membujur East-West
            edges.append(line(*self.P(e_min, n_min), *self.P(e_max, n_min)))
            edges.append(line(*self.P(e_min, n_max), *self.P(e_max, n_max)))

            # Tentukan posisi bent
            bays: List[float] = []
            curr = e_min
            while curr <= e_max + 1e-4:
                bays.append(curr)
                curr += bay_m
            if bays[-1] < e_max - 0.5:
                bays.append(e_max)

            # Bent melintang
            for eb in bays:
                edges.append(line(*self.P(eb, n_min), *self.P(eb, n_max)))

            # Ikatan angin selang-seling (alternating bracing)
            for k in range(len(bays) - 1):
                if k % 2 == 0:
                    edges.append(line(*self.P(bays[k], n_min), *self.P(bays[k + 1], n_max)))
                else:
                    edges.append(line(*self.P(bays[k], n_max), *self.P(bays[k + 1], n_min)))
        else:
            # Rack membujur North-South
            edges.append(line(*self.P(e_min, n_min), *self.P(e_min, n_max)))
            edges.append(line(*self.P(e_max, n_min), *self.P(e_max, n_max)))

            bays = []
            curr = n_min
            while curr <= n_max + 1e-4:
                bays.append(curr)
                curr += bay_m
            if bays[-1] < n_max - 0.5:
                bays.append(n_max)

            for nb in bays:
                edges.append(line(*self.P(e_min, nb), *self.P(e_max, nb)))

            for k in range(len(bays) - 1):
                if k % 2 == 0:
                    edges.append(line(*self.P(e_min, bays[k]), *self.P(e_max, bays[k + 1])))
                else:
                    edges.append(line(*self.P(e_max, bays[k]), *self.P(e_min, bays[k + 1])))

        self.equip.extend(edges)
        return edges

    # Alias sesuai blueprint Bab 4
    pipe_rack_bay = pipe_rack

    def north_arrow_plan(
        self,
        x_mm: float,
        y_mm: float,
        r_mm: float = 10.0,
        layer: str = "REF-SYM",
    ) -> List[bd.Edge]:
        """Kompas Utara 2D standar Plot Plan.

        Menampilkan lingkaran + jarum panah menunjuk ke atas +N dengan separuh bilah terisi SOLID
        serta huruf 'N' di puncak kompas.
        """
        edges: List[bd.Edge] = [circle(x_mm, y_mm, r_mm)]

        tip_y = y_mm + r_mm * 0.95
        tail_y = y_mm - r_mm * 0.95
        w_half = r_mm * 0.28

        p_tip = (x_mm, tip_y)
        p_tail = (x_mm, tail_y)
        p_left = (x_mm - w_half, y_mm)
        p_right = (x_mm + w_half, y_mm)
        p_mid = (x_mm, y_mm)

        # Bilah kanan atas & kiri bawah terisi SOLID (gaya kompas navigasi formal)
        self.solid_triangle(p_tip, p_mid, p_right, layer=layer)
        self.solid_triangle(p_tail, p_mid, p_left, layer=layer)

        # Garis perimeter jarum
        edges.extend([
            line(*p_tip, *p_left),
            line(*p_left, *p_tail),
            line(*p_tail, *p_right),
            line(*p_right, *p_tip),
            line(*p_tip, *p_tail),
            line(*p_left, *p_right),
        ])

        # Huruf 'N' di atas puncak
        self.text("N", x_mm, tip_y + 3.0, size=2.5, layer="REF-TEXT", att=5)

        self.sym.extend(edges)
        return edges

    def coord_callout(
        self,
        e: float,
        n: float,
        el_mm: Optional[int] = None,
        dx_mm: float = 10.0,
        dy_mm: float = 10.0,
        shelf_len: float = 28.0,
        layer: str = "REF-SYM",
    ) -> List[bd.Edge]:
        """Garis penunjuk (leader) dari titik Plant (e, n) ke rak horizontal + teks koordinat.

        Menampilkan N xxxx / E xxxx (dan EL. +xxxx bila el_mm tidak None).
        """
        px, py = self.P(e, n)
        lx, ly = px + dx_mm, py + dy_mm
        s_dir = 1.0 if dx_mm >= 0 else -1.0
        sx = lx + s_dir * shelf_len

        # Titik pusat penanda target
        self.solid_dot(px, py, r=0.45, layer=layer)

        edges = [
            line(px, py, lx, ly),
            line(lx, ly, sx, ly),
        ]

        mid_x = (lx + sx) / 2.0
        n_str = f"N {n * 1000:,.0f}"
        e_str = f"E {e * 1000:,.0f}"

        if el_mm is not None:
            self.text(f"{n_str}  {e_str}", mid_x, ly + 2.0, size=1.8, att=5)
            el_sign = "+" if el_mm >= 0 else ""
            self.text(f"EL. {el_sign}{el_mm}", mid_x, ly - 2.0, size=1.8, att=5)
        else:
            self.text(n_str, mid_x, ly + 2.0, size=1.8, att=5)
            self.text(e_str, mid_x, ly - 2.0, size=1.8, att=5)

        self.sym.extend(edges)
        return edges

    def matchline(
        self,
        e0: float,
        n0: float,
        e1: float,
        n1: float,
        text_str: str = "MATCHLINE — SEE DWG ...",
        label: Optional[str] = None,
        dash: float = 6.0,
        gap: float = 2.5,
        layer: str = "REF-SYM",
    ) -> List[bd.Edge]:
        """Garis batas area putus-putus tebal (matchline) beserta label referensi gambar."""
        if label is not None:
            text_str = label

        x1, y1 = self.P(e0, n0)
        x2, y2 = self.P(e1, n1)

        edges = dashed(x1, y1, x2, y2, dash=dash, gap=gap)
        self.sym.extend(edges)

        # Hitung sudut & posisi teks di tengah garis
        mx, my = (x1 + x2) / 2.0, (y1 + y2) / 2.0
        dx, dy = x2 - x1, y2 - y1
        ang = math.degrees(math.atan2(dy, dx))
        if ang > 90.0:
            ang -= 180.0
        elif ang < -90.0:
            ang += 180.0

        rad = math.radians(ang + 90.0)
        tx = mx + 3.0 * math.cos(rad)
        ty = my + 3.0 * math.sin(rad)

        self.text(text_str, tx, ty, size=2.2, rot=ang, layer="REF-TEXT", att=5)
        return edges

    def battery_limit_arrow(
        self,
        e: float,
        n: float,
        direction: int = 1,
        size_mm: float = 3.5,
        tag: str = "",
        layer: str = "REF-SYM",
    ) -> List[bd.Edge]:
        """Simbol panah Battery Limit di koordinat (e, n). direction: 1 = +X, -1 = -X."""
        x, y = self.P(e, n)
        d = 1.0 if direction >= 0 else -1.0
        edges = [
            line(x, y - size_mm, x, y + size_mm),
            line(x, y - size_mm, x + 8.0 * d, y),
            line(x + 8.0 * d, y, x, y + size_mm),
        ]
        if tag:
            self.text(tag, x + 4.0 * d, y + size_mm + 2.0, size=2.0, att=5)
        self.sym.extend(edges)
        return edges

    # -------------------------------------------------------------------------
    # PERALATAN TAMPAK ATAS (EQUIPMENT PRIMITIVES)
    # -------------------------------------------------------------------------
    def equipment_box(
        self,
        e0: float,
        n0: float,
        e1: float,
        n1: float,
        tag: str = "",
        desc: str = "",
        layer: str = "REF-EQUIP",
    ) -> List[bd.Edge]:
        """Kotak peralatan tampak atas persegi panjang dalam koordinat plant."""
        x0, y0 = self.P(e0, n0)
        x1, y1 = self.P(e1, n1)
        edges = rect(x0, y0, x1, y1)
        self.equip.extend(edges)

        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        if tag and desc:
            self.text(tag, cx, cy + 2.0, size=2.5, att=5)
            self.text(desc, cx, cy - 2.0, size=2.0, att=5)
        elif tag:
            self.text(tag, cx, cy, size=2.5, att=5)

        return edges

    def horizontal_vessel(
        self,
        e_center: float,
        n_center: float,
        length_m: float,
        diameter_m: float,
        tag: str = "",
        desc: str = "",
        layer: str = "REF-EQUIP",
    ) -> List[bd.Edge]:
        """Bejana horizontal tampak atas (silinder + 2 ellipsoidal heads) dalam koordinat plant."""
        hl_m = length_m / 2.0
        r_m = diameter_m / 2.0

        e_left = e_center - hl_m
        e_right = e_center + hl_m
        n_bot = n_center - r_m
        n_top = n_center + r_m

        edges: List[bd.Edge] = []
        # Shell persegi
        x0, y0 = self.P(e_left, n_bot)
        x1, y1 = self.P(e_right, n_top)
        edges.append(line(x0, y0, x1, y0))
        edges.append(line(x0, y1, x1, y1))

        # Heads cembung
        hx1, hy = self.P(e_left, n_center)
        hx2, _ = self.P(e_right, n_center)
        head_r = self.m2mm(r_m)
        edges.append(arc(hx1, hy, head_r, 90, 270))
        edges.append(arc(hx2, hy, head_r, 270, 450))

        self.equip.extend(edges)

        cx, cy = self.P(e_center, n_center)
        if tag and desc:
            self.text(tag, cx, cy + 2.0, size=2.5, att=5)
            self.text(desc, cx, cy - 2.0, size=2.0, att=5)
        elif tag:
            self.text(tag, cx, cy, size=2.5, att=5)

        return edges

    def vertical_vessel(
        self,
        e_center: float,
        n_center: float,
        diameter_m: float,
        tag: str = "",
        desc: str = "",
        layer: str = "REF-EQUIP",
    ) -> List[bd.Edge]:
        """Bejana vertikal / kolom tampak atas (lingkaran) dalam koordinat plant."""
        cx, cy = self.P(e_center, n_center)
        r = self.m2mm(diameter_m / 2.0)
        c = circle(cx, cy, r)
        self.equip.append(c)

        if tag and desc:
            if r >= 8.0:
                self.text(tag, cx, cy + 2.0, size=2.5, att=5)
                self.text(desc, cx, cy - 2.0, size=2.0, att=5)
            else:
                self.text(tag, cx, cy, size=2.2, att=5)
                self.text(desc, cx, cy - (r + 2.5), size=2.0, att=5)
        elif tag:
            self.text(tag, cx, cy, size=2.5, att=5)

        return [c]

    def storage_tank(
        self,
        e_center: float,
        n_center: float,
        diameter_m: float,
        bund_w_m: Optional[float] = None,
        bund_l_m: Optional[float] = None,
        tag: str = "",
        desc: str = "",
        layer: str = "REF-EQUIP",
    ) -> List[bd.Edge]:
        """Tangki timbun atmosferik API STD 650 13th Ed. 2020 tampak atas + tanggul penampung (bund wall)."""
        edges: List[bd.Edge] = []
        tcx, tcy = self.P(e_center, n_center)
        tank_r = self.m2mm(diameter_m / 2.0)
        edges.append(circle(tcx, tcy, tank_r))

        if bund_w_m and bund_l_m:
            bw2 = bund_w_m / 2.0
            bl2 = bund_l_m / 2.0
            bx0, by0 = self.P(e_center - bw2, n_center - bl2)
            bx1, by1 = self.P(e_center + bw2, n_center + bl2)
            edges.extend(rect(bx0, by0, bx1, by1))
            # Garis dinding dalam ganda bund wall (jarak 0.3 m)
            ix0, iy0 = self.P(e_center - bw2 + 0.3, n_center - bl2 + 0.3)
            ix1, iy1 = self.P(e_center + bw2 - 0.3, n_center + bl2 - 0.3)
            edges.extend(rect(ix0, iy0, ix1, iy1))

            # Arsiran dinding tanggul bundwall sudut 45 derajat (REF-HATCH)
            hatch_edges: List[bd.Edge] = []
            x = bx0 + 2.0
            wall_t = self.m2mm(0.3)
            while x < bx1 - 1.5:
                hatch_edges.append(line(x, by0, min(x + wall_t, bx1), by0 + wall_t))
                hatch_edges.append(line(x, by1, min(x + wall_t, bx1), by1 - wall_t))
                x += 4.0
            y = by0 + 2.0
            while y < by1 - 1.5:
                hatch_edges.append(line(bx0, y, bx0 + wall_t, min(y + wall_t, by1)))
                hatch_edges.append(line(bx1, y, bx1 - wall_t, min(y + wall_t, by1)))
                y += 4.0
            self.hatch.extend(hatch_edges)

        self.equip.extend(edges)

        if tag and desc:
            self.text(tag, tcx, tcy + 2.0, size=2.5, att=5)
            self.text(desc, tcx, tcy - 2.0, size=2.0, att=5)
        elif tag:
            self.text(tag, tcx, tcy, size=2.5, att=5)

        return edges

    # -------------------------------------------------------------------------
    # FURNITURE LEMBAR A1 (FRAME, TITLE BLOCK, GRID, ROAD, FENCE)
    # -------------------------------------------------------------------------
    def setup_a1_frame(
        self,
        doc_no: str,
        title: str,
        rev: str = "A0",
        scale_str: str = "1:200 @ A1",
        date_str: str = "23 OCT 2026",
    ) -> List[bd.Edge]:
        """Border lembar A1 (841 x 594 mm) + referensi grid zona A-F, 1-8 + Title Block ISO 7200."""
        sw, sh = 841.0, 594.0
        bx1, by1, bx2, by2 = 20.0, 10.0, 831.0, 584.0

        edges: List[bd.Edge] = rect(0.0, 0.0, sw, sh) + rect(bx1, by1, bx2, by2)

        # Referensi zona tepi 1-8 dan A-F
        for i in range(8):
            cx = bx1 + (bx2 - bx1) / 8.0 * (i + 0.5)
            t = str(i + 1)
            self.text(t, cx, 589.0, 2.5, att=5, layer="REF-FRAME")
            self.text(t, cx, 5.0, 2.5, att=5, layer="REF-FRAME")

        for j in range(6):
            cy = by1 + (by2 - by1) / 6.0 * (j + 0.5)
            t = chr(65 + j)
            self.text(t, 15.0, cy, 2.5, att=5, layer="REF-FRAME")
            self.text(t, 836.0, cy, 2.5, att=5, layer="REF-FRAME")

        self.frame.extend(edges)

        # Title Block ISO 7200 di pojok kanan bawah
        tb_edges: List[bd.Edge] = rect(651.0, 15.0, 827.0, 105.0)
        tb_edges.extend([
            line(651.0, 105.0, 651.0, 125.0),
            line(651.0, 120.0, 827.0, 120.0),
            line(651.0, 125.0, 827.0, 125.0),
            line(827.0, 105.0, 827.0, 125.0),
            line(700.0, 120.0, 700.0, 125.0),
            line(770.0, 120.0, 770.0, 125.0),
        ])
        for y in (88.0, 71.0, 57.25, 43.5, 29.75):
            tb_edges.append(line(651.0, y, 827.0, y))

        self.text("GAS PRODUCTION FACILITY — ONSHORE FIELD", 739.0, 96.5, 3.0, att=5, layer="REF-TITLE")
        self.text(title, 739.0, 79.5, 3.0, att=5, layer="REF-TITLE")

        fields = [
            (64.1, f"DOC NO: {doc_no}"),
            (50.4, f"REV: {rev} (ISSUED FOR REVIEW)    SCALE: {scale_str}"),
            (36.6, f"DATE: {date_str}    UNITS: mm    SHEET: 1 OF 1"),
            (22.4, "DRAWN: GLM-5.3-FLASH    CHECKED: PM (AI)    APPROVED: —"),
        ]
        for y, s in fields:
            self.text(s, 655.0, y, 2.5, left=True, layer="REF-TITLE")

        # Header tabel revisi
        self.text("REV", 675.5, 117.3, 2.0, att=5, layer="REF-TITLE")
        self.text("DESCRIPTION", 735.0, 117.3, 2.0, att=5, layer="REF-TITLE")
        self.text("DATE", 798.5, 117.3, 2.0, att=5, layer="REF-TITLE")

        self.title.extend(tb_edges)
        return edges + tb_edges

    def setup_plant_grid(
        self,
        e_max: float = 100.0,
        n_max: float = 60.0,
        step_m: float = 10.0,
    ) -> List[bd.Edge]:
        """Garis penanda grid plant (ticks) dan label kolom A..K & baris 1..6."""
        edges: List[bd.Edge] = []
        n_cols = int(e_max / step_m) + 1
        for i in range(n_cols):
            x, _ = self.P(step_m * i, 0.0)
            _, y2 = self.P(0.0, -0.6)
            edges.append(line(x, self.py0, x, y2))
            self.text(chr(65 + i), x, self.py0 - 6.0, 2.5, att=5, layer="REF-GRID")

        n_rows = int(n_max / step_m)
        for j in range(n_rows):
            x1, y = self.P(-0.6, step_m * (j + 1))
            edges.append(line(x1, y, self.px0, y))
            self.text(str(j + 1), self.px0 - 6.0, y, 2.5, att=5, layer="REF-GRID")

        self.grid.extend(edges)
        return edges

    def setup_plot_fence(
        self,
        e0: float = 0.0,
        n0: float = 0.0,
        e1: float = 100.0,
        n1: float = 60.0,
        dash: float = 6.0,
        gap: float = 2.0,
    ) -> List[bd.Edge]:
        """Pagar keliling plot plant (dashed line)."""
        x0, y0 = self.P(e0, n0)
        x1, y1 = self.P(e1, n1)

        edges: List[bd.Edge] = []
        edges.extend(dashed(x0, y0, x1, y0, dash, gap))
        edges.extend(dashed(x1, y0, x1, y1, dash, gap))
        edges.extend(dashed(x1, y1, x0, y1, dash, gap))
        edges.extend(dashed(x0, y1, x0, y0, dash, gap))

        self.fence.extend(edges)
        return edges

    def setup_road(
        self,
        e0: float,
        e1: float,
        n_bot: float,
        n_top: float,
        tag: str = "ACCESS ROAD",
    ) -> List[bd.Edge]:
        """Jalan akses plot plan dengan 2 batas tepi dan garis tengah putus-putus."""
        edges: List[bd.Edge] = [
            line(*self.P(e0, n_bot), *self.P(e1, n_bot)),
            line(*self.P(e0, n_top), *self.P(e1, n_top)),
        ]
        n_mid = (n_bot + n_top) / 2.0
        x0, ym = self.P(e0, n_mid)
        x1, _ = self.P(e1, n_mid)

        if tag:
            mid_x = (x0 + x1) / 2.0
            tag_hw = len(tag) * 0.62 * 2.5 / 2.0 + 3.0
            edges.extend(dashed(x0, ym, mid_x - tag_hw, ym, dash=3.0, gap=2.0))
            edges.extend(dashed(mid_x + tag_hw, ym, x1, ym, dash=3.0, gap=2.0))
            self.text(tag, mid_x, ym, size=2.5, att=5, layer="REF-ROAD")
        else:
            edges.extend(dashed(x0, ym, x1, ym, dash=3.0, gap=2.0))

        self.road.extend(edges)
        return edges

    # -------------------------------------------------------------------------
    # EXPORT & INTEGRASI KANONIK (POST-PROCESSOR COMPATIBILITY)
    # -------------------------------------------------------------------------
    def get_layers(self) -> Dict[str, bd.Compound]:
        """Mengembalikan dictionary bd.Compound per layer sesuai Company Standard §3.

        Hanya mengembalikan layer yang memiliki geometri (menghindari DxfContractError
        dari cadgen karena layer kosong).
        """
        layer_candidates = [
            ("REF-FRAME", self.frame),
            ("REF-TITLE", self.title),
            ("REF-GRID", self.grid),
            ("REF-FENCE", self.fence),
            ("REF-ROAD", self.road),
            ("REF-EQUIP", self.equip),
            ("REF-PROC", self.proc),
            ("REF-SYM", self.sym),
            ("REF-DIM", self.dim),
            ("REF-HATCH", self.hatch),
        ]
        layers: Dict[str, bd.Compound] = {}
        for name, edges in layer_candidates:
            if edges:
                layers[name] = comp(edges)
        return layers

    def save_manifest(self, filepath: Union[str, Path]) -> None:
        """Menyimpan manifest teks, dimensi, dan solid ke file .texts.json."""
        manifest = {
            "texts": self.texts,
            "dims": self.dims,
            "solids": self.solids,
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    def export_manifest(self, json_path: Union[str, Path]) -> Dict[str, bd.Compound]:
        """Menyimpan .texts.json dan mengembalikan dictionary bd.Compound per layer."""
        path = Path(json_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.save_manifest(path)
        return self.get_layers()
