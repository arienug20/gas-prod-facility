"""Reusable Custody Transfer & Allocation Metering Station Library.

Versi 1.0.0 (Pipeline Metering CAD Suite — Bagian IV.1 dokumen
GPF-00-PM-PLN-0008 Rev A2).

Standar acuan:
  - AGA Report No. 3 (Orifice), No. 7 (Turbine), No. 9 (Ultrasonic),
    No. 11 (Coriolis / mass & energy) + AGA 8 (GHV / compressibility)
  - API MPMS Chapter 5 (Metering), Chapter 14 (Natural Gas)
  - ISO 5167 (Pressure differential devices), ISO 17089 (Ultrasonic gas meters)
  - API 6D (Double Block & Bleed isolation) / ANSI/ISA-5.1-2024
  - ISO 10628-2:2012 (Graphical symbols)

Arsitektur stasiun (multi-run):
  Inlet Header -> N x Meter Run paralel (duty / standby) -> Outlet Header.
  Setiap run diisolasi Double Block & Bleed (DBB) twin/expanding plug valve
  bubble-tight pada inlet & outlet dengan cavity bleed valve; analisis komposisi
  online via fast loop sampling probe + Gas Chromatograph (C1-C6+, CO2, N2,
  Gross Heating Value) ke flow computer FQI.

Katalog modul meter:
  - usm_meter_run        : USM spool 10D-20D + flow conditioner (Zanker/tube
                           bundle) + transduser multi-path + FQI (AGA 9)
  - coriolis_meter       : tabung U-tube + drive/pickup coil + klem
                           anti-vibrasi + FT/DT transmitter (AGA 11)
  - orifice_meter_run    : senior dual-chamber orifice fitting (ganti piringan
                           tanpa shutdown) + corner/flange taps (AGA 3)
  - turbine_meter        : rotor bilah + pick-up coil + pelurus aliran hulu
                           (AGA 7)
  - dbb_valve_h          : Double Block & Bleed twin plug valve + cavity bleed
  - fast_loop / gc_analyzer : sampling probe + GC online analyzer

Wajib di-import oleh semua script P&ID metering proyek agar simbol meter,
DBB, sampling, flow computer, dan furnitur lembar A1 100% konsisten.
Gaya mengikuti pid_common.py: kelas context + fungsi gambar, layer REF-*,
teks via manifest TEXTS (MTEXT ARIAL via apply_text.py).
"""

from __future__ import annotations

import math

from cadgen import build123d as bd

from pid_common import (
    BUBBLE_R,
    PIDContext,
    arc,
    circle,
    dashed,
    line,
    pipe_run_h,
    pipe_run_v,
    rect,
)

# Half-width (mm) pipa yang di-gap untuk setiap simbol (untuk pipe_run_h gaps)
DBB_HALF = 15.0          # DBB twin plug valve + flange ticks
USM_BODY_L = 44.0        # panjang body USM (spool meter)
METER_BODY_L = 36.0      # panjang body orifice senior / coriolis / turbine
METER_BODY_H = 16.0      # tinggi body meter run
TURBINE_BODY_H = 14.0    # tinggi body turbine meter


