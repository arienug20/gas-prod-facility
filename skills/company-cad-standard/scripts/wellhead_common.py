"""Reusable Wellhead & Christmas Tree Symbol Library (API SPEC 6A / ISO 10423, API RP 14C).

Versi 1.0.0 (Modul Hulu — GPF-00-PM-PLN-0008 Bagian I).

Standar acuan:
  - API SPEC 6A / ISO 10423 (Wellhead and Christmas Tree Equipment)
  - API RP 14C (Analysis, Design, Installation and Testing of Safety Systems)
  - ANSI/ISA-5.1-2024 (Instrumentation Symbols and Identification)
  - ISO 10628-2:2012 (Graphical symbols for chemical & petrochemical industry)
  - Referensi blueprint: dokumen/08-plan-pipeline-metering-lbcv-underground.md (Bagian I)

Katalog komponen (subclass WellheadContext di atas PIDContext agar manifest
TEXTS/SOLIDS, schedule MTO, dan furniture layer REF-* 100% seragam):
  1. valve_gate_manual_h/v     — LMV / KWV / Swab (Crown) Valve, gate manual T-bar.
  2. valve_gate_hydraulic_h/v  — UMV / PWV, gate + aktuator hidrolik fail-close (FC).
  3. valve_needle_h            — katup jarum outlet annulus A/B/C.
  4. choke_adjustable_h        — choke adjustable (jarum karbida + mikrometer).
  5. choke_positive_h          — choke positive (rumah jepitan + choke bean tetap).
  6. bleeder_valve_h           — bleeder valve kecil (puncak tree).
  7. tubing_head_flange        — flensa kepala tubing (THF).
  8. wellbore                  — casing + tubing di bawah flensa (gap otomatis utk SCSSV).
  9. scssv                     — SCSSV/DHSV downhole (fail-close, hyd open).
 10. annulus_outlet_h          — outlet annulus lengkap: stub + needle valve + PI.
 11. gauge_pi                  — bubble PI (ANSI/ISA-5.1).
 12. panel_box                 — kotak panel hidrolik ESD sumur.
 13. hydraulic_signal          — sinyal hidraulik dashed REF-SIG dengan break 3 mm.

Semua simbol mematuhi linter cad/validate_cad_rules.py: ujung REF-PROC/REF-EQUIP
terhubung (tanpa dangling), garis minor di-break gap 3 mm pada persilangan, dan
seluruh teks dicatat via manifest (MTEXT ARIAL, 0.5–3.0 mm) — tanpa bd.Text.
"""

from __future__ import annotations

from cadgen import build123d as bd

from pid_common import (
    BUBBLE_R,
    PIDContext,
    dashed_brk,
    hatch45,
    line,
    pipe_run_h,
    pipe_run_v,
    rect,
)

VERSION = "1.0.0"


