"""P&ID GPF-00-PI-PID-0012 Rev A0 — GAS COMPRESSION PACKAGE (2-STAGE RECIP).

Sheet A1 (841 x 594 mm), origin kiri-bawah.
Skema satu jalur gas 2 tingkat (API STD 618):
  BL -> V-201 suction scrubber -> K-201A stage 1 (pulsation dampener PD-201A/B,
  valve unloader 0-50-100 %, lube oil FSL-205, packing purge) -> E-201
  intercooler fin-fan (API 661, TIC-201 auto louver) -> V-202 suction scrubber
  -> K-201B stage 2 -> E-202 aftercooler -> F-201 coalescing filter separator
  -> BL gas export.
Loop proteksi: anti-surge recycle 200-CG-3006 (ASV-201 fast-open <= 1 s +
booster relay FY, UIC-201 dari PT-201/FT-202/PT-207/TT-207) dan blowdown/vent
(PSV-201/202, BDV-201) ke flare 200-FL-3008; drain LV otomatis ke 200-CD-3009.

Standar acuan:
  - API STD 618 / ISO 13631 (kompresor torak, pulsation DA-3, unloader,
    lube oil + FSL, distance piece purge)
  - API STD 617 (kompresor sentrifugal + DGS — simbol di LEGEND)
  - API STD 661 / ISO 13706 (fin-fan, auto louver TIC)
  - TEMA (shell & tube alternatif), API Spec 12J (scrubber), API STD 521
  - ANSI/ISA-5.1-2024, ISO 10628-2:2012, ISO 5457, ISO 7200

Layers:
  REF-FRAME  border lembar, grid referensi, kotak tabel furniture
  REF-TITLE  title block + rev table (ISO 7200 / Company Standard)
  REF-EQUIP  vessel, kompresor, fin-fan, coalescer, dampener, baseplate
  REF-PROC   line proses, valves, PSV, orifice, BL/continuity boxes
  REF-SYM    bubbles instrumen, DCS/UIC, louver, mini legend
  REF-SIG    signal listrik (dashed 4.0 / 1.6)
  REF-SIGP   signal pneumatic (solid + "//")
  REF-HATCH  arsiran 45 deg demister/coalescer/bundle
  REF-TEXT   ditulis post-build oleh apply_text.py dari manifest TEXTS (ARIAL)
"""

from __future__ import annotations

from pathlib import Path

from cadgen import dxf
from pid_common import (
    arc3,
    circle,
    dashed,
    dashed_brk,
    hatch45,
    line,
    pipe_run_h,
    pipe_run_v,
    pneu,
    rect,
)
from compression_common import CompressionContext


