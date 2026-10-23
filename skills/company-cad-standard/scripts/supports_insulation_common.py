"""Reusable Pipe Support Catalog (MSS SP-58) & Insulation Class Library.

Versi 1.0.0 (GPF-00-PM-PLN-0008 Bagian V.2-V.3 — Tipe Support & Insulasi).

Standar acuan:
  - MSS SP-58 (Pipe Hangers and Supports — Materials, Design, Manufacture).
  - ASME B31.3-2022 (Process Piping — support & restraint requirements).
  - ISO 6412-2:2017 (simplified representation of pipelines — isometric).
  - ISO 12241 & ASTM C585 (thermal insulation classes & dimensions).
  - Company CAD Standard (skill company-cad-standard): teks MTEXT Arial via
    manifest TEXTS/DIMS/SOLIDS + cad/apply_text.py.

Katalog (Bagian V.2):
  ANC  Anchor                  — tahan translasi X,Y,Z & rotasi (kaku mutlak)
  RES  Resting / Simple Shoe   — tahan beban vertikal (-Z); bebas X, Y
  GUI  Guide                   — hanya aksial (+/-X); tahan lateral (+/-Y)
  STP  Line Stop               — tahan aksial (+/-X); bebas lateral (+/-Y)
  HNG  Rigid Hanger            — menggantung pipa dari struktur atas (-Z)
  VSP  Variable Spring Hanger  — gaya pegas variabel, perpindahan sedang
  CSP  Constant Spring Hanger  — gaya konstan, perpindahan kritis/besar
  TRN  Trunnion / Dummy Leg    — stub pipa dilas ke siku menopang ke struktur

Shoe height (Bagian V.2): SH-0 (bare/pad), SH-100 (insul <= 50 mm),
SH-150 (insul 60-100 mm), SH-200 (insul > 100 mm).

Kode kelas insulasi (Bagian V.3): PP / HC / CC / AC / ET / ST dengan simbol
P&ID garis selubung ganda + label [KODE-TEBAL] dan simbol batas insulasi
isometrik (garis rantai chain line).
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from cadgen import build123d as bd

from pid_common import (
    arc,
    circle,
    comp,
    dashed,
    line,
    rect,
)

# =============================================================================
# DATA KATALOG (SUMBER KEBENARAN: dokumen 08 Bagian V.2 & V.3)
# =============================================================================
SUPPORT_CATALOG: List[Dict[str, str]] = [
    {
        "code": "ANC",
        "name": "ANCHOR",
        "func": "RESTRAINS TRANSLATION X, Y, Z & ROTATION - FULLY RIGID",
    },
    {
        "code": "RES",
        "name": "RESTING / SIMPLE SHOE",
        "func": "CARRIES VERTICAL LOAD (-Z); FREE TO EXPAND IN X, Y",
    },
    {
        "code": "GUI",
        "name": "GUIDE",
        "func": "ALLOWS AXIAL (+/-X) ONLY; RESTRAINS LATERAL (+/-Y)",
    },
    {
        "code": "STP",
        "name": "LINE STOP",
        "func": "RESTRAINS AXIAL (+/-X); FREE LATERAL (+/-Y)",
    },
    {
        "code": "HNG",
        "name": "RIGID HANGER",
        "func": "SUSPENDS PIPE FROM STRUCTURE ABOVE (GRAVITY -Z)",
    },
    {
        "code": "VSP",
        "name": "VARIABLE SPRING HANGER",
        "func": "VARIABLE SPRING FORCE FOR MODERATE THERMAL TRAVEL",
    },
    {
        "code": "CSP",
        "name": "CONSTANT SPRING HANGER",
        "func": "CONSTANT FORCE FOR CRITICAL / LARGE THERMAL TRAVEL",
    },
    {
        "code": "TRN",
        "name": "TRUNNION / DUMMY LEG",
        "func": "DUMMY LEG WELDED TO ELBOW BEARING ON STRUCTURE",
    },
]

# Standar tinggi sepatu pipa vs ketebalan insulasi (Bagian V.2)
SHOE_HEIGHTS: List[Tuple[str, str, str]] = [
    ("SH-0", "BARE PIPE OR WEAR PAD", "0"),
    ("SH-100", "INSULATION <= 50 MM", "100"),
    ("SH-150", "INSULATION 60 - 100 MM", "150"),
    ("SH-200", "INSULATION > 100 MM", "200"),
]

# Kode kelas insulasi & heat tracing (Bagian V.3)
INSULATION_CLASSES: List[Tuple[str, str]] = [
    ("PP", "PERSONNEL PROTECTION"),
    ("HC", "HEAT CONSERVATION"),
    ("CC", "COLD CONSERVATION"),
    ("AC", "ACOUSTIC"),
    ("ET", "ELECTRIC TRACING"),
    ("ST", "STEAM TRACING"),
]

TRACED_CLASSES = ("ET", "ST")  # kelas dengan heat tracing


def shoe_height_for_insulation(insul_mm: float) -> Tuple[str, int]:
    """Pilih kode shoe height untuk ketebalan insulasi (mm) — Bagian V.2."""
    if insul_mm <= 0.0:
        return ("SH-0", 0)
    if insul_mm <= 50.0:
        return ("SH-100", 100)
    if insul_mm <= 100.0:
        return ("SH-150", 150)
    return ("SH-200", 200)


def chain_line(
    x1: float, y1: float, x2: float, y2: float,
    dash: float = 3.0, gap: float = 1.1, dot: float = 0.4,
) -> List[bd.Edge]:
    """Garis rantai (chain / dash-dot) untuk batas insulasi isometrik."""
    dx, dy = x2 - x1, y2 - y1
    ln = math.hypot(dx, dy)
    if ln < 1e-6:
        return []
    ux, uy = dx / ln, dy / ln
    out: List[bd.Edge] = []
    t = 0.0
    while t < ln - 1e-9:
        # dash panjang
        t2 = min(t + dash, ln)
        out.append(line(x1 + ux * t, y1 + uy * t, x1 + ux * t2, y1 + uy * t2))
        t = t2 + gap
        if t >= ln:
            break
        # titik (dot)
        t2 = min(t + dot, ln)
        if t2 - t > 0.05:
            out.append(line(x1 + ux * t, y1 + uy * t, x1 + ux * t2, y1 + uy * t2))
        t = t2 + gap
    return out


# =============================================================================
# KELAS UTAMA KONTEKS SUPPORT & INSULATION (SupInsContext)
# =============================================================================
class SupInsContext:
    """Konteks pembuat gambar standar pipe support & insulasi (A3 420x297 mm).

    Layer:
      frame  REF-FRAME  border, grid, garis tabel katalog
      title  REF-TITLE  title block + rev table (ISO 7200)
      proc   REF-PROC   garis pipa contoh proses (utuh, 0.50)
      equip  REF-EQUIP  struktur / sketsa mekanikal
      sym    REF-SYM    simbol support (iso & plan), selubung insulasi
      texts / solids / dims — manifest post-process apply_text.py
    """

    def __init__(self) -> None:
        self.frame: List[bd.Edge] = []
        self.title: List[bd.Edge] = []
        self.equip: List[bd.Edge] = []
        self.proc: List[bd.Edge] = []
        self.sym: List[bd.Edge] = []
        self.texts: List[Dict[str, Any]] = []
        self.dims: List[Dict[str, Any]] = []
        self.solids: List[Dict[str, Any]] = []

    # -------------------------------------------------------------------------
    # MANIFEST (MTEXT / DIMENSION / SOLID)
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
    ) -> list:
        if not t:
            return []
        h = max(0.5, min(3.0, float(size)))
        self.texts.append(
            {
                "t": str(t),
                "x": round(float(x), 3),
                "y": round(float(y), 3),
                "h": round(h, 2),
                "rot": round(float(rot), 1),
                "layer": layer,
                "att": 4 if left else 5,
            }
        )
        return []

    def dimrec(
        self,
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        txt: str,
        angle: float = 0.0,
        base: Optional[Tuple[float, float]] = None,
    ) -> None:
        d: Dict[str, Any] = {
            "p1": [round(float(p1[0]), 3), round(float(p1[1]), 3)],
            "p2": [round(float(p2[0]), 3), round(float(p2[1]), 3)],
            "angle": round(float(angle), 1),
            "text": str(txt),
        }
        if base is not None:
            d["base"] = [round(float(base[0]), 3), round(float(base[1]), 3)]
        self.dims.append(d)

    def solid_triangle(
        self,
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        p3: Tuple[float, float],
        layer: str = "REF-SYM",
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

    def solid_quad(
        self,
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        p3: Tuple[float, float],
        p4: Tuple[float, float],
        layer: str = "REF-SYM",
    ) -> None:
        self.solid_triangle(p1, p2, p3, layer=layer)
        self.solid_triangle(p1, p3, p4, layer=layer)

    # -------------------------------------------------------------------------
    # SIMBOL ISOMETRIK 8 TIPE SUPPORT (ISO 6412-2, Bagian V.2)
    # Sel panggilan +-11 x +-8 mm; pusat (x, y) pada sumbu pipa.
    # Garis pipa contoh digambar pemanggil (pipe_stub_h) atau otomatis.
    # -------------------------------------------------------------------------
    def pipe_stub_h(self, x: float, y: float, half: float = 9.0) -> List[bd.Edge]:
        """Garis pipa contoh horizontal pada sel simbol (REF-PROC, utuh)."""
        edges = [line(x - half, y, x + half, y)]
        self.proc.extend(edges)
        return edges

    def iso_anc(self, x: float, y: float) -> List[bd.Edge]:
        """ANC — kotak silang ganda dengan penopang kaku (rigid brace + base)."""
        edges = [
            # kotak pada pipa
            line(x - 4.0, y - 2.0, x + 4.0, y - 2.0),
            line(x + 4.0, y - 2.0, x + 4.0, y + 2.0),
            line(x + 4.0, y + 2.0, x - 4.0, y + 2.0),
            line(x - 4.0, y + 2.0, x - 4.0, y - 2.0),
            # silang ganda (X + plus)
            line(x - 4.0, y - 2.0, x + 4.0, y + 2.0),
            line(x - 4.0, y + 2.0, x + 4.0, y - 2.0),
            line(x - 4.0, y, x + 4.0, y),
            line(x, y - 2.0, x, y + 2.0),
            # penopang kaku ke base plate
            line(x - 4.0, y - 2.0, x - 7.0, y - 6.0),
            line(x + 4.0, y - 2.0, x + 7.0, y - 6.0),
            line(x - 8.5, y - 6.0, x + 8.5, y - 6.0),
        ]
        self.sym.extend(edges)
        return edges

    def iso_res(self, x: float, y: float) -> List[bd.Edge]:
        """RES — garis tumpuan horizontal + kaki segitiga."""
        edges = [
            line(x - 5.0, y - 1.6, x + 5.0, y - 1.6),
            line(x - 4.0, y - 1.6, x, y - 6.0),
            line(x, y - 6.0, x + 4.0, y - 1.6),
            line(x - 5.0, y - 6.0, x + 5.0, y - 6.0),
        ]
        self.sym.extend(edges)
        return edges

    def iso_gui(self, x: float, y: float) -> List[bd.Edge]:
        """GUI — tumpuan resting + sepasang garis pembatas lateral."""
        edges = self.iso_res(x, y)
        edges += [
            line(x - 6.0, y - 1.6, x - 6.0, y + 2.4),
            line(x + 6.0, y - 1.6, x + 6.0, y + 2.4),
            line(x - 6.0, y + 2.4, x - 4.6, y + 2.4),
            line(x + 6.0, y + 2.4, x + 4.6, y + 2.4),
        ]
        self.sym.extend(edges[-4:])
        return edges

    def iso_stp(self, x: float, y: float) -> List[bd.Edge]:
        """STP — sepasang sirip pengganjal vertikal pada sepatu + balok penahan."""
        edges = self.iso_res(x, y)
        edges += [
            line(x - 4.6, y - 1.6, x - 4.6, y + 1.8),
            line(x + 4.6, y - 1.6, x + 4.6, y + 1.8),
            line(x - 4.6, y - 3.4, x + 4.6, y - 3.4),
        ]
        self.sym.extend(edges[-3:])
        return edges

    def iso_hng(self, x: float, y: float) -> List[bd.Edge]:
        """HNG — batang vertikal dari klem pipa dengan loop engsel ke struktur."""
        edges = [
            # struktur atas
            line(x - 8.0, y + 6.0, x + 8.0, y + 6.0),
            # batang gantung
            line(x, y + 6.0, x, y + 2.0),
            # loop engsel
            circle(x, y + 4.0, 1.1),
            # klem pipa
            line(x - 3.0, y + 2.0, x + 3.0, y + 2.0),
            line(x - 3.0, y + 2.0, x - 3.0, y - 1.6),
            line(x + 3.0, y + 2.0, x + 3.0, y - 1.6),
        ]
        self.sym.extend(edges)
        return edges

    def _spring_zigzag(
        self, x: float, y0: float, y1: float, w: float, n: int = 6
    ) -> List[bd.Edge]:
        edges = []
        step = (y1 - y0) / n
        for i in range(n):
            ya = y0 + i * step
            yb = ya + step
            sx = x - w if i % 2 == 0 else x + w
            edges.append(line(sx, ya, -sx + 2 * x, yb))
        return edges

    def iso_vsp(self, x: float, y: float) -> List[bd.Edge]:
        """VSP — tabung silinder vertikal dengan kumparan pegas di dalamnya."""
        edges = [
            # silinder pegas
            line(x - 3.0, y - 4.6, x + 3.0, y - 4.6),
            line(x + 3.0, y - 4.6, x + 3.0, y + 4.6),
            line(x + 3.0, y + 4.6, x - 3.0, y + 4.6),
            line(x - 3.0, y + 4.6, x - 3.0, y - 4.6),
            # batang atas ke struktur / titik gantung
            line(x, y + 4.6, x, y + 6.2),
            line(x - 2.0, y + 6.2, x + 2.0, y + 6.2),
            # batang bawah ke klem pipa
            line(x, y - 4.6, x, y - 6.2),
            line(x - 2.5, y - 6.2, x + 2.5, y - 6.2),
        ]
        edges += self._spring_zigzag(x, y - 3.9, y + 3.9, w=2.0, n=6)
        self.sym.extend(edges)
        return edges

    def iso_csp(self, x: float, y: float) -> List[bd.Edge]:
        """CSP — tabung silinder horizontal, pegas lengan momen (lever)."""
        edges = [
            # silinder horizontal
            line(x - 6.0, y - 3.2, x + 6.0, y - 3.2),
            line(x + 6.0, y - 3.2, x + 6.0, y + 3.2),
            line(x + 6.0, y + 3.2, x - 6.0, y + 3.2),
            line(x - 6.0, y + 3.2, x - 6.0, y - 3.2),
            # pivot engsel kiri
            circle(x - 6.0, y, 0.8),
            # lengan momen keluar dari silinder
            line(x, y + 3.2, x + 4.6, y + 6.0),
            # batang beban ke klem pipa
            line(x, y - 3.2, x, y - 5.2),
            line(x - 2.5, y - 5.2, x + 2.5, y - 5.2),
        ]
        # kumparan pegas pada lengan momen
        edges += [
            line(x + 1.1, y + 3.9, x + 3.2, y + 4.6),
            line(x + 3.2, y + 4.6, x + 1.5, y + 5.2),
            line(x + 1.5, y + 5.2, x + 3.6, y + 5.9),
        ]
        self.sym.extend(edges)
        return edges

    def iso_trn(self, x: float, y: float) -> List[bd.Edge]:
        """TRN — garis pipa buntu terputus tepat di punggung siku (elbow +
        stub ke bawah dengan break mark).
        """
        edges = [
            # pipa datang + siku miter turun
            line(x - 8.0, y + 4.0, x + 2.0, y + 4.0),
            line(x + 2.0, y + 4.0, x + 2.0, y - 2.0),
            # stub trunnion ke bawah
            line(x + 2.0, y - 2.0, x + 2.0, y - 4.6),
            # break mark (zigzag putus)
            line(x + 0.6, y - 4.6, x + 3.4, y - 5.4),
            line(x + 3.4, y - 5.4, x + 0.6, y - 6.2),
        ]
        self.sym.extend(edges)
        return edges

    def draw_iso_support(self, code: str, x: float, y: float) -> List[bd.Edge]:
        """Dispatch simbol isometrik berdasarkan kode katalog."""
        fn = {
            "ANC": self.iso_anc, "RES": self.iso_res, "GUI": self.iso_gui,
            "STP": self.iso_stp, "HNG": self.iso_hng, "VSP": self.iso_vsp,
            "CSP": self.iso_csp, "TRN": self.iso_trn,
        }.get(code.strip().upper())
        if fn is None:
            raise ValueError(f"Kode support tidak dikenal: {code}")
        return fn(x, y)

    # -------------------------------------------------------------------------
    # SIMBOL PIPING PLAN 2D 8 TIPE SUPPORT (Bagian V.2)
    # -------------------------------------------------------------------------
    def plan_rest_base(self, x: float, y: float) -> List[bd.Edge]:
        """Dasar bersama simbol resting: pelat tumpu di bawah sumbu pipa."""
        return [
            line(x - 4.0, y - 1.8, x + 4.0, y - 1.8),
            line(x - 4.0, y - 1.8, x - 4.0, y - 3.2),
            line(x + 4.0, y - 1.8, x + 4.0, y - 3.2),
        ]

    def plan_anc(self, x: float, y: float) -> List[bd.Edge]:
        """ANC — kotak pejal dengan silang ganda (X + plus)."""
        edges = [
            line(x - 2.6, y - 2.0, x + 2.6, y - 2.0),
            line(x + 2.6, y - 2.0, x + 2.6, y + 2.0),
            line(x + 2.6, y + 2.0, x - 2.6, y + 2.0),
            line(x - 2.6, y + 2.0, x - 2.6, y - 2.0),
            line(x - 2.6, y - 2.0, x + 2.6, y + 2.0),
            line(x - 2.6, y + 2.0, x + 2.6, y - 2.0),
            line(x - 2.6, y, x + 2.6, y),
            line(x, y - 2.0, x, y + 2.0),
        ]
        self.sym.extend(edges)
        return edges

    def plan_res(self, x: float, y: float) -> List[bd.Edge]:
        edges = self.plan_rest_base(x, y)
        self.sym.extend(edges)
        return edges

    def plan_gui(self, x: float, y: float) -> List[bd.Edge]:
        """GUI — tumpuan resting + dua sayap penjepit lateral."""
        edges = self.plan_rest_base(x, y)
        edges += [
            line(x - 5.2, y, x - 6.8, y),
            line(x - 6.8, y - 1.2, x - 6.8, y + 1.2),
            line(x + 5.2, y, x + 6.8, y),
            line(x + 6.8, y - 1.2, x + 6.8, y + 1.2),
        ]
        self.sym.extend(edges)
        return edges

    def plan_stp(self, x: float, y: float) -> List[bd.Edge]:
        """STP — tumpuan resting + balok penahan aksial di bawah pelat."""
        edges = self.plan_rest_base(x, y)
        edges += [
            line(x - 3.2, y - 3.2, x + 3.2, y - 3.2),
            line(x - 3.2, y - 3.2, x - 3.2, y - 4.4),
            line(x + 3.2, y - 3.2, x + 3.2, y - 4.4),
        ]
        self.sym.extend(edges)
        return edges

    def plan_hng(self, x: float, y: float) -> List[bd.Edge]:
        """HNG — lingkaran klem kecil + garis leader ke balok atas."""
        edges = [
            circle(x, y, 1.8),
            line(x, y + 1.8, x, y + 4.6),
            line(x - 5.5, y + 4.6, x + 5.5, y + 4.6),
        ]
        self.sym.extend(edges)
        return edges

    def plan_vsp(self, x: float, y: float) -> List[bd.Edge]:
        """VSP — tabung lingkaran konsentris dengan notasi VS."""
        edges = [circle(x, y, 2.2), circle(x, y, 3.2)]
        self.text("VS", x, y, size=1.4)
        self.sym.extend(edges)
        return edges

    def plan_csp(self, x: float, y: float) -> List[bd.Edge]:
        """CSP — tabung persegi panjang dengan notasi CS."""
        edges = rect(x - 3.6, y - 2.2, x + 3.6, y + 2.2)
        self.text("CS", x, y, size=1.4)
        self.sym.extend(edges)
        return edges

    def plan_trn(self, x: float, y: float) -> List[bd.Edge]:
        """TRN — proyeksi pipa vertikal di bawah siku (lingkaran + stub)."""
        edges = [circle(x, y, 2.0)]
        edges += dashed(x, y - 2.0, x, y - 6.4, dash=1.6, gap=1.0)
        self.sym.extend(edges)
        return edges

    def draw_plan_support(self, code: str, x: float, y: float) -> List[bd.Edge]:
        """Dispatch simbol plan berdasarkan kode katalog."""
        fn = {
            "ANC": self.plan_anc, "RES": self.plan_res, "GUI": self.plan_gui,
            "STP": self.plan_stp, "HNG": self.plan_hng, "VSP": self.plan_vsp,
            "CSP": self.plan_csp, "TRN": self.plan_trn,
        }.get(code.strip().upper())
        if fn is None:
            raise ValueError(f"Kode support tidak dikenal: {code}")
        return fn(x, y)

    # -------------------------------------------------------------------------
    # SIMBOL INSULASI (Bagian V.3)
    # -------------------------------------------------------------------------
    def pid_insulation_jacket(
        self,
        x0: float,
        x1: float,
        y: float,
        cls: str = "PP",
        thk_mm: int = 50,
        jacket_half: float = 2.4,
        tracing: Optional[bool] = None,
        label_dy: float = 4.8,
        pipe_layer: str = "REF-SYM",
    ) -> List[bd.Edge]:
        """Simbol P&ID garis selubung ganda + label [KLAS-TEBAL].

        - Garis pipa carrier utuh x0..x1.
        - Selubung: dua garis paralel +-jacket_half + garis penutup ujung.
        - Kelas ET/ST: garis tracer putus-putus di dalam selubung.
        Label otomatis: [PP-50] / [ET-HC-40] (cls boleh 'PP' atau 'ET-HC').
        """
        carrier = line(x0, y, x1, y)
        if pipe_layer == "REF-PROC":
            self.proc.append(carrier)
        else:
            self.sym.append(carrier)
        edges = [
            line(x0, y - jacket_half, x1, y - jacket_half),
            line(x0, y + jacket_half, x1, y + jacket_half),
            line(x0, y - jacket_half, x0, y + jacket_half),
            line(x1, y - jacket_half, x1, y + jacket_half),
        ]
        if tracing is None:
            tracing = any(c in cls for c in TRACED_CLASSES)
        if tracing:
            edges += dashed(x0 + 3.0, y + 1.2, x1 - 3.0, y + 1.2, dash=2.2, gap=1.3)
        self.sym.extend(edges)
        self.text(f"[{cls}-{thk_mm}]", (x0 + x1) / 2.0, y + label_dy, size=2.0)
        return edges

    def iso_insulation_break(
        self,
        x: float,
        y: float,
        half: float = 4.5,
        pipe_half: float = 9.0,
        label: str = "INSULATION BREAK",
        pipe_layer: str = "REF-PROC",
    ) -> List[bd.Edge]:
        """Simbol batas insulasi isometrik: garis rantai (chain line) tegak
        lurus pipa + label. Garis pipa contoh ikut digambar utuh (default
        REF-PROC; gunakan REF-SYM untuk sel katalog/legend agar bebas dangling).
        """
        carrier = line(x - pipe_half, y, x + pipe_half, y)
        if pipe_layer == "REF-PROC":
            self.proc.append(carrier)
        else:
            self.sym.append(carrier)
        edges = chain_line(x, y - half, x, y + half)
        self.sym.extend(edges)
        if label:
            self.text(label, x, y + half + 2.6, size=1.8)
        return edges

    # -------------------------------------------------------------------------
    # FURNITUR LEMBAR A3 — ISO 5457 + TITLE BLOCK ISO 7200 (Company Standard)
    # -------------------------------------------------------------------------
    def setup_a3_furniture(
        self,
        doc_no: str,
        title_lines: List[str],
        notes: List[str],
        ref_docs: List[Tuple[str, str]],
        scale_str: str = "NTS",
        rev: str = "A0",
        rev_desc: str = "ISSUED FOR REVIEW",
        date_str: str = "23 OCT 2026",
    ) -> Dict[str, float]:
        """Border A3 + grid referensi + kolom kanan; LEGEND disiapkan kotaknya."""
        self.frame += rect(2.0, 1.3, 418.0, 295.7)
        self.frame += rect(7.0, 6.3, 413.0, 290.7)

        step_x = (413.0 - 7.0) / 12.0
        for i in range(1, 12):
            gx = 7.0 + i * step_x
            self.frame += [line(gx, 290.7, gx, 295.7), line(gx, 1.3, gx, 6.3)]
        for i in range(12):
            gxc = 7.0 + (i + 0.5) * step_x
            self.text(str(i + 1), gxc, 293.2, size=1.6)
            self.text(str(i + 1), gxc, 3.8, size=1.6)
        step_y = (290.7 - 6.3) / 8.0
        for j in range(1, 8):
            gy = 6.3 + j * step_y
            self.frame += [line(2.0, gy, 7.0, gy), line(413.0, gy, 418.0, gy)]
        for j in range(8):
            gyc = 290.7 - (j + 0.5) * step_y
            self.text("ABCDEFGH"[j], 4.5, gyc, size=1.6)
            self.text("ABCDEFGH"[j], 415.5, gyc, size=1.6)

        fx0, fx1 = 336.0, 413.0
        self.frame.append(line(fx0, 6.3, fx0, 290.7))

        # NOTES
        self.frame.append(line(fx0, 238.0, fx1, 238.0))
        self.text("NOTES", (fx0 + fx1) / 2.0, 286.0, size=2.5)
        self.frame.append(line(fx0, 283.0, fx1, 283.0))
        ny = 278.5
        for note in notes:
            self.text(note, fx0 + 3.0, ny, size=1.8, left=True)
            ny -= 6.3

        # LEGEND (kotak untuk penelepon)
        self.frame.append(line(fx0, 170.0, fx1, 170.0))
        self.text("LEGEND", (fx0 + fx1) / 2.0, 234.0, size=2.5)
        self.frame.append(line(fx0, 231.0, fx1, 231.0))

        # REFERENCE DOCUMENT
        self.frame.append(line(fx0, 142.0, fx1, 142.0))
        self.text("REFERENCE DOCUMENT", (fx0 + fx1) / 2.0, 166.0, size=2.0)
        self.frame.append(line(fx0, 163.0, fx1, 163.0))
        ry = 157.0
        for doc_id, doc_title in ref_docs:
            self.text(doc_id, fx0 + 3.0, ry, size=1.5, left=True)
            self.text(doc_title, fx0 + 36.0, ry, size=1.5, left=True)
            ry -= 6.0

        # REV TABLE
        self.title += [
            line(fx0, 118.0, fx1, 118.0),
            line(fx0, 136.0, fx1, 136.0),
            line(fx0, 127.0, fx1, 127.0),
            line(fx0, 142.0, fx1, 142.0),
            line(346.0, 118.0, 346.0, 142.0),
            line(356.0, 118.0, 356.0, 142.0),
            line(396.0, 118.0, 396.0, 142.0),
        ]
        self.text("NO", 341.0, 138.5, size=1.8)
        self.text("REV", 351.0, 138.5, size=1.8)
        self.text("DESCRIPTION", 358.0, 138.5, size=1.8, left=True)
        self.text("DATE", 404.5, 138.5, size=1.8)
        self.text("1", 341.0, 131.5, size=1.8)
        self.text(rev, 351.0, 131.5, size=1.8)
        self.text(rev_desc, 358.0, 131.5, size=1.8, left=True)
        self.text(date_str, 404.5, 131.5, size=1.8)

        # TITLE BLOCK
        self.title += [
            line(fx0, 92.0, fx1, 92.0),
            line(fx0, 68.0, fx1, 68.0),
            line(fx0, 54.0, fx1, 54.0),
            line(fx0, 40.0, fx1, 40.0),
            line(fx0, 26.0, fx1, 26.0),
        ]
        tcx = (fx0 + fx1) / 2.0
        self.text("PROJECT:", fx0 + 3.0, 114.8, size=1.6, left=True)
        self.text("GAS PRODUCTION FACILITY - ONSHORE FIELD", fx0 + 3.0, 111.0,
                  size=2.0, left=True)
        self.text("COMPANY:", fx0 + 3.0, 106.8, size=1.6, left=True)
        self.text("PM OIL & GAS SURFACE FACILITY", fx0 + 3.0, 103.0,
                  size=2.0, left=True)
        self.text("CONSULTANT:", fx0 + 3.0, 98.8, size=1.6, left=True)
        self.text("REKAYASA ENGINEERING", fx0 + 3.0, 95.0, size=2.0, left=True)

        ty = 82.5
        for tl in title_lines[:2]:
            self.text(tl, tcx, ty, size=2.6)
            ty -= 6.0

        self.text("DRAWING NO:", fx0 + 3.0, 64.0, size=1.6, left=True)
        self.text(doc_no, fx0 + 3.0, 58.0, size=2.8, left=True)

        self.text("REV:", fx0 + 3.0, 50.0, size=1.6, left=True)
        self.text(rev, fx0 + 8.0, 44.0, size=2.4)
        self.text("SCALE:", fx0 + 29.0, 50.0, size=1.6, left=True)
        self.text(scale_str, fx0 + 36.0, 44.0, size=2.4)
        self.text("SHEET:", fx0 + 56.0, 50.0, size=1.6, left=True)
        self.text("1 OF 1", fx0 + 62.0, 44.0, size=2.4)

        self.text("DATE:", fx0 + 3.0, 36.0, size=1.6, left=True)
        self.text(date_str, fx0 + 8.0, 30.0, size=2.0)
        self.text("DRAWN:", fx0 + 36.0, 36.0, size=1.6, left=True)
        self.text("GLM-5.3-FLASH", fx0 + 40.0, 30.0, size=2.0)

        self.text("CHECKED:", fx0 + 3.0, 22.0, size=1.6, left=True)
        self.text("PM (AI)", fx0 + 10.0, 16.0, size=2.0)
        self.text("APPROVED:", fx0 + 40.0, 22.0, size=1.6, left=True)
        # APPROVED sengaja kosong (company standard)

        return {"x0": fx0, "x1": fx1, "y_top": 231.0, "y_bot": 170.0}

    # -------------------------------------------------------------------------
    # EXPORT
    # -------------------------------------------------------------------------
    def get_layers(self) -> Dict[str, bd.Compound]:
        mapping = {
            "REF-FRAME": self.frame,
            "REF-TITLE": self.title,
            "REF-EQUIP": self.equip,
            "REF-PROC": self.proc,
            "REF-SYM": self.sym,
        }
        return {name: comp(items) for name, items in mapping.items() if items}

    def export_manifest(self, json_path: Path | str) -> Dict[str, bd.Compound]:
        path = Path(json_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        manifest = {"texts": self.texts, "dims": self.dims, "solids": self.solids}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        return self.get_layers()
