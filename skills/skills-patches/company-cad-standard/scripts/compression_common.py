"""Reusable Gas Compression Package Symbol Library (API 618 / API 617 / API 661 / TEMA).

Versi 1.0.0 (Compression & Rotating Equipment CAD Suite).
Sumber kebenaran: dokumen/dokumen/08-plan-pipeline-metering-lbcv-underground.md
Bagian II (GPF-00-PM-PLN-0008 Rev A2).

Standar acuan:
  - API STD 618 / ISO 13631 (Reciprocating Compressors, pulsation Design
    Approach 3, valve unloader 0-50-100 %, lube oil + FSL, distance piece
    packing purge ke flare)
  - API STD 617 (Centrifugal Compressors, barrel / horizontally split
    casing, dry gas seal DGS, anti-surge loop ASV fast-opening + UIC)
  - API STD 661 / ISO 13706 (Air-Cooled Heat Exchanger, auto-louver TIC)
  - TEMA Standards (Shell & Tube exchanger)
  - ANSI/ISA-5.1-2024, ISO 10628-2:2012 (simbol & tagging)

Wajib di-import oleh semua script P&ID paket kompresi agar simbol kompresor
torak/sentrifugal, pulsation dampener, scrubber, fin-fan, coalescer, drain
LV otomatis, anti-surge valve, dan furniture box BL 100% konsisten.
"""

from __future__ import annotations

import math

from cadgen import build123d as bd

