"""P&ID GPF-00-PI-PID-0011 Rev A0 — WELLHEAD & CHRISTMAS TREE (API SPEC 6A).

Sheet A1 (841 x 594 mm), origin kiri-bawah.
Modul hulu — GPF-00-PM-PLN-0008 Bagian I. Pustaka simbol: cad/wellhead_common.py.

Standar acuan:
  - API SPEC 6A / ISO 10423 (Wellhead and Christmas Tree Equipment)
  - API RP 14C (Surface & Subsurface Safety Systems)
  - ANSI/ISA-5.1-2024 (Instrumentation Symbols and Identification)
  - ISO 10628-2:2012 (Graphical symbols)
  - Referensi Perusahaan: SSY-PRO-PID-002 & SSY-PRO-PID-003

Isi: satu christmas tree vertikal lengkap dari puncak (PI + bleeder, swab valve,
crossbar sayap produksi & kill, choke adjustable, UMV, LMV, tubing head flange),
SCSSV di badan sumur, flowline produksi 150-WH-2001 ke battery limit, kill line
masuk sayap kill, dan panel hydraulic ESD dengan sinyal dashed (REF-SIG) ke
UMV / PWV / SCSSV control line.

Layers:
  REF-FRAME  border lembar, grid referensi, kotak tabel furniture, ground line
  REF-TITLE  title block + rev table (ISO 7200 / Company Standard)
  REF-EQUIP  casing head, THF, wellbore, panel ESD, tabel data
  REF-PROC   line proses, valves, choke, SCSSV, continuity boxes
  REF-SYM    bubbles instrumen PI
  REF-SIG    sinyal hidraulik panel (dashed, break 3 mm pada persilangan)
  REF-HATCH  arsiran semen sepatu casing
  REF-TEXT   ditulis post-build oleh apply_text.py dari manifest TEXTS (ARIAL)
"""

from __future__ import annotations

from pathlib import Path

from cadgen import dxf
from pid_common import (
    circle,
    dashed,
    line,
    pipe_run_h,
    pipe_run_v,
    rect,
)
from wellhead_common import WellheadContext


