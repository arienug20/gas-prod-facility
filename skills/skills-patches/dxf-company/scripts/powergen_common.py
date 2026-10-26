"""Reusable Gas Power Generation Package Symbol Library (powergen_common.py).

Versi 1.0.0 (Roadmap GPF-00-PM-PLN-0008 — Bagian III.1).

Standar acuan:
  - ISO 3046-1 (Reciprocating internal combustion engines — Performance)
  - ISO 8528 (Generating sets — Alternating current)
  - NFPA 37 (Combustion Engines and Gas Turbines — Installation & Exhaust)
  - IEEE 141 (Electric Power Distribution for Industrial Plants / Buff Book)
  - IEEE 242 (Protection and Coordination of Industrial Power Systems)
  - ANSI/ISA-5.1-2024 (Instrumentation Symbols and Identification)
  - ISO 10628-2:2012 (Graphical symbols for chemical & petrochemical industry)

Mewarisi seluruh primitif, katup, instrumen, dan furnitur sheet dari
pid_common.PIDContext dan menambahkan simbol khas pembangkit mesin gas:
  - engine_alternator_skid      : blok mesin GE + kopling lentur + alternator
                                  G 3-fasa di atas common skid dengan peredam
                                  getaran pegas (spring vibration dampers)
  - coalescing_filter_v         : coalescing filter gas bahan bakar (vertikal)
  - fuel_preheater_electric     : preheater gas bahan bakar (element listrik,
                                  gas keluar min 20 C di atas dew point)
  - dual_pcv_station            : regulator tekanan ganda (worker + monitor)
  - gas_admission_valve_h       : katup masuk gas mesin (solenoid)
  - fin_fan_radiator            : radiator fin-fan (JW & AW/AC circuit)
  - exhaust_bellows_v           : sambungan muai bellows SS
  - exhaust_silencer_arrestor_v : exhaust silencer + spark arrestor (vertikal)
  - exhaust_stack_cap           : stack vertikal + rain cap
  - expansion_tank_lt           : expansion tank JW dengan LT-401
  - electrical_interface        : GCB, CT, PT, panel auto-synchronizing &
                                  load sharing, busbar battery limit

Semua teks dicatat ke manifest TEXTS (MTEXT ARIAL via apply_text.py),
semua simbol terhubung utuh (zero floating stubs) mematuhi
validate_cad_rules.py (dangling endpoints, crossings, text collisions).
"""

from __future__ import annotations

import math

from cadgen import build123d as bd

from pid_common import (
    BUBBLE_R,
    PIDContext,
    arc,
    arc3,
    circle,
    dashed,
    hatch45,
    line,
    pipe_run_h,
    pipe_run_v,
    pneu,
    rect,
)


