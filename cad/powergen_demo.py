"""P&ID GPF-00-PI-PID-0013 Rev A0 — POWER GENERATION PACKAGE.

Sheet A1 (841 x 594 mm), origin kiri-bawah.
Paket pembangkit listrik mesin gas (ISO 3046, ISO 8528, NFPA 37, IEEE 141/242)
per dokumen 08-plan Bagian III.1, memakai pustaka cad/powergen_common.py:
  - Jalur gas bahan bakar dari BL: FG-401 coalescer -> E-401 preheater
    (TIC-401, min 20 C di atas dew point) -> dual PCV-401A/B -> GA-401
    gas admission ke mesin.
  - Siklus JW (blok/kepala silinder - radiator fin-fan HX-401 - pompa
    P-401A + expansion tank CT-401) dan AW/AC turbocharger (HX-402, P-402A).
  - Jalur exhaust: bellows SS - silencer + spark arrestor - stack + rain cap.
  - Generator + GCB/CT/PT + panel auto-synchronizing ke busbar BL.
  - Instrumen PT/TT/LT/FT per ANSI/ISA-5.1; nomor line 080-FG-4001 dst.

Layers:
  REF-FRAME  border lembar, grid referensi, kotak tabel furniture
  REF-TITLE  title block + rev table (ISO 7200 / Company Standard)
  REF-EQUIP  mesin, alternator, skid, radiator, tanki, air box, ground
  REF-PROC   line proses, valves, orifice, continuity box, exhaust
  REF-SYM    bubbles instrumen, DCS, solenoid, GCB/CT/PT, element heater
  REF-SIG    signal listrik / kabel daya (dashed 4.0 / 1.6)
  REF-SIGP   signal pneumatic (solid + "//")
  REF-HATCH  arsiran 45 deg coalescer element, silencer, ground
  REF-TEXT   ditulis post-build oleh apply_text.py dari manifest TEXTS (ARIAL)
"""

from __future__ import annotations

from pathlib import Path

from cadgen import dxf
from pid_common import (
    circle,
    dashed,
    dashed_brk,
    line,
    pneu,
    pipe_run_h,
    pipe_run_v,
    rect,
)
from powergen_common import PowerGenContext


