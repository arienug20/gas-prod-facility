"""Reusable Pipeline Alignment Sheet Builder (doc GPF-00-PM-PLN-0008, Bagian VI).

Memadukan data survei topografi GIS (CSV stasiun KP) dengan gambar teknik pipa
transmisi bentang panjang pada satu lembar A1 split-window:
  - Panel Atas  (40%): PLAN VIEW  — sumbu pipa per stasiun KP, batas ROW
    15-25 m, tikungan cold/hot bend, penyeberangan jalan/sungai, north arrow.
  - Panel Tengah(30%): PROFILE VIEW — skala vertikal berlebih (VEX), kontur
    tanah asli NGL, elevasi dasar pipa BOP, depth of cover, galian terbuka
    vs HDD.
  - Panel Bawah (30%): DATA BANDS — 8 band vertikal per stasiun KP
    (Ground Elev, Pipe Elev, Depth of Cover, Chainage KP, Wall Thickness &
    Grade API 5L, Class Location ASME B31.8, Coating 3LPE/Concrete, Klasifikasi
    Tanah).

Parser data survei: `parse_survey_csv()` membaca CSV kolom KP, Northing,
Easthing, Elevasi (+ kolom atribut opsional) — see `parse_survey_csv`.

Gaya kode mengikuti `plan_common.py` / `pid_common.py`: kelas context +
fungsi gambar, layer REF-*, teks HANYA via manifest TEXTS (MTEXT Arial
ditulis post-build oleh cad/apply_text.py — DILARANG outline bd.Text).

Standar acuan: ASME B31.8-2022 (gas transmission & distribution piping),
API 5L (line pipe), ISO 5457:1999 (lembar A1), ISO 7200:2004 (title block),
Company CAD Standard (skill company-cad-standard).
"""

from __future__ import annotations

import csv
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

from cadgen import build123d as bd

__all__ = [
    "PIPE_OD_M",
    "SurveyStation",
    "Bend",
    "Crossing",
    "parse_kp",
    "fmt_kp",
    "parse_survey_csv",
    "derive_features",
    "AlignmentSheetContext",
    "line",
    "circle",
    "arc",
    "rect",
    "dashed",
    "comp",
]

# OD pipa demo/transmisi tipikal (20 inch) dalam meter — dipakai BOP = NGL - DOC - OD.
PIPE_OD_M = 0.508


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
    """Create a 2D circular arc edge centered at (x, y) from a1 to a2 deg."""
    return bd.Location((x, y, 0)) * bd.Edge.make_circle(r, start_angle=a1, end_angle=a2)


def rect(x0: float, y0: float, x1: float, y1: float) -> List[bd.Edge]:
    """4 edges forming an axis-aligned rectangle (x0, y0) to (x1, y1)."""
    return [
        line(x0, y0, x1, y0),
        line(x1, y0, x1, y1),
        line(x1, y1, x0, y1),
        line(x0, y1, x0, y0),
    ]


def dashed(
    x1: float, y1: float, x2: float, y2: float, dash: float = 4.0, gap: float = 1.6
) -> List[bd.Edge]:
    """Dashed line segments between (x1, y1) and (x2, y2)."""
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
# DATA MODEL SURVEI & PARSER CSV
# =============================================================================
_KP_RE = re.compile(r"^\s*(\d+)\s*\+\s*(\d+(?:\.\d+)?)\s*$")

# Alias header CSV (case-insensitive).
_COL_ALIASES: Dict[str, Tuple[str, ...]] = {
    "kp": ("KP", "CHAINAGE", "STATION", "STA"),
    "northing": ("NORTHING", "N", "NORTE"),
    "easting": ("EASTING", "E", "ESTE"),
    "ground_elev": ("ELEVASI", "ELEVATION", "ELEV", "GROUND_ELEV", "GL", "NGL"),
    "depth_cover": ("DEPTH_OF_COVER", "DOC", "COVER", "KEDALAMAN"),
    "wall_thk": ("WALL_THK", "WALLTHICKNESS", "WT", "TEBAL"),
    "grade": ("GRADE", "MATERIAL", "API_GRADE"),
    "class_loc": ("CLASS_LOCATION", "CLASSLOC", "CLASS", "LOKASI_KELAS"),
    "coating": ("COATING", "LAPIS", "COAT"),
    "soil": ("SOIL", "SOIL_TYPE", "SOILCLASS", "TANAH"),
    "feature": ("FEATURE", "REMARK", "REMARKS", "FASILITAS", "CROSSING"),
}


def parse_kp(value: Union[str, float, int]) -> float:
    """Parses nilai KP menjadi meter rantai (chainage).

    Menerima format '0+000', '1+900', '1+050.5', maupun float meter langsung.
    """
    if isinstance(value, (int, float)):
        return float(value)
    m = _KP_RE.match(str(value))
    if m:
        return float(m.group(1)) * 1000.0 + float(m.group(2))
    return float(str(value).strip())


def fmt_kp(kp_m: float) -> str:
    """Format meter rantai menjadi label KP 'x+xxx' (mis. 1900.0 -> '1+900')."""
    total = int(round(float(kp_m) * 1000.0))
    km, rem = divmod(total, 1_000_000)
    m = rem // 1000
    frac = rem % 1000
    if frac:
        return f"{km}+{m:03d}.{frac:03d}"
    return f"{km}+{m:03d}"


@dataclass
class SurveyStation:
    """Satu stasiun survei sepanjang rute pipa (satu baris CSV)."""

    kp_m: float                     # chainage (meter)
    northing: float                 # meter
    easting: float                  # meter
    ground_elev: float              # NGL (m atas datum)
    depth_cover: float = 1.2        # depth of cover ke puncak pipa (m), ASME B31.8 >= 1.0-1.2
    wall_thk: float = 9.5           # wall thickness (mm)
    grade: str = "X52"              # grade API 5L
    class_loc: str = "CL1-D2"       # class location ASME B31.8
    coating: str = "3LPE"           # coating (3LPE / 3LPE+CONC)
    soil: str = "CL"                # klasifikasi tanah (USCS)
    feature: str = ""               # penanda: BEND / ROAD / RIVER (format ; separated)

    @property
    def pipe_elev(self) -> float:
        """Elevasi dasar pipa BOP (m) = NGL - depth of cover - OD."""
        return self.ground_elev - self.depth_cover - PIPE_OD_M

    @property
    def kp_label(self) -> str:
        return fmt_kp(self.kp_m)


@dataclass
class Bend:
    """Tikungan pipa (cold bend / hot bend) pada satu stasiun KP."""

    kp_m: float
    kind: str                       # "COLD" atau "HOT"
    deflection_deg: float           # sudut belok (deg, selalu positif)
    side: str = "R"                 # "R" (kanan) / "L" (kiri)

    @property
    def label(self) -> str:
        return f"{self.kind} BEND {self.deflection_deg:.0f}\u00b0{self.side}"


@dataclass
class Crossing:
    """Penyeberangan (jalan / sungai / fasilitas lain) pada satu KP."""

    kp_m: float
    kind: str                       # "ROAD" / "RIVER"
    name: str = ""
    method: str = "OPEN CUT"        # "OPEN CUT" / "HDD"
    width_m: float = 8.0            # lebar objek yang diberok (m)


