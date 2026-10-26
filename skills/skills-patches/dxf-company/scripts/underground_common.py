"""Reusable Underground Piping, Trench Cross-Section, CP & Cased Crossing Library.

Versi 1.0.0 (GPF-00-PM-PLN-0008 Bagian V.1 — Perpipaan Bawah Tanah).

Standar acuan:
  - ASME B31.8 (Gas Transmission and Distribution Piping Systems) — cover depth
    minimum 1.0-1.2 m; 1.5 m pada penyeberangan jalan.
  - API RP 1102 (Steel Pipelines Crossing Railroads and Highways) — cased road
    crossing: casing spacers plastik, end seals, vent pipe.
  - NACE SP0169 (Control of External Corrosion) — Monolithic Isolation Joint
    (MIJ) & CP test post.
  - 95% Standard Proctor backfill compaction; sand bedding 150 mm; sand padding;
    warning tape 300-500 mm di bawah tanah.
  - ISO 5457:1999 / ISO 7200:2004 (lembar A3 & title block).
  - Company CAD Standard (skill company-cad-standard): teks MTEXT Arial via
    manifest TEXTS/DIMS/SOLIDS + cad/apply_text.py.

Layer khusus modul ini:
  REF-PROC-UG  garis pipa bawah tanah, PUTUS-PUTUS (dash 4.0 / gap 1.6),
               lineweight 0.35 mm (35) — distempel via stamp_layer_pens()
               karena apply_text.py hanya memasang pens layer standar.

Wajib di-import oleh semua script detail underground agar simbol soil-to-air
interface, trench cross-section, MIJ, CP test post, dan cased crossing 100%
konsisten.
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
    dashed_brk,
    hatch45,
    line,
    rect,
)

# Konstanta gaya bawah tanah
UG_DASH = 4.0          # panjang dash REF-PROC-UG (mm kertas)
UG_GAP = 1.6           # jarak antar dash (mm kertas)
UG_PEN = 35            # lineweight DXF REF-PROC-UG (0.35 mm x 100)
UG_BREAK_HALF = 1.5    # setengah celah break 3 mm pada persilangan

STANDAR_PENS = {
    "REF-PROC": 50, "REF-EQUIP": 35, "REF-FRAME": 35, "REF-SYM": 25,
    "REF-TITLE": 25, "REF-TEXT": 18, "REF-ROAD": 18, "REF-SIG": 13,
    "REF-HATCH": 13, "REF-DIM": 9,
}


def stamp_layer_pens(dxf_path: Path | str, extra_pens: Dict[str, int]) -> int:
    """Pasang lineweight layer TAMBAHAN (mis. REF-PROC-UG = 35) pada DXF hasil build.

    apply_text.py hanya memasang pens untuk layer standar perusahaan; layer baru
    seperti REF-PROC-UG (0.35 mm, Bagian V.1 dokumen 08) distempel di sini
    sesaat SETELAH build dan SEBELUM apply_text.py (aman: apply_text tidak
    menimpa lineweight layer di luar PENS-nya).
    """
    import ezdxf

    doc = ezdxf.readfile(str(dxf_path))
    applied = 0
    for layer in doc.layers:
        name = layer.dxf.name
        if name in extra_pens:
            layer.dxf.lineweight = int(extra_pens[name])
            applied += 1
    doc.saveas(str(dxf_path))
    return applied


def hatch_poly(pts: Sequence[Tuple[float, float]], spacing: float = 4.0) -> List[bd.Edge]:
    """Arsiran 45 derajat ter-clip terhadap poligon tertutup (convex).

    Digunakan untuk zona backfill trapesium pada trench cross-section.
    """
    out: List[bd.Edge] = []
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    n = len(pts)
    c = math.floor((min(xs) - max(ys)) / spacing) * spacing
    c_max = max(xs) - min(ys)
    while c <= c_max:
        hits: List[float] = []
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            den = (x2 - x1) - (y2 - y1)
            if abs(den) < 1e-9:
                continue
            t = (c - x1 + y1) / den
            if -1e-9 <= t <= 1.0 + 1e-9:
                hits.append(y1 + t * (y2 - y1))
        if len(hits) >= 2:
            ya, yb = min(hits), max(hits)
            if yb - ya > 0.2:
                out.append(line(c + ya, ya, c + yb, yb))
        c += spacing
    return out


# =============================================================================
# KELAS UTAMA KONTEKS UNDERGROUND (UndergroundContext)
# =============================================================================
class UndergroundContext:
    """Konteks pembuat gambar perpipaan bawah tanah (sheet A3 420x297 mm).

    Layer:
      frame    REF-FRAME     border, grid, kotak tabel
      title    REF-TITLE     title block + rev table (ISO 7200)
      road     REF-ROAD      jalan pada plan mini
      equip    REF-EQUIP     struktur galian, bedding, padding, pipa section
      proc     REF-PROC      line proses DI ATAS tanah (solid 0.50)
      proc_ug  REF-PROC-UG   line proses BAWAH tanah (dashed 0.35)
      sym      REF-SYM       simbol MIJ, CP post, casing, flange, panah plan
      sig      REF-SIG       sinyal (cadangan)
      hatch    REF-HATCH     arsiran tanah/backfill
      texts/dims/solids      manifest post-process apply_text.py
    """

    def __init__(self) -> None:
        self.frame: List[bd.Edge] = []
        self.title: List[bd.Edge] = []
        self.road: List[bd.Edge] = []
        self.equip: List[bd.Edge] = []
        self.proc: List[bd.Edge] = []
        self.proc_ug: List[bd.Edge] = []
        self.sym: List[bd.Edge] = []
        self.sig: List[bd.Edge] = []
        self.hatch: List[bd.Edge] = []

        self.texts: List[Dict[str, Any]] = []
        self.dims: List[Dict[str, Any]] = []
        self.solids: List[Dict[str, Any]] = []

    # -------------------------------------------------------------------------
    # MANIFEST (MTEXT / DIMENSION / SOLID) — pola pid_common & plan_common
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
        """Catat MTEXT Arial (tinggi 0.5..3.0 mm; att=4 bila left, att=5 bila tengah)."""
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
        """Catat DIMENSION (dimstyle GPF-ISO via apply_text.py; angka mm bulat)."""
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
    # PANAH ALIRAN (wajib pada setiap line proses, atas maupun bawah tanah)
    # -------------------------------------------------------------------------
    def flow_arrow_h(
        self, x: float, y: float, direction: int = 1, size: float = 3.0,
        layer: str = "REF-PROC",
    ) -> None:
        if direction >= 0:
            self.solid_triangle(
                (x, y), (x - size * 1.5, y + size * 0.5), (x - size * 1.5, y - size * 0.5),
                layer=layer,
            )
        else:
            self.solid_triangle(
                (x, y), (x + size * 1.5, y + size * 0.5), (x + size * 1.5, y - size * 0.5),
                layer=layer,
            )

    def flow_arrow_v(
        self, x: float, y: float, direction: int = 1, size: float = 3.0,
        layer: str = "REF-PROC",
    ) -> None:
        if direction >= 0:
            self.solid_triangle(
                (x, y), (x - size * 0.5, y - size * 1.5), (x + size * 0.5, y - size * 1.5),
                layer=layer,
            )
        else:
            self.solid_triangle(
                (x, y), (x - size * 0.5, y + size * 1.5), (x + size * 0.5, y + size * 1.5),
                layer=layer,
            )

    # -------------------------------------------------------------------------
    # LINE PROSES BAWAH TANAH — REF-PROC-UG (DASHED 0.35 mm)
    # -------------------------------------------------------------------------
    def ug_pipe_run_h(
        self,
        y: float,
        x0: float,
        x1: float,
        breaks: Optional[List[Tuple[float, float]]] = None,
    ) -> List[bd.Edge]:
        """Pipa bawah tanah horizontal, dashed REF-PROC-UG.

        breaks: daftar (center_x, half_width_mm) — celah break 3 mm standar pada
        persilangan/simbol (garis minor di-break, gap terpusat).
        """
        brk_pts: List[float] = []
        for c, hw in (breaks or []):
            brk_pts.extend((c - hw, c + hw))
        edges = dashed_brk(x0, y, x1, y, brk=brk_pts, dash=UG_DASH, gap=UG_GAP, half=0.0)
        self.proc_ug.extend(edges)
        return edges

    def ug_pipe_run_v(
        self,
        x: float,
        y0: float,
        y1: float,
        breaks: Optional[List[Tuple[float, float]]] = None,
    ) -> List[bd.Edge]:
        """Pipa bawah tanah vertikal, dashed REF-PROC-UG (breaks=(center_y, half))."""
        brk_pts = []
        for c, hw in (breaks or []):
            brk_pts.extend((c - hw, c + hw))
        edges = dashed_brk(x, y0, x, y1, brk=brk_pts, dash=UG_DASH, gap=UG_GAP, half=0.0)
        self.proc_ug.extend(edges)
        return edges

    def ug_segment(
        self, p1: Tuple[float, float], p2: Tuple[float, float]
    ) -> List[bd.Edge]:
        """Segmen dashed REF-PROC-UG bebas antara dua titik (untuk legenda/rute)."""
        edges = dashed(p1[0], p1[1], p2[0], p2[1], dash=UG_DASH, gap=UG_GAP)
        self.proc_ug.extend(edges)
        return edges

    # -------------------------------------------------------------------------
    # SOIL-TO-AIR INTERFACE — PUDDLE FLANGE / WATER STOP (Bagian V.1.1)
    # -------------------------------------------------------------------------
    def puddle_flange_plan(
        self, cx: float, cy: float, r_out: float = 5.0, r_in: float = 3.0
    ) -> List[bd.Edge]:
        """Simbol tampak atas: cincin ganda (flensa penahan rembesan) pada titik
        pipa keluar/masuk tanah. Ujung pipa proses menyambung ke keliling r_in.
        """
        edges = [circle(cx, cy, r_out), circle(cx, cy, r_in)]
        self.sym.extend(edges)
        return edges

    def puddle_flange_section(
        self, cx: float, cy: float, pipe_r: float = 4.2
    ) -> List[bd.Edge]:
        """Simbol potong: pelat vertikal ganda melintang pipa + kerah (collar)
        segitiga atas & bawah — puddle flange / water stop.
        """
        edges = [
            line(cx - 0.9, cy - pipe_r - 2.6, cx - 0.9, cy + pipe_r + 2.6),
            line(cx + 0.9, cy - pipe_r - 2.6, cx + 0.9, cy + pipe_r + 2.6),
            line(cx - 0.9, cy + pipe_r + 2.6, cx + 0.9, cy + pipe_r + 2.6),
            line(cx - 0.9, cy - pipe_r - 2.6, cx + 0.9, cy - pipe_r - 2.6),
            # kerah beton kiri-kanan
            line(cx - 0.9, cy + pipe_r + 2.6, cx - 3.4, cy + pipe_r + 5.0),
            line(cx + 0.9, cy + pipe_r + 2.6, cx + 3.4, cy + pipe_r + 5.0),
            line(cx - 0.9, cy - pipe_r - 2.6, cx - 3.4, cy - pipe_r - 5.0),
            line(cx + 0.9, cy - pipe_r - 2.6, cx + 3.4, cy - pipe_r - 5.0),
        ]
        self.sym.extend(edges)
        return edges

    # -------------------------------------------------------------------------
    # MONOLITHIC ISOLATION JOINT — MIJ (NACE SP0169)
    # -------------------------------------------------------------------------
    def mij_plan(
        self, cx: float, cy: float, w: float = 3.0, h: float = 7.0,
        tag: str = "", tag_dy: float = -7.0,
    ) -> List[bd.Edge]:
        """Simbol tampak atas MIJ: blok solid melintang pipa (sambungan isolasi
        tanpa flensa). Tag tercatat di bawah simbol (equipment 2.5 mm).
        """
        edges = rect(cx - w / 2.0, cy - h / 2.0, cx + w / 2.0, cy + h / 2.0)
        self.sym.extend(edges)
        self.solid_quad(
            (cx - w / 2.0 + 0.5, cy - h / 2.0 + 0.5),
            (cx + w / 2.0 - 0.5, cy - h / 2.0 + 0.5),
            (cx + w / 2.0 - 0.5, cy + h / 2.0 - 0.5),
            (cx - w / 2.0 + 0.5, cy + h / 2.0 - 0.5),
            layer="REF-SYM",
        )
        if tag:
            self.text(tag, cx, cy + tag_dy, size=2.5)
        return edges

    def mij_section(
        self, cx: float, cy: float, pipe_r: float = 4.2, w: float = 2.6
    ) -> List[bd.Edge]:
        """Simbol potong MIJ: blok isolasi solid di sekeliling pipa."""
        edges = rect(cx - w / 2.0, cy - pipe_r - 1.6, cx + w / 2.0, cy + pipe_r + 1.6)
        self.sym.extend(edges)
        self.solid_quad(
            (cx - w / 2.0 + 0.4, cy - pipe_r - 1.2),
            (cx + w / 2.0 - 0.4, cy - pipe_r - 1.2),
            (cx + w / 2.0 - 0.4, cy + pipe_r + 1.2),
            (cx - w / 2.0 + 0.4, cy + pipe_r + 1.2),
            layer="REF-SYM",
        )
        return edges

    # -------------------------------------------------------------------------
    # CP TEST POST (NACE SP0169)
    # -------------------------------------------------------------------------
    def cp_test_post(
        self,
        cx: float,
        cy: float,
        tag: str = "TP-01",
        dx: float = 0.0,
        dy: float = 8.0,
        shelf_len: float = 22.0,
    ) -> List[bd.Edge]:
        """Simbol tiang uji potensial: kotak kecil di sisi jalur + leader ke rak
        teks dua baris (CP TEST POST / tag).
        """
        s = 2.0  # setengah sisi kotak tiang
        edges = rect(cx - s + dx, cy + dy - s, cx + s + dx, cy + s + dy)
        # terminal titik ukur
        edges.append(circle(cx + dx, cy + dy, 0.8))
        # leader ke rak horizontal
        ex = cx + dx
        ey = cy + dy + s
        sx = ex + (shelf_len if shelf_len >= 0 else -shelf_len)
        edges.append(line(ex, ey, ex, ey + 4.0))
        edges.append(line(ex, ey + 4.0, sx, ey + 4.0))
        mid_x = (ex + sx) / 2.0
        self.text(tag, mid_x, ey + 7.0, size=2.5)
        self.text("CP TEST POST", mid_x, ey + 11.0, size=1.8)
        self.sym.extend(edges)
        return edges

    # -------------------------------------------------------------------------
    # CASED ROAD CROSSING — API RP 1102
    # -------------------------------------------------------------------------
    def cased_road_crossing(
        self,
        cx: float,
        cy: float,
        half_len: float = 50.0,
        casing_half: float = 3.0,
        spacer_step: float = 12.0,
        vent: bool = True,
        vent_dx: float = -0.72 * 50.0,
        vent_h: float = 12.0,
        label: str = "CASED ROAD CROSSING (API RP 1102)",
        label_dy: float = -11.5,
    ) -> Dict[str, float]:
        """Selubung pelindung penyeberangan jalan (tampak atas).

        - Dinding casing atas & bawah sepanjang [cx-half_len, cx+half_len].
        - End seal solid di kedua ujung casing.
        - Casing spacer plastik (tick vertikal) berjarak spacer_step.
        - Vent pipe riser + label pada ujung hulu casing (vent=True).
        Pipa carrier digambar terpisah (ug_pipe_run_h) menerus di dalam casing.
        Returns dict koordinat kunci untuk anotasi penelepon.
        """
        x0, x1 = cx - half_len, cx + half_len
        y0, y1 = cy - casing_half, cy + casing_half
        edges = [
            line(x0, y0, x1, y0),
            line(x0, y1, x1, y1),
        ]
        # End seals (solid quads) kedua ujung
        for xe in (x0, x1):
            s = 1.4
            self.solid_quad((xe - s, y0), (xe + s, y0), (xe + s, y1), (xe - s, y1),
                            layer="REF-SYM")
        # Casing spacer plastik (tick vertikal di dalam casing)
        xs = x0 + 6.0
        while xs <= x1 - 6.0:
            edges.append(line(xs, y0 + 0.7, xs, y1 - 0.7))
            xs += spacer_step
        # Vent pipe (riser + kepala vent)
        if vent:
            vx = cx + vent_dx
            edges.append(line(vx, y1, vx, y1 + vent_h))
            edges.append(circle(vx, y1 + vent_h + 1.8, 1.8))
            self.text("VENT", vx, y1 + vent_h + 6.2, size=1.8)
        if label:
            self.text(label, cx, cy + label_dy, size=2.0)
            self.text("CASING SPACERS + END SEALS", cx, cy + label_dy - 4.2, size=1.6)
        self.sym.extend(edges)
        return {"x0": x0, "x1": x1, "y0": y0, "y1": y1}

    def road_band(
        self, x0: float, x1: float, y0: float, y1: float, label: str = "ACCESS ROAD"
    ) -> List[bd.Edge]:
        """Batas jalan (dua garis tegak REF-ROAD) + label rotasi 90 di tengah band."""
        edges = [line(x0, y0, x0, y1), line(x1, y0, x1, y1)]
        self.road.extend(edges)
        if label:
            self.text(label, (x0 + x1) / 2.0 + 4.0, (y0 + y1) / 2.0, size=1.8, rot=90.0)
        return edges

    # -------------------------------------------------------------------------
    # GENERATOR TYPICAL TRENCH CROSS-SECTION TERDIMENSI (Bagian V.1.2)
    # -------------------------------------------------------------------------
    def trench_cross_section(
        self,
        x_cl: float,
        y_grade: float,
        x_min: float,
        x_max: float,
        y_min: float,
        scale: float = 50.0,           # mm kertas per meter
        cover_m: float = 1.2,          # ASME B31.8: 1.0-1.2 m (1.5 m di jalan)
        pipe_od_mm: float = 168.0,     # DN150
        bedding_mm: float = 150.0,     # sand bedding di bawah pipa
        pad_side_m: float = 0.20,      # sand padding sisi
        pad_top_m: float = 0.20,       # sand padding atas
        tape_below_m: float = 0.50,    # warning tape 300-500 mm di bawah tanah
        bottom_w_m: float = 1.20,      # lebar dasar galian
        side_slope: float = 1.0,       # kemiringan dinding (H per V)
        pipe_label: str = "DN150 CARRIER PIPE (3LPE)",
        pipe_sublabel: str = "",
    ) -> Dict[str, float]:
        """Gambar typical trench cross-section terdimensi lengkap.

        Zona: native soil (hatch 45), backfill terpadat 95% Standard Proctor
        (hatch trapesium), warning tape, sand padding, sand bedding 150 mm,
        pipa carrier. Dimensi (REF-DIM via manifest): lebar atas/dasar galian,
        cover depth, kedalaman tape, tebal bedding (angka mm bulat).
        Returns dict koordinat kunci.
        """
        od = pipe_od_mm / 1000.0 * scale
        r = od / 2.0
        cover = cover_m * scale
        y_pipe_top = y_grade - cover
        y_cl = y_pipe_top - r
        y_pipe_bot = y_cl - r
        bed = bedding_mm / 1000.0 * scale
        y_trench_bot = y_pipe_bot - bed
        depth = y_grade - y_trench_bot
        half_bot = bottom_w_m * scale / 2.0
        half_top = half_bot + side_slope * depth

        xt0, xt1 = x_cl - half_top, x_cl + half_top
        xb0, xb1 = x_cl - half_bot, x_cl + half_bot

        y_tape = y_grade - tape_below_m * scale
        half_tape = half_bot + side_slope * (y_tape - y_trench_bot)
        x_tape0, x_tape1 = x_cl - half_tape, x_cl + half_tape

        pad_hw = r + pad_side_m * scale
        px0, px1 = x_cl - pad_hw, x_cl + pad_hw
        y_pad_top = y_pipe_top + pad_top_m * scale
        half_bf = half_bot + side_slope * (y_pad_top - y_trench_bot)
        x_bf0, x_bf1 = x_cl - half_bf, x_cl + half_bf

        # --- Struktur galian & permukaan tanah (REF-EQUIP) ---
        self.equip += [
            line(x_min, y_grade, xt0, y_grade),          # grade kiri
            line(xt1, y_grade, x_max, y_grade),          # grade kanan
            line(xt0, y_grade, xb0, y_trench_bot),       # slope kiri
            line(xt1, y_grade, xb1, y_trench_bot),       # slope kanan
            line(xb0, y_trench_bot, xb1, y_trench_bot),  # dasar galian
            # tick penutup ujung garis tanah (3 mm, anti-dangling)
            line(x_min, y_grade, x_min, y_grade - 3.0),
            line(x_max, y_grade, x_max, y_grade - 3.0),
        ]
        # --- Sand bedding 150 mm (tanpa duplikasi dasar galian) ---
        self.equip += [
            line(xb0, y_pipe_bot, xb1, y_pipe_bot),
            line(xb0, y_trench_bot, xb0, y_pipe_bot),
            line(xb1, y_trench_bot, xb1, y_pipe_bot),
        ]
        # --- Sand padding (kotak 3 sisi; bawah = top edge bedding) ---
        self.equip += [
            line(px0, y_pipe_bot, px0, y_pad_top),
            line(px0, y_pad_top, px1, y_pad_top),
            line(px1, y_pad_top, px1, y_pipe_bot),
        ]
        # --- Pipa carrier ---
        self.equip.append(circle(x_cl, y_cl, r))
        # --- Warning tape 300-500 mm (ujung menempel dinding galian) ---
        self.equip += [
            line(x_tape0, y_tape, x_tape1, y_tape),
            line(x_tape0, y_tape + 1.4, x_tape1, y_tape + 1.4),
        ]
        # --- Arsiran native soil & backfill (REF-HATCH, tanpa blok tumpang) ---
        self.hatch += hatch45(x_min, y_min, xt0, y_grade, spacing=4.5)
        self.hatch += hatch45(xt1, y_min, x_max, y_grade, spacing=4.5)
        self.hatch += hatch45(xt0, y_min, xt1, y_trench_bot, spacing=4.5)
        backfill_poly = [(xt0, y_grade), (xt1, y_grade), (x_bf1, y_pad_top),
                         (x_bf0, y_pad_top)]
        self.hatch += hatch_poly(backfill_poly, spacing=6.0)

        # --- Label zona ---
        self.text("NATIVE SOIL", (x_min + xt0) / 2.0, y_grade - 9.0, size=1.8)
        self.text("NATIVE SOIL", (x_max + xt1) / 2.0, y_grade - 9.0, size=1.8)
        self.text("COMPACTED BACKFILL", x_cl, y_tape - 11.0, size=2.0)
        self.text("95% STD. PROCTOR", x_cl, y_tape - 15.0, size=1.8)

        # Warning tape label + leader (di zona native kanan, bebas slope)
        lx = x_tape1 + 18.0
        self.sym += [
            line(x_tape1, y_tape + 0.7, lx, y_tape + 9.0),
            line(lx, y_tape + 9.0, lx + 20.0, y_tape + 9.0),
        ]
        self.text("WARNING TAPE", lx + 1.0, y_tape + 11.6, size=1.8, left=True)
        self.text("300-500 BELOW GRADE", lx + 1.0, y_tape + 6.6, size=1.6, left=True)

        # Sand bedding label + leader
        self.sym += [
            line(xb0 + 1.0, y_pipe_bot - bed / 2.0, xb0 - 16.0, y_trench_bot - 11.0),
            line(xb0 - 16.0, y_trench_bot - 11.0, xb0 - 44.0, y_trench_bot - 11.0),
        ]
        self.text("SAND BEDDING 150 MM", xb0 - 43.0, y_trench_bot - 8.6,
                  size=1.8, left=True)

        # Sand padding label + leader
        self.sym += [
            line(px1, y_pad_top - pad_top_m * scale / 2.0,
                 px1 + 18.0, y_pad_top + 6.0),
            line(px1 + 18.0, y_pad_top + 6.0, px1 + 40.0, y_pad_top + 6.0),
        ]
        self.text("SAND PADDING", px1 + 19.0, y_pad_top + 8.6, size=1.8, left=True)

        # Carrier pipe label + leader (di zona native kiri, bebas slope)
        lp0 = (x_cl + r * 0.62, y_cl + r * 0.62)
        lp1 = (x_cl - 71.0, y_cl + 7.2)
        self.sym += [line(*lp0, *lp1), line(lp1[0], lp1[1], lp1[0] - 26.0, lp1[1])]
        self.text(pipe_label, lp1[0] - 25.0, lp1[1] + 2.6, size=1.8, left=True)
        if pipe_sublabel:
            self.text(pipe_sublabel, lp1[0] - 25.0, lp1[1], size=1.6, left=True)

        # --- Dimensi (REF-DIM via manifest, angka mm bulat) ---
        top_w_mm = (xt1 - xt0) / scale * 1000.0
        self.dimrec((xt0, y_grade), (xt1, y_grade), str(int(round(top_w_mm))),
                    angle=0.0, base=(x_cl, y_grade + 10.0))
        self.dimrec((xb0, y_trench_bot), (xb1, y_trench_bot),
                    str(int(round(bottom_w_m * 1000))), angle=0.0,
                    base=(x_cl, y_trench_bot - 9.0))
        self.dimrec((x_max - 20.0, y_grade), (x_max - 20.0, y_pipe_top),
                    str(int(round(cover_m * 1000))), angle=90.0,
                    base=(x_max - 4.0, y_grade))
        self.dimrec((x_max - 28.0, y_grade), (x_max - 28.0, y_tape),
                    str(int(round(tape_below_m * 1000))), angle=90.0,
                    base=(x_max - 13.0, y_grade))
        self.dimrec((xb0 - 12.0, y_pipe_bot), (xb0 - 12.0, y_trench_bot),
                    str(int(round(bedding_mm))), angle=90.0,
                    base=(xb0 - 21.0, y_pipe_bot))

        return {
            "x_cl": x_cl, "y_grade": y_grade, "y_cl": y_cl, "r": r,
            "y_pipe_top": y_pipe_top, "y_pipe_bot": y_pipe_bot,
            "y_trench_bot": y_trench_bot, "y_tape": y_tape, "y_pad_top": y_pad_top,
            "xt0": xt0, "xt1": xt1, "xb0": xb0, "xb1": xb1,
        }

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
        """Border A3 + grid referensi + kolom kanan (NOTES, LEGEND, REF DOC,
        REV TABLE, TITLE BLOCK). LEGEND disiapkan kotaknya; isian baris dilakukan
        penelepon. Returns bounds legenda {x0, x1, y_top, y_bot}.
        """
        # Border luar & dalam
        self.frame += rect(2.0, 1.3, 418.0, 295.7)
        self.frame += rect(7.0, 6.3, 413.0, 290.7)

        # Grid referensi 1-12 / A-H
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

        # Kolom kanan
        fx0, fx1 = 336.0, 413.0
        self.frame.append(line(fx0, 6.3, fx0, 290.7))

        # --- NOTES (y = 238..290.7) ---
        self.frame.append(line(fx0, 238.0, fx1, 238.0))
        self.text("NOTES", (fx0 + fx1) / 2.0, 286.0, size=2.5)
        self.frame.append(line(fx0, 283.0, fx1, 283.0))
        ny = 278.5
        for note in notes:
            self.text(note, fx0 + 3.0, ny, size=1.8, left=True)
            ny -= 6.3

        # --- LEGEND (y = 170..238) — kotak disiapkan, isian oleh penelepon ---
        self.frame.append(line(fx0, 170.0, fx1, 170.0))
        self.text("LEGEND", (fx0 + fx1) / 2.0, 234.0, size=2.5)
        self.frame.append(line(fx0, 231.0, fx1, 231.0))

        # --- REFERENCE DOCUMENT (y = 142..170) ---
        self.frame.append(line(fx0, 142.0, fx1, 142.0))
        self.text("REFERENCE DOCUMENT", (fx0 + fx1) / 2.0, 166.0, size=2.0)
        self.frame.append(line(fx0, 163.0, fx1, 163.0))
        ry = 157.0
        for doc_id, doc_title in ref_docs:
            self.text(doc_id, fx0 + 3.0, ry, size=1.5, left=True)
            self.text(doc_title, fx0 + 36.0, ry, size=1.5, left=True)
            ry -= 6.0

        # --- REV TABLE (y = 118..142, bottom-up A0 di bawah) ---
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

        # --- TITLE BLOCK (y = 6.3..118) ---
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
            "REF-ROAD": self.road,
            "REF-EQUIP": self.equip,
            "REF-PROC": self.proc,
            "REF-PROC-UG": self.proc_ug,
            "REF-SYM": self.sym,
            "REF-SIG": self.sig,
            "REF-HATCH": self.hatch,
        }
        return {name: comp(items) for name, items in mapping.items() if items}

    def export_manifest(self, json_path: Path | str) -> Dict[str, bd.Compound]:
        path = Path(json_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        manifest = {"texts": self.texts, "dims": self.dims, "solids": self.solids}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        return self.get_layers()