# =============================================================================
# MODEL UTAMA P&ID REV A0
# =============================================================================
@dxf
def wellhead_demo():
    ctx = WellheadContext()

    # -------------------------------------------------------------------------
    # 1. BORDER LEMBAR A1 & GRID REFERENSI (ISO 5457)
    # -------------------------------------------------------------------------
    ctx.frame += rect(10, 7, 831, 587)      # Outer border
    ctx.frame += rect(20, 15, 823, 579)     # Inner border

    dx_col = (823.0 - 20.0) / 12.0
    for k in range(1, 12):
        x = 20.0 + dx_col * k
        ctx.frame += [line(x, 7, x, 15), line(x, 579, x, 587)]
    for i in range(12):
        cx = 20.0 + dx_col * (i + 0.5)
        ctx.text(str(i + 1), cx, 11.0, size=2.5)
        ctx.text(str(i + 1), cx, 583.0, size=2.5)

    dy_row = (579.0 - 15.0) / 8.0
    for k in range(1, 8):
        y = 15.0 + dy_row * k
        ctx.frame += [line(10, y, 20, y), line(823, y, 831, y)]
    for i in range(8):
        cy = 579.0 - dy_row * (i + 0.5)
        ctx.text("ABCDEFGH"[i], 15.0, cy, size=2.5)
        ctx.text("ABCDEFGH"[i], 827.0, cy, size=2.5)

    # -------------------------------------------------------------------------
    # 2. KOLOM FURNITURE KANAN (x = 655..823)
    # -------------------------------------------------------------------------
    ctx.frame.append(line(655, 15, 655, 579))

    # --- 2.1 NOTES (y = 435..579) ---
    ctx.frame.append(line(655, 435, 823, 435))
    ctx.frame.append(line(655, 567, 823, 567))
    ctx.text("NOTES", 739, 573, size=2.5)
    notes = [
        "1. SCHEMATIC - NOT TO SCALE. NO ORIENTATION IMPLIED.",
        "2. WELLHEAD & CHRISTMAS TREE PER API SPEC 6A (ISO 10423),",
        "   RATED 5000 PSI WP / 10000 PSI TEST.",
        "3. SAFETY SYSTEM (UMV, PWV, SCSSV) PER API RP 14C.",
        "4. UMV-201 & PWV-201: HYDRAULIC GATE VALVES, SPRING-RETURN",
        "   FAIL-CLOSE (FC), ACTUATED FROM WELLHEAD HYDRAULIC ESD",
        "   PANEL (FROM ESD-1 LOGIC SOLVER).",
        "5. SCSSV-201: FAIL-CLOSE ON LOSS OF HYDRAULIC CONTROL",
        "   PRESSURE (3000-10000 PSI).",
        "6. XOV-201: ADJUSTABLE CHOKE, TUNGSTEN CARBIDE NEEDLE +",
        "   MICROMETER HEAD. POSITIVE CHOKE SHOWN IN LEGEND.",
        "7. ANNULUS A/B/C MONITORED VIA NEEDLE VALVE + PI (TABLE).",
        "8. NRV-201 PREVENTS BACKFLOW FROM KILL LINE 050-WH-2002.",
        "9. ALL GATE VALVES FULL OPEN OR FULL CLOSED - NO THROTTLING.",
        "10. LINE NUMBERING PER PIPING LINE INDEX; SIZES FOR CLARITY.",
    ]
    ny = 560.0
    for ln in notes:
        ctx.text(ln, 659, ny, size=2.0, left=True)
        ny -= 8.3

    # --- 2.2 LEGEND & SYMBOLS (y = 185..435) ---
    ctx.frame.append(line(655, 185, 823, 185))
    ctx.frame.append(line(655, 423, 823, 423))
    ctx.text("LEGEND & SYMBOLS", 739, 429, size=2.5)

    # Process line
    ctx.proc.append(line(660, 413, 685, 413))
    ctx.flow_arrow_h(675, 413, direction=1)
    ctx.text("PROCESS LINE", 690, 413, size=2.0, left=True)

    # Hydraulic signal (dashed)
    ctx.sig += dashed(660, 398, 685, 398)
    ctx.text("HYDRAULIC SIGNAL (ESD PANEL / SCSSV)", 690, 398, size=2.0, left=True)

    # Manual gate valve
    ctx.sym += ctx.valve_gate_manual_h(668, 383, w=8, h=5)
    ctx.text("GATE VALVE - MANUAL (LMV/KWV/SWAB)", 690, 383, size=2.0, left=True)

    # Hydraulic actuated gate valve (FC)
    ctx.proc += ctx.valve_gate_hydraulic_h(668, 364, w=8, h=5, act_w=8, act_h=6, fail="")
    ctx.text("GATE VALVE - HYDRAULIC ACTUATOR, FC", 690, 364, size=2.0, left=True)

    # Needle valve
    ctx.proc += ctx.valve_needle_h(668, 350, w=6, h=4)
    ctx.text("NEEDLE VALVE (ANNULUS OUTLET)", 690, 350, size=2.0, left=True)

    # Adjustable choke
    ctx.proc += ctx.choke_adjustable_h(670, 333, w=10, h=7)
    ctx.text("ADJUSTABLE CHOKE (CARBIDE NEEDLE)", 690, 333, size=2.0, left=True)

    # Positive choke
    ctx.proc += ctx.choke_positive_h(670, 316, w=10, h=7)
    ctx.text("POSITIVE CHOKE (FIXED BEAN)", 690, 316, size=2.0, left=True)

    # SCSSV (downhole)
    ctx.proc += ctx.scssv(670, 300, w=6, h=9)
    ctx.text("SCSSV (DOWNHOLE, FAIL-CLOSE)", 690, 300, size=2.0, left=True)

    # Bleeder + PI
    ctx.sym.append(circle(663, 285, 4.0))
    ctx.text("PI", 663, 285, size=1.8)
    ctx.proc += [line(667, 285, 673.5, 285)]
    ctx.proc += ctx.bleeder_valve_h(676, 285, w=5, h=3)
    ctx.text("BLEEDER VALVE + PRESSURE GAUGE (PI)", 690, 285, size=2.0, left=True)

    # Battery limit arrow
    ctx.proc += [line(660, 270, 681, 270), line(681, 267.5, 681, 272.5)]
    ctx.flow_arrow_h(672, 270, direction=1, size=2.2)
    ctx.text("BATTERY LIMIT (CONTINUITY ARROW)", 690, 270, size=2.0, left=True)

    # Abbreviations
    ctx.text("H = HYDRAULIC ACTUATOR | FC = FAIL CLOSE", 659, 255, size=1.8, left=True)
    ctx.text("STANDARD ABBREVIATIONS:", 659, 240, size=1.9, left=True)
    ctx.text("UMV/LMV: UPPER/LOWER MASTER VALVE", 659, 231, size=1.8, left=True)
    ctx.text("PWV/KWV: PRODUCTION/KILL WING VALVE", 659, 222, size=1.8, left=True)
    ctx.text("SCSSV: SUB-SURFACE SAFETY VALVE (DOWNHOLE)", 659, 213, size=1.8, left=True)
    ctx.text("NC: NORMALLY CLOSED    | THF: TUBING HEAD FLANGE", 659, 204, size=1.8, left=True)
    ctx.text("BL: BATTERY LIMIT      | XOV: CHOKE VALVE", 659, 195, size=1.8, left=True)

    # --- 2.3 REFERENCE DRAWINGS (y = 148..185) ---
    ctx.frame.append(line(655, 148, 823, 148))
    ctx.frame.append(line(655, 175, 823, 175))
    ctx.text("REFERENCE DRAWINGS", 739, 180, size=2.2)
    ref_dwgs = [
        ("GPF-00-DB-0001", "DESIGN BASIS - GAS PRODUCTION FACILITY", 169.0),
        ("GPF-00-PI-PID-0001", "P&ID - 3-PHASE SEPARATOR V-101", 163.5),
        ("GPF-00-PI-PLN-0002", "PIPING PLAN - SEPARATOR AREA", 158.0),
        ("GPF-00-PM-PLN-0008", "BLUEPRINT MODUL HULU s/d ALIGNMENT (REV A2)", 152.5),
    ]
    for doc_no, doc_title, ry in ref_dwgs:
        ctx.text(f"{doc_no} : {doc_title}", 659, ry, size=1.8, left=True)

    # --- 2.4 REVISION TABLE (y = 136.8..148, A0 only) ---
    ctx.title += [
        line(655, 142.0, 823, 142.0),
        line(655, 136.8, 823, 136.8),
        line(675, 136.8, 675, 148),
        line(763, 136.8, 763, 148),
        line(795, 136.8, 795, 148),
        line(809, 136.8, 809, 148),
    ]
    ctx.text("REV", 665, 145.0, size=1.8)
    ctx.text("DESCRIPTION", 719, 145.0, size=1.8)
    ctx.text("DATE", 779, 145.0, size=1.8)
    ctx.text("CHK", 802, 145.0, size=1.8)
    ctx.text("APP", 816, 145.0, size=1.8)
    ctx.text("A0", 665, 139.4, size=1.8)
    ctx.text("ISSUED FOR REVIEW", 678, 139.4, size=1.8, left=True)
    ctx.text("23 OCT 26", 779, 139.4, size=1.8)
    ctx.text("PM", 802, 139.4, size=1.8)
    ctx.text("RE", 816, 139.4, size=1.8)

    # --- 2.5 TITLE BLOCK (y = 15..116) ---
    ctx.title += [
        line(655, 96, 823, 96),
        line(655, 74, 823, 74),
        line(655, 60, 823, 60),
        line(655, 48, 823, 48),
        line(655, 36, 823, 36),
        line(655, 25, 823, 25),
        line(739, 15, 739, 60),
    ]
    ctx.text("GAS PRODUCTION FACILITY - ONSHORE FIELD", 739, 108.5, size=2.8)
    ctx.text("PM OIL & GAS SURFACE FACILITY", 739, 102.5, size=2.2)
    ctx.text("REKAYASA ENGINEERING", 739, 98.0, size=2.0)
    ctx.text("PIPING & INSTRUMENTATION DIAGRAM", 739, 87.0, size=2.8)
    ctx.text("WELLHEAD & CHRISTMAS TREE (API SPEC 6A)", 739, 80.0, size=2.5)
    ctx.text("DRAWING NO:", 658, 70.0, size=1.8, left=True)
    ctx.text("GPF-00-PI-PID-0011", 739, 65.5, size=2.8)
    ctx.text("REV:", 658, 56.5, size=1.8, left=True)
    ctx.text("A0", 697, 52.5, size=3.0)
    ctx.text("SCALE:", 742, 56.5, size=1.8, left=True)
    ctx.text("NTS", 781, 52.5, size=2.5)
    ctx.text("DATE:", 658, 44.5, size=1.8, left=True)
    ctx.text("23 OCT 2026", 697, 40.5, size=2.2)
    ctx.text("SHEET:", 742, 44.5, size=1.8, left=True)
    ctx.text("1 OF 1", 781, 40.5, size=2.5)
    ctx.text("DRAWN:", 658, 32.5, size=1.8, left=True)
    ctx.text("GLM-5.3-FLASH", 697, 29.0, size=2.2)
    ctx.text("CHECKED:", 658, 21.5, size=1.8, left=True)
    ctx.text("PM (AI)", 697, 18.5, size=2.2)
    ctx.text("APPROVED:", 742, 21.5, size=1.8, left=True)

    # -------------------------------------------------------------------------
    # 3. TABEL DATA (y = 505..553)
    # -------------------------------------------------------------------------
    # Tabel 1: WELLHEAD & CHRISTMAS TREE DATA (x = 25..430)
    ctx.equip += rect(25, 505, 430, 553)
    ctx.equip.append(line(25, 547, 430, 547))
    ctx.equip.append(line(147, 505, 147, 547))
    ctx.text("WELLHEAD & CHRISTMAS TREE DATA - API SPEC 6A / ISO 10423", 227, 550, size=2.4)
    wh_rows = [
        ("TAG NUMBER", "XMAS TREE WT-201 (WELL GPF-201)"),
        ("DESIGN STANDARD", "API SPEC 6A (ISO 10423), PSL 2"),
        ("RATING", "5000 PSI WP / 10000 PSI TEST"),
        ("SERVICE", "GAS PRODUCTION (ONSHORE)"),
        ("SCSSV", "HYDRAULIC 3000-10000 PSI, FAIL-CLOSE"),
        ("ESD ACTION", "CLOSE UMV-201 & PWV-201 (API RP 14C)"),
    ]
    for k, (cap, val) in enumerate(wh_rows):
        ry = 542.0 - k * 6.5
        if k > 0:
            ctx.equip.append(line(25, ry + 3.25, 430, ry + 3.25))
        ctx.text(cap, 28, ry, size=1.8, left=True)
        ctx.text(val, 150, ry, size=2.0, left=True)

    # Tabel 2: ANNULUS MONITORING DATA (x = 450..645)
    ctx.equip += rect(450, 505, 645, 553)
    ctx.equip.append(line(450, 547, 645, 547))
    ctx.equip.append(line(545, 505, 545, 547))
    ctx.text("ANNULUS MONITORING DATA", 547, 550, size=2.4)
    an_rows = [
        ("ANNULUS A", "5-1/2 x 9-5/8 IN (N2 PAD)"),
        ("ANNULUS B", "9-5/8 x 13-3/8 IN (BRINE)"),
        ("ANNULUS C", "13-3/8 x 20 IN (CEMENTED)"),
        ("MONITORING", "NEEDLE VALVE + PI EACH OUTLET"),
        ("ACCESS", "MANUAL, TOP-OF-WORK STRING"),
        ("ALARM", "PI LOCAL READING PER SHIFT"),
    ]
    for k, (cap, val) in enumerate(an_rows):
        ry = 542.0 - k * 6.5
        if k > 0:
            ctx.equip.append(line(450, ry + 3.25, 645, ry + 3.25))
        ctx.text(cap, 453, ry, size=1.8, left=True)
        ctx.text(val, 548, ry, size=2.0, left=True)

    # -------------------------------------------------------------------------
    # 4. CHRISTMAS TREE VERTIKAL (cx = 170) — API SPEC 6A
    # -------------------------------------------------------------------------
    cx_tree = 170.0

    # 4.1 Wellbore: casing + tubing dengan gap SCSSV (REF-EQUIP)
    ctx.equip += ctx.wellbore(cx_tree, y_head_bot=138.0, y_shoe=45.0, scssv_cy=95.0)
    # Ground line (muka tanah) + arsiran tanah
    ctx.frame += [line(130, 138, 156, 138), line(184, 138, 215, 138)]
    for gx in range(134, 155, 4):
        ctx.hatch.append(line(gx, 138, gx - 3, 134.5))
    for gx in range(188, 214, 4):
        ctx.hatch.append(line(gx, 138, gx - 3, 134.5))
    ctx.text("WELL GPF-201", cx_tree, 30.0, size=2.5)
    ctx.text_right("SURFACE CASING 13-3/8 IN", 150.0, 110.0, size=1.8)

    # 4.2 SCSSV di badan sumur + label + control line masuk dari kanan (y=95)
    ctx.proc += ctx.scssv(cx_tree, 95.0, tag="SCSSV-201")
    ctx.text("SCSSV-201", 198.0, 100.0, size=2.2)
    ctx.text("HYD FAIL-CLOSE", 198.0, 90.0, size=1.8)

    # 4.3 Tubing head flange (THF) — REF-EQUIP
    ctx.equip += ctx.tubing_head_flange(cx_tree, 178.0, half_w=17.0, gap=3.0)
    ctx.text_right("TUBING HEAD FLANGE", 144.0, 179.5, size=1.8)

    # 4.4 Casing head body (REF-EQUIP) — rect menempel dinding casing
    ctx.equip += rect(156, 138, 184, 178)

    # 4.5 Bore utama tree (REF-PROC) — gap di LMV/UMV/Swab (flange tick 6.2)
    #      dan gap 233..241 di badan kotak aktuator UMV (garis masuk-keluar kotak).
    ctx.proc += pipe_run_v(cx_tree, 178.0, 305.0, gaps=[
        (195.0, 6.2), (225.0, 6.2), (237.0, 4.0), (285.0, 6.2),
    ])

    # 4.6 LMV — lower master valve (manual)
    ctx.proc += ctx.valve_gate_manual_v(cx_tree, 195.0, tag="LMV-201")
    ctx.text("LMV-201", 152.0, 195.0, size=2.2)

    # 4.7 UMV — upper master valve (hydraulic FC)
    ctx.proc += ctx.valve_gate_hydraulic_v(
        cx_tree, 225.0, act_w=12.0, act_h=8.0, tag="UMV-201", fail="FC"
    )
    ctx.text_right("UMV-201", 152.0, 208.0, size=2.2)

    # 4.8 Swab (crown) valve — manual, puncak tree
    ctx.proc += ctx.valve_gate_manual_v(cx_tree, 285.0, tag="SWV-201")
    ctx.text("SWV-201", 152.0, 285.0, size=2.2)

    # 4.9 Puncak tree: stub + PI-201
    ctx.proc += [line(cx_tree, 305.0, cx_tree, 309.0)]
    ctx.sym += ctx.gauge_pi(cx_tree, 315.0, num="201")

    # 4.10 Bleeder valve di puncak (stub ke kiri pada y=300)
    ctx.proc += [
        line(167.0, 300.0, 170.0, 300.0),
        line(162.0, 300.0, 158.0, 300.0),
        line(158.0, 298.5, 158.0, 301.5),
    ]
    ctx.proc += ctx.bleeder_valve_h(164.5, 300.0)

    # 4.11 Crossbar (y=255): kill wing (kiri) + production wing (kanan)
    #      Break 3 mm di CL tree (x=170) — bore utama major selalu utuh.
    ctx.proc += pipe_run_h(255.0, 72.5, 585.0, gaps=[
        (115.0, 6.2),   # NRV-201 check valve flanged
        (140.0, 6.2),   # KWV-201 manual gate flanged
        (170.0, 1.5),   # break minor di bore major (CL tree)
        (200.0, 6.2),   # PWV-201 hydraulic gate flanged
        (228.0, 6.5),   # XOV-201 choke house 221.5..234.5
    ])

    # Kill wing: check valve + KWV manual + battery limit dari kill pump
    ctx.proc += ctx.valve_check_h(115.0, 255.0, w=10.0, h=6.0)
    ctx.text("NRV-201", 115.0, 264.5, size=2.0)
    ctx.proc += ctx.valve_gate_manual_h(140.0, 255.0, tag="KWV-201")
    ctx.text("KWV-201", 140.0, 267.0, size=2.2)
    ctx.text("NC", 140.0, 271.5, size=1.8)
    ctx.proc += ctx.continuity_box_left(
        255.0, "050-WH-2002 DN50", "FROM KILL PUMP UNIT", "TIE-IN: WELL CONTROL SKID"
    )

    # Production wing: PWV hydraulic FC + adjustable choke
    ctx.proc += ctx.valve_gate_hydraulic_h(
        200.0, 255.0, act_w=12.0, act_h=8.0, tag="PWV-201", fail="FC"
    )
    ctx.text("PWV-201", 200.0, 247.0, size=2.2)
    ctx.proc += ctx.choke_adjustable_h(228.0, 255.0, w=13.0, h=8.0, tag="XOV-201")
    ctx.text("XOV-201", 228.0, 267.0, size=2.2)
    ctx.text("ADJUSTABLE CHOKE", 228.0, 244.0, size=1.8)

    # Flowline produksi ke battery limit
    ctx.text("150-WH-2001 DN150", 400.0, 261.5, size=1.8)
    ctx.proc += ctx.continuity_box_right(
        255.0, "150-WH-2001 DN150", "TO GAS PROCESSING FACILITY", "BATTERY LIMIT"
    )

    # 4.12 Annulus outlets A/B/C (needle valve + PI)
    ctx.proc += ctx.annulus_outlet_h(
        184.0, 170.0, direction=1, pi_num="202", label="ANNULUS A",
        label_dx=-9.0, label_dy=-5.5, label_left=True,
    )
    ctx.proc += ctx.annulus_outlet_h(
        156.0, 150.0, direction=-1, pi_num="203", label="ANNULUS B",
    )
    ctx.proc += ctx.annulus_outlet_h(
        184.0, 144.0, direction=1, pi_num="204", label="ANNULUS C",
        label_dx=23.0, label_dy=0.0, label_left=True,
    )

    # -------------------------------------------------------------------------
    # 5. PANEL HYDRAULIC ESD + SINYAL (REF-SIG) KE UMV / PWV / SCSSV
    # -------------------------------------------------------------------------
    ctx.equip += ctx.panel_box(380.0, 310.0, 470.0, 355.0)
    ctx.text("WELLHEAD HYDRAULIC", 425.0, 349.0, size=2.2)
    ctx.text("ESD PANEL", 425.0, 343.5, size=2.2)
    ctx.text("(FROM ESD-1 LOGIC SOLVER)", 425.0, 336.0, size=1.8)
    ctx.text("TO UMV-201", 394.0, 345.0, size=1.8, left=True)
    ctx.text("TO PWV-201", 394.0, 330.0, size=1.8, left=True)
    ctx.text("TO SCSSV-201", 394.0, 315.0, size=1.8, left=True)

    # Port 1 (y=345) -> UMV aktuator: drop x=185, break 3 mm di crossbar y=255
    ctx.sig += ctx.hydraulic_signal([(176.0, 239.0), (185.0, 239.0)])
    ctx.sig += ctx.hydraulic_signal([(185.0, 239.0), (185.0, 345.0)], brks=[[16.0]])
    ctx.sig += ctx.hydraulic_signal([(185.0, 345.0), (380.0, 345.0)])

    # Port 2 (y=330) -> PWV aktuator: drop x=200 (tanpa persilangan)
    ctx.sig += ctx.hydraulic_signal([(200.0, 330.0), (380.0, 330.0)])
    ctx.sig += ctx.hydraulic_signal([(200.0, 269.5), (200.0, 330.0)])

    # Port 3 (y=315) -> SCSSV control line: drop x=214 (break di y=255),
    # masuk ke SCSSV pada y=95 (break di casing x=184)
    ctx.sig += ctx.hydraulic_signal([(214.0, 315.0), (380.0, 315.0)])
    ctx.sig += ctx.hydraulic_signal([(214.0, 95.0), (214.0, 315.0)], brks=[[160.0]])
    ctx.sig += ctx.hydraulic_signal([(173.0, 95.0), (214.0, 95.0)], brks=[[11.0]])
    ctx.text("SCSSV CONTROL LINE 3000-10000 PSI", 220.0, 180.0, size=1.8, rot=90.0)

    # -------------------------------------------------------------------------
    # 6. PANAH ALIRAN (setiap line proses >= 1 panah)
    # -------------------------------------------------------------------------
    # Kill wing (masuk ke tree)
    ctx.flow_arrow_h(95.0, 255.0, direction=1, size=3.0)
    ctx.flow_arrow_h(127.0, 255.0, direction=1, size=2.4)
    ctx.flow_arrow_h(157.0, 255.0, direction=1, size=2.4)
    # Production wing & flowline (keluar dari tree)
    ctx.flow_arrow_h(178.0, 255.0, direction=1, size=2.4)
    ctx.flow_arrow_h(255.0, 255.0, direction=1)
    ctx.flow_arrow_h(350.0, 255.0, direction=1)
    ctx.flow_arrow_h(450.0, 255.0, direction=1)
    ctx.flow_arrow_h(550.0, 255.0, direction=1)
    # Bore vertikal naik (dari sumur ke puncak)
    ctx.flow_arrow_v(cx_tree, 130.0, direction=1, size=2.6)
    ctx.flow_arrow_v(cx_tree, 186.5, direction=1, size=2.4)
    ctx.flow_arrow_v(cx_tree, 216.0, direction=1, size=2.4)
    ctx.flow_arrow_v(cx_tree, 268.0, direction=1, size=2.4)
    ctx.flow_arrow_v(cx_tree, 297.0, direction=1, size=2.4)

    # -------------------------------------------------------------------------
    # 7. REGISTRASI LINE & EKSPOR MANIFEST
    # -------------------------------------------------------------------------
    ctx.register_line("150-WH-2001", spec="API 6A 5000 PSI", service="GAS PRODUCTION FLOWLINE", dn=150)
    ctx.register_line("050-WH-2002", spec="API 6A 5000 PSI", service="KILL LINE", dn=50)

    out_json = Path(__file__).resolve().parent / "wellhead_demo.texts.json"
    layers = ctx.export_manifest(out_json)
    return layers


if __name__ == "__main__":
    wellhead_demo()