def _pick(row: Dict[str, str], names: Tuple[str, ...]) -> str:
    for n in names:
        for k, v in row.items():
            if k is not None and k.strip().upper() == n:
                if v is not None and str(v).strip() != "":
                    return str(v).strip()
    return ""


def parse_survey_csv(
    path: Union[str, Path], defaults: Optional[Dict[str, Any]] = None
) -> List[SurveyStation]:
    """Parser data survei CSV stasiun KP -> daftar `SurveyStation`.

    Kolom wajib: KP, Northing, Easting, Elevasi (alias di `_COL_ALIASES`).
    Kolom opsional: Depth_of_Cover, Wall_Thk, Grade, Class_Location, Coating,
    Soil, Feature. Nilai opsional yang kosong diisi dari `defaults` /
    default dataclass.

    Baris diurutkan naik berdasarkan KP. Baris kosong / KP tidak valid
    dilewati. Feature dipertahankan mentah di station.feature (lihat
    `derive_features` untuk mengubahnya menjadi Bend / Crossing).
    """
    d = dict(defaults or {})
    stations: List[SurveyStation] = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row:
                continue
            kp_raw = _pick(row, _COL_ALIASES["kp"])
            if not kp_raw:
                continue
            try:
                kp = parse_kp(kp_raw)
            except (TypeError, ValueError):
                continue
            n_raw, e_raw, z_raw = (
                _pick(row, _COL_ALIASES["northing"]),
                _pick(row, _COL_ALIASES["easting"]),
                _pick(row, _COL_ALIASES["ground_elev"]),
            )
            if not (n_raw and e_raw and z_raw):
                continue
            st = SurveyStation(
                kp_m=kp,
                northing=float(n_raw),
                easting=float(e_raw),
                ground_elev=float(z_raw),
                depth_cover=float(_pick(row, _COL_ALIASES["depth_cover"]) or d.get("depth_cover", 1.2)),
                wall_thk=float(_pick(row, _COL_ALIASES["wall_thk"]) or d.get("wall_thk", 9.5)),
                grade=_pick(row, _COL_ALIASES["grade"]) or str(d.get("grade", "X52")),
                class_loc=_pick(row, _COL_ALIASES["class_loc"]) or str(d.get("class_loc", "CL1-D2")),
                coating=_pick(row, _COL_ALIASES["coating"]) or str(d.get("coating", "3LPE")),
                soil=_pick(row, _COL_ALIASES["soil"]) or str(d.get("soil", "CL")),
                feature=_pick(row, _COL_ALIASES["feature"]),
            )
            stations.append(st)
    stations.sort(key=lambda s: s.kp_m)
    if not stations:
        raise ValueError(f"Tidak ada stasiun valid pada {path}")
    return stations


def derive_features(
    stations: Sequence[SurveyStation],
) -> Tuple[List[Bend], List[Crossing]]:
    """Ekstrak daftar Bend & Crossing dari kolom Feature stasiun.

    Format Feature (field dipisah ';'):
      - "BEND;<COLD|HOT>;<deflection_deg>;<R|L>"
      - "ROAD;<nama>;<OPEN CUT|HDD>;<lebar_m>"
      - "RIVER;<nama>;<OPEN CUT|HDD>;<lebar_m>"
    """
    bends: List[Bend] = []
    crossings: List[Crossing] = []
    for st in stations:
        f = (st.feature or "").strip()
        if not f:
            continue
        parts = [p.strip() for p in f.split(";")]
        head = parts[0].upper()
        if head == "BEND" and len(parts) >= 3:
            kind = parts[1].upper() if parts[1].upper() in ("COLD", "HOT") else "COLD"
            try:
                deg = float(parts[2])
            except ValueError:
                deg = 0.0
            side = (parts[3].upper() if len(parts) > 3 and parts[3].upper() in ("R", "L") else "R")
            bends.append(Bend(kp_m=st.kp_m, kind=kind, deflection_deg=abs(deg), side=side))
        elif head in ("ROAD", "RIVER") and len(parts) >= 2:
            name = parts[1]
            method = (parts[2].upper() if len(parts) > 2 and parts[2] else "OPEN CUT")
            try:
                width = float(parts[3]) if len(parts) > 3 and parts[3] else 8.0
            except ValueError:
                width = 8.0
            crossings.append(
                Crossing(kp_m=st.kp_m, kind=head, name=name, method=method, width_m=width)
            )
    return bends, crossings


def heading_at(stations: Sequence[SurveyStation], kp_m: float) -> float:
    """Heading rute (deg, 0 = Timur, CCW positif) pada chainage kp_m."""
    pts = [(s.easting, s.northing) for s in stations]
    kps = [s.kp_m for s in stations]
    for i in range(len(kps) - 1):
        if kps[i] <= kp_m <= kps[i + 1]:
            de = pts[i + 1][0] - pts[i][0]
            dn = pts[i + 1][1] - pts[i][1]
            if abs(de) < 1e-9 and abs(dn) < 1e-9:
                continue
            return math.degrees(math.atan2(dn, de))
    # di luar rentang: pakai segmen terdekat
    if kp_m < kps[0]:
        de, dn = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
    else:
        de, dn = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    return math.degrees(math.atan2(dn, de))


