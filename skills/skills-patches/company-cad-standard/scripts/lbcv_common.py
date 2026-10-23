"""Reusable Line Break Control Valve (LBCV) Station Library — Pipeline Transmission Safety Valve.

Versi 1.0.0 (Pipeline, Metering & LBCV CAD Suite — Modul M6, Bagian IV.2
GPF-00-PM-PLN-0008 Rev A2).

Standar acuan:
  - ASME B31.8 (Gas Transmission & Distribution Piping Systems)
  - ASME B31.4 (Pipeline Transportation Systems for Liquids)
  - API SPEC 6D (Pipeline and Pipeline Valves — Trunnion Ball, Full Bore, PIG-able)
  - API RP 1130 (Computational Pipeline Monitoring for Liquid Pipelines)
  - ANSI/ISA-5.1-2024 (Instrumentation Symbols and Identification)
  - ISO 10628-2:2012 (Graphical symbols for chemical & petrochemical industry)

Lingkup pustaka (semua teks via manifest TEXTS -> apply_text.py, layer REF-*):
  - ball_valve_mlv_h        : Main Line Valve ball trunnion full-bore (API 6D)
  - stem_extension_v        : Stem extension 1.5-2.5 m untuk badan katup ditanam
  - gas_over_oil_actuator   : Aktuator gas-over-oil fail-close otonom
  - line_break_pilot        : Pilot line break dP/dt (set > 0.5 bar/menit)
  - hand_pump               : Pompa hidrolik darurat (emergency re-open)
  - blowdown_stack_v        : Cerobong blowdown vertikal + katup penutup ganda
  - bypass_equalizing_h     : Bypass equalizing DN50/DN80 dengan 2 katup NC
  - instrument_tap_v        : Tap PT/PI + bubble instrumen ANSI/ISA-5.1
  - gas_supply_takeoff      : Take-off gas bertekanan pipa utk aktuator
  - grade_line_h            : Garis muka tanah (buried below grade)
  - lbcv_station_h          : Rakitan station lengkap (macro, satu panggilan)

Semua komponen mengikuti konvensi koneksi pid_common: ujung pipa tepat pada
garis penutup badan katup, tick flensa memotong ujung pipa (mid-connection),
sehingga lolos Check 6 (dangling endpoints) validate_cad_rules.py.
"""

from __future__ import annotations

from cadgen import build123d as bd

from pid_common import (
    PIDContext,
    circle,
    dashed,
    dashed_brk,
    line,
    pipe_run_h,
    pipe_run_v,
    rect,
)

BUBBLE_R = 6.0  # konsisten dengan pid_common.BUBBLE_R