# =============================================================================
# MODEL UTAMA P&ID POWER GENERATION PACKAGE REV A0
# =============================================================================
@dxf
def powergen_demo():
    c = PowerGenContext()

    # -------------------------------------------------------------------------
    # 1. BORDER LEMBAR A1 & GRID REFERENSI (ISO 5457)
    # -------------------------------------------------------------------------
    c.frame += rect(10, 7, 831, 587)      # Outer border
    c.frame += rect(20, 15, 823, 579)     # Inner border

    dx_col = (823.0 - 20.0) / 12.0
    for k in range(1, 12):
        x = 20.0 + dx_col * k
        c.frame += [line(x, 7, x, 15), line(x, 579, x, 587)]
    for i in range(12):
        cx = 20.0 + dx_col * (i + 0.5)
        c.text(str(i + 1), cx, 11.0, size=2.5)
        c.text(str(i + 1), cx, 583.0, size=2.5)

    dy_row = (579.0 - 15.0) / 8.0
    for k in range(1, 8):
        y = 15.0 + dy_row * k
        c.frame += [line(10, y, 20, y), line(823, y, 831, y)]
    for i in range(8):
        cy = 579.0 - dy_row * (i + 0.5)
        c.text("ABCDEFGH"[i], 15.0, cy, size=2.5)
        c.text("ABCDEFGH"[i], 827.0, cy, size=2.5)

    # -------------------------------------------------------------------------
    # 2. KOLOM FURNITURE KANAN (x = 655..823)
    # -------------------------------------------------------------------------
    c.frame.append(line(655, 15, 655, 579))

    # --- 2.1 NOTES (y = 435..579) ---
    c.frame.append(line(655, 435, 823, 435))
    c.frame.append(line(655, 567, 823, 567))
    c.text("NOTES", 739, 573, size=2.5)
    notes = [
        "1. SCHEMATIC - NOT TO SCALE. NO ORIENTATION IMPLIED.",
        "2. LINE DESIGNATION PER PIPING LINE INDEX. SPEC CLASS A1A (CS RF #150).",
        "3. INSTRUMENT SYMBOLS PER ANSI/ISA-5.1-2024; DIAGRAM PER ISO 10628-2:2012.",
        "4. ENGINE-GEN SET GE-G1 PER ISO 3046-1 & ISO 8528-5; 500 KW / 1500 RPM ON",
        "   COMMON SKID WITH SPRING VIBRATION DAMPERS (3 POINTS).",
        "5. E-401 ELECTRIC PREHEATER KEEPS FUEL GAS MIN 20 DEG C ABOVE DEW POINT;",
        "   TIC-401 + TT-401 VIA SCR HEATER CONTROLLER SC-401.",
        "6. DUAL REGULATION: PCV-401A (WORKER) / PCV-401B (MONITOR) IN SERIES.",
        "7. GA-401 GAS ADMISSION VALVE (SOLENOID) FROM ENGINE CONTROL SYSTEM.",
        "8. EXHAUST PER NFPA 37: SS BELLOWS + SILENCER/SPARK ARRESTOR EXH-SIL-401",
        "   + VERTICAL STACK WITH RAIN CAP.",
        "9. JW 080-JW-4004: BLOCK/HEADS - HX-401 - P-401A + CT-401 EXPANSION TANK.",
        "10. AW/AC 080-AW-4005: TURBO AFTERCOOLER - HX-402 - PUMP P-402A.",
        "11. ELECTRICAL: GCB-401 + CT/PT; AUTO-SYNC & LOAD SHARING PER IEEE 141/242.",
        "12. FG-401 DRAIN TO CLOSED DRAIN VIA GV-402. NTS - SEE PIPING LINE INDEX.",
    ]
    ny = 559.0
    for ln in notes:
        c.text(ln, 659, ny, size=2.0, left=True)
        ny -= 8.0

    # --- 2.2 LEGEND & SYMBOLS (y = 185..435) ---
    c.frame.append(line(655, 185, 823, 185))
    c.frame.append(line(655, 423, 823, 423))
    c.text("LEGEND & SYMBOLS", 739, 429, size=2.5)

    # Process line
    c.proc.append(line(660, 413, 685, 413))
    c.flow_arrow_h(675, 413, direction=1)
    c.text("PROCESS LINE", 690, 413, size=2.0, left=True)

    # Electric signal / power cable
    c.sig += dashed(660, 397, 685, 397)
    c.text("ELECTRIC SIGNAL / POWER CABLE", 690, 397, size=2.0, left=True)

    # Pneumatic signal
    c.sigp += pneu(660, 381, 685, 381)
    c.text("PNEUMATIC SIGNAL", 690, 381, size=2.0, left=True)

    # Continuity arrow
    c.proc += [
        line(660, 359, 680, 359), line(680, 359, 685, 362),
        line(685, 362, 680, 365), line(680, 365, 660, 365), line(660, 365, 660, 359),
    ]
    c.text("CONTINUITY ARROW (BATTERY LIMIT)", 690, 362, size=2.0, left=True)

    # Control valve
    c.sym += c.control_valve_h(668, 342, w=8, h=5)
    c.text("CONTROL VALVE (PCV)", 690, 342, size=2.0, left=True)

    # Gate + check valve
    c.sym += c.valve_gate_h(666, 326, w=8, h=5, flanged=False)
    c.sym += c.valve_check_h(688, 326, w=8, h=5)
    c.text("GATE", 666, 317, size=1.8)
    c.text("CHECK", 688, 317, size=1.8)

    # Gas admission valve (solenoid)
    c.sym += c.gas_admission_valve_h(668, 296, tag="")
    c.text("GAS ADMISSION VALVE (SOLENOID)", 690, 296, size=2.0, left=True)

    # Fin-fan radiator
    c.sym += rect(660, 274, 676, 282)
    c.sym.append(circle(668, 282, 4.0))
    c.text("FIN-FAN RADIATOR", 690, 278, size=2.0, left=True)

    # Exhaust stack + rain cap
    c.sym += [line(668, 254, 668, 266),
              line(664, 266, 668, 270), line(668, 270, 672, 266)]
    c.text("EXHAUST STACK + RAIN CAP", 690, 260, size=2.0, left=True)

    # GCB / CT / PT
    c.sym += [rect(660, 239, 668, 245),
              circle(674, 242, 3.0), circle(681, 242, 3.0)]
    c.text("GCB / CT / PT", 690, 242, size=2.0, left=True)

    # Field instrument
    c.sym.append(circle(668, 226, 5.0))
    c.sym.append(line(663, 226, 673, 226))
    c.text("FIELD INSTRUMENT", 690, 226, size=2.0, left=True)

    # DCS shared display
    c.sym += [
        line(661, 203, 675, 203), line(675, 203, 675, 217),
        line(675, 217, 661, 217), line(661, 217, 661, 203),
        circle(668, 210, 4.0), line(661, 210, 675, 210),
    ]
    c.text("DCS SHARED DISPLAY / CONTROL", 690, 210, size=2.0, left=True)

    # Abbreviations
    c.text("FC: FAIL CLOSED     | NC: NORMALLY CLOSED", 659, 200, size=1.8, left=True)
    c.text("JW: JACKET WATER    | AW/AC: AUX + AFTERCOOLER", 659, 194, size=1.8, left=True)
    c.text("GE: GAS ENGINE      | G 3~: ALTERNATOR 3-PHASE", 659, 188, size=1.8, left=True)

    # --- 2.3 REFERENCE DRAWINGS (y = 148..185) ---
    c.frame.append(line(655, 148, 823, 148))
    c.frame.append(line(655, 175, 823, 175))
    c.text("REFERENCE DRAWINGS", 739, 180, size=2.2)
    ref_dwgs = [
        ("GPF-00-DB-0001", "DESIGN BASIS - GAS PRODUCTION FACILITY", 169.0),
        ("GPF-00-PI-PID-0001", "P&ID 3-PHASE SEPARATOR V-101 (FG SOURCE)", 163.5),
        ("GPF-00-PI-PID-0011", "P&ID FUEL GAS HEADER", 158.0),
        ("GPF-00-PI-ISO-0007", "PIPING ISOMETRIC", 152.5),
    ]
    for doc_no, doc_title, ry in ref_dwgs:
        c.text(f"{doc_no} : {doc_title}", 659, ry, size=1.8, left=True)

    # --- 2.4 REVISION TABLE (Bottom-Up, y = 116..148) ---
    c.title += [
        line(655, 116, 823, 116),
        line(655, 142.0, 823, 142.0),
        line(655, 136.8, 823, 136.8),
        line(655, 131.6, 823, 131.6),
        line(655, 126.4, 823, 126.4),
        line(655, 121.2, 823, 121.2),
        line(675, 116, 675, 148),
        line(763, 116, 763, 148),
        line(795, 116, 795, 148),
        line(809, 116, 809, 148),
    ]
    c.text("REV", 665, 145.0, size=1.8)
    c.text("DESCRIPTION", 719, 145.0, size=1.8)
    c.text("DATE", 779, 145.0, size=1.8)
    c.text("CHK", 802, 145.0, size=1.8)
    c.text("APP", 816, 145.0, size=1.8)
    rev_data = [
        ("A0", "ISSUED FOR REVIEW", "23 OCT 26", "PM", "RE", 139.4),
    ]
    for r_rev, r_desc, r_date, r_chk, r_app, ry in rev_data:
        c.text(r_rev, 665, ry, size=1.8)
        c.text(r_desc, 678, ry, size=1.8, left=True)
        c.text(r_date, 779, ry, size=1.8)
        c.text(r_chk, 802, ry, size=1.8)
        c.text(r_app, 816, ry, size=1.8)

    # --- 2.5 TITLE BLOCK (y = 15..116) ---
    c.title += [
        line(655, 96, 823, 96),
        line(655, 74, 823, 74),
        line(655, 60, 823, 60),
        line(655, 48, 823, 48),
        line(655, 36, 823, 36),
        line(655, 25, 823, 25),
        line(739, 15, 739, 60),
    ]
    c.text("GAS PRODUCTION FACILITY - ONSHORE FIELD", 739, 108.5, size=2.8)
    c.text("PM OIL & GAS SURFACE FACILITY", 739, 102.5, size=2.2)
    c.text("REKAYASA ENGINEERING", 739, 98.0, size=2.0)
    c.text("PIPING & INSTRUMENTATION DIAGRAM", 739, 87.0, size=2.8)
    c.text("POWER GENERATION PACKAGE", 739, 80.0, size=2.5)
    c.text("DRAWING NO:", 658, 70.0, size=1.8, left=True)
    c.text("GPF-00-PI-PID-0013", 739, 65.5, size=2.8)
    c.text("REV:", 658, 56.5, size=1.8, left=True)
    c.text("A0", 697, 52.5, size=3.0)
    c.text("SCALE:", 742, 56.5, size=1.8, left=True)
    c.text("NTS", 781, 52.5, size=2.5)
    c.text("DATE:", 658, 44.5, size=1.8, left=True)
    c.text("23 OCT 2026", 697, 40.5, size=2.2)
    c.text("SHEET:", 742, 44.5, size=1.8, left=True)
    c.text("1 OF 1", 781, 40.5, size=2.5)
    c.text("DESIGNED:", 658, 32.5, size=1.8, left=True)
    c.text("CAD/FEED", 697, 29.0, size=2.2)
    c.text("DRAWN:", 742, 32.5, size=1.8, left=True)
    c.text("GLM-5.3-FLASH", 781, 29.0, size=2.2)
    c.text("CHECKED:", 658, 21.5, size=1.8, left=True)
    c.text("PM (AI)", 697, 18.5, size=2.2)
    c.text("APPROVED:", 742, 21.5, size=1.8, left=True)

    # -------------------------------------------------------------------------
    # 3. EQUIPMENT DATA TABLES (y = 515..573)
    # -------------------------------------------------------------------------
    c.equip += rect(135, 515, 375, 573)
    c.equip.append(line(135, 565, 375, 565))
    c.equip.append(line(228, 515, 228, 565))
    c.text("EQUIPMENT DATA - GAS ENGINE GENERATOR SET GE-G1", 255, 569, size=2.4)
    ge_rows = [
        ("TAG NUMBER", "GE-G1", 561.0),
        ("SERVICE", "GAS ENGINE GENERATOR SET (PKG)", 553.0),
        ("RATING", "500 KW / 1500 RPM (ISO 3046-1)", 545.0),
        ("TYPE", "V-TYPE GAS ENGINE + ALTERNATOR 3~ (ISO 8528)", 537.0),
        ("MOUNTING", "COMMON SKID + SPRING VIBRATION DAMPERS", 529.0),
        ("GOVERNOR", "ELECTRONIC, LOAD SHARING (IEEE 141)", 521.0),
    ]
    for k, (cap, val, ry) in enumerate(ge_rows):
        if k > 0:
            c.equip.append(line(135, ry + 4.0, 375, ry + 4.0))
        c.text(cap, 138, ry, size=1.8, left=True)
        c.text(val, 232, ry, size=2.0, left=True)

    c.equip += rect(395, 515, 635, 573)
    c.equip.append(line(395, 565, 635, 565))
    c.equip.append(line(470, 515, 470, 565))
    c.text("EQUIPMENT DATA - FUEL GAS & EXHAUST SYSTEM", 515, 569, size=2.4)
    fg_rows = [
        ("FG-401", "COALESCING FILTER (LIQUID MIST REMOVAL)", 561.0),
        ("E-401", "ELECTRIC PREHEATER, +20 DEG C ABOVE DEW POINT", 553.0),
        ("PCV-401A/B", "DUAL PRESSURE REGULATOR (WORKER/MONITOR)", 545.0),
        ("GA-401", "GAS ADMISSION VALVE (SOLENOID)", 537.0),
        ("EXH-SIL-401", "EXH SILENCER + SPARK ARRESTOR (NFPA 37)", 529.0),
        ("STACK", "VERTICAL + RAIN CAP, SS BELLOWS AT ENGINE", 521.0),
    ]
    for k, (cap, val, ry) in enumerate(fg_rows):
        if k > 0:
            c.equip.append(line(395, ry + 4.0, 635, ry + 4.0))
        c.text(cap, 398, ry, size=1.8, left=True)
        c.text(val, 474, ry, size=2.0, left=True)

    # -------------------------------------------------------------------------
    # 4. JALUR GAS BAHAN BAKAR (080-FG-4001..4003)
    # -------------------------------------------------------------------------
    # Battery limit: dari fuel gas header (separator P&ID)
    c.proc += c.continuity_box_left(460, "080-FG-4001 DN50",
                                    "FROM FUEL GAS HEADER", "GPF-00-PI-PID-0001")
    c.proc += pipe_run_h(460, 72.5, 87)
    c.proc += c.flow_arrow_h(80, 460, 1)

    # FG-401 Coalescing filter + drain GV-402
    c.proc += c.coalescing_filter_v(100, 418, 478, r=13, tag="FG-401")
    c.text("COALESCING FILTER", 60, 448, size=1.8, left=True)

    # 080-FG-4002: coalescer -> preheater (atas-kanan-turun)
    c.proc += pipe_run_v(100, 484.5, 496)
    c.proc += c.flow_arrow_v(100, 491, 1)
    c.proc += pipe_run_h(496, 100, 145)
    c.proc += c.flow_arrow_h(122, 496, 1)
    c.text("080-FG-4002 DN50", 122, 489.5, size=1.8)
    c.proc += pipe_run_v(145, 474, 496)
    c.proc += c.flow_arrow_v(145, 484, -1)
    c.proc += pipe_run_h(474, 145, 159)
    c.proc += c.flow_arrow_h(152, 474, 1)

    # E-401 electric preheater + TIC-401 loop (TT-401 -> TIC -> SC-401 -> heater)
    c.proc += c.fuel_preheater_electric(185, 460, tag="E-401")
    c.proc += pipe_run_v(195, 420, 436)                       # impulse TT-401
    c.sym += c.bubble(195, 414, "TT", "401")
    c.sig += dashed(195, 408, 195, 402.5)
    c.sym += c.dcs(195, 395, "TIC", "401")
    c.sig += dashed_brk(187.5, 395, 148, 395)                 # TIC -> kiri
    c.sig += dashed_brk(148, 395, 148, 498, brk=[79.0])       # naik, break di FG y=474
    c.sig += dashed(148, 498, 175, 498)
    c.sym += rect(175, 498, 195, 508)
    c.text("SC", 185, 504.5, size=1.8)
    c.text("401", 185, 501.5, size=1.8)
    c.sig += dashed(185, 484, 185, 498)                       # SC -> heater terminal box

    # 080-FG-4003: preheater -> dual PCV -> engine admission
    c.proc += pipe_run_v(159, 436, 446)
    c.proc += c.flow_arrow_v(159, 441, -1)
    c.proc += pipe_run_h(436, 159, 228)
    c.proc += c.flow_arrow_h(180, 436, 1)
    c.text("080-FG-4003 DN50", 172, 429, size=1.8)
    c.proc += pipe_run_v(228, 436, 460)
    c.proc += c.flow_arrow_v(228, 448, 1)
    c.proc += pipe_run_h(460, 228, 338, gaps=[(252, 6.2), (282, 6.2), (312, 6.2)])
    c.proc += c.flow_arrow_h(240, 460, 1)
    c.proc += c.flow_arrow_h(266, 460, 1)
    c.proc += c.flow_arrow_h(296, 460, 1)
    c.proc += c.flow_arrow_h(330, 460, 1)

    # Dual fuel gas regulator (worker + monitor) + loop PIC
    c.dual_pcv_station(460, 252, 282)

    # GV-401 block valve
    c.proc += c.valve_gate_h(312, 460, w=10.0, h=6.0, flanged=True, tag="GV-401")
    c.text("GV-401", 312, 451, size=2.2)

    # Turun ke mesin + orifice FE-401/FT-401 + admission GA-401
    c.proc += pipe_run_v(338, 122, 460)
    c.proc += c.flow_arrow_v(338, 420, -1)
    c.proc += c.flow_arrow_v(338, 300, -1)
    c.proc += c.flow_arrow_v(338, 190, -1)
    c.text("080-FG-4003 DN50", 332, 310, size=1.8, rot=90.0)
    c.proc += c.orifice_h(362, 122, tag_fe="FE-401")
    c.proc += pipe_run_v(368, 122, 130)
    c.sym += c.bubble(368, 136, "FT", "401")
    c.sig += dashed(368, 142, 368, 148.5)
    c.sym += c.dcs(368, 156, "FI", "401")
    c.proc += c.gas_admission_valve_h(382, 122, tag="GA-401")
    c.text("GA-401", 382, 112, size=2.2)
    c.sig += dashed(382, 140, 382, 144)
    c.text("ENGINE CONTROL", 390, 142, size=1.8, left=True)
    c.proc += pipe_run_h(122, 338, 405, gaps=[(362, 1.2), (382, 6.2)])
    c.proc += c.flow_arrow_h(350, 122, 1, size=2.4)
    c.proc += c.flow_arrow_h(396, 122, 1, size=2.4)

    # -------------------------------------------------------------------------
    # 5. SIKLUS PENDINGIN JW (080-JW-4004)
    # -------------------------------------------------------------------------
    c.proc += pipe_run_v(410, 135, 270)                       # JW keluar blok
    c.proc += c.flow_arrow_v(410, 200, 1)
    c.proc += pipe_run_h(270, 334, 410, gaps=[(338, 1.5)])    # ke panel HX-401
    c.proc += c.flow_arrow_h(380, 270, -1)
    c.proc += c.fin_fan_radiator(280, 230, 334, 285, tag="HX-401", label="JW RADIATOR")
    c.proc += pipe_run_h(240, 275, 280)                       # outlet panel (koridor)
    c.proc += c.flow_arrow_h(277.5, 240, -1, size=2.4)
    c.proc += pipe_run_v(275, 88, 240)                        # turun ke hisap pompa
    c.proc += c.flow_arrow_v(275, 150, -1)
    c.proc += pipe_run_h(88, 275, 288)
    c.proc += c.flow_arrow_h(279, 88, 1, size=2.4)
    c.proc += c.package_pump(295, 88, r=7)
    c.text("P-401A", 295, 74, size=2.5)
    c.proc += pipe_run_h(88, 302, 405)                        # discharge ke blok
    c.proc += c.flow_arrow_h(330, 88, 1, size=2.4)
    c.proc += c.flow_arrow_h(392, 88, 1, size=2.4)
    c.text("080-JW-4004 DN80", 362, 94, size=1.8)
    # Expansion tank CT-401 + LT-401 (di jalur hisap)
    c.proc += c.expansion_tank_lt(251, 190, 267, 220, branch=(267, 205, 275, 205))

    # -------------------------------------------------------------------------
    # 6. SIKLUS AW/AC TURBOCHARGER (080-AW-4005)
    # -------------------------------------------------------------------------
    c.proc += pipe_run_v(430, 135, 215)                       # AW keluar blok
    c.proc += c.flow_arrow_v(430, 175, 1)
    c.proc += pipe_run_h(215, 270, 430, gaps=[(275, 1.5), (338, 1.5), (410, 1.5)])
    c.proc += pipe_run_v(270, 215, 230)                       # nozzle panel HX-402
    c.proc += c.flow_arrow_h(300, 215, 1, size=2.4)
    c.proc += c.flow_arrow_h(370, 215, 1, size=2.4)
    c.proc += c.flow_arrow_h(422, 215, 1, size=2.4)
    c.text("080-AW-4005 DN50", 358, 221, size=1.8)
    c.proc += c.fin_fan_radiator(215, 230, 270, 285, tag="HX-402", label="AW/AC RADIATOR")
    c.proc += pipe_run_h(245, 205, 215)                       # outlet panel
    c.proc += c.flow_arrow_h(210, 245, -1, size=2.4)
    c.proc += pipe_run_v(205, 106, 245)                       # turun ke hisap pompa
    c.proc += c.flow_arrow_v(205, 170, -1)
    c.proc += pipe_run_h(106, 205, 298, gaps=[(275, 1.5)])
    c.proc += c.flow_arrow_h(250, 106, 1, size=2.4)
    c.text("080-AW-4005 DN50", 240, 112, size=1.8)
    c.proc += c.package_pump(305, 106, r=7)
    c.text("P-402A", 317, 92, size=2.5)
    c.proc += pipe_run_h(106, 312, 405)                       # discharge ke blok
    c.proc += c.flow_arrow_h(330, 106, 1, size=2.4)
    c.proc += c.flow_arrow_h(392, 106, 1, size=2.4)

    # -------------------------------------------------------------------------
    # 7. MESIN GAS + ALTERNATOR DI COMMON SKID (ISO 3046 / ISO 8528)
    # -------------------------------------------------------------------------
    c.proc += c.engine_alternator_skid(
        x0=405, yb=75, bw=65, bh=60, alt_cx=505, alt_r=22, coupling=13,
        skid_x0=385, skid_x1=560, yskid=60, dampers=(395, 470, 545), tag="GE-G1",
    )

    # Air intake filter box (di atas blok) + turbocharger
    c.equip += rect(440, 148, 463, 162)
    c.equip += [line(444, 148, 444, 135), line(459, 148, 459, 135)]
    c.proc += c.flow_arrow_v(451, 162, -1, size=2.4)
    c.text("AIR INTAKE FILTER", 451, 170, size=1.8)
    c.equip.append(circle(469, 155, 6.0))
    c.text("TC", 469, 155, size=2.0)
    c.text("TC-401", 469, 142, size=2.0)

    # -------------------------------------------------------------------------
    # 8. SISTEM EXHAUST (NFPA 37) — 080-EG-4006
    # -------------------------------------------------------------------------
    c.proc += pipe_run_v(469, 161, 166)                       # turbo -> bellows
    c.proc += c.flow_arrow_v(469, 163, 1, size=2)
    c.proc += c.exhaust_bellows_v(469, 166, 178, w=12)
    c.proc += pipe_run_v(469, 178, 185)                       # bellows -> silencer
    c.proc += c.exhaust_silencer_arrestor_v(469, 185, 250, w=20, tag="EXH-SIL-401")
    c.proc += pipe_run_v(469, 250, 480)                       # stack vertikal
    c.proc += c.flow_arrow_v(469, 300, 1)
    c.proc += c.flow_arrow_v(469, 420, 1)
    c.proc += c.exhaust_stack_cap(469, 480, w=16, label="RAIN CAP")
    c.text("EXH-ST-401 STACK + RAIN CAP", 485, 470, size=1.8, left=True)
    c.text("080-EG-4006 DN200", 463, 330, size=1.8, rot=90.0)

    # -------------------------------------------------------------------------
    # 9. ANTARMUKA KELISTRIKAN (GCB / CT / PT / AUTO-SYNC PANEL)
    # -------------------------------------------------------------------------
    c.electrical_interface(cable_x=545, y_bus=405, alt_x=527, y_alt=105)

    # -------------------------------------------------------------------------
    # 10. REGISTRASI LINE & EKSPOR MANIFEST
    # -------------------------------------------------------------------------
    c.register_line("080-FG-4001", spec="150# A1A", service="Fuel Gas to Coalescer", dn=50)
    c.register_line("080-FG-4002", spec="150# A1A", service="Fuel Gas to Preheater", dn=50)
    c.register_line("080-FG-4003", spec="150# A1A", service="Fuel Gas to Engine", dn=50)
    c.register_line("080-JW-4004", spec="150# A1A", service="Jacket Water Cooling", dn=80)
    c.register_line("080-AW-4005", spec="150# A1A", service="Aux/Aftercooler Water", dn=50)
    c.register_line("080-EG-4006", spec="A1A", service="Engine Exhaust to Stack", dn=200)

    out_json = Path(__file__).resolve().parent / "powergen_demo.texts.json"
    layers = c.export_manifest(out_json)
    return layers


if __name__ == "__main__":
    powergen_demo()