class MeteringContext(PIDContext):
    """Konteks P&ID stasiun metering custody transfer — memperluas PIDContext.

    Menambahkan simbol khas metering: DBB twin plug valve, meter run
    USM/Coriolis/orifice senior/turbine, fast loop sampling probe, GC
    analyzer, dan flow computer FQI. Seluruh teks dicatat via self.text()
    (manifest TEXTS -> MTEXT ARIAL oleh apply_text.py).
    """

    # ---------------------------------------------------------------------
    # DOUBLE BLOCK & BLEED (API 6D) — twin/expanding plug, bubble-tight
    # ---------------------------------------------------------------------
    def dbb_valve_h(self, cx: float, cy: float, tag: str = "") -> list[bd.Edge]:
        """DBB horizontal: dua plug valve seri + cavity bleed valve (atas).

        Geometri (setengah-lebar total DBB_HALF = 15 mm):
          - Plug valve A di cx-10, plug valve B di cx+10 (bowtie w=10 h=6)
          - Spool penghubung di antara kedua plug valve
          - Cavity bleed: stub naik dari spool + port + plug valve kecil +
            vent line + cap tick, label "BLD"
        Pipe di-gap dengan (cx, DBB_HALF); flange tick 12 mm di ujung luar.
        """
        out: list[bd.Edge] = []
        # Plug valve A & B (bowtie + 2 garis penutup vertikal)
        for vx in (cx - 10.0, cx + 10.0):
            out += [
                line(vx - 5.0, cy - 3.0, vx, cy),
                line(vx, cy, vx - 5.0, cy + 3.0),
                line(vx - 5.0, cy - 3.0, vx - 5.0, cy + 3.0),
                line(vx + 5.0, cy - 3.0, vx, cy),
                line(vx, cy, vx + 5.0, cy + 3.0),
                line(vx + 5.0, cy - 3.0, vx + 5.0, cy + 3.0),
            ]
        # Spool penghubung antar plug valve
        out.append(line(cx - 5.0, cy, cx + 5.0, cy))
        # Cavity bleed: stub + port bawah + plug valve kecil + port atas +
        # vent + cap tick (seluruh endpoint menempel geometry sekitarnya)
        out += [
            line(cx, cy, cx, cy + 3.2),                       # stub naik
            line(cx - 1.8, cy + 3.2, cx + 1.8, cy + 3.2),     # port bawah
            line(cx - 1.8, cy + 3.2, cx, cy + 4.5),           # bowtie bleed
            line(cx, cy + 4.5, cx + 1.8, cy + 3.2),
            line(cx + 1.8, cy + 3.2, cx, cy + 5.8),
            line(cx, cy + 5.8, cx - 1.8, cy + 3.2),
            line(cx - 1.8, cy + 3.2, cx - 1.8, cy + 5.8),     # sisi kiri
            line(cx + 1.8, cy + 3.2, cx + 1.8, cy + 5.8),     # sisi kanan
            line(cx - 1.8, cy + 5.8, cx + 1.8, cy + 5.8),     # port atas
            line(cx, cy + 5.8, cx, cy + 8.4),                 # vent line
            line(cx - 1.5, cy + 8.4, cx + 1.5, cy + 8.4),     # cap tick
        ]
        # Flange tick 12 mm di kedua ujung luar (titik tengah pada pipa)
        out += [
            line(cx - 16.2, cy - 6.0, cx - 16.2, cy + 6.0),
            line(cx + 16.2, cy - 6.0, cx + 16.2, cy + 6.0),
        ]
        self.proc += out
        self.text("BLD", cx + 5.5, cy + 7.1, size=1.8)
        if tag:
            # Tag di bawah footprint assembly (flange tick berakhir cy-6)
            # agar bebas dari simbol DBB (QA visual: tag menimpa area assembly).
            self.text(tag, cx, cy - 12.0, size=1.8)
            self.schedule_valves.append({
                "tag": tag,
                "type": "DOUBLE BLOCK & BLEED (TWIN PLUG, BUBBLE-TIGHT)",
                "orientation": "H",
                "x": round(cx, 3),
                "y": round(cy, 3),
            })
            self.schedule_valves.append({
                "tag": f"{tag}-BLD",
                "type": "CAVITY BLEED VALVE (PLUG)",
                "orientation": "V",
                "x": round(cx, 3),
                "y": round(cy + 4.5, 3),
            })
        return out

    # ---------------------------------------------------------------------
    # FLOW CONDITIONER (ZANKER / TUBE BUNDLE) — internal meter run
    # ---------------------------------------------------------------------
    def flow_conditioner(
        self, cx: float, cy: float, height: float = 16.0, kind: str = "zanker"
    ) -> list[bd.Edge]:
        """Flow conditioner di dalam spool meter (tinggi = body height).

        kind="zanker"       : plat perforasi (2 garis plat + lubang bulat)
        kind="tube_bundle"  : berkas tabung (deretan lingkaran kecil)
        """
        hh = height / 2.0
        out: list[bd.Edge] = []
        if kind == "tube_bundle":
            for i in range(4):
                out.append(circle(cx, cy - hh + 2.2 + i * (height - 4.4) / 3.0, 1.3))
        else:  # zanker plate perforated
            out += [
                line(cx - 0.5, cy - hh, cx - 0.5, cy + hh),
                line(cx + 0.5, cy - hh, cx + 0.5, cy + hh),
            ]
            for i in range(4):
                out.append(circle(cx, cy - hh + 2.2 + i * (height - 4.4) / 3.0, 0.9))
        return out

    # ---------------------------------------------------------------------
    # FLOW COMPUTER (FQI) + INSTRUMENT STACK VERTIKAL (ANSI/ISA-5.1)
    # ---------------------------------------------------------------------
    def ft_stack(
        self,
        x: float,
        y_body_top: float,
        fe_pair: tuple[str, str],
        fqi_pair: tuple[str, str],
        bubble_dy: float = 13.0,
        fqi_dy: float = 32.0,
    ) -> None:
        """Stack instrumen vertikal di atas body meter: tap stub + bubble FT +
        sinyal dashed ke flow computer FQI (DCS shared display).

        Titik sambung tanpa ujung menggantung: stub dari y_body_top (garis
        dinding body) tepat ke tepi bawah bubble; sinyal dashed dari tepi atas
        bubble ke tepi bawah kotak FQI.
        """
        y_bub = y_body_top + bubble_dy
        y_fqi = y_body_top + fqi_dy
        self.proc.append(line(x, y_body_top, x, y_bub - BUBBLE_R))
        self.sym += self.bubble(x, y_bub, fe_pair[0], fe_pair[1])
        self.sig += dashed(x, y_bub + BUBBLE_R, x, y_fqi - 7.5, dash=2.0, gap=1.2)
        self.sym += self.dcs(x, y_fqi, fqi_pair[0], fqi_pair[1])

    # ---------------------------------------------------------------------
    # ULTRASONIC FLOW METER (AGA 9 / ISO 17089)
    # ---------------------------------------------------------------------
    def usm_meter_run(
        self,
        cx: float,
        cy: float,
        tag: str = "USM-6001",
        fe_pair: tuple[str, str] = ("FT", "611"),
        fqi_pair: tuple[str, str] = ("FQI", "611"),
        length: float = USM_BODY_L,
        height: float = METER_BODY_H,
        conditioner: str = "zanker",
        paths: int = 2,
    ) -> float:
        """USM multi-path lengkap: spool body + flow conditioner + transduser
        multi-path (korda diagonal) + stack FT/FQI di atas.

        Returns:
            half-width gap untuk pipe_run_h (length / 2).
        """
        hw, hh = length / 2.0, height / 2.0
        x0, x1 = cx - hw, cx + hw
        y0, y1 = cy - hh, cy + hh
        # Spool body tertutup + flange tick 12 mm di kedua ujung
        # (tick 1.2 mm di luar ujung gap pipa agar aman Check 4/6)
        out = rect(x0, y0, x1, y1)
        out += [
            line(x0 - 1.2, cy - 6.0, x0 - 1.2, cy + 6.0),
            line(x1 + 1.2, cy - 6.0, x1 + 1.2, cy + 6.0),
        ]
        # Flow conditioner di dekat inlet (10% dari hulu)
        out += self.flow_conditioner(x0 + 10.0, cy, height=height, kind=conditioner)
        # Transduser multi-path: korda diagonal dinding-ke-dinding
        for p in range(paths):
            ya = y1 - 3.5 - p * 5.0
            yb = ya - 4.0
            out.append(line(x0, ya, x1, yb))
        self.proc += out
        # Instrument stack (stub + FT + FQI) — koneksi bebas ujung menggantung
        self.ft_stack(cx, y1, fe_pair, fqi_pair)
        # Label
        self.text("FC", x0 + 10.0, y1 + 3.0, size=1.8)
        self.text(tag, cx, y0 - 9.0, size=2.5)
        if tag:
            self.schedule_equipment.append({
                "tag": tag,
                "type": "ULTRASONIC FLOW METER (AGA 9 / ISO 17089)",
                "x": round(cx, 3),
                "y": round(cy, 3),
                "length": round(length, 3),
                "conditioner": conditioner,
                "paths": paths,
            })
        return hw

    # ---------------------------------------------------------------------
    # ORIFICE METER RUN — SENIOR DUAL-CHAMBER FITTING (AGA 3 / ISO 5167)
    # ---------------------------------------------------------------------
    def orifice_meter_run(
        self,
        cx: float,
        cy: float,
        tag: str = "OF-6021",
        fe_pair: tuple[str, str] = ("FT", "621"),
        fqi_pair: tuple[str, str] = ("FQI", "621"),
        length: float = METER_BODY_L,
    ) -> float:
        """Senior dual-chamber orifice fitting: kamper bawah (meter chamber)
        + kamper atas (valve chamber — ganti piringan tanpa shutdown) +
        orifice plate center + corner/flange taps dengan isolation valve +
        impulse manifold + bubble FT + FQI.

        Returns:
            half-width gap untuk pipe_run_h (length / 2).
        """
        hw = length / 2.0
        x0, x1 = cx - hw, cx + hw
        # Kamper bawah menempel pipa (y = cy-12 .. cy), kamper atas di atasnya
        y_lower0, y_lower1 = cy - 12.0, cy
        y_upper1 = cy + 14.0
        out = rect(x0, y_lower0, x1, y_lower1)
        out += [
            line(x0 + 6.0, y_lower1, x0 + 6.0, y_upper1),   # kamper atas kiri
            line(x1 - 6.0, y_lower1, x1 - 6.0, y_upper1),   # kamper atas kanan
            line(x0 + 6.0, y_upper1, x1 - 6.0, y_upper1),   # atap kamper atas
        ]
        # Orifice plate (center, dinding-ke-dinding kedua kamper, di-break
        # gap 3 mm pada persilangan dinding pembatas kamper y = cy)
        out += pipe_run_v(cx - 1.2, y_lower0, y_upper1, gaps=[(cy, 1.5)])
        out += pipe_run_v(cx + 1.2, y_lower0, y_upper1, gaps=[(cy, 1.5)])
        # Flange tick 12 mm (1.2 mm di luar ujung gap pipa)
        out += [
            line(x0 - 1.2, cy - 6.0, x0 - 1.2, cy + 6.0),
            line(x1 + 1.2, cy - 6.0, x1 + 1.2, cy + 6.0),
        ]
        self.proc += out
        # Corner/flange taps + isolation valve + impulse manifold + FT + FQI
        y_man = y_upper1 + 9.0                      # impulse manifold
        y_bub = y_man + 8.0                         # bubble FT center
        y_fqi = y_bub + 18.0                        # FQI center
        for xt in (x0 + 10.0, x1 - 10.0):
            self.proc.append(line(xt, y_upper1, xt, y_man))
            self.valve_gate_v(xt, y_upper1 + 4.5, w=3.2, h=5.0, flanged=False)
        self.proc.append(line(x0 + 10.0, y_man, x1 - 10.0, y_man))
        self.proc.append(line(cx, y_man, cx, y_bub - BUBBLE_R))
        self.sym += self.bubble(cx, y_bub, fe_pair[0], fe_pair[1])
        self.sig += dashed(cx, y_bub + BUBBLE_R, cx, y_fqi - 7.5, dash=2.0, gap=1.2)
        self.sym += self.dcs(cx, y_fqi, fqi_pair[0], fqi_pair[1])
        # Label
        self.text(tag, cx, y_lower0 - 9.0, size=2.5)
        self.text("DUAL CHAMBER", cx + 22.0, cy + 10.5, size=1.8)
        if tag:
            self.schedule_equipment.append({
                "tag": tag,
                "type": "SENIOR DUAL-CHAMBER ORIFICE FITTING (AGA 3 / ISO 5167)",
                "x": round(cx, 3),
                "y": round(cy, 3),
                "length": round(length, 3),
                "taps": "corner/flange",
            })
        return hw

    # ---------------------------------------------------------------------
    # CORIOLIS MASS METER (AGA 11 / API MPMS 5.6)
    # ---------------------------------------------------------------------
    def coriolis_meter(
        self,
        cx: float,
        cy: float,
        tag: str = "CM-6031",
        ft_pair: tuple[str, str] = ("FT", "631"),
        dt_pair: tuple[str, str] = ("DT", "632"),
        fqi_pair: tuple[str, str] = ("FQI", "631"),
        length: float = METER_BODY_L,
        height: float = METER_BODY_H,
    ) -> float:
        """Coriolis U-tube: body + tabung ganda dengan U-bend + drive & pickup
        coil (solid dot + stem) + flange tick + klem anti-vibrasi (tick ganda
        di dinding body) + transmitter FT (massa) & DT (densitas/temperatur)
        + FQI.

        Returns:
            half-width gap untuk pipe_run_h (length / 2).
        """
        hw, hh = length / 2.0, height / 2.0
        x0, x1 = cx - hw, cx + hw
        y0, y1 = cy - hh, cy + hh
        out = rect(x0, y0, x1, y1)
        # Tabung U: dua tube paralel + bend kanan + manifold kiri
        yt, yb = cy + 4.0, cy - 4.0
        x_tube0, x_tube1 = x0 + 3.0, x1 - 6.0
        out += [
            line(x_tube0, yt, x_tube1, yt),
            line(x_tube0, yb, x_tube1, yb),
            line(x_tube0, yt, x_tube0, yb),
            arc(x_tube1, cy, 4.0, -90, 90),
        ]
        # Drive & pickup coil (stem dinding-ke-dinding + solid dot)
        for xd in (cx - 2.0, cx + 6.0):
            out.append(line(xd, yb, xd, yt))
            self.solid_dot(xd, cy, r=0.9, layer="REF-EQUIP")
        # Klem anti-vibrasi: plat tick dinding-ke-dinding kiri & kanan
        out += [
            line(x0 + 2.0, y0, x0 + 2.0, y1),
            line(x1 - 2.0, y0, x1 - 2.0, y1),
        ]
        # Flange tick 12 mm (1.2 mm di luar ujung gap pipa)
        out += [
            line(x0 - 1.2, cy - 6.0, x0 - 1.2, cy + 6.0),
            line(x1 + 1.2, cy - 6.0, x1 + 1.2, cy + 6.0),
        ]
        self.proc += out
        # Transmitter stack: FT (center) + DT (kanan, tangent stub)
        y_bub = y1 + 13.0
        y_fqi = y1 + 32.0
        x_dt = x1 - 6.0
        self.proc.append(line(cx, y1, cx, y_bub - BUBBLE_R))
        self.sym += self.bubble(cx, y_bub, ft_pair[0], ft_pair[1])
        self.proc.append(line(x_dt, y1, x_dt, y_bub))
        self.sym += self.bubble(x_dt + 6.0, y_bub, dt_pair[0], dt_pair[1])
        # Sinyal FT & DT ke FQI
        self.sig += dashed(cx, y_bub + BUBBLE_R, cx, y_fqi - 7.5, dash=2.0, gap=1.2)
        self.sig += dashed(x_dt + 6.0, y_bub + BUBBLE_R, x_dt + 6.0, y_fqi - 7.5, dash=2.0, gap=1.2)
        self.sig += dashed(x_dt + 6.0, y_fqi - 7.5, cx + 7.5, y_fqi - 7.5, dash=2.0, gap=1.2)
        self.sym += self.dcs(cx, y_fqi, fqi_pair[0], fqi_pair[1])
        # Label
        self.text(tag, cx, y0 - 9.0, size=2.5)
        # Label klem digeser turun agar berjarak dari label nomor line run
        # (QA visual: klaster anotasi meter terlalu dekat label line).
        self.text("ANTI-VIB CLAMP", x0 - 14.0, y0 - 8.0, size=1.8)
        if tag:
            self.schedule_equipment.append({
                "tag": tag,
                "type": "CORIOLIS MASS METER (AGA 11 / API MPMS 5.6)",
                "x": round(cx, 3),
                "y": round(cy, 3),
                "length": round(length, 3),
                "transmitters": ["FT", "DT", "TT"],
            })
        return hw

    # ---------------------------------------------------------------------
    # TURBINE FLOW METER (AGA 7 / API MPMS 5.3)
    # ---------------------------------------------------------------------
    def turbine_meter(
        self,
        cx: float,
        cy: float,
        tag: str = "TB-6041",
        fe_pair: tuple[str, str] = ("FT", "641"),
        fqi_pair: tuple[str, str] = ("FQI", "641"),
        length: float = METER_BODY_L,
        height: float = TURBINE_BODY_H,
    ) -> float:
        """Turbine meter: body + pelurus aliran hulu (tube bundle) + rotor
        bilah (hub solid + 4 bilah) + pick-up coil (kotak PU pada stem atas)
        + stack FT/FQI.

        Returns:
            half-width gap untuk pipe_run_h (length / 2).
        """
        hw, hh = length / 2.0, height / 2.0
        x0, x1 = cx - hw, cx + hw
        y0, y1 = cy - hh, cy + hh
        out = rect(x0, y0, x1, y1)
        # Pelurus aliran hulu: tube bundle (4 lingkaran vertikal)
        out += self.flow_conditioner(x0 + 6.0, cy, height=height, kind="tube_bundle")
        # Rotor bilah
        r_rotor = min(hh - 2.5, 4.5)
        out.append(circle(cx + 8.0, cy, r_rotor))
        for ang in (45.0, 135.0, 225.0, 315.0):
            a = math.radians(ang)
            out.append(line(
                cx + 8.0 + 1.2 * math.cos(a), cy + 1.2 * math.sin(a),
                cx + 8.0 + r_rotor * math.cos(a), cy + r_rotor * math.sin(a),
            ))
        self.solid_dot(cx + 8.0, cy, r=1.2, layer="REF-EQUIP")
        # Pick-up coil: stem dinding-ke-dinding + kotak PU
        x_pu = cx + 8.0
        out.append(line(x_pu, y1, x_pu, y1 + 4.0))
        out += rect(x_pu - 3.0, y1 + 4.0, x_pu + 3.0, y1 + 8.0)
        # Flange tick 12 mm (1.2 mm di luar ujung gap pipa)
        out += [
            line(x0 - 1.2, cy - 6.0, x0 - 1.2, cy + 6.0),
            line(x1 + 1.2, cy - 6.0, x1 + 1.2, cy + 6.0),
        ]
        self.proc += out
        self.text("PU", x_pu, y1 + 6.0, size=1.8)
        # Stack FT + FQI di atas kotak PU
        self.ft_stack(x_pu, y1 + 8.0, fe_pair, fqi_pair)
        # Label
        self.text(tag, cx, y0 - 9.0, size=2.5)
        if tag:
            self.schedule_equipment.append({
                "tag": tag,
                "type": "TURBINE FLOW METER (AGA 7 / API MPMS 5.3)",
                "x": round(cx, 3),
                "y": round(cy, 3),
                "length": round(length, 3),
                "straightener": "tube bundle",
            })
        return hw

    # ---------------------------------------------------------------------
    # FAST LOOP SAMPLING PROBE + GC ANALYZER ONLINE
    # ---------------------------------------------------------------------
    def fast_loop(self, x: float, y_pipe: float, y_top: float) -> list[bd.Edge]:
        """Sampling probe fast loop pada pipa proses: probe stub + isolation
        valve + riser sample line hingga y_top (mis. dasar kotak GC).

        Riser digambar satu garis utuh dari tee di pipa (y_pipe) ke y_top;
        valve dipasang menempel pada riser (tanpa ujung menggantung).
        """
        out: list[bd.Edge] = [line(x, y_pipe, x, y_top)]
        self.proc += out
        self.valve_gate_v(x, y_pipe + 4.8, w=3.2, h=5.0, flanged=False)
        self.flow_arrow_v(x, y_pipe + (y_top - y_pipe) * 0.55, direction=-1)
        self.register_line("200-SA-6010", spec="TUBING SS316", service="GC FAST LOOP SAMPLE", dn=15)
        return out

    def gc_analyzer(
        self,
        cx: float,
        cy: float,
        w: float = 90.0,
        h: float = 40.0,
        tag: str = "AT-6090",
        comp_lines: tuple[str, ...] = (
            "GAS CHROMATOGRAPH",
            "ONLINE ANALYZER AT-6090",
            "C1-C6+ / CO2 / N2",
            "GHV TO FQI (AGA 8)",
        ),
    ) -> list[bd.Edge]:
        """Gas Chromatograph online analyzer: kotak analyzer + tag + daftar
        analisis (fraksi C1-C6+, CO2, N2, Gross Heating Value)."""
        x0, x1 = cx - w / 2.0, cx + w / 2.0
        y0, y1 = cy - h / 2.0, cy + h / 2.0
        out = rect(x0, y0, x1, y1)
        self.equip += out
        n = len(comp_lines)
        for i, ln in enumerate(comp_lines):
            ty = y1 - 5.0 - i * ((h - 10.0) / max(1, n - 1))
            size = 2.2 if i == 0 else 1.8
            self.text(ln, cx, ty, size=size)
        self.schedule_equipment.append({
            "tag": tag,
            "type": "ONLINE GAS CHROMATOGRAPH (C1-C6+, CO2, N2, GHV)",
            "x": round(cx, 3),
            "y": round(cy, 3),
        })
        return out

    # ---------------------------------------------------------------------
    # HEADER & MANIFOLD METERING
    # ---------------------------------------------------------------------
    def metering_header(
        self,
        x0: float,
        x1: float,
        y: float,
        line_no: str,
        dn: int = 300,
        label_dy: float = -7.0,
        label_x: float | None = None,
    ) -> list[bd.Edge]:
        """Segmen header metering horizontal + panah aliran + label nomor line
        (kategori line number 1.5-2.0 mm). label_x = posisi center teks."""
        out = pipe_run_h(y, x0, x1)
        self.proc += out
        self.flow_arrow_h(x0 + (x1 - x0) * 0.22, y, direction=1)
        lx = label_x if label_x is not None else x0 + (x1 - x0) * 0.42
        self.text(f"{line_no} DN{dn}", lx, y + label_dy, size=2.0)
        self.register_line(line_no, spec="A1A", service="GAS METERING", dn=dn)
        return out

    def meter_run_pipe(
        self, x0: float, x1: float, y: float, gaps: list[tuple[float, float]]
    ) -> list[bd.Edge]:
        """Pipa meter run horizontal dengan seluruh gap simbol (DBB/meter)."""
        out = pipe_run_h(y, x0, x1, gaps=gaps)
        self.proc += out
        return out

    def manifold_v(self, x: float, y0: float, y1: float) -> list[bd.Edge]:
        """Manifold/header vertikal penghubung N run paralel (major line)."""
        out = pipe_run_v(x, y0, y1)
        self.proc += out
        return out