# =============================================================================
# ALIGNMENT SHEET CONTEXT (A1 841 x 594, SPLIT-WINDOW 40/30/30)
# =============================================================================
class AlignmentSheetContext:
    """Framework Pipeline Alignment Sheet A1 split-window (plan / profile / bands).

    Mapping koordinat (semua panel berbagi sumbu chainage horizontal):
      x_sheet = ch_x0 + (KP_m - kp_min) * h_scale        (h_scale mm/m, 1:4000 = 0.25)
      y_plan  = plan_y_ref + (Northing - plan_n_ref) * h_scale
      y_prof  = prof_y0 + (Elevasi - prof_el0) * v_scale  (v_scale mm/m, 1:250 = 4.0)

    Manifest TEXTS/SOLIDS/DIMS ditulis via text()/solid_*()/dimrec() dan
    diekspor export_manifest() untuk post-processor cad/apply_text.py.
    """

    # Panel split-window (fraksi tinggi area dalam border): plan 40 / profile 30 / bands 30.
    PLAN_FRAC = 0.40
    PROF_FRAC = 0.30
    BAND_FRAC = 0.30

    def __init__(
        self,
        stations: Sequence[SurveyStation],
        bends: Sequence[Bend] = (),
        crossings: Sequence[Crossing] = (),
        *,
        ch_x0: float = 110.0,
        h_scale: float = 0.25,          # 1:4000 @ A1
        v_scale: float = 4.0,           # 1:250 @ A1 (VEX 16:1 vs 1:4000)
        plan_y_ref: float = 470.0,
        plan_n_ref: Optional[float] = None,
        prof_y0: float = 196.0,
        prof_el0: float = 90.0,
        prof_el1: float = 117.0,
        pipe_od_m: float = PIPE_OD_M,
        doc_no: str = "GPF-00-PI-PLN-0019",
        title_main: str = "PIPELINE ALIGNMENT SHEET",
        title_sub: str = "",
        project: str = "GAS PRODUCTION FACILITY - ONSHORE FIELD",
        company: str = "PM OIL & GAS SURFACE FACILITY",
        consultant: str = "REKAYASA ENGINEERING",
        drawn_by: str = "GLM-5.3-FLASH",
        checked_by: str = "PM (AI)",
        approved: str = "\u2014",
        rev: str = "A0",
        rev_desc: str = "ISSUED FOR REVIEW",
        date_str: str = "23 OCT 2026",
        sheet_str: str = "1 OF 1",
        units_str: str = "mm",
    ) -> None:
        if not stations:
            raise ValueError("stations kosong")
        self.stations = list(stations)
        self.bends = list(bends)
        self.crossings = list(crossings)
        self.kp_min = min(s.kp_m for s in self.stations)
        self.kp_max = max(s.kp_m for s in self.stations)
        self.ch_x0 = float(ch_x0)
        self.h_scale = float(h_scale)
        self.v_scale = float(v_scale)
        self.plan_y_ref = float(plan_y_ref)
        self.plan_n_ref = (
            float(plan_n_ref)
            if plan_n_ref is not None
            else sum(s.northing for s in self.stations) / len(self.stations)
        )
        self.prof_y0 = float(prof_y0)
        self.prof_el0 = float(prof_el0)
        self.prof_el1 = float(prof_el1)
        self.pipe_od_m = float(pipe_od_m)

        # Title block fields (ISO 7200 / company standard)
        self.doc_no = doc_no
        self.title_main = title_main
        self.title_sub = title_sub or (
            f"KP {fmt_kp(self.kp_min)} TO {fmt_kp(self.kp_max)}"
        )
        self.project = project
        self.company = company
        self.consultant = consultant
        self.drawn_by = drawn_by
        self.checked_by = checked_by
        self.approved = approved
        self.rev = rev
        self.rev_desc = rev_desc
        self.date_str = date_str
        self.sheet_str = sheet_str
        self.units_str = units_str

        # Koleksi layer standar drawing (REF-*)
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

        # Manifest entitas pasca-build (MTEXT, SOLID, DIMENSION)
        self.texts: List[Dict[str, Any]] = []
        self.solids: List[Dict[str, Any]] = []
        self.dims: List[Dict[str, Any]] = []

        # Geometri panel dihitung dari border ISO 5457 (inner 20,10 - 831,584)
        self.bx1, self.by1, self.bx2, self.by2 = 20.0, 10.0, 831.0, 584.0
        h_in = self.by2 - self.by1
        self.plan_y1 = self.by2 - 4.0                       # atas plan panel
        self.plan_y0 = self.by2 - 4.0 - h_in * self.PLAN_FRAC      # = separator 1
        self.prof_y0p = self.plan_y0 - h_in * self.PROF_FRAC       # = separator 2
        self.bands_y1 = self.prof_y0p - 6.0                        # axis label strip
        self.bands_y0 = self.by1 + 8.0
        # Areal chainage horizontal (sama utk plan/profile/bands)
        self.axis_x0 = 105.0
        self.axis_x1 = 590.0

    # -------------------------------------------------------------------------
    # TRANSFORMASI KOORDINAT
    # -------------------------------------------------------------------------
    def kp_x(self, kp_m: float) -> float:
        """Chainage (m) -> sheet X (mm)."""
        return self.ch_x0 + (float(kp_m) - self.kp_min) * self.h_scale

    def plan_y(self, northing: float) -> float:
        """Northing (m) -> sheet Y panel plan (mm)."""
        return self.plan_y_ref + (float(northing) - self.plan_n_ref) * self.h_scale

    def prof_y(self, elev: float) -> float:
        """Elevasi (m) -> sheet Y panel profile (mm, skala-V berlebih)."""
        return self.prof_y0 + (float(elev) - self.prof_el0) * self.v_scale

    # -------------------------------------------------------------------------
    # MANIFEST ENTITIES (MTEXT, SOLID, DIMENSION) — gaya plan_common
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
        """Catat entitas MTEXT ke manifest (tanpa geometri edge).

        Tinggi karakter di-clamp 0.5 <= size <= 3.0 mm (Company Standard §1).
        att: 4 = Middle-Left (left=True), 5 = Middle-Center, 6 = Middle-Right.
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
        layer: str = "REF-SYM",
    ) -> None:
        """Catat entitas SOLID segitiga ke manifest."""
        self.solids.append({
            "pts": [
                [round(float(p1[0]), 3), round(float(p1[1]), 3)],
                [round(float(p2[0]), 3), round(float(p2[1]), 3)],
                [round(float(p3[0]), 3), round(float(p3[1]), 3)],
            ],
            "layer": layer,
        })

    def solid_dot(
        self, cx: float, cy: float, r: float = 0.6, layer: str = "REF-SYM"
    ) -> None:
        """Lingkaran penuh SOLID via 8-segitiga fan (bend point, weld, dsb.)."""
        n = 8
        pts = [
            (cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n))
            for i in range(n)
        ]
        for i in range(n):
            self.solid_triangle((cx, cy), pts[i], pts[(i + 1) % n], layer=layer)

    # -------------------------------------------------------------------------
    # SIMBOL DASAR
    # -------------------------------------------------------------------------
    def flow_arrow(
        self,
        x: float,
        y: float,
        ang_deg: float,
        size_mm: float = 3.2,
        line_layer: str = "REF-PROC",
    ) -> List[bd.Edge]:
        """Kepala panah aliran di titik (x, y) sheet: SOLID (REF-SYM) + outline.

        Ujung panah menempel pada line proses; outline pendek (<8 mm) dan
        solid memastikan endpoint tidak dangling (validate_cad_rules Check 6).
        """
        rad = math.radians(ang_deg)
        ux, uy = math.cos(rad), math.sin(rad)
        nx, ny = -uy, ux
        length = size_mm * 1.5
        half_w = size_mm * 0.55

        p_tip = (x, y)
        p_left = (x - length * ux + half_w * nx, y - length * uy + half_w * ny)
        p_right = (x - length * ux - half_w * nx, y - length * uy - half_w * ny)

        self.solid_triangle(p_tip, p_left, p_right, layer="REF-SYM")
        edges = [
            line(*p_tip, *p_left),
            line(*p_tip, *p_right),
            line(*p_left, *p_right),
        ]
        if line_layer == "REF-SYM":
            self.sym.extend(edges)
        else:
            self.proc.extend(edges)
        return edges

    def leader_text(
        self,
        tx: float,
        ty: float,
        ex: float,
        ey: float,
        shelf_len: float,
        lines: Sequence[str],
        size: float = 1.8,
        side: int = 1,
    ) -> List[bd.Edge]:
        """Leader dari titik target (tx, ty) naik/turun ke elbow + shelf teks.

        Teks ditulis 2.1 mm di atas / bawah shelf agar bebas tabrakan
        (Company Standard §4). Mengembalikan edge leader (layer REF-SYM).
        """
        elbow = (tx + 8.0 * side, ey)
        shelf_end = (elbow[0] + side * shelf_len, ey)
        edges = [line(tx, ty, *elbow), line(*elbow, *shelf_end)]
        mid_x = (elbow[0] + shelf_end[0]) / 2.0
        n = len(lines)
        for i, s in enumerate(lines):
            dy = (n - 1) * 2.1 - i * 4.2  # baris pertama paling atas
            self.text(s, mid_x, ey + dy, size=size, att=5)
        self.sym.extend(edges)
        return edges

    def bl_arrow(
        self,
        x: float,
        y: float,
        direction: int = 1,
        size_mm: float = 3.5,
        lines: Optional[Sequence[str]] = None,
        label_dx: float = 0.0,
        label_dy: float = 6.5,
        label_left: Optional[bool] = None,
    ) -> List[bd.Edge]:
        """Panah battery limit di (x, y): bar vertikal + sayap; route wajib
        berujung PADA bar agar Check 6 lolos.

        label_left: penempatan teks label relatif thd bar — None = otomatis
        (kiri utk direction<0, kanan utk direction>=0). Ujung BL kanan panel
        plan wajib label_left=True (teks berakhir 2 mm di KIRI bar) agar teks
        tidak menimpa sayap panah terminal / furnitur di kanannya.
        """
        d = 1.0 if direction >= 0 else -1.0
        edges = [
            line(x, y - size_mm, x, y + size_mm),
            line(x, y - size_mm, x + 8.0 * d, y),
            line(x + 8.0 * d, y, x, y + size_mm),
        ]
        self.sym.extend(edges)
        if lines:
            left = (d < 0) if label_left is None else bool(label_left)
            att = 6 if left else 4
            lx = x + (-2.0 if left else 2.0) + label_dx
            n = len(lines)
            for i, s in enumerate(lines):
                dy = (n - 1) * 3.5 - i * 7.0
                self.text(s, lx, y + label_dy + dy, size=1.8, att=att)
        return edges

    def north_arrow(
        self, x_mm: float, y_mm: float, r_mm: float = 8.0
    ) -> List[bd.Edge]:
        """Kompas Utara 2D: lingkaran + jarum berbilah ganda separuh SOLID."""
        edges: List[bd.Edge] = [circle(x_mm, y_mm, r_mm)]
        tip = (x_mm, y_mm + r_mm * 0.95)
        tail = (x_mm, y_mm - r_mm * 0.95)
        left = (x_mm - r_mm * 0.28, y_mm)
        right = (x_mm + r_mm * 0.28, y_mm)
        self.solid_triangle(tip, (x_mm, y_mm), right, layer="REF-SYM")
        self.solid_triangle(tail, (x_mm, y_mm), left, layer="REF-SYM")
        edges.extend([
            line(*tip, *left), line(*left, *tail),
            line(*tail, *right), line(*right, *tip),
            line(*tip, *tail), line(*left, *right),
        ])
        self.text("N", x_mm, tip[1] + 3.0, size=2.5, att=5)
        self.sym.extend(edges)
        return edges

    # -------------------------------------------------------------------------
    # FURNITURE LEMBAR: FRAME, PANEL, TITLE BLOCK
    # -------------------------------------------------------------------------
    def setup_frame(self) -> None:
        """Border ISO 5457 A1 + zona referensi + separator panel 40/30/30."""
        sw, sh = 841.0, 594.0
        self.frame.extend(rect(0.0, 0.0, sw, sh))
        self.frame.extend(rect(self.bx1, self.by1, self.bx2, self.by2))

        # Zona referensi: kolom 1-8 (atas/bawah), baris A-F (kiri/kanan)
        for i in range(8):
            cx = self.bx1 + (self.bx2 - self.bx1) / 8.0 * (i + 0.5)
            t = str(i + 1)
            self.text(t, cx, 589.0, 2.5, att=5, layer="REF-TEXT")
            self.text(t, cx, 5.0, 2.5, att=5, layer="REF-TEXT")
        for j in range(6):
            cy = self.by1 + (self.by2 - self.by1) / 6.0 * (j + 0.5)
            t = chr(65 + j)
            self.text(t, 15.0, cy, 2.5, att=5, layer="REF-TEXT")
            self.text(t, 836.0, cy, 2.5, att=5, layer="REF-TEXT")

        # Separator panel split-window (plan 40% / profile 30% / bands 30%)
        self.frame.append(line(self.bx1, self.plan_y0, self.bx2, self.plan_y0))
        self.frame.append(line(self.bx1, self.prof_y0p, self.bx2, self.prof_y0p))

        # Judul panel
        h_str = f"1:{int(round(1000.0 / self.h_scale))}"
        v_str = f"1:{int(round(1000.0 / self.v_scale))}"
        vex = (1000.0 / self.v_scale) / (1000.0 / self.h_scale)
        self.text(
            f"PLAN VIEW - SCALE H {h_str} @ A1 (ALONG CHAINAGE, N PER ARROW)",
            30.0, self.plan_y1 - 7.0, 2.5, left=True,
        )
        self.text(
            f"PROFILE VIEW - SCALE H {h_str} / V {v_str} (VEX {vex:.0f}:1) @ A1",
            30.0, self.plan_y0 - 7.0, 2.5, left=True,
        )
        self.text("DATA BANDS (PER STASIUN KP)", 30.0, self.bands_y1 + 3.0, 2.2, left=True)

    def setup_title_block(self) -> None:
        """Title block ISO 7200 (x 651-827, y 15-105) + tabel revisi (105-125)."""
        x0, x1 = 651.0, 827.0
        self.title.extend(rect(x0, 15.0, x1, 105.0))
        for y in (26.0, 35.0, 44.0, 53.0, 62.0, 70.0, 81.0, 89.0, 97.0):
            self.title.append(line(x0, y, x1, y))
        self.title.append(line(x0, 20.5, x1, 20.5))

        self.text(self.project, (x0 + x1) / 2.0, 101.0, 2.4, att=5, layer="REF-TITLE")
        self.text(f"COMPANY: {self.company}", (x0 + x1) / 2.0, 93.0, 1.8, att=5, layer="REF-TITLE")
        self.text(f"CONSULTANT: {self.consultant}", (x0 + x1) / 2.0, 85.0, 1.8, att=5, layer="REF-TITLE")
        self.text(self.title_main, (x0 + x1) / 2.0, 75.5, 3.0, att=5, layer="REF-TITLE")
        self.text(self.title_sub, (x0 + x1) / 2.0, 66.0, 2.0, att=5, layer="REF-TITLE")

        h_str = f"1:{int(round(1000.0 / self.h_scale))}"
        v_str = f"1:{int(round(1000.0 / self.v_scale))}"
        fields = [
            (57.5, f"DOC NO: {self.doc_no}"),
            (48.5, f"REV: {self.rev} ({self.rev_desc})"),
            (39.5, f"SCALE: H {h_str} / V {v_str} @ A1"),
            (30.5, f"DATE: {self.date_str}   UNITS: {self.units_str}   SHEET: {self.sheet_str}"),
            (23.2, f"DRAWN: {self.drawn_by}    CHECKED: {self.checked_by}"),
            (17.8, f"APPROVED: {self.approved}"),
        ]
        for y, s in fields:
            self.text(s, x0 + 4.0, y, 2.2, left=True, layer="REF-TITLE")

        # Tabel revisi (y 105-125): REV | DESCRIPTION | DATE
        self.title.extend([
            line(x0, 105.0, x0, 125.0),
            line(x1, 105.0, x1, 125.0),
            line(x0, 125.0, x1, 125.0),
            line(x0, 120.0, x1, 120.0),
            line(700.0, 105.0, 700.0, 125.0),
            line(770.0, 105.0, 770.0, 125.0),
        ])
        self.text("REV", 675.5, 122.4, 2.0, att=5, layer="REF-TITLE")
        self.text("DESCRIPTION", 735.0, 122.4, 2.0, att=5, layer="REF-TITLE")
        self.text("DATE", 798.5, 122.4, 2.0, att=5, layer="REF-TITLE")
        self.text(self.rev, 675.5, 112.5, 1.8, att=5, layer="REF-TITLE")
        self.text(self.rev_desc, 735.0, 112.5, 1.8, att=5, layer="REF-TITLE")
        self.text(self.date_str, 798.5, 112.5, 1.8, att=5, layer="REF-TITLE")

    def setup_reference_docs(self, entries: Sequence[str]) -> None:
        """Kotak REFERENCE DOCUMENTS di atas title block (y 130-180)."""
        x0, x1 = 651.0, 827.0
        y0, y1 = 130.0, 180.0
        self.frame.extend(rect(x0, y0, x1, y1))
        self.frame.append(line(x0, y1 - 8.0, x1, y1 - 8.0))
        self.text("REFERENCE DOCUMENTS", (x0 + x1) / 2.0, y1 - 4.0, 2.2, att=5, layer="REF-TEXT")
        y = y1 - 14.0
        for e in entries:
            self.text(e, x0 + 4.0, y, 1.8, left=True)
            y -= 7.0

    # -------------------------------------------------------------------------
    # PANEL 1: PLAN VIEW (40%)
    # -------------------------------------------------------------------------
    def _route_points(self) -> List[Tuple[float, float]]:
        """Titik-titik sumbu pipa di sheet (plan, straightened along chainage)."""
        return [(self.kp_x(s.kp_m), self.plan_y(s.northing)) for s in self.stations]

    def _offset_polyline(
        self, pts: Sequence[Tuple[float, float]], off: float
    ) -> List[Tuple[float, float]]:
        """Offset polyline sederhana (miter rata-rata normal) untuk batas ROW."""
        n_pts = len(pts)
        normals: List[Tuple[float, float]] = []
        for i in range(n_pts - 1):
            dx = pts[i + 1][0] - pts[i][0]
            dy = pts[i + 1][1] - pts[i][1]
            ln = math.hypot(dx, dy)
            if ln < 1e-9:
                normals.append((0.0, 0.0))
            else:
                normals.append((-dy / ln, dx / ln))
        out: List[Tuple[float, float]] = []
        for i in range(n_pts):
            if i == 0:
                n = normals[0]
            elif i == n_pts - 1:
                n = normals[-1]
            else:
                nx, ny = normals[i - 1][0] + normals[i][0], normals[i - 1][1] + normals[i][1]
                ln = math.hypot(nx, ny)
                n = (nx / ln, ny / ln) if ln > 1e-9 else normals[i]
            out.append((pts[i][0] + n[0] * off, pts[i][1] + n[1] * off))
        return out

    def draw_plan_view(
        self,
        *,
        row_width_m: float = 25.0,
        axis_tick_step_m: float = 200.0,
        arrow_step_m: float = 200.0,
        from_label: Sequence[str] = ("FROM METERING STATION",),
        to_label: Sequence[str] = ("TO SALES GAS DELIVERY POINT",),
        route_label: str = "",
    ) -> None:
        """Plan view: sumbu pipa REF-PROC, ROW REF-FENCE, bend, crossings, BL.

        Plan digambar ter-buang (straightened) sepanjang chainage: sumbu X =
        KP, sumbu Y = deviasi Northing — sumbu pipa tetap per stasiun KP dan
        sejajar penuh dengan panel profile & bands (praktik alignment sheet).
        """
        pts = self._route_points()

        # Sumbu pipa (major process line — selalu utuh, tersambung di tiap vertex)
        for i in range(len(pts) - 1):
            self.proc.append(line(*pts[i], *pts[i + 1]))

        # Batas ROW kiri/kanan (dashed REF-FENCE), offset tegak lurus rute
        row_mm = row_width_m * self.h_scale
        self._row_mm = row_mm   # dipakai _draw_plan_crossing utk leader label
        for sign in (1.0, -1.0):
            op = self._offset_polyline(pts, sign * row_mm)
            for i in range(len(op) - 1):
                self.fence.extend(dashed(*op[i], *op[i + 1], dash=4.0, gap=1.6))
        self.text(
            f"ROW {int(row_width_m * 2)} m ({int(row_width_m)} m L/R)",
            (self.axis_x0 + 30.0), self.plan_y0 + 22.0, 1.8, att=5,
        )

        # Axis chainage plan + ticks + label KP
        axis_y = self.plan_y0 + 48.0
        self.grid.append(line(self.axis_x0, axis_y, self.axis_x1, axis_y))
        step = axis_tick_step_m
        kp = math.ceil(self.kp_min / step) * step
        while kp <= self.kp_max + 1e-6:
            x = self.kp_x(kp)
            self.grid.append(line(x, axis_y, x, axis_y - 4.0))
            self.text(fmt_kp(kp), x, axis_y - 6.5, 1.8, att=5)
            kp += step

        # Panah aliran sepanjang rute (major line proses wajib panah);
        # ujung terakhir tidak menempel bar battery limit.
        kp = self.kp_min + arrow_step_m / 2.0
        while kp <= self.kp_max - arrow_step_m * 0.25:
            x = self.kp_x(kp)
            y = self.plan_y(self._northing_at(kp))
            self.flow_arrow(x, y, heading_at(self.stations, kp))
            kp += arrow_step_m

        # Battery limit di kedua ujung (bar tepat pada endpoint rute).
        # Ujung kanan: label di KIRI bar, DI BAWAH dashed ROW bawah
        # (label_dy negatif) agar bebas dari sayap panah terminal, dashed
        # ROW, dan furnitur LEGEND di tepi kanan panel (temuan QA #2).
        self.bl_arrow(pts[0][0], pts[0][1], direction=-1, lines=list(from_label), label_dy=7.0)
        self.bl_arrow(pts[-1][0], pts[-1][1], direction=1, lines=list(to_label),
                      label_dy=-13.5, label_left=True)

        # Label rute
        if route_label:
            mid_kp = (self.kp_min + self.kp_max) / 2.0
            self.text(route_label, self.kp_x(mid_kp), self.plan_y1 - 50.0, 2.0, att=5)

        # Tikungan cold/hot bend: dot + leader + label 2 baris
        for b in self.bends:
            bx = self.kp_x(b.kp_m)
            by = self.plan_y(self._northing_at(b.kp_m))
            above = by >= self.plan_y(self.plan_n_ref)
            if above:
                self.solid_dot(bx, by, r=1.0)
                self.leader_text(bx, by, bx, by + 16.0, 22.0,
                                 [b.label, f"KP {fmt_kp(b.kp_m)}"], side=1)
            else:
                self.solid_dot(bx, by, r=1.0)
                self.leader_text(bx, by, bx, by - 16.0, 22.0,
                                 [b.label, f"KP {fmt_kp(b.kp_m)}"], side=1)

        # Penyeberangan jalan / sungai
        for c in self.crossings:
            self._draw_plan_crossing(c)

        # North arrow kanan-atas panel
        self.north_arrow(self.axis_x1 + 205.0, self.plan_y1 - 20.0, r_mm=8.0)

    def _northing_at(self, kp_m: float) -> float:
        """Interpolasi linier Northing pada chainage kp_m."""
        sts = self.stations
        if kp_m <= sts[0].kp_m:
            return sts[0].northing
        if kp_m >= sts[-1].kp_m:
            return sts[-1].northing
        for i in range(len(sts) - 1):
            if sts[i].kp_m <= kp_m <= sts[i + 1].kp_m:
                t = (kp_m - sts[i].kp_m) / (sts[i + 1].kp_m - sts[i].kp_m)
                return sts[i].northing + t * (sts[i + 1].northing - sts[i].northing)
        return sts[-1].northing

    def _draw_plan_crossing(self, c: Crossing) -> None:
        """Simbol penyeberangan plan: band jalan (rect) / sungai (dashed).

        Leader label dirutekan agar TIDAK menembus dashed ROW maupun garis
        band penyeberangan (Company Standard §4 + temuan QA visual):
          - ROAD : leader mulai di tepi band DI ATAS batas ROW upper,
          - RIVER: leader mulai tepat pada ujung ATAS dash tepi band.
        """
        cx = self.kp_x(c.kp_m)
        cy = self.plan_y(self._northing_at(c.kp_m))
        half_mm = max(c.width_m * self.h_scale / 2.0, 1.0)
        span = 25.0
        row_mm = float(getattr(self, "_row_mm", 25.0 * self.h_scale))
        if c.kind == "ROAD":
            # Jalan melintang (band vertikal) + arsiran tepi
            self.road.extend(rect(cx - half_mm, cy - span, cx + half_mm, cy + span))
            self.road.extend(dashed(cx, cy - span, cx, cy + span, dash=3.0, gap=2.0))
            label_lines = [f"{c.name}" if c.name else "ROAD CROSSING",
                           f"{c.method} AT KP {fmt_kp(c.kp_m)}"]
            self.leader_text(cx + half_mm, cy + row_mm + 3.0,
                             cx + half_mm + 10.0, cy + row_mm + 10.5,
                             24.0, label_lines, side=1)
        else:  # RIVER
            self.road.extend(dashed(cx - half_mm, cy - span, cx - half_mm, cy + span, 3.0, 2.0))
            self.road.extend(dashed(cx + half_mm, cy - span, cx + half_mm, cy + span, 3.0, 2.0))
            self.road.extend(dashed(cx - half_mm * 0.33, cy - span, cx - half_mm * 0.33, cy + span, 2.0, 2.5))
            self.road.extend(dashed(cx + half_mm * 0.33, cy - span, cx + half_mm * 0.33, cy + span, 2.0, 2.5))
            label_lines = [f"{c.name}" if c.name else "RIVER CROSSING",
                           f"{c.method} AT KP {fmt_kp(c.kp_m)}"]
            self.leader_text(cx + half_mm, cy + span,
                             cx + half_mm + 10.0, cy + span + 4.0,
                             26.0, label_lines, side=1)

    def draw_plan_legend(self, entries: Optional[Sequence[Tuple[str, str]]] = None) -> None:
        """Kotak LEGEND di sisi kanan panel plan (sample simbol + label)."""
        x0, x1 = self.axis_x1 + 20.0, 820.0
        y0, y1 = self.plan_y0 + 8.0, self.plan_y1 - 35.0
        self.frame.extend(rect(x0, y0, x1, y1))
        self.frame.append(line(x0, y1 - 9.0, x1, y1 - 9.0))
        self.text("LEGEND", (x0 + x1) / 2.0, y1 - 4.5, 2.5, att=5)

        if entries is None:
            entries = [
                ("proc", "PIPELINE CENTERLINE (PLAN)"),
                ("row", "ROW LIMIT - RIGHT OF WAY"),
                ("cold", "COLD BEND (FIELD BEND)"),
                ("hot", "HOT BEND (INDUCTION BEND)"),
                ("road", "ROAD CROSSING (OPEN CUT)"),
                ("river", "RIVER CROSSING (HDD METHOD)"),
                ("kp", "KP STATION / CHAINAGE"),
                ("bl", "BATTERY LIMIT"),
                ("flow", "FLOW DIRECTION (GAS)"),
                ("ngl", "NGL - GROUND SURFACE (PROFILE)"),
                ("bop", "PIPE BOP - BOTTOM OF PIPE (PROFILE)"),
            ]
        sample_x0, sample_x1 = x0 + 6.0, x0 + 38.0
        tx = x0 + 44.0
        pitch = (y1 - 9.0 - y0 - 6.0) / max(len(entries), 1)
        y = y1 - 9.0 - pitch / 2.0
        for kind, label in entries:
            if kind == "proc":
                self.proc.append(line(sample_x0, y, sample_x1 - 4.0, y))
                # dot pengikat ujung kiri (mencegah dangling endpoint Check 6)
                self.solid_dot(sample_x0, y, r=0.6)
                self.flow_arrow(sample_x1 - 4.0, y, 0.0, size_mm=2.6, line_layer="REF-SYM")
            elif kind == "row":
                self.fence.extend(dashed(sample_x0, y, sample_x1, y, 4.0, 1.6))
            elif kind in ("cold", "hot"):
                self.solid_dot((sample_x0 + sample_x1) / 2.0, y, r=1.1)
                self.sym.append(line(sample_x0, y, (sample_x0 + sample_x1) / 2.0 - 2.0, y))
                self.sym.append(line((sample_x0 + sample_x1) / 2.0 + 2.0, y, sample_x1, y))
                if kind == "hot":
                    self.sym.append(circle((sample_x0 + sample_x1) / 2.0, y, 2.4))
            elif kind == "road":
                self.road.extend(rect((sample_x0 + sample_x1) / 2.0 - 1.2, y - 4.5,
                                      (sample_x0 + sample_x1) / 2.0 + 1.2, y + 4.5))
            elif kind == "river":
                self.road.extend(dashed((sample_x0 + sample_x1) / 2.0 - 3.0, y - 4.5,
                                        (sample_x0 + sample_x1) / 2.0 - 3.0, y + 4.5, 2.0, 1.6))
                self.road.extend(dashed((sample_x0 + sample_x1) / 2.0 + 3.0, y - 4.5,
                                        (sample_x0 + sample_x1) / 2.0 + 3.0, y + 4.5, 2.0, 1.6))
            elif kind == "kp":
                self.grid.append(line((sample_x0 + sample_x1) / 2.0, y - 3.5,
                                      (sample_x0 + sample_x1) / 2.0, y + 3.5))
            elif kind == "bl":
                edges = [
                    line(sample_x1 - 6.0, y - 3.0, sample_x1 - 6.0, y + 3.0),
                    line(sample_x1 - 6.0, y - 3.0, sample_x1, y),
                    line(sample_x1, y, sample_x1 - 6.0, y + 3.0),
                ]
                self.sym.extend(edges)
            elif kind == "flow":
                self.flow_arrow((sample_x0 + sample_x1) / 2.0, y, 0.0, size_mm=2.8,
                                line_layer="REF-SYM")
            elif kind == "ngl":
                self.proc.append(line(sample_x0, y, sample_x1 - 8.0, y + 1.2))
                self.proc.append(line(sample_x1 - 8.0, y + 1.2, sample_x1, y - 0.6))
                self.solid_dot(sample_x0, y, r=0.6)
                self.solid_dot(sample_x1, y - 0.6, r=0.6)
            elif kind == "bop":
                self.proc.append(line(sample_x0, y - 1.2, sample_x1 - 8.0, y - 2.0))
                self.proc.append(line(sample_x1 - 8.0, y - 2.0, sample_x1, y - 0.4))
                self.solid_dot(sample_x0, y - 1.2, r=0.6)
                self.solid_dot(sample_x1, y - 0.4, r=0.6)
            self.text(label, tx, y, 1.8, left=True)
            y -= pitch

    # -------------------------------------------------------------------------
    # PANEL 2: PROFILE VIEW (30%)
    # -------------------------------------------------------------------------
    def draw_profile_view(
        self,
        *,
        elev_step: float = 5.0,
        axis_tick_step_m: float = 200.0,
        arrow_step_m: float = 700.0,
        arrow_gap_mm: float = 3.0,
        annotations: Optional[Sequence[Dict[str, Any]]] = None,
    ) -> None:
        """Profile view: kontur NGL + BOP REF-PROC, grid elevasi & KP REF-GRID.

        Skala vertikal berlebih (v_scale >> h_scale). Ujung NGL/BOP diikat
        end-link vertikal REF-PROC agar tidak dangling (Check 6).
        Panah aliran di-OFFSET `arrow_gap_mm` DI ATAS line BOP — pada panel
        profile panah tidak digambar menempel garis agar tidak terbelah oleh
        line pipa (temuan QA #5); arah panah tetap sejajar rute.
        """
        x0, x1 = self.kp_x(self.kp_min), self.kp_x(self.kp_max)

        # Grid elevasi (REF-GRID) + label kiri
        el = math.ceil(self.prof_el0 / elev_step) * elev_step
        while el <= self.prof_el1 + 1e-6:
            y = self.prof_y(el)
            self.grid.append(line(self.axis_x0, y, self.axis_x1, y))
            self.text(f"EL +{el:.0f}", self.axis_x0 - 2.0, y, 1.8, att=6)
            el += elev_step
        # Batas sisi kiri/kanan panel profile (REF-GRID)
        self.grid.append(line(self.axis_x0, self.prof_y0, self.axis_x0, self.prof_y0p + 8.0))
        self.grid.append(line(self.axis_x1, self.prof_y0, self.axis_x1, self.prof_y0p + 8.0))

        # Garis station vertikal (REF-GRID) + axis KP bawah
        axis_y = self.prof_y0p + 6.0
        step = axis_tick_step_m
        kp = math.ceil(self.kp_min / step) * step
        while kp <= self.kp_max + 1e-6:
            x = self.kp_x(kp)
            self.grid.append(line(x, self.prof_y0, x, self.prof_y(self.prof_el1)))
            self.grid.append(line(x, axis_y + 4.0, x, axis_y))
            self.text(fmt_kp(kp), x, axis_y + 5.5, 1.8, att=5)
            kp += step
        self.grid.append(line(self.axis_x0, axis_y, self.axis_x1, axis_y))

        # Kontur tanah asli NGL + elevasi dasar pipa BOP (REF-PROC)
        ngl_pts = [(self.kp_x(s.kp_m), self.prof_y(s.ground_elev)) for s in self.stations]
        bop_pts = [(self.kp_x(s.kp_m), self.prof_y(s.pipe_elev)) for s in self.stations]
        for poly in (ngl_pts, bop_pts):
            for i in range(len(poly) - 1):
                self.proc.append(line(*poly[i], *poly[i + 1]))
        # End-link pengikat ujung NGL-BOP (mencegah dangling endpoint)
        self.proc.append(line(ngl_pts[0][0], ngl_pts[0][1], bop_pts[0][0], bop_pts[0][1]))
        self.proc.append(line(ngl_pts[-1][0], ngl_pts[-1][1], bop_pts[-1][0], bop_pts[-1][1]))

        # Label garis
        mid_kp = self.kp_min + 0.08 * (self.kp_max - self.kp_min)
        mx = self.kp_x(mid_kp)
        self.text("NGL", mx, self.prof_y(self._elev_at(mid_kp)) + 7.0, 1.8, att=5)
        self.text("BOP", mx, self.prof_y(self._pipe_elev_at(mid_kp)) - 6.0, 1.8, att=5)

        # Panah aliran gas: DI ATAS line BOP (offset arrow_gap_mm) agar
        # outline/solid panah tidak terbelah garis pipa (temuan QA #5).
        kp = self.kp_min + arrow_step_m / 2.0
        while kp <= self.kp_max:
            self.flow_arrow(self.kp_x(kp),
                            self.prof_y(self._pipe_elev_at(kp)) + arrow_gap_mm,
                            0.0)
            kp += arrow_step_m

        # Anotasi galian terbuka vs HDD (leader REF-SYM ke line BOP/NGL)
        if annotations is None:
            annotations = self._default_profile_annotations()
        for ann in annotations:
            kpc = float(ann["kp"])
            target = str(ann.get("target", "BOP")).upper()
            ty = self.prof_y(self._pipe_elev_at(kpc) if target == "BOP" else self._elev_at(kpc))
            tx = self.kp_x(kpc)
            label_lines = list(ann["lines"])
            y_text = float(ann.get("y_text", self.prof_y0 + 12.0))
            self.leader_text(tx, ty, tx + float(ann.get("dx", 8.0)), y_text,
                             float(ann.get("shelf", 26.0)), label_lines,
                             side=1 if float(ann.get("dx", 8.0)) >= 0 else -1)

    def _default_profile_annotations(self) -> List[Dict[str, Any]]:
        """Anotasi default: HDD utk RIVER, OPEN CUT utk ROAD (dari crossings)."""
        anns: List[Dict[str, Any]] = []
        for c in self.crossings:
            if c.kind == "RIVER":
                anns.append({
                    "kp": c.kp_m, "target": "NGL", "dx": 14.0,
                    "y_text": self.prof_y0 + 116.0, "shelf": 30.0,
                    "lines": [f"{c.name} - {c.method}" if c.name else f"RIVER - {c.method}",
                              f"KP {fmt_kp(max(c.kp_m - 100.0, self.kp_min))} - {fmt_kp(min(c.kp_m + 100.0, self.kp_max))}"],
                })
            else:
                anns.append({
                    "kp": c.kp_m, "target": "BOP", "dx": 12.0,
                    "y_text": self.prof_y0 + 10.0, "shelf": 30.0,
                    "lines": [f"{c.name} - {c.method}" if c.name else f"ROAD - {c.method}",
                              f"DOC {self._doc_at(c.kp_m):.1f} m AT KP {fmt_kp(c.kp_m)}"],
                })
        return anns

    def _elev_at(self, kp_m: float) -> float:
        sts = self.stations
        if kp_m <= sts[0].kp_m:
            return sts[0].ground_elev
        if kp_m >= sts[-1].kp_m:
            return sts[-1].ground_elev
        for i in range(len(sts) - 1):
            if sts[i].kp_m <= kp_m <= sts[i + 1].kp_m:
                t = (kp_m - sts[i].kp_m) / (sts[i + 1].kp_m - sts[i].kp_m)
                return sts[i].ground_elev + t * (sts[i + 1].ground_elev - sts[i].ground_elev)
        return sts[-1].ground_elev

    def _pipe_elev_at(self, kp_m: float) -> float:
        sts = self.stations
        if kp_m <= sts[0].kp_m:
            return sts[0].pipe_elev
        if kp_m >= sts[-1].kp_m:
            return sts[-1].pipe_elev
        for i in range(len(sts) - 1):
            if sts[i].kp_m <= kp_m <= sts[i + 1].kp_m:
                t = (kp_m - sts[i].kp_m) / (sts[i + 1].kp_m - sts[i].kp_m)
                a = sts[i].pipe_elev
                b = sts[i + 1].pipe_elev
                return a + t * (b - a)
        return sts[-1].pipe_elev

    def _doc_at(self, kp_m: float) -> float:
        for s in self.stations:
            if abs(s.kp_m - kp_m) < 1e-6:
                return s.depth_cover
        return 1.2

    def draw_profile_notes(self, notes: Sequence[str], size: float = 1.8) -> None:
        """Kotak NOTES di sisi kanan panel profile."""
        x0, x1 = self.axis_x1 + 20.0, 820.0
        y0, y1 = self.prof_y0p + 4.0, self.plan_y0 - 4.0
        self.frame.extend(rect(x0, y0, x1, y1))
        self.frame.append(line(x0, y1 - 9.0, x1, y1 - 9.0))
        self.text("NOTES", (x0 + x1) / 2.0, y1 - 4.5, 2.5, att=5)
        y = y1 - 16.0
        pitch = (y1 - 16.0 - y0 - 4.0) / max(len(notes), 1)
        for s in notes:
            self.text(s, x0 + 4.0, y, size, left=True)
            y -= pitch

    # -------------------------------------------------------------------------
    # PANEL 3: DATA BANDS (30%)
    # -------------------------------------------------------------------------
    def band_specs(self) -> List[Tuple[Tuple[str, ...], Callable[[SurveyStation], str]]]:
        """8 band data standar (Bagian VI doc 08), urut atas -> bawah."""
        return [
            (("GROUND ELEV (m)",), lambda s: f"{s.ground_elev:.1f}"),
            (("PIPE ELEV BOP (m)",), lambda s: f"{s.pipe_elev:.1f}"),
            (("DEPTH OF COVER (m)",), lambda s: f"{s.depth_cover:.2f}"),
            (("CHAINAGE (KP)",), lambda s: fmt_kp(s.kp_m)),
            (("WALL THK / GRADE", "API 5L"), lambda s: f"{s.wall_thk:.1f}/{s.grade}"),
            (("CLASS LOCATION", "ASME B31.8"), lambda s: s.class_loc),
            (("COATING",), lambda s: s.coating),
            (("SOIL TYPE (USCS)",), lambda s: s.soil),
        ]

    def draw_data_bands(
        self,
        *,
        x0: float = 25.0,
        x1: float = 645.0,
        label_div: float = 105.0,
    ) -> None:
        """Data bands berjejer vertikal per stasiun KP (grid REF-GRID tipis).

        Semua garis band di REF-GRID (lineweight 0.09) sehingga nilai teks
        di dalam sel bebas aturan tabrakan teks-vs-garis proses.

        Penyejajaran (temuan QA #3): SELURUH band memakai grid KP yang sama
        — nilai tiap baris diletakkan tepat pada kp_x stasiun (att=5), jadi
        baris GROUND/PIPE ELEV segaris persis dengan baris CHAINAGE. Batas
        kanan area band dijaga >= 40 mm setelah kolom stasiun terakhir agar
        kolom terakhir tidak tergencet tepi kanan.

        Garis stasiun vertikal di-BREAK 3 mm di sekeliling teks nilai pada
        setiap baris (Company Standard: teks tidak boleh tertembus garis —
        temuan QA #4, sel COATING '3LPE+CONC' tampak terpotong).
        """
        specs = self.band_specs()
        y0, y1 = self.bands_y0, self.bands_y1
        n = len(specs)
        band_h = (y1 - y0) / n
        x1 = max(float(x1), self.kp_x(self.kp_max) + 40.0)

        # Batas band horizontal + kolom label + batas kanan
        for i in range(n + 1):
            self.grid.append(line(x0, y0 + i * band_h, x1, y0 + i * band_h))
        self.grid.append(line(label_div, y0, label_div, y1))
        self.grid.append(line(x1, y0, x1, y1))

        # Label band (kolom kiri) + nilai per stasiun (center sel, PADA grid
        # KP). Band pertama (GROUND ELEV) di ATAS: sumbu Y DXF naik ke atas.
        val_half_h = 1.8 / 2.0 + 0.7          # break vline: teks 1.8 + bebas 1.4 (gap 3 mm)
        breaks_by_station: Dict[int, List[float]] = {}
        for i, (label_lines, value_fn) in enumerate(specs):
            y_mid = y1 - (i + 0.5) * band_h
            if len(label_lines) == 1:
                self.text(label_lines[0], x0 + 5.0, y_mid, 1.7, left=True)
            else:
                offs = (len(label_lines) - 1) * 2.2
                for j, ln in enumerate(label_lines):
                    self.text(ln, x0 + 5.0, y_mid + offs - j * 4.4, 1.7, left=True)
            for k, s in enumerate(self.stations):
                self.text(value_fn(s), self.kp_x(s.kp_m), y_mid, 1.8, att=5)
                breaks_by_station.setdefault(k, [])
                breaks_by_station[k].append(y_mid - val_half_h)
                breaks_by_station[k].append(y_mid + val_half_h)

        # Garis stasiun vertikal menembus seluruh band, di-BREAK di sekitar
        # teks nilai tiap baris (REF-GRID minor — aturan break perusahaan).
        # breaks_by_station memuat PASANGAN (bawah-gap, atas-gap) per baris.
        for k, s in enumerate(self.stations):
            x = self.kp_x(s.kp_m)
            brs = sorted(breaks_by_station.get(k, []))
            ya = y0
            for i in range(0, len(brs) - 1, 2):
                yb_lo, yb_hi = brs[i], brs[i + 1]
                if yb_lo - ya > 0.5:
                    self.grid.append(line(x, ya, x, yb_lo))
                ya = yb_hi
            if y1 - ya > 0.5:
                self.grid.append(line(x, ya, x, y1))

    # -------------------------------------------------------------------------
    # EXPORT & INTEGRASI POST-PROCESSOR
    # -------------------------------------------------------------------------
    def get_layers(self) -> Dict[str, bd.Compound]:
        """Dict bd.Compound per layer (layer kosong dilewati)."""
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
        """Simpan manifest texts/solids/dims ke .texts.json."""
        manifest = {
            "texts": self.texts,
            "dims": self.dims,
            "solids": self.solids,
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    def export_manifest(self, json_path: Union[str, Path]) -> Dict[str, bd.Compound]:
        """Simpan .texts.json dan kembalikan dict layer siap @dxf."""
        path = Path(json_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.save_manifest(path)
        return self.get_layers()