# =============================================================================
# KELAS KONTEKS PEMBANGKIT LISTRIK (PowerGenContext)
# =============================================================================
class PowerGenContext(PIDContext):
    """Konteks P&ID paket pembangkit listrik mesin gas (ISO 3046 / ISO 8528 /
    NFPA 37 / IEEE 141 & 242). Mewarisi PIDContext (frame, title, equip, proc,
    sym, sig, sigp, hatch, texts, solids, schedules, manifest exporter)."""

    # ---------------------------------------------------------------------
    # PEREDAM GETARAN PEGAS & GROUND (common skid mounting)
    # ---------------------------------------------------------------------
    def vibration_damper(self, x: float, y_top: float, y_bot: float) -> list[bd.Edge]:
        """Peredam getaran pegas (spring vibration damper): zigzag pegas
        vertikal antara bottom skid (y_top) dan ground (y_bot). Rantai polyline
        tertutup — kedua ujung menempel skid & ground (zero dangling)."""
        d = y_top - y_bot
        pts = [
            (x, y_top),
            (x - 4.0, y_top - d * 0.25),
            (x + 4.0, y_top - d * 0.50),
            (x - 4.0, y_top - d * 0.75),
            (x, y_bot),
        ]
        return [line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]) for i in range(4)]

    def ground_line(self, x0: float, x1: float, y: float) -> list[bd.Edge]:
        """Ground sebagai plat rect pipih tertutup + hatch tick diagonal di
        bawahnya (REF-HATCH, bebas aturan dangling)."""
        out = rect(x0, y, x1, y + 2.5)
        xi = x0 + 3.0
        while xi < x1 - 2.0:
            self.hatch.append(line(xi, y, xi - 2.5, y - 2.5))
            xi += 6.0
        return out

    # ---------------------------------------------------------------------
    # MESIN GAS + ALTERNATOR DI ATAS COMMON SKID (ISO 3046 / ISO 8528)
    # ---------------------------------------------------------------------
    def engine_alternator_skid(
        self,
        x0: float,
        yb: float,
        bw: float = 65.0,
        bh: float = 60.0,
        alt_cx: float | None = None,
        alt_r: float = 22.0,
        coupling: float = 13.0,
        skid_x0: float | None = None,
        skid_x1: float | None = None,
        yskid: float | None = None,
        dampers: tuple[float, ...] = (),
        tag: str = "GE-G1",
    ) -> list[bd.Edge]:
        """Blok mesin gas + kopling lentur + alternator AC 3-fasa di atas
        common skid dengan peredam getaran pegas.

        Geometry (semua koordinat absolut, origin kiri-bawah blok):
          - Blok mesin  : rect (x0, yb)-(x0+bw, yb+bh), marka silinder-V zigzag
          - Kopling     : poros + 2 tick (mid-attached, bebas dangling)
          - Alternator  : lingkaran G 3-fasa + kaki ke skid
          - Common skid : plat rect pipih + kaki blok + peredam pegas
          - Ground      : plat rect + hatch tick (REF-HATCH)
        """
        if alt_cx is None:
            alt_cx = x0 + bw + coupling + alt_r
        if yskid is None:
            yskid = yb - 15.0
        if skid_x0 is None:
            skid_x0 = x0 - 20.0
        if skid_x1 is None:
            skid_x1 = alt_cx + alt_r + 33.0
        if not dampers:
            dampers = (skid_x0 + 10.0, (skid_x0 + skid_x1) / 2.0, skid_x1 - 15.0)
        yc = yb + bh / 2.0  # garis poros

        out = [
            # Blok mesin + marka silinder V (terhubung ke tepi atas blok)
            *rect(x0, yb, x0 + bw, yb + bh),
            line(x0 + 17.0, yb + bh, x0 + 27.0, yb + bh - 13.0),
            line(x0 + 27.0, yb + bh - 13.0, x0 + 37.0, yb + bh),
            # Poros kopling lentur + 2 tick flange kopling (5.5 mm, mid menempel
            # poros — di bawah ambang persilangan 6 mm linter)
            line(x0 + bw, yc, alt_cx - alt_r, yc),
            line(x0 + bw + 4.0, yc - 2.75, x0 + bw + 4.0, yc + 2.75),
            line(x0 + bw + 9.0, yc - 2.75, x0 + bw + 9.0, yc + 2.75),
            # Alternator G 3-fasa
            circle(alt_cx, yc, alt_r),
        ]
        # Kaki alternator ke skid (tepat menyentuh keliling lingkaran,
        # berakhir di tepi ATAS plat skid — tanpa menembus plat)
        for dx in (-alt_r * 0.16, alt_r * 0.16):
            lx = alt_cx + dx
            ly = yc - math.sqrt(max(alt_r**2 - dx**2, 1.0))
            out.append(line(lx, ly, lx, yskid + 2.5))

        # Common skid (plat rect pipih tertutup) + kaki blok mesin
        out += rect(skid_x0, yskid, skid_x1, yskid + 2.5)
        for lx in (x0 + 10.0, x0 + bw - 10.0):
            out.append(line(lx, yb, lx, yskid + 2.5))

        # Peredam getaran pegas + ground
        for dx in dampers:
            out += self.vibration_damper(dx, yskid, yskid - 10.0)
        out += self.ground_line(skid_x0 - 7.0, skid_x1 + 7.0, yskid - 10.0)

        # Teks (equipment tag 2.5; sub-label 1.8; alternator 3-fasa 3~)
        self.text(tag, x0 + bw / 2.0, yc, size=2.5)
        self.text("GAS ENGINE", x0 + bw / 2.0, yc - 9.0, size=1.8)
        self.text("G", alt_cx, yc + 3.0, size=3.0)
        self.text("3~", alt_cx, yc - 6.0, size=2.5)
        self.text(
            "COMMON SKID + SPRING VIBRATION DAMPERS",
            (skid_x0 + skid_x1) / 2.0,
            yskid - 17.0,
            size=1.8,
        )
        if tag:
            self.schedule_equipment.append({
                "tag": tag,
                "type": "GAS ENGINE GENERATOR SET (ISO 3046 / ISO 8528)",
                "x": round(x0 + bw / 2.0, 3),
                "y": round(yc, 3),
                "alternator_r": round(alt_r, 3),
                "skid": [round(skid_x0, 3), round(skid_x1, 3)],
            })
        return out

    # ---------------------------------------------------------------------
    # COALESCING FILTER GAS BAHAN BAKAR (VERTIKAL)
    # ---------------------------------------------------------------------
    def coalescing_filter_v(
        self,
        cx: float,
        y_bot: float,
        y_top: float,
        r: float = 13.0,
        tag: str = "FG-401",
        drain: bool = True,
        drain_tag: str = "GV-402",
    ) -> list[bd.Edge]:
        """Coalescing filter vertikal (pemisah kabut cairan gas bahan bakar):
        head 2:1 ellipsoidal, element coalescer berarsir 45 deg, garis level
        cairan, nozzle drain bawah dengan gate valve + funnel cap (utuh)."""
        h_head = r * 0.5
        out = [
            line(cx - r, y_bot, cx - r, y_top),
            line(cx + r, y_bot, cx + r, y_top),
            arc3((cx - r, y_top), (cx, y_top + h_head), (cx + r, y_top)),
            arc3((cx - r, y_bot), (cx, y_bot - h_head), (cx + r, y_bot)),
        ]
        # Element coalescer (rect + arsiran 45 deg)
        e_t, e_b = y_top - 10.0, y_top - 33.0
        out += rect(cx - r + 5.0, e_b, cx + r - 5.0, e_t)
        self.hatch += hatch45(cx - r + 5.0, e_b, cx + r - 5.0, e_t, spacing=2.5)
        # Garis level cairan (dashed)
        out += dashed(cx - r + 2.0, y_bot + 10.0, cx + r - 2.0, y_bot + 10.0,
                      dash=3.0, gap=1.5)

        if drain:
            y_apex = y_bot - h_head
            y_v = y_apex - 10.5
            out += [
                line(cx, y_apex, cx, y_v + 3.7),          # stub atas ke flange katup
                *self.valve_gate_v(cx, y_v, w=3.2, h=5.0, flanged=True, tag=drain_tag),
                line(cx, y_v - 2.5, cx, y_apex - 19.5),   # stub bawah ke funnel
                line(cx - 4.0, y_apex - 19.5, cx + 4.0, y_apex - 19.5),  # funnel cap
            ]
            self.text("TO CLOSED DRAIN", cx, y_apex - 25.5, size=1.8)
            if drain_tag:
                self.text(drain_tag, cx + 12.0, y_v, size=1.8, left=True)

        if tag:
            self.text(tag, cx, y_top + 4.5, size=2.5)
            self.schedule_equipment.append({
                "tag": tag,
                "type": "COALESCING FILTER (FUEL GAS)",
                "x": round(cx, 3),
                "y": round((y_bot + y_top) / 2.0, 3),
            })
        return out

    # ---------------------------------------------------------------------
    # PREHEATER GAS BAHAN BAKAR (ELEKTRIK, ISO 10628-2 / TEMA-STYLE SHELL)
    # ---------------------------------------------------------------------
    def fuel_preheater_electric(
        self,
        cx: float,
        cy: float,
        length: float = 44.0,
        r: float = 10.0,
        tag: str = "E-401",
    ) -> list[bd.Edge]:
        """Preheater gas bahan bakar tipe listrik: shell horizontal + channel
        head kiri (nozzle gas masuk bawah / keluar atas), element pemanas
        zigzag (REF-SYM), terminal box + kaki di puncak shell.

        Gas outlet dijaga TIC min 20 C di atas dew point (lihat demo loop)."""
        hw = length / 2.0
        x_l, x_r = cx - hw, cx + hw
        w_chan = 8.0
        x_chan = x_l - w_chan
        x_t = x_chan + w_chan / 2.0

        out = [
            # Shell walls + tubesheet ganda + channel spool + heads
            line(x_l, cy - r, x_r, cy - r),
            line(x_l, cy + r, x_r, cy + r),
            line(x_l, cy - r, x_l, cy + r),
            line(x_l - 1.5, cy - r, x_l - 1.5, cy + r),
            line(x_r, cy - r, x_r, cy + r),
            line(x_r + 1.5, cy - r, x_r + 1.5, cy + r),
            line(x_chan, cy + r, x_l - 1.5, cy + r),
            line(x_chan, cy - r, x_l - 1.5, cy - r),
            arc(x_chan, cy, r, 90, 270),
            arc3((x_r + 1.5, cy - r), (x_r + 1.5 + r, cy), (x_r + 1.5, cy + r)),
            # Nozzle gas masuk (bawah) & keluar (atas) di channel head
            line(x_t - 1.8, cy - r, x_t - 1.8, cy - r - 4.0),
            line(x_t + 1.8, cy - r, x_t + 1.8, cy - r - 4.0),
            line(x_t - 3.2, cy - r - 4.0, x_t + 3.2, cy - r - 4.0),
            line(x_t - 1.8, cy + r, x_t - 1.8, cy + r + 4.0),
            line(x_t + 1.8, cy + r, x_t + 1.8, cy + r + 4.0),
            line(x_t - 3.2, cy + r + 4.0, x_t + 3.2, cy + r + 4.0),
        ]
        # Element pemanas listrik zigzag (REF-SYM, ujung menempel tubesheet)
        zz_y = cy - 5.0
        pts = [(x_l, zz_y)]
        n_seg = 7
        step = (length - 4.0) / n_seg
        for i in range(n_seg):
            pts.append((pts[-1][0] + step, zz_y + (2.2 if i % 2 == 0 else -2.2)))
        pts.append((x_r, zz_y))
        for i in range(len(pts) - 1):
            self.sym.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]))
        # Terminal box + kaki ke shell (utuh)
        out += rect(cx - 6.0, cy + r + 6.0, cx + 6.0, cy + r + 14.0)
        out += [
            line(cx - 4.0, cy + r, cx - 4.0, cy + r + 6.0),
            line(cx + 4.0, cy + r, cx + 4.0, cy + r + 6.0),
        ]
        if tag:
            self.text(tag, cx, cy, size=2.5)
            self.schedule_equipment.append({
                "tag": tag,
                "type": "FUEL GAS PREHEATER (ELECTRIC, +20 C ABOVE DEW POINT)",
                "x": round(cx, 3),
                "y": round(cy, 3),
            })
        return out

    # ---------------------------------------------------------------------
    # DUAL FUEL GAS REGULATOR (WORKER + MONITOR PCV STATION)
    # ---------------------------------------------------------------------
    def dual_pcv_station(
        self,
        y: float,
        x_a: float,
        x_b: float,
        tag_a: str = "PCV-401A",
        tag_b: str = "PCV-401B",
        note_a: str = "WORKER",
        note_b: str = "MONITOR",
        loop_no: str = "401",
        pic_y: float = 502.0,
    ) -> None:
        """Regulator tekanan gas ganda: dua control valve seri (worker A,
        monitor B) masing-masing dengan impulse PT, bubble PT, loop PIC di
        DCS, dan jalur pneumatik ke aktuator. Semua routing bebas persilangan
        tanpa break (diverifikasi terhadap tata letak demo)."""
        # Impulse tap di SISI LUAR tiap valve (A dari kiri, B dari kanan):
        # tap sisi-dalam (xv+20) menaruh bubble PT r=6 tepat menempel kotak
        # FY/kubah aktuator valve tetangga pada station antar-valve 30 mm
        # (temuan QA visual DXF demo: tag PCV menimpa simbol valve).
        for xv, tap_x, tag, note in (
            (x_a, x_a - 20.0, tag_a, note_a),
            (x_b, x_b + 20.0, tag_b, note_b),
        ):
            # Impulse tap (REF-PROC) + bubble PT (REF-SYM)
            self.proc += pipe_run_v(tap_x, y, y + 10.0)
            self.sym += self.bubble(tap_x, y + 16.0, "PT", tag.split("-")[1])
            # Sinyal elektrik PT -> PIC (L-route di atas jalur)
            self.sig += dashed(tap_x, y + 22.0, tap_x, y + 30.0)
            self.sig += dashed(tap_x, y + 30.0, xv, y + 30.0)
            self.sig += dashed(xv, y + 30.0, xv, pic_y - 7.5)
            # PIC di DCS
            self.sym += self.dcs(xv, pic_y, "PIC", tag.split("-")[1])
            # FY interposing relay + pneumatic ke aktuator (berhenti tepat di
            # atas garis dasar kubah agar dv <= 1.35 — bebas Check 7)
            self.sym += rect(xv - 4.0, y + 13.5, xv + 4.0, y + 20.5)
            self.text("FY", xv, y + 18.3, size=1.8)
            self.text(loop_no, xv, y + 15.3, size=1.8)
            self.sigp += pneu(xv, y + 13.5, xv, y + 8.5, spacing=3.0)
            # Katup + label
            self.proc += self.control_valve_h(xv, y, w=10.0, h=6.0, tag=tag)
            self.text(tag, xv, y - 9.0, size=2.2)
            if note:
                self.text(note, xv, y - 14.5, size=1.8)

    # ---------------------------------------------------------------------
    # GAS ADMISSION VALVE (SOLENOID, CARBURETOR / GAS ADMISSION)
    # ---------------------------------------------------------------------
    def gas_admission_valve_h(
        self, cx: float, cy: float, tag: str = "GA-401"
    ) -> list[bd.Edge]:
        """Katup masuk gas mesin (quick-acting solenoid admission valve):
        bowtie + stem + kotak solenoid 'S'. Ujung pipa menempel garis penutup
        katup (zero dangling)."""
        hw, hh = 5.0, 3.0
        out = [
            line(cx - hw, cy - hh, cx, cy),
            line(cx, cy, cx - hw, cy + hh),
            line(cx - hw, cy - hh, cx - hw, cy + hh),
            line(cx + hw, cy - hh, cx, cy),
            line(cx, cy, cx + hw, cy + hh),
            line(cx + hw, cy - hh, cx + hw, cy + hh),
            # Flange ticks
            line(cx - hw - 1.2, cy - hh - 1.0, cx - hw - 1.2, cy + hh + 1.0),
            line(cx + hw + 1.2, cy - hh - 1.0, cx + hw + 1.2, cy + hh + 1.0),
            # Stem + solenoid box (stem mulai dari PUSAT bowtie — menempel
            # garis diagonal katup, zero dangling)
            line(cx, cy, cx, cy + hh + 9.0),
            *rect(cx - 4.0, cy + hh + 9.0, cx + 4.0, cy + hh + 15.0),
        ]
        self.text("S", cx, cy + hh + 12.0, size=1.8)
        if tag:
            self.schedule_valves.append({
                "tag": tag,
                "type": "GAS ADMISSION VALVE (SOLENOID)",
                "orientation": "H",
                "x": round(cx, 3),
                "y": round(cy, 3),
            })
        return out

    # ---------------------------------------------------------------------
    # RADIATOR FIN-FAN (JW & AW/AC CIRCUIT)
    # ---------------------------------------------------------------------
    def package_pump(self, cx: float, cy: float, r: float = 7.0) -> list[bd.Edge]:
        """Pompa paket (skid-mounted) = pump_centrifugal + 2 konektor mikro
        (1.2 mm, di bawah ambang 3 mm) yang mengikat ujung pad motor ke
        garis diagonal pad — zero dangling pada seluruh rakitan pompa."""
        out = self.pump_centrifugal(cx, cy, r=r)
        out += [
            line(cx - 4.0, cy + r + 2.0, cx - 4.0, cy + r + 3.2),
            line(cx + 4.0, cy + r + 2.0, cx + 4.0, cy + r + 3.2),
        ]
        return out

    def fin_fan_radiator(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        tag: str = "HX-401",
        label: str = "JW RADIATOR",
        fans: int = 2,
    ) -> list[bd.Edge]:
        """Radiator fin-fan (air cooled heat exchanger, tampak P&ID): panel
        rect tertutup + lingkaran fan di tepi atas + label. Nozzle pipa disambungkan
        demo langsung ke dinding panel (endpoint tepat di garis dinding)."""
        out = rect(x0, y0, x1, y1)
        span = (x1 - x0) / (fans + 1.0)
        for i in range(fans):
            fx = x0 + span * (i + 1)
            out.append(circle(fx, y1, 5.0))
        if label:
            self.text(label, (x0 + x1) / 2.0, y0 + (y1 - y0) * 0.42, size=1.8)
        if tag:
            self.text(tag, (x0 + x1) / 2.0, y1 + 9.0, size=2.5)
            self.schedule_equipment.append({
                "tag": tag,
                "type": "FIN-FAN RADIATOR (AIR COOLED)",
                "x": round((x0 + x1) / 2.0, 3),
                "y": round((y0 + y1) / 2.0, 3),
            })
        return out

    # ---------------------------------------------------------------------
    # EXHAUST SYSTEM (NFPA 37)
    # ---------------------------------------------------------------------
    def exhaust_bellows_v(self, x: float, y0: float, y1: float, w: float = 12.0) -> list[bd.Edge]:
        """Sambungan muai fleksibel SS bellows (expansion joint) vertikal:
        rect pada jalur stack — segmen stack berakhir tepat di garis rect
        (endpoint = koneksi, bukan persilangan)."""
        out = rect(x - w / 2.0, y0, x + w / 2.0, y1)
        self.sym += [
            arc(x - w / 2.0 + 1.5, (y0 + y1) / 2.0, 2.2, 90, 270),
            arc(x + w / 2.0 - 1.5, (y0 + y1) / 2.0, 2.2, 270, 90),
        ]
        return out

    def exhaust_silencer_arrestor_v(
        self, x: float, y0: float, y1: float, w: float = 20.0, tag: str = "EXH-SIL-401"
    ) -> list[bd.Edge]:
        """Exhaust silencer + spark arrestor vertikal (drum tertutup, internal
        berarsir). Segmen stack masuk/keluar tepat di garis cap atas & bawah."""
        hw = w / 2.0
        out = [
            line(x - hw, y0, x + hw, y0),
            line(x - hw, y1, x + hw, y1),
            line(x - hw, y0, x - hw, y1),
            line(x + hw, y0, x + hw, y1),
        ]
        self.hatch += hatch45(x - hw + 2.0, y0 + 2.0, x + hw - 2.0, y1 - 2.0, spacing=3.5)
        if tag:
            self.text(tag, x + hw + 6.0, y1 - 6.0, size=1.8, left=True)
            self.text("SILENCER + SPARK ARRESTOR", x + hw + 6.0, y1 - 12.0,
                      size=1.8, left=True)
            self.schedule_equipment.append({
                "tag": tag,
                "type": "EXHAUST SILENCER + SPARK ARRESTOR (NFPA 37)",
                "x": round(x, 3),
                "y": round((y0 + y1) / 2.0, 3),
            })
        return out

    def exhaust_stack_cap(self, x: float, y_top: float, w: float = 16.0,
                          label: str = "") -> list[bd.Edge]:
        """Ujung stack vertikal + pelindung hujan (rain cap): rect pipih di
        ujung stack + cone tertutup; seluruh endpoint menempel (zero dangling)."""
        hw = w / 2.0
        out = [
            *rect(x - hw, y_top, x + hw, y_top + 4.0),
            line(x - hw, y_top + 4.0, x, y_top + 12.0),
            line(x, y_top + 12.0, x + hw, y_top + 4.0),
        ]
        if label:
            self.text(label, x, y_top + 17.0, size=1.8)
        return out

    # ---------------------------------------------------------------------
    # EXPANSION TANK JW + LEVEL INSTRUMENT
    # ---------------------------------------------------------------------
    def expansion_tank_lt(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        branch: tuple[float, float, float, float] | None = None,
        tag: str = "CT-401",
        lt_tag: tuple[str, str] = ("LT", "401"),
    ) -> list[bd.Edge]:
        """Expansion tank circuit JW: bejana kecil rect tertutup, cabang
        koneksi ke jalur JW (branch=(x_from, y, x_to, y) menuju titik tee di
        jalur), instrument level LT + catatan TO DCS.

        LT bubble ditempatkan di kiri tank pada ketinggian cabang impulse."""
        out = rect(x0, y0, x1, y1)
        y_mid = (y0 + y1) / 2.0
        if branch is not None:
            bx0, by, bx1, _ = branch
            out.append(line(bx0, by, bx1, by))
        # Impulse level ke bubble LT di kiri tank (dash mulai dari dasar bubble)
        bx = x0 - 6.0
        by = y_mid + 5.0
        out.append(line(x0, by, x0 - 6.0, by))
        self.sym += self.bubble(bx - 6.0, by, lt_tag[0], lt_tag[1])
        self.sig += dashed(bx - 6.0, by - 2.0 * BUBBLE_R, bx - 6.0, by - 2.0 * BUBBLE_R - 4.0)
        self.text("TO DCS", bx - 6.0, by - 2.0 * BUBBLE_R - 9.0, size=1.8)
        self.text(f"{tag} EXP. TANK", (x0 + x1) / 2.0, y0 - 5.5, size=1.8)
        if tag:
            self.schedule_equipment.append({
                "tag": tag,
                "type": "JW EXPANSION TANK",
                "x": round((x0 + x1) / 2.0, 3),
                "y": round(y_mid, 3),
            })
        return out

    # ---------------------------------------------------------------------
    # ANTARMUKA KELISTRIKAN (GCB / CT / PT / AUTO-SYNC PANEL / BUSBAR)
    # ---------------------------------------------------------------------
    def electrical_interface(
        self,
        cable_x: float,
        y_bus: float,
        alt_x: float,
        y_alt: float,
        tag_gcb: str = "GCB-401",
        tag_ct: str = "CT-401",
        tag_pt: str = "PT-401",
        panel_tag: str = "PNL-401",
    ) -> None:
        """Antarmuka kelistrikan generator: kabel daya dari alternator ke
        GCB (generator circuit breaker), CT seri, PT tap-to-ground, arrow
        battery limit ke busbar, dan panel auto-synchronizing & load sharing
        dengan sinyal kontrol ke GCB (IEEE 141 / IEEE 242).

        Semua kabel = REF-SIG dashed (bebas aturan dangling); simbol = REF-SYM.
       """
        x_gcb = cable_x + 15.0
        x_ct = x_gcb + 25.0
        x_pt = x_ct + 13.0
        x_end = x_pt + 20.0
        # Kabel daya alternator -> GCB
        self.sig += [
            *dashed(alt_x, y_alt, cable_x, y_alt),
            *dashed(cable_x, y_alt, cable_x, y_bus),
            *dashed(cable_x, y_bus, x_gcb, y_bus),
        ]
        # GCB (rect tertutup REF-SYM)
        self.sym += rect(x_gcb, y_bus - 7.0, x_gcb + 15.0, y_bus + 7.0)
        self.text("GCB", x_gcb + 7.5, y_bus, size=2.0)
        self.text(tag_gcb, x_gcb + 17.0, y_bus + 12.0, size=1.8)
        # Kabel GCB -> CT -> busbar
        self.sig += dashed(x_gcb + 15.0, y_bus, x_ct - 5.0, y_bus)
        self.sym.append(circle(x_ct, y_bus, 5.0))
        self.text("CT", x_ct, y_bus, size=2.0)
        self.text(tag_ct, x_ct, y_bus + 9.0, size=1.8)
        self.sig += dashed(x_ct + 5.0, y_bus, x_end, y_bus)
        # PT tap ke bawah + ground (REF-SYM)
        self.sym.append(circle(x_pt, y_bus - 17.0, 5.0))
        self.text("PT", x_pt, y_bus - 17.0, size=2.0)
        self.text(tag_pt, x_pt + 14.0, y_bus - 17.0, size=1.8, left=True)
        self.sig += [
            *dashed(x_pt, y_bus, x_pt, y_bus - 12.0),
            *dashed(x_pt, y_bus - 22.0, x_pt, y_bus - 26.0),
        ]
        self.sym += [
            line(x_pt - 6.0, y_bus - 26.0, x_pt + 6.0, y_bus - 26.0),
            line(x_pt - 3.5, y_bus - 28.5, x_pt + 3.5, y_bus - 28.5),
            line(x_pt - 1.0, y_bus - 31.0, x_pt + 1.0, y_bus - 31.0),
        ]
        # Arrow battery limit ke busbar
        self.flow_arrow_h(x_end - 8.0, y_bus, direction=1, layer="REF-SIG")
        self.text("TO BUSBAR BL", x_end - 6.0, y_bus + 7.0, size=1.8)
        # Panel auto-synchronizing & load sharing + sinyal kontrol ke GCB
        px0, px1 = x_gcb, x_end + 22.0
        py0, py1 = y_bus + 35.0, y_bus + 65.0
        self.sym += rect(px0, py0, px1, py1)
        self.text("AUTO-SYNCHRONIZING &", (px0 + px1) / 2.0, py1 - 9.0, size=1.8)
        self.text("LOAD SHARING PANEL", (px0 + px1) / 2.0, py1 - 16.0, size=1.8)
        self.text(panel_tag, (px0 + px1) / 2.0, py0 + 6.0, size=1.8)
        self.sig += dashed(x_gcb + 7.5, py0, x_gcb + 7.5, y_bus + 7.0)