class LBCVContext(PIDContext):
    """Konteks pembuat drawing Line Break Control Valve station (mewarisi PIDContext).

    Mewarisi seluruh simbol P&ID (valve_gate_h/v, valve_globe_h, bubble, dcs,
    flow_arrow_h/v, solid_dot, text, continuity_box_*, schedules, export_manifest).
    """

    # -------------------------------------------------------------------------
    # 1. MAIN LINE VALVE — BALL VALVE TRUNNION MOUNTED FULL BORE (API 6D)
    # -------------------------------------------------------------------------
    def ball_valve_mlv_h(
        self,
        cx: float,
        cy: float,
        w: float = 18.0,
        h: float = 9.0,
        tag: str = "",
        trunnion: bool = True,
        flanged: bool = True,
    ) -> list[bd.Edge]:
        """Simbol MLV ball valve trunnion mounted full-bore (ISO 10628-2 + API 6D).

        Bowtie + lingkaran bola (r = w/2, menyinggung garis penutup ujung) +
        titik trunnion solid pada puncak bawah lingkaran + 2 tick flensa.
        Celah pipa yang benar: gaps=[(cx, w/2 + 1.2)] agar ujung pipa tepat di
        tick flensa (mid-connection) — lihat lbcv_station_h.
        """
        hw, hh = w / 2.0, h / 2.0
        out = [
            # Garis penutup ujung (vertikal) — titik sambung pipa
            line(cx - hw, cy - hh, cx - hw, cy + hh),
            line(cx + hw, cy - hh, cx + hw, cy + hh),
            # Bowtie (dua segitiga berhadapan)
            line(cx - hw, cy - hh, cx, cy),
            line(cx, cy, cx - hw, cy + hh),
            line(cx + hw, cy - hh, cx, cy),
            line(cx, cy, cx + hw, cy + hh),
            # Bola full-bore (menyinggung kedua garis penutup)
            circle(cx, cy, hw),
        ]
        if flanged:
            out += [
                line(cx - hw - 1.2, cy - hh - 1.0, cx - hw - 1.2, cy + hh + 1.0),
                line(cx + hw + 1.2, cy - hh - 1.0, cx + hw + 1.2, cy + hh + 1.0),
            ]
        if trunnion:
            # Tanda trunnion bearing (pivot dot solid) di bawah bola
            self.solid_dot(cx, cy - hw - 0.1, r=0.9, layer="REF-PROC")
        if tag:
            self.schedule_valves.append(
                {
                    "tag": tag,
                    "type": "BALL VALVE, TRUNNION MOUNTED, FULL BORE (API 6D)",
                    "orientation": "H",
                    "x": round(cx, 3),
                    "y": round(cy, 3),
                }
            )
        return out

    def stem_extension_v(
        self, x: float, y_valve: float, y_actuator: float, half: float = 1.5
    ) -> list[bd.Edge]:
        """Stem extension katup ditanam (1.5-2.5 m) — pasungan ganda vertikal.

        y_valve = puncak badan katup (sisi atas lingkaran bola dikurangi 0.14 mm
        agar ujung bawah pasungan menempel keliling lingkaran), y_actuator =
        dasar aktuator. Ujung atas menempel sisi bawah kotak aktuator.
        """
        y0 = y_valve - 0.14
        return [
            line(x - half, y0, x - half, y_actuator),
            line(x + half, y0, x + half, y_actuator),
        ]

    # -------------------------------------------------------------------------
    # 2. AKTUATOR GAS-OVER-OIL (FAIL-CLOSE OTONOM)
    # -------------------------------------------------------------------------
    def gas_over_oil_actuator(
        self,
        cx: float,
        y_bot: float,
        w: float = 36.0,
        h: float = 36.0,
        label: str = "GAS-OVER-OIL ACTUATOR",
        sublabel: str = "FAIL-CLOSE, AUTONOMOUS",
    ) -> list[bd.Edge]:
        """Kotak aktuator gas-over-oil dua ruang: gas (atas) / oli hidrolik (bawah).

        Akumulator gas bertekanan pipa menggerakkan oli penutup katup tanpa
        sumber tenaga eksternal (fail-safe). Label peralatan 2.5 mm di atas kotak.
        """
        hw = w / 2.0
        out = rect(cx - hw, y_bot, cx + hw, y_bot + h)
        out.append(line(cx - hw, y_bot + h / 2.0, cx + hw, y_bot + h / 2.0))
        # Nama ruang di dalam kotak
        self.text("GAS", cx, y_bot + h * 0.75, size=1.8)
        self.text("OIL", cx, y_bot + h * 0.25, size=1.8)
        if label:
            self.text(label, cx, y_bot + h + 6.5, size=2.5)
        if sublabel:
            self.text(sublabel, cx, y_bot + h + 11.5, size=1.8)
        self.schedule_equipment.append(
            {
                "tag": "GAS-OVER-OIL ACTUATOR",
                "type": "PNEUMATIC/HYDRAULIC ACTUATOR (GAS-OVER-OIL, FAIL-CLOSE)",
                "x": round(cx, 3),
                "y": round(y_bot + h / 2.0, 3),
            }
        )
        return out

    # -------------------------------------------------------------------------
    # 3. LINE BREAK PILOT (dP/dt)
    # -------------------------------------------------------------------------
    def line_break_pilot(
        self,
        x0: float,
        y0: float,
        w: float = 60.0,
        h: float = 24.0,
        title: str = "LINE BREAK PILOT",
        sub: str = "dP/dt RATE SENSING",
        setpoint: str = "SET > 0.5 BAR/MIN",
        tag: str = "LBP-7001",
    ) -> list[bd.Edge]:
        """Kotak pilot line break: sensor laju penurunan tekanan pipa.

        Memicu penutupan MLV seketika bila dP/dt melebihi setting (> 0.5 bar/menit).
        """
        out = rect(x0, y0, x0 + w, y0 + h)
        cx = x0 + w / 2.0
        self.text(title, cx, y0 + h - 7.0, size=2.0)
        self.text(sub, cx, y0 + h - 12.5, size=2.0)
        self.text(setpoint, cx, y0 + h - 18.0, size=2.0)
        if tag:
            self.schedule_instruments.append(
                {
                    "tag": tag,
                    "type": "LINE BREAK PILOT (dP/dt)",
                    "x": round(cx, 3),
                    "y": round(y0 + h / 2.0, 3),
                }
            )
        return out

    # -------------------------------------------------------------------------
    # 4. EMERGENCY HAND PUMP
    # -------------------------------------------------------------------------
    def hand_pump(
        self,
        x0: float,
        y0: float,
        w: float = 30.0,
        h: float = 24.0,
        l1: str = "EMERGENCY",
        l2: str = "HAND PUMP",
        tag: str = "HP-7001",
    ) -> list[bd.Edge]:
        """Pompa hidrolik manual darurat untuk membuka kembali MLV setelah inspeksi."""
        out = rect(x0, y0, x0 + w, y0 + h)
        cx = x0 + w / 2.0
        self.text(l1, cx, y0 + h - 8.0, size=1.8)
        self.text(l2, cx, y0 + h - 15.0, size=1.8)
        if tag:
            self.text(tag, cx, y0 - 5.0, size=2.5)
            self.schedule_equipment.append(
                {
                    "tag": tag,
                    "type": "EMERGENCY HAND PUMP (HYDRAULIC)",
                    "x": round(cx, 3),
                    "y": round(y0 + h / 2.0, 3),
                }
            )
        return out

    # -------------------------------------------------------------------------
    # 5. BLOWDOWN STACK (KATUP PENUTUP GANDA + CEROBONG VERTIKAL)
    # -------------------------------------------------------------------------
    def blowdown_stack_v(
        self,
        x: float,
        y_line: float,
        y_top: float,
        tags: tuple[str, str] = ("BD-7006A", "BD-7006B"),
        tag_dx: float = 9.0,
    ) -> list[bd.Edge]:
        """Cerobong blowdown vertikal dari pipa utama: 2 katup gate seri + bibir buang.

        Katup di y_line+22 dan y_line+46; riser berakhir di y_top dengan bibir
        (lip) horizontal 12 mm (mid-connection ke riser). Label TO ATMOSPHERE
        dan panah aliran ke atas ditambahkan otomatis.
        """
        y1, y2 = y_line + 22.0, y_line + 46.0
        out = pipe_run_v(x, y_line, y_top, gaps=[(y1, 5.0), (y2, 5.0)])
        out += self.valve_gate_v(x, y1, w=6.0, h=10.0, flanged=True, tag=tags[0])
        out += self.valve_gate_v(x, y2, w=6.0, h=10.0, flanged=True, tag=tags[1])
        # Bibir buang stack (12 mm, mid menempel ujung riser)
        out += [line(x - 6.0, y_top, x + 6.0, y_top)]
        # Panah aliran ke atas + label tujuan
        self.flow_arrow_v(x, y_top - 11.0, direction=1)
        self.text("TO ATM", x, y_top + 6.0, size=1.8)
        if tags[0]:
            self.text(tags[0], x + tag_dx, y1, size=1.8, left=True)
        if tags[1]:
            self.text(tags[1], x + tag_dx, y2, size=1.8, left=True)
        return out

    # -------------------------------------------------------------------------
    # 6. BYPASS EQUALIZING (DN50/DN80, 2 KATUP NC)
    # -------------------------------------------------------------------------
    def bypass_equalizing_h(
        self,
        x_left: float,
        x_right: float,
        y_line: float,
        y_bp: float,
        valve_tags: tuple[str, str] = ("BV-7005A", "BV-7005B"),
        label: str = "",
        w: float = 9.0,
        h: float = 5.4,
    ) -> list[bd.Edge]:
        """Bypass equalizing melingkari MLV: 2 riser + 2 katup globe NC seri.

        Menyeimbangkan tekanan hulu-hilir sebelum MLV dibuka. Riser menyambung
        tepat di garis utama (junction); pipa bypass pada y_bp di bawah garis utama.
        """
        dx_v = (x_right - x_left) / 2.0 - 13.0  # posisi katup relatif center
        cx = (x_left + x_right) / 2.0
        xv1, xv2 = cx - dx_v, cx + dx_v
        out = [
            line(x_left, y_line, x_left, y_bp),
            line(x_right, y_line, x_right, y_bp),
        ]
        hw = w / 2.0
        out += pipe_run_h(y_bp, x_left, x_right, gaps=[(xv1, hw), (xv2, hw)])
        out += self.valve_globe_h(xv1, y_bp, w=w, h=h, nc=True, flanged=False, tag=valve_tags[0])
        out += self.valve_globe_h(xv2, y_bp, w=w, h=h, nc=True, flanged=False, tag=valve_tags[1])
        self.flow_arrow_h(cx, y_bp, direction=1)
        if label:
            self.text(label, cx, y_bp - 8.0, size=1.8)
        return out

    # -------------------------------------------------------------------------
    # 7. TAP INSTRUMEN PT/PI & TAKE-OFF GAS AKTUATOR
    # -------------------------------------------------------------------------
    def instrument_tap_v(
        self,
        x: float,
        y_line: float,
        tag1: str = "PT",
        tag2: str = "7001",
        label: str = "",
    ) -> list[bd.Edge]:
        """Tap instrumen tekanan dari pipa utama: riser pendek + bubble ISA-5.1.

        Riser 24 mm, bubble r=6 pada y_line+30, label tag gabungan di y_line+40.
        """
        out = pipe_run_v(x, y_line, y_line + 24.0)
        self.sym += self.bubble(x, y_line + 30.0, tag1, tag2)
        if label:
            self.text(label, x, y_line + 40.0, size=2.0)
        return out

    def gas_supply_takeoff(
        self,
        x_tap: float,
        y_line: float,
        y_top: float,
        x_end: float,
        valve_tag: str = "GV-7005",
        label: str = "",
    ) -> list[bd.Edge]:
        """Take-off gas bertekanan pipa untuk aktuator gas-over-oil.

        Riser dari pipa utama (junction) dengan katup gate kecil, lalu horizontal
        menuju sisi kiri kotak aktuator (x_end, y_top). Ujung kanan menempel sisi
        kotak aktuator.
        """
        yv = y_line + 30.0
        hh_v = 4.2
        out = pipe_run_v(x_tap, y_line, y_top, gaps=[(yv, hh_v)])
        out += self.valve_gate_v(x_tap, yv, w=5.0, h=2 * hh_v, flanged=False, tag=valve_tag)
        out += pipe_run_h(y_top, x_tap, x_end)
        self.flow_arrow_h((x_tap + x_end) / 2.0, y_top, direction=1)
        if label:
            self.text(label, (x_tap + x_end) / 2.0 - 1.0, y_top + 5.0, size=1.8)
        return out

    def grade_line_h(
        self,
        x0: float,
        x1: float,
        y: float,
        brk: tuple[float, ...] | list[float] = (),
        label: str = "GRADE EL. +0.000",
        label_dx: float = 50.0,
        breaks: tuple[tuple[float, float], ...] | list[tuple[float, float]] = (),
    ) -> list[bd.Edge]:
        """Garis muka tanah (putus-putus, REF-EQUIP): MLV body buried below grade.

        brk = posisi break standar (jarak dari x0, gap 3 mm half=1.5).
        breaks = daftar (jarak dari x0, setengah lebar gap) untuk celah
        lebar-variabel: gap lebar pada stem extension ganda agar ujung dash
        tidak menempel garis stem, dan gap 3 mm pada persilangan line
        impulse/supply aktuator agar line proses tetap utuh (grade line
        yang menyingkir).
        """
        if breaks:
            L = x1 - x0
            runs: list[tuple[float, float]] = []
            a = 0.0
            for c, hw in sorted(breaks):
                if hw <= 0.0 or not (0.0 < c < L):
                    continue
                lo, hi = max(0.0, c - hw), min(L, c + hw)
                if lo > a:
                    runs.append((a, lo))
                a = max(a, hi)
            if L > a:
                runs.append((a, L))
            out: list[bd.Edge] = []
            for ra, rb in runs:
                if rb - ra >= 0.3:
                    out += dashed(x0 + ra, y, x0 + rb, y, dash=4.0, gap=1.6)
        else:
            out = dashed_brk(x0, y, x1, y, brk=list(brk))
        if label:
            self.text(label, x0 + label_dx, y + 5.0, size=1.5)
        return out

    # -------------------------------------------------------------------------
    # 8. MACRO: STATION LBCV LENGKAP (SATU PANGGILAN)
    # -------------------------------------------------------------------------
    def lbcv_station_h(
        self,
        x0: float,
        x1: float,
        y: float,
        cx: float = 250.0,
        mlv_tag: str = "MLV-7000",
        us_line: str = "300-ML-7001 DN600",
        ds_line: str = "300-ML-7002 DN600",
        bypass_line: str = "300-BP-7005 DN80",
        supply_line: str = "300-GS-7008",
        bd_us: tuple[str, str] = ("BD-7006A", "BD-7006B"),
        bd_ds: tuple[str, str] = ("BD-7007A", "BD-7007B"),
        pt_us: tuple[str, str] = ("PT", "7001"),
        pi_us: tuple[str, str] = ("PI", "7002"),
        pt_ds: tuple[str, str] = ("PT", "7003"),
        pi_ds: tuple[str, str] = ("PI", "7004"),
    ) -> dict:
        """Rakitan LBCV station lengkap pada garis utama horizontal (x0..x1, elevasi y).

        Tata letak (relatif cx=MLV center, default sheet A1):
          - MLV ball trunnion di cx, gap pipa (cx, w/2+1.2)
          - Stem extension + aktuator gas-over-oil di atas (y+36..y+72)
          - Pilot line break dP/dt kanan-atas (cx+34..cx+94, y+116..y+140)
            dengan sinyal sensing dari tap hulu (x=cx-140) dan output ke aktuator
          - Emergency hand pump kanan (cx+28..cx+58, y+36..y+60)
          - Take-off gas aktuator di x=cx-40 (katup kecil di y+30, sambung y+66)
          - Bypass equalizing di y-38 (riser cx-35 / cx+35, 2 katup NC)
          - Blowdown stack ganda: hulu x=cx-100, hilir x=cx+80 (puncak y+104)
          - Tap PT/PI tiap sisi (cx-155, cx-125, cx+140, cx+170)
          - Garis muka tanah y+12 dengan break pada stem (gap lebar) dan
            take-off gas aktuator (buried MLV)
          - Panah aliran & label line number 300-ML-7001/7002

        Returns:
            dict koordinat kunci (untuk test/QA): mlv, actuator, pilot, pump,
            stacks, bypass, ground.
        """
        # --- Pipa utama + MLV ---
        gap_mlv = 9.0 + 1.2  # hw bola + tick flensa
        self.proc += pipe_run_h(y, x0, x1, gaps=[(cx, gap_mlv)])
        self.proc += self.ball_valve_mlv_h(cx, y, w=18.0, h=9.0, tag=mlv_tag)
        self.text(mlv_tag, cx, y - 14.5, size=2.5)
        self.text("(BURIED)", cx, y - 20.0, size=1.8)

        # --- Stem extension + aktuator gas-over-oil ---
        self.equip += self.stem_extension_v(cx, y + 9.0, y + 36.0)
        self.equip += self.gas_over_oil_actuator(cx, y + 36.0)

        # --- Pilot line break dP/dt + sinyal sensing & output ---
        self.sym += self.line_break_pilot(cx + 34.0, y + 116.0)
        # Sinyal sensing dari tap hulu (REF-SIG dashed, tidak menembus apa pun)
        self.sig += dashed(cx - 140.0, y + 2.0, cx - 140.0, y + 130.0, dash=2.5, gap=1.2)
        self.sig += dashed(cx - 140.0, y + 130.0, cx + 34.0, y + 130.0, dash=2.5, gap=1.2)
        # Output pilot ke sisi kanan aktuator (bebas label & kotak hand pump)
        self.sig += dashed(cx + 54.0, y + 116.0, cx + 54.0, y + 64.0, dash=2.5, gap=1.2)
        self.sig += dashed(cx + 54.0, y + 64.0, cx + 18.0, y + 64.0, dash=2.5, gap=1.2)

        # --- Emergency hand pump + konektor hidrolik ke ruang OIL ---
        self.sym += self.hand_pump(cx + 28.0, y + 36.0)
        self.sigp += [line(cx + 18.0, y + 48.0, cx + 28.0, y + 48.0)]

        # --- Take-off gas aktuator ---
        self.proc += self.gas_supply_takeoff(
            cx - 40.0, y, y + 66.0, cx - 18.0, valve_tag="GV-7005", label=supply_line
        )

        # --- Bypass equalizing ---
        self.proc += self.bypass_equalizing_h(
            cx - 35.0, cx + 35.0, y, y - 38.0, label=bypass_line
        )

        # --- Blowdown stack ganda ---
        self.proc += self.blowdown_stack_v(cx - 100.0, y, y + 104.0, tags=bd_us)
        self.proc += self.blowdown_stack_v(cx + 80.0, y, y + 104.0, tags=bd_ds)

        # --- Tap instrumen PT/PI tiap sisi ---
        self.proc += self.instrument_tap_v(cx - 155.0, y, pt_us[0], pt_us[1], f"{pt_us[0]}-{pt_us[1]}")
        self.proc += self.instrument_tap_v(cx - 125.0, y, pi_us[0], pi_us[1], f"{pi_us[0]}-{pi_us[1]}")
        self.proc += self.instrument_tap_v(cx + 140.0, y, pi_ds[0], pi_ds[1], f"{pi_ds[0]}-{pi_ds[1]}")
        self.proc += self.instrument_tap_v(cx + 170.0, y, pt_ds[0], pt_ds[1], f"{pt_ds[0]}-{pt_ds[1]}")

        # --- Garis muka tanah (MLV buried): celah variabel pada stem extension
        # (half 4.0 -> bebas 2.5 mm dari tiap garis stem) dan pada take-off gas
        # aktuator di cx-40 (half 1.5 -> gap 3 mm) agar simbol aktuator dan
        # line impulse tetap utuh (grade line yang di-break) ---
        self.equip += self.grade_line_h(
            cx - 70.0,
            cx + 70.0,
            y + 12.0,
            breaks=[(30.0, 1.5), (70.0, 4.0)],
        )

        # --- Label nomor line hulu/hilir ---
        if us_line:
            self.text(us_line, cx - 113.0, y + 7.0, size=1.8)
        if ds_line:
            self.text(ds_line, cx + 125.0, y + 7.0, size=1.8)

        # --- Panah aliran garis utama ---
        for ax in (cx - 165.0, cx - 70.0, cx + 105.0, cx + 200.0, cx + 295.0):
            if x0 + 8.0 < ax < x1 - 8.0:
                self.flow_arrow_h(ax, y, direction=1)

        # --- Registrasi line list ---
        for ln, dn, svc in (
            (us_line.split(" ")[0], 600, "GAS TRANSMISSION UPSTREAM OF MLV"),
            (ds_line.split(" ")[0], 600, "GAS TRANSMISSION DOWNSTREAM OF MLV"),
            (bypass_line.split(" ")[0], 80, "MLV EQUALIZING BYPASS"),
            (supply_line.split(" ")[0], 50, "ACTUATOR GAS SUPPLY TAKE-OFF"),
        ):
            if ln:
                self.register_line(ln, spec="API 6D / ASME B31.8", service=svc, dn=dn)

        return {
            "mlv": (cx, y),
            "actuator": (cx, y + 36.0, y + 72.0),
            "pilot": (cx + 34.0, y + 116.0, cx + 94.0, y + 140.0),
            "pump": (cx + 28.0, y + 36.0, cx + 58.0, y + 60.0),
            "stacks": (cx - 100.0, cx + 80.0),
            "bypass_y": y - 38.0,
            "ground_y": y + 12.0,
        }