# =============================================================================
# KELAS KONTEKS WELLHEAD (API SPEC 6A / API RP 14C)
# =============================================================================
class WellheadContext(PIDContext):
    """Konteks pembuat drawing kepala sumur & christmas tree (A1, ISO 10628-2 & ISA-5.1).

    Mewarisi seluruh mekanisme PIDContext (manifest TEXTS/SOLIDS, panah aliran,
    bubble instrumen, continuity box, schedule MTO, export JSON) dan menambahkan
    katalog simbol API SPEC 6A di bawah ini.
    """

    def text_right(self, t: str, x: float, y: float, size: float = 1.8) -> None:
        """Catat MTEXT rata-kanan (attachment 6) — untuk label di sisi kiri simbol."""
        if not t:
            return
        self.text(t, x, y, size=size)
        self.texts[-1]["att"] = 6

    # -------------------------------------------------------------------------
    # KATUP GATE MANUAL (LMV / KWV / SWAB-CROWN) — API SPEC 6A
    # -------------------------------------------------------------------------
    def valve_gate_manual_h(
        self, cx: float, cy: float, w: float = 10.0, h: float = 6.0, tag: str = ""
    ) -> list[bd.Edge]:
        """Gate valve manual horizontal (T-bar handwheel) — LMV/KWV/bleeder."""
        out = self.valve_gate_h(cx, cy, w=w, h=h, flanged=(w >= 8.0))
        if tag:
            self.schedule_valves.append({
                "tag": tag,
                "type": "GATE VALVE (MANUAL, API 6A)",
                "orientation": "H",
                "x": round(cx, 3),
                "y": round(cy, 3),
            })
        return out

    def valve_gate_manual_v(
        self, cx: float, cy: float, w: float = 6.0, h: float = 10.0, tag: str = ""
    ) -> list[bd.Edge]:
        """Gate valve manual vertikal (T-bar handwheel) — LMV/Swab (Crown) Valve."""
        out = self.valve_gate_v(cx, cy, w=w, h=h, flanged=(h >= 8.0))
        if tag:
            self.schedule_valves.append({
                "tag": tag,
                "type": "GATE VALVE (MANUAL, API 6A)",
                "orientation": "V",
                "x": round(cx, 3),
                "y": round(cy, 3),
            })
        return out

    # -------------------------------------------------------------------------
    # KATUP GATE HIDRAULIK FAIL-CLOSE (UMV / PWV) — API SPEC 6A & API RP 14C
    # -------------------------------------------------------------------------
    def valve_gate_hydraulic_h(
        self,
        cx: float,
        cy: float,
        w: float = 10.0,
        h: float = 6.0,
        act_w: float = 12.0,
        act_h: float = 8.0,
        tag: str = "",
        fail: str = "FC",
    ) -> list[bd.Edge]:
        """Gate valve horizontal + aktuator hidrolik spring-return fail-close.

        Bowtie + tick flensa, stem ke atas, kotak aktuator (label 'H'), dan teks
        fail action di kanan kotak. Kotak aktuator terhubung penuh (tanpa stub
        menggantung) sehingga lolos Check 6 dangling endpoints.
        """
        hw, hh = w / 2.0, h / 2.0
        stem_top = cy + hh + 3.0
        by0, by1 = stem_top, stem_top + act_h
        bx0, bx1 = cx - act_w / 2.0, cx + act_w / 2.0
        out = [
            line(cx - hw, cy - hh, cx - hw, cy + hh),
            line(cx + hw, cy - hh, cx + hw, cy + hh),
            line(cx - hw, cy - hh, cx, cy),
            line(cx, cy, cx - hw, cy + hh),
            line(cx + hw, cy - hh, cx, cy),
            line(cx, cy, cx + hw, cy + hh),
            # Tick flensa
            line(cx - hw - 1.2, cy - hh - 1.0, cx - hw - 1.2, cy + hh + 1.0),
            line(cx + hw + 1.2, cy - hh - 1.0, cx + hw + 1.2, cy + hh + 1.0),
            # Stem ke kotak aktuator
            line(cx, cy + hh, cx, stem_top),
        ]
        out += rect(bx0, by0, bx1, by1)
        self.text("H", cx, (by0 + by1) / 2.0, size=2.0)
        if fail:
            self.text(fail, bx1 + 2.5, (by0 + by1) / 2.0, size=1.8, left=True)
        if tag:
            self.schedule_valves.append({
                "tag": tag,
                "type": "GATE VALVE (HYDRAULIC ACTUATOR, FAIL-CLOSE)",
                "orientation": "H",
                "x": round(cx, 3),
                "y": round(cy, 3),
                "fail": fail,
            })
        return out

    def valve_gate_hydraulic_v(
        self,
        cx: float,
        cy: float,
        w: float = 6.0,
        h: float = 10.0,
        act_w: float = 12.0,
        act_h: float = 8.0,
        tag: str = "",
        fail: str = "FC",
    ) -> list[bd.Edge]:
        """Gate valve vertikal + aktuator hidrolik spring-return fail-close (UMV)."""
        hw, hh = w / 2.0, h / 2.0
        stem_top = cy + hh + 3.0
        by0, by1 = stem_top, stem_top + act_h
        bx0, bx1 = cx - act_w / 2.0, cx + act_w / 2.0
        out = [
            line(cx - hw, cy - hh, cx + hw, cy - hh),
            line(cx - hw, cy + hh, cx + hw, cy + hh),
            line(cx - hw, cy - hh, cx, cy),
            line(cx + hw, cy - hh, cx, cy),
            line(cx - hw, cy + hh, cx, cy),
            line(cx + hw, cy + hh, cx, cy),
            # Tick flensa (vertikal: tick horizontal atas & bawah)
            line(cx - hw - 0.8, cy - hh - 1.2, cx + hw + 0.8, cy - hh - 1.2),
            line(cx - hw - 0.8, cy + hh + 1.2, cx + hw + 0.8, cy + hh + 1.2),
            # Stem ke kotak aktuator
            line(cx, cy + hh, cx, stem_top),
        ]
        out += rect(bx0, by0, bx1, by1)
        self.text("H", cx, (by0 + by1) / 2.0, size=2.0)
        if fail:
            self.text_right(fail, bx0 - 2.5, (by0 + by1) / 2.0, size=1.8)
        if tag:
            self.schedule_valves.append({
                "tag": tag,
                "type": "GATE VALVE (HYDRAULIC ACTUATOR, FAIL-CLOSE)",
                "orientation": "V",
                "x": round(cx, 3),
                "y": round(cy, 3),
                "fail": fail,
            })
        return out

    # -------------------------------------------------------------------------
    # KATUP JARUM & CHOKE (API SPEC 6A)
    # -------------------------------------------------------------------------
    def valve_needle_h(
        self, cx: float, cy: float, w: float = 6.0, h: float = 4.0, tag: str = ""
    ) -> list[bd.Edge]:
        """Katup jarum kecil (outlet annulus A/B/C) — bowtie + stem + T-bar mini."""
        hw, hh = w / 2.0, h / 2.0
        out = [
            line(cx - hw, cy - hh, cx - hw, cy + hh),
            line(cx + hw, cy - hh, cx + hw, cy + hh),
            line(cx - hw, cy - hh, cx, cy),
            line(cx, cy, cx - hw, cy + hh),
            line(cx + hw, cy - hh, cx, cy),
            line(cx, cy, cx + hw, cy + hh),
            line(cx, cy + hh, cx, cy + hh + 2.5),
            line(cx - 2.0, cy + hh + 2.5, cx + 2.0, cy + hh + 2.5),
        ]
        if tag:
            self.schedule_valves.append({
                "tag": tag,
                "type": "NEEDLE VALVE",
                "orientation": "H",
                "x": round(cx, 3),
                "y": round(cy, 3),
            })
        return out

    def choke_adjustable_h(
        self,
        cx: float,
        cy: float,
        w: float = 13.0,
        h: float = 8.0,
        tag: str = "",
        label: str = "",
    ) -> list[bd.Edge]:
        """Adjustable choke — rumah jepitan + jarum ujung karbida + mikrometer (T-bar).

        Rumah (rect) menggantikan segmen pipa: panggilan wajib memberi gap pipa
        gaps=[(cx, w/2)] pada pipe_run_h agar tepi rumah menempel ujung pipa.
        """
        hw, hh = w / 2.0, h / 2.0
        stem_top = cy + hh + 4.0
        out = rect(cx - hw, cy - hh, cx + hw, cy + hh)
        # Batang jarum + mikrometer head (T-bar)
        out += [
            line(cx, cy + hh, cx, stem_top),
            line(cx - 2.5, stem_top, cx + 2.5, stem_top),
            # Ujung jarum di dalam rumah (pendek <= 3 mm, helper-exempt)
            line(cx, cy + hh, cx, cy + 1.6),
        ]
        if label:
            self.text(label, cx, cy - hh - 5.0, size=1.8)
        if tag:
            self.schedule_valves.append({
                "tag": tag,
                "type": "CHOKE VALVE (ADJUSTABLE, CARBIDE NEEDLE)",
                "orientation": "H",
                "x": round(cx, 3),
                "y": round(cy, 3),
            })
        return out

    def choke_positive_h(
        self,
        cx: float,
        cy: float,
        w: float = 13.0,
        h: float = 8.0,
        tag: str = "",
        label: str = "",
    ) -> list[bd.Edge]:
        """Positive choke — rumah jepitan dengan choke bean tetap (sepasang plat berlubang)."""
        hw, hh = w / 2.0, h / 2.0
        out = rect(cx - hw, cy - hh, cx + hw, cy + hh)
        for bx in (cx - 1.5, cx + 1.5):
            out += [
                line(bx, cy - hh + 1.0, bx, cy - 0.9),
                line(bx, cy + 0.9, bx, cy + hh - 1.0),
            ]
        if label:
            self.text(label, cx, cy - hh - 5.0, size=1.8)
        if tag:
            self.schedule_valves.append({
                "tag": tag,
                "type": "CHOKE VALVE (POSITIVE, FIXED BEAN)",
                "orientation": "H",
                "x": round(cx, 3),
                "y": round(cy, 3),
            })
        return out

    def bleeder_valve_h(
        self, cx: float, cy: float, w: float = 5.0, h: float = 3.0, tag: str = ""
    ) -> list[bd.Edge]:
        """Bleeder valve kecil (puncak christmas tree)."""
        out = self.valve_gate_h(cx, cy, w=w, h=h, flanged=False)
        if tag:
            self.schedule_valves.append({
                "tag": tag,
                "type": "BLEEDER VALVE",
                "orientation": "H",
                "x": round(cx, 3),
                "y": round(cy, 3),
            })
        return out

    # -------------------------------------------------------------------------
    # STRUKTUR WELLHEAD & WELLBORE
    # -------------------------------------------------------------------------
    def tubing_head_flange(
        self, cx: float, y: float, half_w: float = 17.0, gap: float = 3.0
    ) -> list[bd.Edge]:
        """Tubing Head Flange (THF): pasang flensa ganda + penutup ujung (REF-EQUIP)."""
        return [
            line(cx - half_w, y, cx + half_w, y),
            line(cx - half_w, y + gap, cx + half_w, y + gap),
            line(cx - half_w, y, cx - half_w, y + gap),
            line(cx + half_w, y, cx + half_w, y + gap),
        ]

    def wellbore(
        self,
        cx: float,
        y_head_bot: float,
        y_shoe: float,
        scssv_cy: float | None = None,
        casing_half: float = 14.0,
        tubing_half: float = 3.0,
        cement: bool = True,
    ) -> list[bd.Edge]:
        """Wellbore di bawah casing head: casing pasangan + tubing pasangan (REF-EQUIP).

        scssv_cy: pusat SCSSV — tubing otomatis diberi gap (scssv_cy, h/2=5.0)
        untuk tempat simbol SCSSV (w=6, h=10). Semua ujung terhubung: kaki casing
        & tubing menempel garis shoe, ujung atas menempel garis bawah casing head.
        """
        ch, th = casing_half, tubing_half
        out = [
            line(cx - ch, y_shoe, cx - ch, y_head_bot),
            line(cx + ch, y_shoe, cx + ch, y_head_bot),
            line(cx - ch, y_shoe, cx + ch, y_shoe),
        ]
        for dx in (-th, th):
            if scssv_cy is not None:
                out += pipe_run_v(cx + dx, y_shoe, y_head_bot, gaps=[(scssv_cy, 5.0)])
            else:
                out += pipe_run_v(cx + dx, y_shoe, y_head_bot)
        if cement:
            self.hatch += hatch45(
                cx - ch + 1.0, y_shoe + 0.5, cx + ch - 1.0, y_shoe + 7.0, spacing=2.5
            )
        return out

    def scssv(
        self, cx: float, cy: float, w: float = 6.0, h: float = 10.0, tag: str = ""
    ) -> list[bd.Edge]:
        """SCSSV/DHSV downhole — bowtie weld-in tanpa aktuator (fail-close, hyd open)."""
        hw, hh = w / 2.0, h / 2.0
        out = [
            line(cx - hw, cy - hh, cx - hw, cy + hh),
            line(cx + hw, cy - hh, cx + hw, cy + hh),
            line(cx - hw, cy - hh, cx, cy),
            line(cx, cy, cx - hw, cy + hh),
            line(cx + hw, cy - hh, cx, cy),
            line(cx, cy, cx + hw, cy + hh),
        ]
        if tag:
            self.schedule_equipment.append({
                "tag": tag,
                "type": "SCSSV — SURFACE CONTROLLED SUB-SURFACE SAFETY VALVE",
                "x": round(cx, 3),
                "y": round(cy, 3),
            })
        return out

    def annulus_outlet_h(
        self,
        x_face: float,
        y: float,
        direction: int = 1,
        pi_num: str = "",
        label: str = "",
        label_dx: float = 0.0,
        label_dy: float = -6.5,
        label_left: bool = False,
        valve_tag: str = "",
    ) -> list[bd.Edge]:
        """Outlet annulus lengkap: stub + katup jarum + cap + bubble PI (API SPEC 6A).

        direction=+1 keluar ke kanan, -1 ke kiri. Stub menghadap muka casing
        (x_face). Panah aliran kecil keluar mengarah keluar annulus.
        """
        d = 1 if direction >= 0 else -1
        x_end = x_face + d * 20.0
        x_valve = x_face + d * 11.0
        out = pipe_run_h(y, x_face, x_end, gaps=[(x_valve, 3.0)])
        out += self.valve_needle_h(x_valve, y, w=6.0, h=4.0, tag=valve_tag)
        # Cap tick di ujung stub (3 mm — helper-exempt; ujung stub menempel tick)
        out.append(line(x_end, y - 1.5, x_end, y + 1.5))
        # Connector dari puncak stem katup ke bubble PI (di atas katup)
        out.append(line(x_valve, y + 4.5, x_valve, y + 6.0))
        self.sym += self.bubble(x_valve, y + 12.0, "PI", pi_num)
        # Panah aliran kecil keluar (arah venting annulus)
        self.flow_arrow_h(x_face + d * 5.5, y, direction=d, size=2.2)
        if label:
            self.text(label, x_valve + label_dx, y + label_dy, size=1.8, left=label_left)
        return out

    # -------------------------------------------------------------------------
    # INSTRUMEN & PANEL KENDALI SUMUR (API RP 14C)
    # -------------------------------------------------------------------------
    def gauge_pi(self, cx: float, cy: float, num: str = "", r: float = BUBBLE_R) -> list[bd.Edge]:
        """Bubble PI (ANSI/ISA-5.1) — pressure indicator terpasang lokal."""
        return self.bubble(cx, cy, "PI", num)

    def panel_box(
        self, x0: float, y0: float, x1: float, y1: float
    ) -> list[bd.Edge]:
        """Kotak panel (REF-EQUIP) — panel hidrolik ESD sumur / logic solver antarmuka."""
        return rect(x0, y0, x1, y1)

    def hydraulic_signal(
        self, pts: list[tuple[float, float]], brks: list | None = None
    ) -> list[bd.Edge]:
        """Rute sinyal hidraulik dashed (REF-SIG) multi-segmen ortogonal.

        brks[i] = daftar jarak break (mm dari awal segmen i) untuk persilangan
        dengan garis proses (gap 3 mm, half=1.5, standar perusahaan).
        """
        brks = list(brks) if brks else []
        out: list[bd.Edge] = []
        for i in range(len(pts) - 1):
            (x1, y1), (x2, y2) = pts[i], pts[i + 1]
            b = brks[i] if i < len(brks) else ()
            out += dashed_brk(x1, y1, x2, y2, brk=b)
        return out