from pid_common import (
    BUBBLE_R,
    PIDContext,
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
# KONTEKS PAKET KOMPRESI (memperluas PIDContext)
# =============================================================================
class CompressionContext(PIDContext):
    """Konteks P&ID paket kompresi gas (A1, API 618/617/661, TEMA)."""

    # -------------------------------------------------------------------------
    # KOMPRESOR TORAK DOUBLE-ACTING (API STD 618 / ISO 13631)
    # -------------------------------------------------------------------------
    def compressor_reciprocating(
        self,
        cx: float,
        line_y: float,
        tag: str = "K-201",
        driver: str = "M",
        stage_label: str = "",
        fsl_loop: str = "",
    ) -> dict:
        """Kompresor torak double-acting lengkap sesuai API STD 618.

        Isi simbol (semua koordinat turunan dari cx dan line_y):
          - Driver motor listrik `M` / gas engine `GE` (lingkaran + kaki)
          - Kopling poros, crankcase + crankshaft, crosshead
          - Distance piece (purge packing keluar port bawah, x = cx-3)
          - Silinder double-acting + piston + 4 katup piringan otomatis
          - Actuator valve unloader 0-50-100 % di puncak silinder
          - Stub nozzle hisap (cx+6) & tekan (cx+18) menuju pulsation
            dampener di line_y (stub digambar di sini)
          - Line injeksi lube oil + bubble FSL di bawah silinder
          - Baseplate skid
        Mengembalikan dict titik sambung untuk wiring demo/test.
        """
        cy = line_y - 13.0          # garis poros shaflight
        y_base = cy - 15.0
        y_cyl_top, y_cyl_bot = cy + 6.0, cy - 6.0

        out = [
            # Baseplate (hanya di bawah motor + crankcase; purge drop bebas)
            line(cx - 44.0, y_base, cx - 8.0, y_base),
            line(cx - 44.0, y_base - 1.2, cx - 8.0, y_base - 1.2),
            line(cx - 44.0, y_base - 1.2, cx - 44.0, y_base),
            line(cx - 8.0, y_base - 1.2, cx - 8.0, y_base),
            # Motor + kaki (endpoint kaki tepat pada keliling lingkaran)
            circle(cx - 34.0, cy, 7.0),
            line(cx - 38.95, cy - 4.95, cx - 40.0, y_base),
            line(cx - 29.05, cy - 4.95, cx - 28.0, y_base),
            # Kopling poros
            line(cx - 27.0, cy, cx - 20.0, cy),
            # Crankcase + crankshaft
            line(cx - 20.0, cy - 9.0, cx - 8.0, cy - 9.0),
            line(cx - 8.0, cy - 9.0, cx - 8.0, cy + 9.0),
            line(cx - 8.0, cy + 9.0, cx - 20.0, cy + 9.0),
            line(cx - 20.0, cy + 9.0, cx - 20.0, cy - 9.0),
            circle(cx - 14.0, cy, 2.6),
            # Kaki crankcase ke baseplate
            line(cx - 18.0, cy - 9.0, cx - 18.0, y_base),
            line(cx - 10.0, cy - 9.0, cx - 10.0, y_base),
            # Distance piece (purge packing keluar port bawah di cx-3)
            line(cx - 8.0, cy - 3.5, cx + 2.0, cy - 3.5),
            line(cx + 2.0, cy - 3.5, cx + 2.0, cy + 3.5),
            line(cx + 2.0, cy + 3.5, cx - 8.0, cy + 3.5),
            # Crosshead + piston rod + piston
            line(cx - 8.0, cy - 2.5, cx - 4.0, cy - 2.5),
            line(cx - 4.0, cy - 2.5, cx - 4.0, cy + 2.5),
            line(cx - 4.0, cy + 2.5, cx - 8.0, cy + 2.5),
            line(cx - 4.0, cy, cx + 7.0, cy),
            line(cx + 7.0, cy - 3.5, cx + 11.0, cy - 3.5),
            line(cx + 11.0, cy - 3.5, cx + 11.0, cy + 3.5),
            line(cx + 11.0, cy + 3.5, cx + 7.0, cy + 3.5),
            line(cx + 7.0, cy + 3.5, cx + 7.0, cy - 3.5),
            # Silinder double-acting
            line(cx + 2.0, y_cyl_bot, cx + 22.0, y_cyl_bot),
            line(cx + 22.0, y_cyl_bot, cx + 22.0, y_cyl_top),
            line(cx + 22.0, y_cyl_top, cx + 2.0, y_cyl_top),
            line(cx + 2.0, y_cyl_top, cx + 2.0, y_cyl_bot),
            # 4 katup piringan otomatis (plate valves, 2 ujung x hisap/tekan)
            line(cx + 4.0, cy + 3.0, cx + 6.0, cy + 3.0),
            line(cx + 6.0, cy + 3.0, cx + 6.0, cy + 4.5),
            line(cx + 6.0, cy + 4.5, cx + 4.0, cy + 4.5),
            line(cx + 4.0, cy + 4.5, cx + 4.0, cy + 3.0),
            line(cx + 4.0, cy - 4.5, cx + 6.0, cy - 4.5),
            line(cx + 6.0, cy - 4.5, cx + 6.0, cy - 3.0),
            line(cx + 6.0, cy - 3.0, cx + 4.0, cy - 3.0),
            line(cx + 4.0, cy - 3.0, cx + 4.0, cy - 4.5),
            line(cx + 18.0, cy + 3.0, cx + 20.0, cy + 3.0),
            line(cx + 20.0, cy + 3.0, cx + 20.0, cy + 4.5),
            line(cx + 20.0, cy + 4.5, cx + 18.0, cy + 4.5),
            line(cx + 18.0, cy + 4.5, cx + 18.0, cy + 3.0),
            line(cx + 18.0, cy - 4.5, cx + 20.0, cy - 4.5),
            line(cx + 20.0, cy - 4.5, cx + 20.0, cy - 3.0),
            line(cx + 20.0, cy - 3.0, cx + 18.0, cy - 3.0),
            line(cx + 18.0, cy - 3.0, cx + 18.0, cy - 4.5),
            # Actuator valve unloader 0-50-100 % (kotak kecil di puncak silinder)
            line(cx + 11.0, y_cyl_top, cx + 15.0, y_cyl_top),
            line(cx + 15.0, y_cyl_top, cx + 15.0, cy + 9.5),
            line(cx + 15.0, cy + 9.5, cx + 11.0, cy + 9.5),
            line(cx + 11.0, cy + 9.5, cx + 11.0, y_cyl_top),
            # Stub hisap & tekan menuju pulsation dampener di line_y
            line(cx + 6.0, y_cyl_top, cx + 6.0, line_y),
            line(cx + 18.0, y_cyl_top, cx + 18.0, line_y),
            # Lube oil injection line (dari bawah silinder ke bubble FSL)
            line(cx + 15.0, y_cyl_bot, cx + 15.0, cy - 14.0),
            line(cx + 15.0, cy - 14.0, cx + 26.0, cy - 14.0),
        ]
        self.equip += out

        self.text(driver, cx - 34.0, cy, size=2.2)
        if tag:
            self.text(tag, cx - 15.0, cy - 20.0, size=2.5)
        if stage_label:
            self.text(stage_label, cx - 15.0, cy - 25.0, size=1.8)
        self.text("0-50-100 %", cx - 15.0, cy - 30.0, size=1.8)

        fsl_x = cx + 32.0
        self.sym += self.bubble(fsl_x, cy - 14.0, "FSL", fsl_loop)
        self.text("LUBE OIL", fsl_x, cy - 25.0, size=1.8)

        if tag:
            self.schedule_equipment.append({
                "tag": tag,
                "type": "RECIPROCATING COMPRESSOR (API STD 618)",
                "x": round(cx, 3),
                "y": round(cy, 3),
                "driver": driver,
            })
        return {
            "cx": cx,
            "cy": cy,
            "line_y": line_y,
            "suction_x": cx + 6.0,
            "discharge_x": cx + 18.0,
            "purge_x": cx - 3.0,
            "purge_y": cy - 3.5,
            "lube_start": (cx + 15.0, y_cyl_bot),
            "fsl_xy": (fsl_x, cy - 14.0),
        }

    # -------------------------------------------------------------------------
    # PULSATION DAMPENER (API 618 DESIGN APPROACH 3)
    # -------------------------------------------------------------------------
    def pulsation_dampener(self, x: float, line_y: float, tag: str = "") -> list:
        """Botol pulsasi vertikal duduk di atas line proses (dinding + dome)."""
        y_top = line_y + 14.0
        out = [
            line(x - 3.5, line_y, x - 3.5, y_top),
            line(x + 3.5, line_y, x + 3.5, y_top),
            arc3((x - 3.5, y_top), (x, y_top + 3.0), (x + 3.5, y_top)),
        ]
        self.equip += out
        if tag:
            self.text(tag, x, y_top + 8.0, size=1.8)
            self.schedule_equipment.append({
                "tag": tag,
                "type": "PULSATION DAMPENER (API 618 DA-3)",
                "x": round(x, 3),
                "y": round(line_y, 3),
            })
        return out

    # -------------------------------------------------------------------------
    # SUCTION SCRUBBER VERTIKAL (API SPEC 12J) + DRAIN APEX
    # -------------------------------------------------------------------------
    def suction_scrubber(
        self,
        cx: float,
        y_bot: float,
        y_top: float,
        r: float = 20.0,
        tag: str = "V-201",
        service: str = "SUCTION SCRUBBER",
        inlet_y: float | None = None,
        label_tag: bool = True,
    ) -> dict:
        """Scrubber vertikal 2:1: dinding, head ellipsoidal, seam, skirt,
        demister, inlet deflector, nozzle hisap samping, nozzle atas
        (gas out & PSV), drain apex + vortex breaker."""
        inlet_y = inlet_y if inlet_y is not None else y_bot + 0.5 * (y_top - y_bot)
        h_head = r * 0.5
        apex = y_bot - h_head
        out = [
            line(cx - r, y_bot, cx - r, y_top),
            line(cx + r, y_bot, cx + r, y_top),
            arc3((cx - r, y_top), (cx, y_top + h_head), (cx + r, y_top)),
            arc3((cx - r, y_bot), (cx, apex), (cx + r, y_bot)),
        ]
        out += dashed(cx - r, y_bot, cx + r, y_bot, dash=3.0, gap=1.5)
        out += dashed(cx - r, y_top, cx + r, y_top, dash=3.0, gap=1.5)

        # Skirt + base ring
        y_sk = y_bot - 7.0
        out += [
            line(cx - r, y_bot, cx - r, y_sk),
            line(cx + r, y_bot, cx + r, y_sk),
            line(cx - r - 2.5, y_sk, cx + r + 2.5, y_sk),
            line(cx - r - 2.5, y_sk - 1.2, cx + r + 2.5, y_sk - 1.2),
            line(cx - r - 2.5, y_sk - 1.2, cx - r - 2.5, y_sk),
            line(cx + r + 2.5, y_sk - 1.2, cx + r + 2.5, y_sk),
        ]

        # Demister pad
        y_d1, y_d2 = y_top - 3.0, y_top - 9.0
        w_d = r - 2.0
        out += rect(cx - w_d, y_d2, cx + w_d, y_d1)
        self.hatch += hatch45(cx - w_d, y_d2, cx + w_d, y_d1, spacing=2.5)

        # Inlet deflector + nozzle hisap samping kiri (stub ke tick terluar)
        out += [
            arc3((cx - r + 2.0, inlet_y - 11.0), (cx - r + 5.0, inlet_y), (cx - r + 2.0, inlet_y + 11.0)),
            line(cx - r, inlet_y - 2.5, cx - r - 3.2, inlet_y - 2.5),
            line(cx - r, inlet_y + 2.5, cx - r - 3.2, inlet_y + 2.5),
            line(cx - r - 2.0, inlet_y - 6.0, cx - r - 2.0, inlet_y + 6.0),
            line(cx - r - 3.2, inlet_y - 6.0, cx - r - 3.2, inlet_y + 6.0),
        ]

        # Nozzle atas: gas outlet (kanan) & PSV (kiri). Stub menembus head
        # hingga flange ganda di y_top+12 (bebas zona lengkung head arc),
        # tick flange vertikal 1.2 mm di ujung.
        dx_out, dx_psv = 0.4 * r, -0.4 * r
        y_fl1, y_fl2 = y_top + 12.0, y_top + 13.2
        yc_head, r_head = y_top - 0.75 * r, 1.25 * r
        for dx in (dx_out, dx_psv):
            for ddx in (-5.0, 5.0):
                y_arc = yc_head + math.sqrt(r_head ** 2 - (dx + ddx) ** 2)
                out.append(line(cx + dx + ddx, y_arc, cx + dx + ddx, y_fl1))
            out += [
                line(cx + dx - 6.0, y_fl1, cx + dx + 6.0, y_fl1),
                line(cx + dx - 6.0, y_fl2, cx + dx + 6.0, y_fl2),
                line(cx + dx - 6.0, y_fl1, cx + dx - 6.0, y_fl2),
                line(cx + dx + 6.0, y_fl1, cx + dx + 6.0, y_fl2),
            ]

        # Drain apex + vortex breaker inverted-T + flange drain
        out += [
            line(cx - 4.0, apex + 4.0, cx + 4.0, apex + 4.0),
            line(cx, apex, cx, apex + 4.0),
            line(cx, apex, cx, apex - 5.0),
            line(cx - 2.8, apex - 5.0, cx + 2.8, apex - 5.0),
            line(cx - 2.8, apex - 6.2, cx + 2.8, apex - 6.2),
        ]
        self.equip += out

        if label_tag and tag:
            self.text(tag, cx, y_top - 25.0, size=2.5)
            if service:
                self.text(service, cx, y_top - 31.0, size=2.0)
            self.schedule_equipment.append({
                "tag": tag,
                "type": "VERTICAL GAS SCRUBBER (API SPEC 12J)",
                "x": round(cx, 3),
                "y": round(y_bot, 3),
                "r": round(r, 3),
            })
        return {
            "inlet_x": cx - r - 2.0,
            "inlet_y": inlet_y,
            "outlet_x": cx + dx_out,
            "psv_x": cx + dx_psv,
            "top_flange_y": y_fl2,
            "drain_x": cx,
            "drain_y": apex - 6.2,
            "shell_right": cx + r,
            "shell_left": cx - r,
        }

    # -------------------------------------------------------------------------
    # COALESCING FILTER SEPARATOR VERTIKAL
    # -------------------------------------------------------------------------
    def coalescing_filter(
        self,
        cx: float,
        y_bot: float,
        y_top: float,
        r: float = 14.0,
        tag: str = "F-201",
        inlet_y: float | None = None,
    ) -> dict:
        """Coalescing filter separator: vessel vertikal + elemen coalescer
        berarsir + demister + drain apex. Nozzle inlet samping kiri."""
        inlet_y = inlet_y if inlet_y is not None else y_bot + 0.55 * (y_top - y_bot)
        h_head = r * 0.5
        apex = y_bot - h_head
        out = [
            line(cx - r, y_bot, cx - r, y_top),
            line(cx + r, y_bot, cx + r, y_top),
            arc3((cx - r, y_top), (cx, y_top + h_head), (cx + r, y_top)),
            arc3((cx - r, y_bot), (cx, apex), (cx + r, y_bot)),
        ]
        out += dashed(cx - r, y_bot, cx + r, y_bot, dash=3.0, gap=1.5)
        out += dashed(cx - r, y_top, cx + r, y_top, dash=3.0, gap=1.5)

        # Elemen coalescer + demister
        y_e1, y_e2 = inlet_y - 23.0, inlet_y + 17.0
        w_e = r - 2.0
        out += rect(cx - w_e, y_e1, cx + w_e, y_e2)
        self.hatch += hatch45(cx - w_e, y_e1, cx + w_e, y_e2, spacing=2.8)
        y_d1, y_d2 = y_top - 3.0, y_top - 8.0
        out += rect(cx - w_e, y_d2, cx + w_e, y_d1)
        self.hatch += hatch45(cx - w_e, y_d2, cx + w_e, y_d1, spacing=2.2)

        # Nozzle inlet kiri (stub tembus ke tick flange terluar)
        out += [
            line(cx - r, inlet_y - 2.5, cx - r - 3.2, inlet_y - 2.5),
            line(cx - r, inlet_y + 2.5, cx - r - 3.2, inlet_y + 2.5),
            line(cx - r - 2.0, inlet_y - 5.5, cx - r - 2.0, inlet_y + 5.5),
            line(cx - r - 3.2, inlet_y - 5.5, cx - r - 3.2, inlet_y + 5.5),
        ]

        # Gas outlet puncak (flange y_top+12/13.2, stub berbasis arc head)
        y_fl1, y_fl2 = y_top + 12.0, y_top + 13.2
        yc_head, r_head = y_top - 0.75 * r, 1.25 * r
        for ddx in (-5.0, 5.0):
            y_arc = yc_head + math.sqrt(r_head ** 2 - ddx ** 2)
            out.append(line(cx + ddx, y_arc, cx + ddx, y_fl1))
        out += [
            line(cx - 6.0, y_fl1, cx + 6.0, y_fl1),
            line(cx - 6.0, y_fl2, cx + 6.0, y_fl2),
            line(cx - 6.0, y_fl1, cx - 6.0, y_fl2),
            line(cx + 6.0, y_fl1, cx + 6.0, y_fl2),
            line(cx, apex, cx, apex - 5.0),
            line(cx - 2.8, apex - 5.0, cx + 2.8, apex - 5.0),
            line(cx - 2.8, apex - 6.2, cx + 2.8, apex - 6.2),
        ]
        self.equip += out

        if tag:
            self.text(tag, cx, y_e2 + 6.0, size=2.5)
            self.schedule_equipment.append({
                "tag": tag,
                "type": "COALESCING FILTER SEPARATOR",
                "x": round(cx, 3),
                "y": round(y_bot, 3),
                "r": round(r, 3),
            })
        return {
            "inlet_x": cx - r - 2.0,
            "inlet_y": inlet_y,
            "outlet_x": cx,
            "top_flange_y": y_top + 7.2,
            "drain_x": cx,
            "drain_y": apex - 6.2,
            "shell_right": cx + r,
        }

    # -------------------------------------------------------------------------
    # FIN-FAN AIR COOLER (API STD 661 / ISO 13706)
    # -------------------------------------------------------------------------
    def fin_fan_cooler(
        self,
        cx: float,
        line_y: float,
        tag: str = "E-201",
        hw: float = 25.0,
        tee_dx: float = 20.0,
    ) -> dict:
        """Fin-fan: bundle finned tube (box + arsiran), auto louver (tick
        diagonal), fan + motor M, riser tees ke line proses di bawah."""
        y0, y1 = line_y + 8.0, line_y + 30.0
        out = rect(cx - hw, y0, cx + hw, y1)
        self.hatch += hatch45(cx - hw + 2.0, y0 + 2.0, cx + hw - 2.0, y1 - 2.0, spacing=3.0)

        # Auto louver (tick diagonal di atas bundle, REF-SYM — bukan pipa)
        louver: list = []
        x = cx - hw + 2.0
        while x + 3.0 <= cx + hw - 2.0:
            louver.append(line(x, y1 + 1.0, x + 3.0, y1 + 5.0))
            x += 4.0
        self.sym += louver

        # Fan + blades + shaft + motor
        y_fan = line_y + 44.0
        out += [
            circle(cx, y_fan, 7.0),
            line(cx - 5.0, y_fan - 6.0, cx + 5.0, y_fan + 6.0),
            line(cx - 5.0, y_fan + 6.0, cx + 5.0, y_fan - 6.0),
            line(cx + 7.0, y_fan, cx + 9.5, y_fan),
            circle(cx + 14.0, y_fan, 4.5),
        ]
        self.text("M", cx + 14.0, y_fan, size=2.0)

        # Riser tees
        out += [
            line(cx - tee_dx, line_y, cx - tee_dx, y0),
            line(cx + tee_dx, line_y, cx + tee_dx, y0),
        ]
        self.equip += out

        if tag:
            self.schedule_equipment.append({
                "tag": tag,
                "type": "AIR COOLED HEAT EXCHANGER (API STD 661)",
                "x": round(cx, 3),
                "y": round(line_y, 3),
                "hw": round(hw, 3),
            })
        return {
            "tee_in": cx - tee_dx,
            "tee_out": cx + tee_dx,
            "bundle_top": y1,
            "louver_y": y1 + 3.0,
            "fan_xy": (cx, y_fan),
        }

    # -------------------------------------------------------------------------
    # ANTI-SURGE VALVE (GLOBE FAST-OPENING + BOOSTER RELAY FY)
    # -------------------------------------------------------------------------
    def anti_surge_valve_h(
        self,
        cx: float,
        cy: float,
        tag: str = "ASV-201",
        fail: str = "FC",
        fy_no: str = "201",
    ) -> list:
        """ASV: globe control valve + kubah diafragma + FY booster relay
        (kotak I/P/P) + sinyal pneumatik. Fast-opening <= 1.0 s (note)."""
        out = self.control_valve_h(cx, cy, w=10.0, h=6.0, tag=tag, fail="")
        # Booster relay FY di atas kubah dome (dome top = cy+12.5)
        out += rect(cx - 4.0, cy + 16.0, cx + 4.0, cy + 22.0)
        self.sym += out
        self.text("FY", cx, cy + 20.0, size=1.8)
        if fy_no:
            self.text(fy_no, cx, cy + 17.6, size=1.8)
        self.sigp += pneu(cx, cy + 16.0, cx, cy + 12.5, spacing=3.0)
        if tag:
            self.text(tag, cx, cy - 7.0, size=2.2)
        if fail:
            self.text(fail, cx, cy - 11.5, size=1.8)
        return out

    # -------------------------------------------------------------------------
    # KOMPRESOR SENTRIFUGAL API STD 617 (BARREL / H-SPLIT) + DGS
    # -------------------------------------------------------------------------
    def compressor_centrifugal_617(
        self,
        cx: float,
        cy: float,
        r_in: float = 5.0,
        r_out: float = 8.0,
        tag: str = "K-301",
        casing: str = "BARREL",
        driver: str = "M",
    ) -> dict:
        """Kompresor sentrifugal casing tirus ISO 10628-2 + DGS.
        casing: 'BARREL' (vertically split, cincin joint) atau
        'H-SPLIT' (horizontally split, seam putus-putus).
        Ukuran ringkas sehingga cocok untuk legend / kanvas test."""
        hw = 8.0
        slope = (r_in - r_out) / (2.0 * hw)
        out = [
            line(cx - hw, cy - r_out, cx - hw, cy + r_out),
            line(cx + hw, cy - r_in, cx + hw, cy + r_in),
            line(cx - hw, cy + r_out, cx + hw, cy + r_in),
            line(cx - hw, cy - r_out, cx + hw, cy - r_in),
        ]
        if casing == "BARREL":
            out += [
                line(cx - hw - 2.0, cy - 10.0, cx + hw + 2.0, cy - 10.0),
                line(cx + hw + 2.0, cy - 10.0, cx + hw + 2.0, cy + 10.0),
                line(cx + hw + 2.0, cy + 10.0, cx - hw - 2.0, cy + 10.0),
                line(cx - hw - 2.0, cy + 10.0, cx - hw - 2.0, cy - 10.0),
            ]
        else:
            out += dashed(cx - hw, cy, cx + hw, cy, dash=3.0, gap=1.5)

        # Shaft + Dry Gas Seal (DGS) di sisi discharge + seal pot
        out += [
            line(cx + hw, cy, cx + hw + 8.0, cy),
            *rect(cx + hw + 3.0, cy - 2.5, cx + hw + 7.0, cy + 2.5),
            line(cx + hw + 5.0, cy + 2.5, cx + hw + 5.0, cy + 8.0),
            circle(cx + hw + 5.0, cy + 10.5, 2.5),
        ]

        # Driver + kopling + baseplate
        y_base = cy - max(r_out, 10.0) - 4.0
        out += [
            line(cx - hw - 6.0, cy, cx - hw, cy),
            circle(cx - hw - 11.0, cy, 5.0),
            line(cx - hw - 14.0, cy - 4.0, cx - hw - 14.6, y_base),
            line(cx - hw - 8.0, cy - 4.0, cx - hw - 7.4, y_base),
            line(cx - hw - 16.0, y_base, cx + hw + 8.0, y_base),
            line(cx - hw - 16.0, y_base - 1.2, cx + hw + 8.0, y_base - 1.2),
            line(cx - hw - 16.0, y_base - 1.2, cx - hw - 16.0, y_base),
            line(cx + hw + 8.0, y_base - 1.2, cx + hw + 8.0, y_base),
        ]
        self.equip += out

        self.text(driver, cx - hw - 11.0, cy, size=2.2)
        if tag:
            self.text(tag, cx, y_base - 5.0, size=2.5)
            self.schedule_equipment.append({
                "tag": tag,
                "type": f"CENTRIFUGAL COMPRESSOR API STD 617 ({casing})",
                "x": round(cx, 3),
                "y": round(cy, 3),
            })
        return {"cx": cx, "cy": cy, "dgs_x": cx + hw + 5.0}

    # -------------------------------------------------------------------------
    # SHELL & TUBE HEAT EXCHANGER TEMA
    # -------------------------------------------------------------------------
    def shell_tube_tema(
        self,
        cx: float,
        cy: float,
        length: float = 40.0,
        r: float = 10.0,
        tag: str = "E-301",
        tema: str = "AES",
    ) -> dict:
        """Shell & tube TEMA: channel head + cover, tubesheet, shell,
        bundle (dashed), bonnet rear, 4 nozzle, saddles, label TEMA."""
        hw = length / 2.0
        x_l, x_r = cx - hw, cx + hw
        out = [
            # Channel head + cover (kiri) + tubesheet
            line(x_l - 6.0, cy - r, x_l, cy - r),
            line(x_l, cy - r, x_l, cy + r),
            line(x_l, cy + r, x_l - 6.0, cy + r),
            line(x_l - 6.0, cy + r, x_l - 6.0, cy - r),
            line(x_l - 4.5, cy - r, x_l - 4.5, cy + r),
            # Shell
            line(x_l, cy - r, x_r, cy - r),
            line(x_l, cy + r, x_r, cy + r),
            # Rear bonnet (kanan, arc3)
            arc3((x_r, cy - r), (x_r + 5.0, cy), (x_r, cy + r)),
            # Tube bundle (dashed)
            dashed(x_l + 3.0, cy - r + 3.0, x_r - 3.0, cy - r + 3.0, dash=3.0, gap=1.5),
            dashed(x_l + 3.0, cy + r - 3.0, x_r - 3.0, cy + r - 3.0, dash=3.0, gap=1.5),
            # Nozzle shell (bawah kiri / atas kanan) + channel (atas kiri)
            line(cx - length * 0.25, cy - r, cx - length * 0.25, cy - r - 4.0),
            line(cx - length * 0.25 - 2.2, cy - r - 4.0, cx - length * 0.25 + 2.2, cy - r - 4.0),
            line(cx + length * 0.25, cy + r, cx + length * 0.25, cy + r + 4.0),
            line(cx + length * 0.25 - 2.2, cy + r + 4.0, cx + length * 0.25 + 2.2, cy + r + 4.0),
            line(x_l - 3.0, cy + r, x_l - 3.0, cy + r + 4.0),
            line(x_l - 5.2, cy + r + 4.0, x_l - 0.8, cy + r + 4.0),
            # Saddles
            line(cx - length * 0.3, cy - r, cx - length * 0.3 - 1.2, cy - r - 3.5),
            line(cx - length * 0.3 + 2.4, cy - r, cx - length * 0.3 + 3.6, cy - r - 3.5),
            line(cx - length * 0.3 - 2.4, cy - r - 3.5, cx - length * 0.3 + 4.8, cy - r - 3.5),
            line(cx + length * 0.3 - 1.2, cy - r, cx + length * 0.3 - 2.4, cy - r - 3.5),
            line(cx + length * 0.3 + 1.2, cy - r, cx + length * 0.3 + 2.4, cy - r - 3.5),
            line(cx + length * 0.3 - 3.6, cy - r - 3.5, cx + length * 0.3 + 3.6, cy - r - 3.5),
        ]
        self.equip += out

        if tag:
            self.text(tag, cx, cy - r - 8.5, size=2.5)
            if tema:
                self.text(f"TEMA {tema}", cx, cy + r + 7.5, size=1.8)
            self.schedule_equipment.append({
                "tag": tag,
                "type": f"SHELL & TUBE EXCHANGER (TEMA {tema})",
                "x": round(cx, 3),
                "y": round(cy, 3),
            })
        return {"cx": cx, "cy": cy, "shell_in_x": cx - length * 0.25}

    # -------------------------------------------------------------------------
    # DRAIN LV OTOMATIS ANTAR TINGKAT (drop -> jog -> LV -> header)
    # -------------------------------------------------------------------------
    def drain_lv_h(
        self,
        x: float,
        y_start: float,
        y_valve: float,
        y_header: float,
        tag_lv: str = "LV-201",
        lic_tag: str = "",
        dir: int = 1,
        breaks1: tuple = (),
        breaks2: tuple = (),
    ) -> tuple:
        """Drain otomatis scrubber/coalescer: drop vertikal (dengan break
        opsional), jog horizontal, control valve LV, drop ke drain header.
        Mengembalikan titik tee (dx, y_header)."""
        sx = x + dir * 8.0
        dx = x + dir * 18.0
        out = pipe_run_v(x, y_valve, y_start, gaps=[(b, 1.5) for b in breaks1])
        out += [line(x, y_valve, sx - dir * 6.2, y_valve)]
        out += self.control_valve_h(sx, y_valve, w=10.0, h=6.0, tag=tag_lv)
        out += [line(sx + dir * 6.2, y_valve, dx, y_valve)]
        out += pipe_run_v(dx, y_header, y_valve, gaps=[(b, 1.5) for b in breaks2])
        self.proc += out
        self.text(tag_lv, sx, y_valve - 10.0, size=1.8)
        return (dx, y_header)

    # -------------------------------------------------------------------------
    # BOX BATTERY LIMIT / KONTINUITAS ARAH KONFIGURABEL
    # -------------------------------------------------------------------------
    def bl_box(
        self,
        y: float,
        x0: float,
        x1: float,
        tag: str,
        desc: str,
        dwg: str = "",
        dir: int = 1,
    ) -> list:
        """Kotak kontinuitas battery-limit; dir=1 ujung panah ke kanan,
        dir=-1 ujung panah ke kiri (flat side menerima line proses)."""
        hh = 5.0
        tip = x1 + 4.5 if dir >= 0 else x0 - 4.5
        if dir >= 0:
            out = [
                line(x0, y - hh, x1, y - hh),
                line(x1, y - hh, tip, y),
                line(tip, y, x1, y + hh),
                line(x1, y + hh, x0, y + hh),
                line(x0, y + hh, x0, y - hh),
            ]
        else:
            out = [
                line(x0, y - hh, x1, y - hh),
                line(x1, y - hh, x1, y + hh),
                line(x1, y + hh, x0, y + hh),
                line(x0, y + hh, tip, y),
                line(tip, y, x0, y - hh),
            ]
        self.proc += out
        mid = (x0 + x1) / 2.0
        if dwg:
            self.text(dwg, mid, y, size=1.8)
        if desc:
            self.text(desc, mid, y + hh + 2.5, size=2.0)
        if tag:
            self.text(tag, mid, y - hh - 2.5, size=1.8)
        return out

    # -------------------------------------------------------------------------
    # DROP VERTIKAL DENGAN BREAK + KATUP OPSIONAL (BDV / PURGE)
    # -------------------------------------------------------------------------
    def drop_v(
        self,
        x: float,
        y0: float,
        y1: float,
        breaks: tuple = (),
        valve_y: float | None = None,
        valve_w: float = 3.2,
        valve_h: float = 5.0,
        valve_tag: str = "",
        valve_flanged: bool = False,
    ) -> list:
        """Pipa vertikal x dari y0 ke y1 dengan break 3 mm pada `breaks`
        dan gate valve vertikal opsional di valve_y."""
        gaps = [(b, 1.5) for b in breaks]
        if valve_y is not None:
            gaps.append((valve_y, valve_h / 2.0))
        out = pipe_run_v(x, y0, y1, gaps=gaps)
        if valve_y is not None:
            out += self.valve_gate_v(
                x, valve_y, w=valve_w, h=valve_h, flanged=valve_flanged, tag=valve_tag
            )
        self.proc += out
        return out