@dxf
def compression_demo():
    ctx = CompressionContext()

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
        "2. LINE DESIGNATION PER PIPING LINE INDEX. SPEC CLASS A1A / B1A (CS RF).",
        "3. INSTRUMENT SYMBOLS & TAGGING PER ANSI/ISA-5.1-2024; CONTENT PER",
        "   ISO 10628-2:2012.",
        "4. COMPRESSORS K-201A/B PER API STD 618 / ISO 13631, DOUBLE-ACTING",
        "   CYLINDER, AUTOMATIC PLATE SUCTION/DISCHARGE VALVES, DRIVER: MOTOR (M).",
        "5. CAPACITY CONTROL BY VALVE UNLOADERS, STEP 0-50-100 PERCENT.",
        "6. PULSATION DAMPENERS PD-201A/B, PD-202A/B PER API 618 DESIGN",
        "   APPROACH 3 ON SUCTION AND DISCHARGE OF EACH STAGE.",
        "7. CYLINDER LUBE OIL INJECTION FORCE-FED; FSL-205/FSL-206 LOW FLOW",
        "   ALARM/TRIP TO DRIVER. DISTANCE PIECE PACKING PURGED TO FLARE.",
        "8. SCRUBBER/COALESCER DRAINS VIA AUTO LEVEL VALVES LV-201/202/203",
        "   (LIC-201/202/203) TO CLOSED DRAIN 200-CD-3009.",
        "9. ANTI-SURGE: UIC-201 COMPUTES MARGIN TO SURGE LIMIT LINE FROM",
        "   PT-201, FT-202, PT-207, TT-207; OPENS ASV-201 IN <= 1.0 s WITH",
        "   BOOSTER RELAY; RECYCLE 200-CG-3006 RETURNS TO V-201 SUCTION.",
        "10. E-201/E-202 AIR COOLED PER API STD 661 / ISO 13706; TIC-201/202",
        "    MODULATES AUTO LOUVERS. SHELL & TUBE (TEMA) IS APPROVED ALTERNATIVE.",
        "11. PSV-201/202 SIZED PER API STD 521; RELIEF AND BDV-201 TO FLARE.",
        "12. CENTRIFUGAL COMPRESSOR SYMBOL (API STD 617 WITH DRY GAS SEAL)",
        "    SHOWN ON LEGEND - RESERVED FOR HIGH-CAPACITY / EXPORT SERVICE.",
    ]
    ny = 560.0
    for ln in notes:
        ctx.text(ln, 659, ny, size=2.0, left=True)
        ny -= 6.0

    # --- 2.2 LEGEND & SYMBOLS (y = 185..423) ---
    ctx.frame.append(line(655, 185, 823, 185))
    ctx.frame.append(line(655, 423, 823, 423))
    ctx.text("LEGEND & SYMBOLS", 739, 429, size=2.5)

    # Process line
    ctx.proc += [line(660, 413, 685, 413)]
    ctx.flow_arrow_h(676, 413, direction=1)
    ctx.text("PROCESS LINE", 695, 413, size=1.8, left=True)

    # Electric signal
    ctx.sig += dashed(660, 399, 685, 399)
    ctx.text("ELECTRIC SIGNAL (BPCS / SIS)", 695, 399, size=1.8, left=True)

    # Pneumatic signal
    ctx.sigp += pneu(660, 385, 685, 385)
    ctx.text("PNEUMATIC SIGNAL", 695, 385, size=1.8, left=True)

    # Reciprocating compressor mini (API STD 618)
    ctx.sym += [
        circle(663, 367, 4.0),
        line(667, 367, 671, 367),
        *rect(671, 362.5, 679, 371.5),
        line(679, 367, 682, 367),
        *rect(682, 363.5, 690, 370.5),
    ]
    ctx.text("RECIPROCATING COMPRESSOR (API STD 618)", 695, 367, size=1.8, left=True)

    # Centrifugal compressor mini (API STD 617 + DGS) — simbol kedua wajib
    ctx.compressor_centrifugal_617(cx=678, cy=345, r_in=3.5, r_out=5.5,
                                   tag="", casing="BARREL", driver="M")
    ctx.text("CENTRIFUGAL COMPRESSOR (API STD 617, DGS)", 695, 345, size=1.8, left=True)

    # Pulsation dampener mini
    ctx.sym += [line(660, 310, 686, 310)]
    ctx.pulsation_dampener(673, 310, tag="")
    ctx.text("PULSATION DAMPENER (API 618 DA-3)", 695, 315, size=1.8, left=True)

    # Fin-fan mini
    ctx.sym += rect(660, 292, 686, 300)
    ctx.hatch += hatch45(662, 293.5, 684, 298.5, spacing=2.0)
    ctx.sym += [
        circle(673, 304.5, 3.5),
        line(670, 301.5, 676, 307.5),
        line(670, 307.5, 676, 301.5),
    ]
    ctx.text("FIN-FAN AIR COOLER (API STD 661)", 695, 297, size=1.8, left=True)

    # Coalescer mini
    ctx.sym += [circle(667, 282, 5.0)]
    ctx.hatch += hatch45(663.5, 278.5, 670.5, 285.5, spacing=1.8)
    ctx.text("COALESCING FILTER SEPARATOR", 695, 282, size=1.8, left=True)

    # Anti-surge valve mini (globe + dome)
    ctx.sym += ctx.control_valve_h(673, 264, w=8.0, h=5.0, tag="")
    ctx.text("ANTI-SURGE VALVE (FAST-OPEN <= 1 s, BOOSTER FY)", 695, 264, size=1.8, left=True)

    # Valve unloader mini
    ctx.sym += rect(669, 250, 677, 255)
    ctx.text("VALVE UNLOADER 0-50-100 %", 695, 252, size=1.8, left=True)

    # Auto drain LV mini
    ctx.sym += ctx.control_valve_h(673, 234, w=8.0, h=5.0, tag="")
    ctx.text("AUTO DRAIN LV + LEVEL LOOP (LIC)", 695, 234, size=1.8, left=True)

    # Valve row: gate / globe / check
    ctx.sym += ctx.valve_gate_h(662, 222, w=7.0, h=4.5, flanged=False)
    ctx.sym += ctx.valve_globe_h(672, 222, w=7.0, h=4.5, flanged=False)
    ctx.sym += ctx.valve_check_h(683, 222, w=7.0, h=4.5)
    ctx.text("GATE / GLOBE / CHECK VALVE", 695, 222, size=1.8, left=True)

    # PSV mini
    ctx.sym += [
        line(669, 208, 677, 208),
        line(669, 208, 673, 215),
        line(677, 208, 673, 215),
        line(671, 215, 675, 215),
        line(671.5, 217, 674.5, 217),
        line(672, 219, 674, 219),
    ]
    ctx.text("PRESSURE SAFETY VALVE (PSV)", 695, 212, size=1.8, left=True)

    # Abbreviations
    ctx.text("FC: FAIL CLOSED        | CSO: CAR-SEAL OPEN", 659, 203, size=1.8, left=True)
    ctx.text("NC: NORMALLY CLOSED    | BDV: BLOWDOWN VALVE", 659, 197, size=1.8, left=True)
    ctx.text("DGS: DRY GAS SEAL      | SLL: SURGE LIMIT LINE", 659, 191, size=1.8, left=True)

    # --- 2.3 REFERENCE DRAWINGS (y = 148..185) ---
    ctx.frame.append(line(655, 148, 823, 148))
    ctx.frame.append(line(655, 175, 823, 175))
    ctx.text("REFERENCE DRAWINGS", 739, 180, size=2.2)
    ref_dwgs = [
        ("GPF-00-DB-0001", "DESIGN BASIS - GAS PRODUCTION FACILITY", 169.0),
        ("GPF-00-PI-PID-0001", "P&ID 3-PHASE PRODUCTION SEPARATOR V-101", 163.5),
        ("GPF-00-PI-PLN-0002", "PIPING PLAN - SEPARATOR AREA", 158.0),
        ("GPF-00-PM-PLN-0008", "ROADMAP AI-CAD SUITE (BAGIAN II KOMPRESI)", 152.5),
    ]
    for doc_no, doc_title, ry in ref_dwgs:
        ctx.text(f"{doc_no} : {doc_title}", 659, ry, size=1.8, left=True)

    # --- 2.4 REVISION TABLE (y = 116..148) ---
    ctx.title += [
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
    ctx.text("REV", 665, 145.0, size=1.8)
    ctx.text("DESCRIPTION", 719, 145.0, size=1.8)
    ctx.text("DATE", 779, 145.0, size=1.8)
    ctx.text("CHK", 802, 145.0, size=1.8)
    ctx.text("APP", 816, 145.0, size=1.8)
    rev_data = [
        ("A0", "ISSUED FOR REVIEW", "23 OCT 26", "PM", "RE", 118.6),
    ]
    for r_rev, r_desc, r_date, r_chk, r_app, ry in rev_data:
        ctx.text(r_rev, 665, ry, size=1.8)
        ctx.text(r_desc, 678, ry, size=1.8, left=True)
        ctx.text(r_date, 779, ry, size=1.8)
        ctx.text(r_chk, 802, ry, size=1.8)
        ctx.text(r_app, 816, ry, size=1.8)

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
    ctx.text("GAS COMPRESSION PACKAGE (2-STAGE)", 739, 80.0, size=2.5)
    ctx.text("DRAWING NO:", 658, 70.0, size=1.8, left=True)
    ctx.text("GPF-00-PI-PID-0012", 739, 65.5, size=2.8)
    ctx.text("REV:", 658, 56.5, size=1.8, left=True)
    ctx.text("A0", 697, 52.5, size=3.0)
    ctx.text("SCALE:", 742, 56.5, size=1.8, left=True)
    ctx.text("NTS", 781, 52.5, size=2.5)
    ctx.text("DATE:", 658, 44.5, size=1.8, left=True)
    ctx.text("23 OCT 2026", 697, 40.5, size=2.2)
    ctx.text("SHEET:", 742, 44.5, size=1.8, left=True)
    ctx.text("1 OF 1", 781, 40.5, size=2.5)
    ctx.text("DESIGNED:", 658, 32.5, size=1.8, left=True)
    ctx.text("CAD/FEED", 697, 29.0, size=2.2)
    ctx.text("DRAWN:", 742, 32.5, size=1.8, left=True)
    ctx.text("GLM-5.3-FLASH", 781, 29.0, size=2.2)
    ctx.text("CHECKED:", 658, 21.5, size=1.8, left=True)
    ctx.text("PM (AI)", 697, 18.5, size=2.2)
    ctx.text("APPROVED:", 742, 21.5, size=1.8, left=True)

    # -------------------------------------------------------------------------
    # 3. EQUIPMENT DATA TABLES (y = 515..573)
    # -------------------------------------------------------------------------
    ctx.equip += rect(135, 515, 375, 573)
    ctx.equip.append(line(135, 565, 375, 565))
    ctx.equip.append(line(228, 515, 228, 565))
    ctx.text("COMPRESSOR DATA - K-201A/K-201B (API STD 618)", 255, 569, size=2.4)
    k_rows = [
        ("TAG NUMBER", "K-201A / K-201B", 561.0),
        ("SERVICE", "GAS COMPRESSION STAGE 1 / STAGE 2", 553.0),
        ("TYPE", "DOUBLE-ACTING RECIPROCATING, 2-STAGE", 545.0),
        ("STANDARD", "API STD 618 / ISO 13631 (PULSATION DA-3)", 537.0),
        ("CAPACITY CONTROL", "AUTOMATIC VALVE UNLOADER 0-50-100 %", 529.0),
        ("DRIVER / LUBE", "ELECTRIC MOTOR (M) / FSL-205, FSL-206", 521.0),
    ]
    for k, (cap, val, ry) in enumerate(k_rows):
        if k > 0:
            ctx.equip.append(line(135, ry + 4.0, 375, ry + 4.0))
        ctx.text(cap, 138, ry, size=1.8, left=True)
        ctx.text(val, 232, ry, size=2.0, left=True)

    ctx.equip += rect(395, 515, 635, 573)
    ctx.equip.append(line(395, 565, 635, 565))
    ctx.equip.append(line(488, 515, 488, 565))
    ctx.text("ANTI-SURGE, COOLING & SEPARATION DATA", 515, 569, size=2.4)
    as_rows = [
        ("ANTI-SURGE VALVE", "ASV-201 GLOBE FC, FAST-OPEN <= 1.0 s", 561.0),
        ("UIC-201 INPUTS", "PT-201, FT-202, PT-207, TT-207 VS SLL", 553.0),
        ("FIN-FAN E-201/E-202", "API STD 661 / ISO 13706, TIC LOUVER", 545.0),
        ("SCRUBBERS V-201/V-202", "SUCTION SCRUBBER PER API SPEC 12J", 537.0),
        ("F-201", "COALESCING FILTER SEP., AUTO DRAIN LV-203", 529.0),
        ("RELIEF / BLOWDOWN", "PSV-201/202 + BDV-201 TO 200-FL-3008", 521.0),
    ]
    for k, (cap, val, ry) in enumerate(as_rows):
        if k > 0:
            ctx.equip.append(line(395, ry + 4.0, 635, ry + 4.0))
        ctx.text(cap, 398, ry, size=1.8, left=True)
        ctx.text(val, 492, ry, size=2.0, left=True)

    # =========================================================================
    # 4. MAIN GAS PATH (y = 300) — BL -> V-201 -> K-201A -> E-201 -> V-202
    #                     -> K-201B -> E-202 -> F-201 -> BL EXPORT
    # =========================================================================

    # --- 4.1 Battery limit masuk + V-201 suction scrubber ---
    ctx.proc += ctx.bl_box(
        y=300.0, x0=25.0, x1=68.0, dir=1,
        tag="200-CG-3001 DN200",
        desc="FROM PRODUCTION SEPARATOR V-101",
        dwg="DWG: GPF-00-PI-PID-0001",
    )
    ctx.proc += pipe_run_h(300.0, 72.5, 96.0)
    ctx.flow_arrow_h(81.0, 300.0, direction=1, size=2.4)
    ctx.text("200-CG-3001 DN200", 79.0, 308.0, size=1.8)
    scr1 = ctx.suction_scrubber(118.0, 250.0, 350.0, r=20.0, tag="V-201")

    # --- 4.2 V-201 gas outlet detour (atas) menuju stage 1 ---
    # Nozzle atas gas outlet (x=126) sudah digambar library (flange 362/363.2)
    ctx.proc += pipe_run_v(126.0, 363.2, 368.0)
    ctx.proc += pipe_run_h(368.0, 126.0, 210.0)
    ctx.proc += pipe_run_v(210.0, 300.0, 368.0)
    ctx.flow_arrow_v(126.0, 366.0, direction=1, size=1.6)
    ctx.flow_arrow_h(155.0, 368.0, direction=1, size=2.4)
    ctx.flow_arrow_v(210.0, 340.0, direction=-1, size=2.4)

    # --- 4.3 K-201A stage 1 + pulsation dampeners + packing purge ---
    k1 = ctx.compressor_reciprocating(240.0, 300.0, tag="K-201A",
                                      stage_label="STAGE 1", fsl_loop="205")
    ctx.pulsation_dampener(246.0, 300.0, tag="PD-201A")
    ctx.pulsation_dampener(258.0, 300.0, tag="PD-201B")
    ctx.drop_v(k1["purge_x"], 185.0, k1["purge_y"], breaks=(230.0,), valve_y=245.0)
    ctx.text("PURGE TO FLARE", 229.0, 205.0, size=1.8, rot=90.0)
    ctx.flow_arrow_v(237.0, 208.0, direction=-1, size=2.4)

    # --- 4.4 Interstage ke E-201 fin-fan intercooler ---
    ctx.proc += pipe_run_h(300.0, 210.0, 295.0, gaps=[(228.0, 1.2)])
    ctx.proc += ctx.orifice_h(228.0, 300.0, tag_fe="")
    ctx.text("FE-202", 222.0, 292.0, size=1.8, rot=90.0)
    ctx.proc += [line(220.0, 300.0, 220.0, 309.0)]        # PT-201 well
    ctx.sym += ctx.bubble(220.0, 315.0, "PT", "201")
    ctx.proc += [line(228.0, 306.0, 228.0, 309.0)]        # FT-202 lead
    ctx.sig += dashed(228.0, 309.0, 228.0, 339.0)
    ctx.sym += ctx.bubble(228.0, 345.0, "FT", "202")
    ctx.sig += dashed(220.0, 321.0, 220.0, 355.0)
    ctx.sig += dashed(228.0, 321.0, 228.0, 355.0)
    e1 = ctx.fin_fan_cooler(310.0, 300.0, tag="E-201", tee_dx=15.0)
    ctx.text("E-201 INTERCOOLER (FIN-FAN)", 300.0, 402.0, size=2.5)
    ctx.sym += ctx.bubble(325.0, 394.0, "TIC", "201")
    # TIC-201 ke auto louver: jog kanan ke x=337 agar tidak menembus
    # lingkaran motor M E-201 (temuan QA visual). Break 3 mm saat
    # menyeberang line inlet PSV-202 (y=382.8) di x=325.
    ctx.sig += dashed_brk(325.0, 378.0, 325.0, 388.0, brk=[4.8])
    ctx.sig += dashed(325.0, 378.0, 337.0, 378.0)
    ctx.sig += dashed(337.0, 336.0, 337.0, 378.0)
    ctx.sig += dashed(331.0, 336.0, 337.0, 336.0)
    # TT-201 outlet temperature + sinyal ke TIC-201
    ctx.proc += [line(368.0, 300.0, 368.0, 309.0)]
    ctx.sym += ctx.bubble(368.0, 315.0, "TT", "201")
    ctx.sig += dashed_brk(368.0, 321.0, 368.0, 394.0, brk=[63.0])
    ctx.sig += dashed(331.0, 394.0, 368.0, 394.0)

    # --- 4.5 V-202 suction scrubber interstage ---
    ctx.proc += pipe_run_h(300.0, 325.0, 403.0)
    ctx.flow_arrow_h(348.0, 300.0, direction=1, size=2.4)
    scr2 = ctx.suction_scrubber(435.0, 250.0, 350.0, r=20.0, tag="V-202")

    # --- 4.6 V-202 gas outlet detour ke stage 2 ---
    ctx.proc += pipe_run_v(443.0, 363.2, 368.0)
    ctx.proc += pipe_run_h(368.0, 443.0, 500.0)
    ctx.proc += pipe_run_v(500.0, 300.0, 368.0)
    ctx.flow_arrow_v(443.0, 366.0, direction=1, size=1.6)
    ctx.flow_arrow_h(470.0, 368.0, direction=1, size=2.4)
    ctx.flow_arrow_v(500.0, 340.0, direction=-1, size=2.4)
    ctx.text("200-CG-3003 DN150", 470.0, 374.0, size=1.8)

    # --- 4.7 K-201B stage 2 + dampeners + purge ---
    k2 = ctx.compressor_reciprocating(505.0, 300.0, tag="K-201B",
                                      stage_label="STAGE 2", fsl_loop="206")
    ctx.pulsation_dampener(511.0, 300.0, tag="PD-202A")
    ctx.pulsation_dampener(523.0, 300.0, tag="PD-202B")
    ctx.drop_v(k2["purge_x"], 185.0, k2["purge_y"], breaks=(230.0,), valve_y=245.0)
    ctx.text("PURGE TO FLARE", 494.0, 205.0, size=1.8, rot=90.0)
    ctx.flow_arrow_v(502.0, 208.0, direction=-1, size=2.4)

    # --- 4.8 Discharge stage 2 + PT-207/TT-207 + E-202 aftercooler ---
    ctx.proc += pipe_run_h(300.0, 500.0, 550.0)
    ctx.proc += [line(538.0, 300.0, 538.0, 309.0)]
    ctx.proc += [line(538.0, 321.0, 538.0, 329.0)]
    ctx.proc += [line(538.0, 341.0, 538.0, 345.0)]
    ctx.sym += ctx.bubble(538.0, 315.0, "PT", "207")
    ctx.sym += ctx.bubble(538.0, 335.0, "TT", "207")
    e2 = ctx.fin_fan_cooler(570.0, 300.0, tag="E-202", tee_dx=20.0)
    ctx.text("E-202 AFTERCOOLER (FIN-FAN)", 570.0, 402.0, size=2.5)
    ctx.sym += ctx.bubble(556.0, 388.0, "TIC", "202")
    ctx.sig += dashed(556.0, 336.0, 556.0, 382.0)

    # --- 4.9 Tail: up-leg -> F-201 coalescer -> BL gas export ---
    ctx.proc += pipe_run_h(300.0, 590.0, 600.0)
    ctx.flow_arrow_h(596.0, 300.0, direction=1, size=2.0)
    ctx.proc += pipe_run_v(600.0, 300.0, 385.0)
    ctx.flow_arrow_v(600.0, 340.0, direction=1, size=2.4)
    ctx.proc += pipe_run_h(385.0, 600.0, 604.0)
    f1 = ctx.coalescing_filter(620.0, 340.0, 430.0, r=14.0, tag="F-201", inlet_y=385.0)
    ctx.proc += pipe_run_v(620.0, f1["top_flange_y"], 448.0)
    ctx.proc += pipe_run_h(448.0, 603.0, 620.0)
    ctx.flow_arrow_v(620.0, 443.0, direction=1, size=2.4)
    ctx.flow_arrow_h(612.0, 448.0, direction=-1, size=2.4)
    ctx.proc += ctx.bl_box(
        y=448.0, x0=560.0, x1=603.0, dir=-1,
        tag="200-CG-3004 DN100",
        desc="TO GAS EXPORT METERING",
        dwg="DWG: GPF-00-PI-PID-0014",
    )
    ctx.text("200-CG-3004 DN100", 570.0, 290.0, size=1.8)
    ctx.text("200-CG-3004 DN100", 592.0, 342.0, size=1.8, rot=90.0)
    ctx.text("200-CG-3002 DN150", 293.0, 290.0, size=1.8)

    # =========================================================================
    # 5. ANTI-SURGE RECYCLE 200-CG-3006 (discharge -> V-201 suction)
    # =========================================================================
    ctx.drop_v(530.0, 230.0, 300.0)
    ctx.proc += pipe_run_h(230.0, 176.0, 530.0, gaps=[(350.0, 6.2)])
    ctx.drop_v(176.0, 230.0, 368.0)
    ctx.flow_arrow_h(185.0, 230.0, direction=-1, size=2.4)
    ctx.flow_arrow_h(260.0, 230.0, direction=-1, size=2.4)
    ctx.flow_arrow_h(490.0, 230.0, direction=-1, size=2.4)
    ctx.proc += ctx.anti_surge_valve_h(350.0, 230.0, tag="ASV-201", fail="FC", fy_no="201")
    ctx.sym += ctx.dcs(346.0, 262.0, "UIC", "201")
    ctx.text("ANTI-SURGE CONTROLLER", 376.0, 275.0, size=1.8)
    ctx.sig += dashed(350.0, 252.0, 350.0, 254.5)
    # Sinyal hisap: PT-201 & FT-202 -> UIC-201
    ctx.sig += dashed_brk(220.0, 355.0, 342.0, 355.0, brk=[58.0])
    ctx.sig += dashed_brk(342.0, 269.5, 342.0, 355.0, brk=[30.5])
    # Sinyal tekan: PT-207 & TT-207 -> UIC-201. Bus di-jog naik ke y=390
    # (di x=400) agar memutar head V-202 — temuan QA: dashed semula
    # menembus outline vessel. Break 3 mm saat menyeberang line inlet
    # PSV-202 (y=382.8); ujung menggantung lama (x=582) dihapus.
    ctx.sig += dashed(538.0, 345.0, 538.0, 390.0)
    ctx.sig += dashed(350.0, 355.0, 400.0, 355.0)
    ctx.sig += dashed_brk(400.0, 355.0, 400.0, 390.0, brk=[27.8])
    ctx.sig += dashed(400.0, 390.0, 538.0, 390.0)
    ctx.sig += dashed_brk(350.0, 269.5, 350.0, 355.0, brk=[30.5])
    ctx.text("200-CG-3006 DN100", 410.0, 236.0, size=1.8)
    ctx.text("ANTI-SURGE RECYCLE", 410.0, 224.0, size=1.8)

    # =========================================================================
    # 6. FLARE HEADER 200-FL-3008 (y = 185) & DRAIN HEADER 200-CD-3009 (y = 150)
    # =========================================================================
    ctx.proc += pipe_run_h(185.0, 45.0, 560.0)
    ctx.proc += [line(45.0, 182.0, 45.0, 188.0)]
    ctx.proc += ctx.bl_box(
        y=185.0, x0=560.0, x1=603.0, dir=1,
        tag="200-FL-3008 DN150",
        desc="TO FLARE HEADER",
        dwg="DWG: GPF-00-PI-PID-0001",
    )
    ctx.text("200-FL-3008 DN150", 350.0, 191.0, size=1.8)
    ctx.flow_arrow_h(150.0, 185.0, direction=1, size=2.4)
    ctx.flow_arrow_h(320.0, 185.0, direction=1, size=2.4)
    ctx.flow_arrow_h(450.0, 185.0, direction=1, size=2.4)
    ctx.flow_arrow_h(530.0, 185.0, direction=1, size=2.4)

    # PSV-201 (V-201) & PSV-202 (V-202) + isolasi CSO + BDV-201
    ctx.proc += pipe_run_v(110.0, 363.2, 384.0, gaps=[(372.0, 5.0)])
    ctx.proc += ctx.valve_gate_v(110.0, 372.0, w=6.0, h=10.0, flanged=False, tag="GV-203")
    ctx.text("GV-203", 134.0, 380.0, size=1.8)
    ctx.text("CSO", 134.0, 375.8, size=1.8)
    ctx.proc += pipe_run_h(382.8, 65.2, 110.0)
    ctx.proc += [line(54.8, 382.8, 56.0, 384.0)]
    ctx.proc += ctx.psv_angle(60.0, 392.0, tag="PSV-201", size_str="DN100x150",
                              set_press="SET 17.2 BARG")
    ctx.proc += pipe_run_h(392.0, 69.2, 92.0)
    ctx.flow_arrow_h(80.0, 392.0, direction=1, size=2.0)
    ctx.drop_v(92.0, 185.0, 392.0, breaks=(300.0, 382.8))
    ctx.flow_arrow_v(92.0, 240.0, direction=-1, size=2.4)

    ctx.proc += pipe_run_v(427.0, 363.2, 384.0, gaps=[(372.0, 5.0)])
    ctx.proc += ctx.valve_gate_v(427.0, 372.0, w=6.0, h=10.0, flanged=False, tag="GV-204")
    ctx.text("GV-204", 415.0, 380.0, size=1.8)
    ctx.text("CSO", 415.0, 375.8, size=1.8)
    ctx.proc += pipe_run_h(382.8, 270.2, 427.0)
    ctx.proc += [line(259.8, 382.8, 261.0, 384.0)]
    ctx.proc += ctx.psv_angle(265.0, 392.0, tag="PSV-202", size_str="DN100x150",
                              set_press="SET 26.0 BARG")
    ctx.proc += pipe_run_h(392.0, 274.2, 278.0)
    ctx.drop_v(278.0, 185.0, 392.0, breaks=(230.0, 300.0, 382.8))
    ctx.flow_arrow_v(278.0, 210.0, direction=-1, size=2.4)

    ctx.drop_v(546.0, 185.0, 300.0, valve_y=262.0, valve_tag="BDV-201")
    ctx.text("BDV-201", 560.0, 266.0, size=1.8)
    ctx.text("NC", 560.0, 261.0, size=1.8)
    ctx.flow_arrow_v(546.0, 208.0, direction=-1, size=2.4)

    # Drain header
    ctx.proc += pipe_run_h(150.0, 100.0, 648.0)
    ctx.proc += [line(100.0, 147.0, 100.0, 153.0)]
    ctx.flow_arrow_h(652.0, 150.0, direction=1, size=3.2)
    ctx.text("200-CD-3009 DN50", 300.0, 156.0, size=1.8)
    ctx.text("TO CLOSED DRAIN DRUM", 300.0, 143.0, size=2.0)
    ctx.flow_arrow_h(200.0, 150.0, direction=1, size=2.4)
    ctx.flow_arrow_h(240.0, 150.0, direction=1, size=2.4)
    ctx.flow_arrow_h(390.0, 150.0, direction=1, size=2.4)
    ctx.flow_arrow_h(560.0, 150.0, direction=1, size=2.4)
    ctx.flow_arrow_h(620.0, 150.0, direction=1, size=2.4)

    # =========================================================================
    # 7. DRAIN LV OTOMATIS + LEVEL LOOP TIAP BEJANA
    # =========================================================================
    # V-201
    tee = ctx.drain_lv_h(118.0, scr1["drain_y"], 222.0, 150.0, tag_lv="LV-201",
                         breaks2=(185.0,))
    ctx.proc += [line(138.0, 258.0, 142.0, 258.0)]
    ctx.sym += ctx.bubble(148.0, 258.0, "LT", "201")
    ctx.sym += ctx.dcs(148.0, 237.0, "LIC", "201")
    ctx.sig += dashed(148.0, 252.0, 148.0, 244.5)
    ctx.sig += dashed(150.0, 229.5, 150.0, 240.0)
    ctx.sig += dashed(150.0, 240.0, 126.0, 240.0)
    ctx.sig += dashed(126.0, 240.0, 126.0, 235.0)
    ctx.flow_arrow_v(136.0, 190.0, direction=-1, size=2.4)

    # V-202
    tee = ctx.drain_lv_h(435.0, scr2["drain_y"], 222.0, 150.0, tag_lv="LV-202",
                         breaks1=(230.0,), breaks2=(185.0,))
    ctx.proc += [line(455.0, 258.0, 459.0, 258.0)]
    ctx.sym += ctx.bubble(465.0, 258.0, "LT", "202")
    ctx.sym += ctx.dcs(465.0, 240.0, "LIC", "202")
    ctx.sig += dashed(465.0, 252.0, 465.0, 247.5)
    ctx.sig += dashed(457.5, 240.0, 443.0, 240.0)
    ctx.sig += dashed(443.0, 240.0, 443.0, 235.0)
    ctx.flow_arrow_v(453.0, 190.0, direction=-1, size=2.4)

    # F-201
    tee = ctx.drain_lv_h(620.0, f1["drain_y"], 222.0, 150.0, tag_lv="LV-203", dir=-1)
    ctx.proc += [line(634.0, 383.0, 638.0, 383.0)]
    ctx.sym += ctx.bubble(644.0, 383.0, "LT", "203")
    ctx.sym += ctx.dcs(644.0, 355.0, "LIC", "203")
    ctx.sig += dashed(644.0, 377.0, 644.0, 362.5)
    ctx.sig += dashed(644.0, 347.5, 644.0, 240.0)
    ctx.sig += dashed_brk(612.0, 240.0, 644.0, 240.0, brk=[8.0])
    ctx.sig += dashed(612.0, 240.0, 612.0, 235.0)
    ctx.flow_arrow_v(602.0, 190.0, direction=-1, size=2.4)

    # =========================================================================
    # 8. REGISTRI LINE & EXPORT MANIFEST
    # =========================================================================
    ctx.register_line("200-CG-3001", spec="150# A1A", service="Gas suction st.1", dn=200)
    ctx.register_line("200-CG-3002", spec="150# A1A", service="Interstage", dn=150)
    ctx.register_line("200-CG-3003", spec="150# A1A", service="Gas suction st.2", dn=150)
    ctx.register_line("200-CG-3004", spec="300# B1A", service="Gas export", dn=100)
    ctx.register_line("200-CG-3006", spec="150# A1A", service="Anti-surge recycle", dn=100)
    ctx.register_line("200-FL-3008", spec="150# A1A", service="Flare/relief", dn=150)
    ctx.register_line("200-CD-3009", spec="150# A1A", service="Closed drain", dn=50)

    out_json = Path(__file__).resolve().parent / "compression_demo.texts.json"
    layers = ctx.export_manifest(out_json)
    return layers


if __name__ == "__main__":
    compression_demo()
