"""P&ID GPF-00-PI-PID-0015 Rev A0 — CUSTODY METERING STATION.

Sheet A1 (841 x 594 mm), origin kiri-bawah.
Arsitektur multi-run (Bagian IV.1 GPF-00-PM-PLN-0008 Rev A2):
  Inlet Header 200-MT-6001 -> 3 Run Paralel -> Outlet Header 200-MT-6005
    - RUN 1: Ultrasonic Flow Meter (DUTY)      200-MT-6002 (AGA 9 / ISO 17089)
    - RUN 2: Orifice Senior Fitting (DUTY)     200-MT-6003 (AGA 3 / ISO 5167)
    - RUN 3: Coriolis Mass Meter  (STANDBY)    200-MT-6004 (AGA 11 / API MPMS)
  Setiap run diisolasi Double Block & Bleed (twin plug, bubble-tight) di inlet
  & outlet dengan cavity bleed; fast loop sampling probe + Gas Chromatograph
  online (C1-C6+, CO2, N2, GHV) ke flow computer FQI tiap run.

Standar acuan:
  - AGA Report No. 3 / 7 / 9 / 11 (+ AGA 8 untuk GHV), API MPMS Ch. 5 & 14
  - ISO 5167, ISO 17089, API 6D (DBB), ANSI/ISA-5.1-2024, ISO 10628-2:2012
  - ISO 5457:1999 (lembar), ISO 7200:2004 (title block)

Layers:
  REF-FRAME  border lembar, grid referensi, kotak tabel furniture
  REF-TITLE  title block + rev table (ISO 7200 / Company Standard)
  REF-EQUIP  body meter run, GC analyzer, tabel equipment data
  REF-PROC   line proses, manifold, DBB, meter run internals, fast loop
  REF-SYM    bubble instrumen, FQI, simbol legend
  REF-SIG    sinyal elektrik (dashed 2.5 / 1.2) GC & FT ke FQI
  REF-TEXT   ditulis post-build oleh apply_text.py dari manifest TEXTS (ARIAL)
"""

from __future__ import annotations

from pathlib import Path

from cadgen import dxf
from metering_common import (
    DBB_HALF,
    MeteringContext,
    circle,
    dashed,
    line,
    rect,
)
from pid_common import arc, dashed_brk


@dxf
def metering_demo():
    ctx = MeteringContext()

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
        "2. METERING PER AGA RPT 3/7/9/11, API MPMS CH.5 & 14, ISO 5167, ISO 17089.",
        "3. EACH METER RUN ISOLATED BY DOUBLE BLOCK & BLEED (DBB) TWIN PLUG",
        "   VALVES, BUBBLE-TIGHT SHUT-OFF WITH CAVITY BLEED (BLD) TO CLOSED DRAIN.",
        "4. RUN 1 (USM) & RUN 2 (ORIFICE) DUTY; RUN 3 (CORIOLIS) STANDBY -",
        "   AUTOMATIC SWITCHOVER BY FLOW COMPUTERS FQI-611/621/631.",
        "5. SENIOR DUAL-CHAMBER FITTING OF-6021 PERMITS ORIFICE PLATE CHANGE",
        "   UNDER PROCESS PRESSURE WITHOUT SHUTDOWN.",
        "6. USM-6001 SPOOL 10D-20D WITH ZANKER CONDITIONER PER AGA 9 / ISO 17089.",
        "7. FAST LOOP SAMPLE TO GC AT-6090 (C1-C6+, CO2, N2); GHV TO FQI PER",
        "   AGA 8. SAMPLE RETURN VIA SAMPLE RECOVERY - SEE GPF-00-PI-PID-0016.",
        "8. LINE NUMBERS 200-MT-6001..6005 PER PIPING LINE INDEX (PATTERN 200-MT-60XX).",
        "9. SIZES/DIMENSIONS FOR CLARITY ONLY - REFER TO PIPING LINE INDEX.",
        "10. EQUIPMENT DESIGN: METERS PER API MPMS; DBB VALVES PER API 6D.",
    ]
    ny = 560.0
    for ln in notes:
        ctx.text(ln, 659, ny, size=2.0, left=True)
        ny -= 8.3

    # --- 2.2 LEGEND & SYMBOLS (y = 185..435) ---
    ctx.frame.append(line(655, 185, 823, 185))
    ctx.frame.append(line(655, 423, 823, 423))
    ctx.text("LEGEND & SYMBOLS", 739, 429, size=2.5)

    # (a) Ultrasonic meter mini (spool + conditioner + korda transduser)
    ly = 408.0
    ctx.sym += rect(660, ly - 5, 690, ly + 5)
    ctx.sym += [line(665, ly - 5, 665, ly + 5), line(666, ly - 5, 666, ly + 5)]
    ctx.sym += [line(660, ly + 3, 690, ly - 1), line(660, ly + 1, 690, ly - 3)]
    ctx.text("ULTRASONIC FLOW METER (USM) - AGA 9 / ISO 17089", 695, ly, size=2.0, left=True)

    # (b) Flow conditioner mini (Zanker plate + lubang)
    ly = 390.0
    ctx.sym += [line(668, ly - 5, 668, ly + 5), line(669, ly - 5, 669, ly + 5)]
    ctx.sym += [circle(668.5, ly - 3, 0.8), circle(668.5, ly, 0.8), circle(668.5, ly + 3, 0.8)]
    ctx.text("FLOW CONDITIONER (ZANKER / TUBE BUNDLE)", 695, ly, size=2.0, left=True)

    # (c) Coriolis mini (U-tube + drive/pickup)
    ly = 372.0
    ctx.sym += rect(660, ly - 5, 690, ly + 5)
    ctx.sym += [
        line(663, ly + 3, 685, ly + 3), line(663, ly - 3, 685, ly - 3),
        line(663, ly + 3, 663, ly - 3),
    ]
    ctx.sym.append(arc(685.0, ly, 3.0, -90, 90))
    ctx.sym += [line(672, ly - 3, 672, ly + 3), line(678, ly - 3, 678, ly + 3)]
    ctx.text("CORIOLIS MASS METER - AGA 11 / API MPMS 5.6", 695, ly, size=2.0, left=True)

    # (d) Orifice senior fitting mini (dual chamber + plate)
    ly = 352.0
    ctx.sym += rect(660, ly - 6, 690, ly)
    ctx.sym += [
        line(664, ly, 664, ly + 6), line(686, ly, 686, ly + 6),
        line(664, ly + 6, 686, ly + 6),
        line(674, ly - 6, 674, ly + 6), line(675, ly - 6, 675, ly + 6),
    ]
    ctx.text("SENIOR DUAL-CHAMBER ORIFICE FITTING - AGA 3 / ISO 5167", 695, ly, size=2.0, left=True)

    # (e) Turbine mini (bundle + rotor + PU)
    ly = 334.0
    ctx.sym += rect(660, ly - 5, 690, ly + 5)
    ctx.sym += [circle(665, ly - 2.6, 1.0), circle(665, ly, 1.0), circle(665, ly + 2.6, 1.0)]
    ctx.sym.append(circle(679, ly, 3.0))
    ctx.sym += [line(677.9, ly - 1.1, 676.9, ly - 2.1), line(680.1, ly - 1.1, 681.1, ly - 2.1),
                line(677.9, ly + 1.1, 676.9, ly + 2.1), line(680.1, ly + 1.1, 681.1, ly + 2.1)]
    ctx.sym += [line(679, ly + 5, 679, ly + 7), line(676.5, ly + 7, 681.5, ly + 7)]
    ctx.text("TURBINE FLOW METER - AGA 7 / API MPMS 5.3", 695, ly, size=2.0, left=True)

    # (f) DBB mini (twin plug + cavity bleed)
    ly = 316.0
    for vx in (661.0, 673.0):
        ctx.sym += [
            line(vx - 4, ly - 2.5, vx, ly), line(vx, ly, vx - 4, ly + 2.5),
            line(vx - 4, ly - 2.5, vx - 4, ly + 2.5),
            line(vx + 4, ly - 2.5, vx, ly), line(vx, ly, vx + 4, ly + 2.5),
            line(vx + 4, ly - 2.5, vx + 4, ly + 2.5),
        ]
    ctx.sym.append(line(665, ly, 669, ly))
    ctx.sym += [
        line(667, ly, 667, ly + 2.2), line(666, ly + 2.2, 668, ly + 2.2),
        line(666, ly + 2.2, 667, ly + 3.4), line(667, ly + 3.4, 668, ly + 2.2),
        line(666, ly + 2.2, 666, ly + 4.6), line(668, ly + 2.2, 668, ly + 4.6),
        line(666, ly + 4.6, 668, ly + 4.6), line(667, ly + 4.6, 667, ly + 6.0),
        line(665.5, ly + 6.0, 668.5, ly + 6.0),
    ]
    ctx.text("DOUBLE BLOCK & BLEED VALVE (BUBBLE-TIGHT)", 695, ly, size=2.0, left=True)

    # (g) Flow computer FQI mini
    ly = 298.0
    ctx.sym += ctx.dcs(668, ly, "", "")
    ctx.text("FLOW COMPUTER (FQI / FC)", 695, ly, size=2.0, left=True)

    # (h) GC analyzer mini
    ly = 280.0
    ctx.sym += rect(660, ly - 6, 686, ly + 6)
    ctx.text("ONLINE GAS CHROMATOGRAPH (GC) - C1-C6+, CO2, N2, GHV", 695, ly, size=2.0, left=True)

    # (i) Fast loop sampling probe mini
    ly = 262.0
    ctx.sym += [line(670, ly - 3, 670, ly + 5)]
    ctx.sym += ctx.valve_gate_v(670, ly, w=3.2, h=5.0, flanged=False)
    ctx.text("FAST LOOP SAMPLING PROBE + ISOLATION VALVE", 695, ly, size=2.0, left=True)

    # (j) Process line + flow arrow
    ly = 244.0
    ctx.proc += [line(660, ly, 685, ly)]
    ctx.flow_arrow_h(675, ly, direction=1)
    ctx.text("PROCESS LINE / FLOW DIRECTION", 695, ly, size=2.0, left=True)

    # (k) Electric signal
    ly = 228.0
    ctx.sig += dashed(660, ly, 685, ly, dash=2.0, gap=1.2)
    ctx.text("ELECTRIC SIGNAL (GC / FT TO FQI)", 695, ly, size=2.0, left=True)

    # Standard abbreviations
    ctx.text("STANDARD ABBREVIATIONS:", 659, 212, size=1.9, left=True)
    ctx.text("DBB: DOUBLE BLOCK & BLEED  |  BLD: CAVITY BLEED", 659, 203, size=1.8, left=True)
    ctx.text("FQI: FLOW COMPUTER  |  GHV: GROSS HEATING VALUE", 659, 195, size=1.8, left=True)
    ctx.text("DT/TT: DENSITY / TEMPERATURE TRANSMITTER", 659, 187, size=1.8, left=True)

    # --- 2.3 REFERENCE DRAWINGS (y = 148..185) ---
    ctx.frame.append(line(655, 148, 823, 148))
    ctx.frame.append(line(655, 175, 823, 175))
    ctx.text("REFERENCE DRAWINGS", 739, 180, size=2.2)
    ref_dwgs = [
        ("GPF-00-DB-0001", "DESIGN BASIS - GAS PRODUCTION FACILITY", 169.0),
        ("GPF-00-PI-PID-0001", "P&ID - 3-PHASE PRODUCTION SEPARATOR V-101", 163.5),
        ("GPF-00-PI-PID-0016", "P&ID - LBCV / EXPORT PIPELINE STATION", 158.0),
        ("GPF-00-PM-PLN-0008", "ROADMAP METERING, LBCV & UNDERGROUND (REV A2)", 152.5),
    ]
    for doc_no, doc_title, ry in ref_dwgs:
        ctx.text(f"{doc_no} : {doc_title}", 659, ry, size=1.8, left=True)

    # --- 2.4 REVISION TABLE (Bottom-Up, y = 116..148) ---
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
    ctx.text("CUSTODY METERING STATION", 739, 80.0, size=2.5)
    ctx.text("DRAWING NO:", 658, 70.0, size=1.8, left=True)
    ctx.text("GPF-00-PI-PID-0015", 739, 65.5, size=2.8)
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
    ctx.text("EQUIPMENT DATA - METER RUN USM-6001 (RUN 1)", 255, 569, size=2.4)
    usm_rows = [
        ("TAG NUMBER", "USM-6001 (RUN 1 - DUTY)", 561.0),
        ("SERVICE NAME", "CUSTODY TRANSFER GAS METERING", 553.0),
        ("METER TYPE", "MULTI-PATH ULTRASONIC (AGA 9 / ISO 17089)", 545.0),
        ("METER SPOOL", "10D-20D + ZANKER FLOW CONDITIONER", 537.0),
        ("DESIGN P/T", "17.2 BARG / 60 DEG C (OPER 10.0 BARG / 40 DEG C)", 529.0),
        ("OUTPUT", "FQI-611 VOLUME + ENERGY (GHV FROM AT-6090)", 521.0),
    ]
    for k, (cap, val, ry) in enumerate(usm_rows):
        if k > 0:
            ctx.equip.append(line(135, ry + 4.0, 375, ry + 4.0))
        ctx.text(cap, 138, ry, size=1.8, left=True)
        ctx.text(val, 232, ry, size=2.0, left=True)

    ctx.equip += rect(395, 515, 635, 573)
    ctx.equip.append(line(395, 565, 635, 565))
    ctx.equip.append(line(488, 515, 488, 565))
    ctx.text("EQUIPMENT DATA - GAS ANALYZER AT-6090", 515, 569, size=2.4)
    gc_rows = [
        ("TAG NUMBER", "AT-6090 (GC-1)", 561.0),
        ("SERVICE NAME", "ONLINE GAS CHROMATOGRAPH", 553.0),
        ("ANALYSIS", "C1-C6+ / CO2 / N2 (MOLE %)", 545.0),
        ("OUTPUT", "GHV + DENSITY TO FQI PER AGA 8 / ISO 6976", 537.0),
        ("SAMPLE POINT", "FAST LOOP PROBE, INLET HEADER 200-MT-6001", 529.0),
        ("HOUSING", "EXPEDITION GRADE, PRESSURIZED ENCLOSURE (EX P)", 521.0),
    ]
    for k, (cap, val, ry) in enumerate(gc_rows):
        if k > 0:
            ctx.equip.append(line(395, ry + 4.0, 635, ry + 4.0))
        ctx.text(cap, 398, ry, size=1.8, left=True)
        ctx.text(val, 492, ry, size=2.0, left=True)

    # -------------------------------------------------------------------------
    # 4. HEADER MASUK & MANIFOLD INLET (200-MT-6001)
    # -------------------------------------------------------------------------
    ctx.proc += ctx.continuity_box_left(300.0, "200-MT-6001 DN300", "FROM GAS PROCESSING PLANT", "DWG: GPF-00-PI-PID-0001")
    ctx.metering_header(72.5, 130.0, 300.0, "200-MT-6001", dn=300, label_x=78.0)
    ctx.text("INLET HEADER", 77.0, 310.5, size=1.8)
    ctx.manifold_v(130.0, 170.0, 430.0)
    ctx.flow_arrow_v(130.0, 395.0, direction=-1)   # naik ke RUN 1
    ctx.flow_arrow_v(130.0, 230.0, direction=1)    # turun ke RUN 3

    # -------------------------------------------------------------------------
    # 5. TIGA METER RUN PARALEL (x tee = 130, DBB-in 170, meter 245, DBB-out 320)
    # -------------------------------------------------------------------------
    runs = [
        # (y, gap_half_meter, label, dbb_in, dbb_out, label_x, label_dy)
        # Label line RUN 1 & RUN 3 digeser (kiri + turun melewati pita flange
        # tick DBB y=cy-6..cy+6) agar berjarak dari meter run / klaster
        # instrumen (temuan QA visual).
        (430.0, 22.0, "200-MT-6002 DN200", "DBB-611A", "DBB-611B", 194.0, -9.5),
        (300.0, 18.0, "200-MT-6003 DN200", "DBB-621A", "DBB-621B", 205.0, -5.5),
        (170.0, 18.0, "200-MT-6004 DN200", "DBB-631A", "DBB-631B", 195.0, -9.5),
    ]
    for ry, gh, rlabel, dbb_a, dbb_b, rlabel_x, rlabel_dy in runs:
        ctx.meter_run_pipe(130.0, 370.0, ry, [(170.0, DBB_HALF), (245.0, gh), (320.0, DBB_HALF)])
        ctx.dbb_valve_h(170.0, ry, tag=dbb_a)
        ctx.dbb_valve_h(320.0, ry, tag=dbb_b)
        for ax in (142.0, 205.0, 285.0, 352.0):
            ctx.flow_arrow_h(ax, ry, direction=1)
        ctx.text(rlabel, rlabel_x, ry + rlabel_dy, size=2.0)
        ctx.register_line(rlabel.split(" DN")[0], spec="A1A", service="METER RUN", dn=200)

    # RUN 1: USM (spool + Zanker + korda multi-path + FT-611 + FQI-611)
    ctx.usm_meter_run(245.0, 430.0, tag="USM-6001", fe_pair=("FT", "611"), fqi_pair=("FQI", "611"))
    ctx.text("RUN 1 - ULTRASONIC METER (DUTY)", 245.0, 492.0, size=2.2)

    # RUN 2: Orifice senior dual-chamber (FT-621 + FQI-621)
    ctx.orifice_meter_run(245.0, 300.0, tag="OF-6021", fe_pair=("FT", "621"), fqi_pair=("FQI", "621"))
    ctx.text("RUN 2 - ORIFICE METER (DUTY)", 245.0, 362.0, size=2.2)

    # RUN 3: Coriolis standby (FT-631 + DT-632 + FQI-631)
    ctx.coriolis_meter(245.0, 170.0, tag="CM-6031", ft_pair=("FT", "631"), dt_pair=("DT", "632"), fqi_pair=("FQI", "631"))
    ctx.text("RUN 3 - CORIOLIS METER (STANDBY)", 245.0, 223.0, size=2.2)

    # -------------------------------------------------------------------------
    # 6. MANIFOLD OUTLET & HEADER KELUAR (200-MT-6005)
    # -------------------------------------------------------------------------
    ctx.manifold_v(370.0, 170.0, 430.0)
    ctx.flow_arrow_v(370.0, 395.0, direction=1)    # turun dari RUN 1
    ctx.flow_arrow_v(370.0, 230.0, direction=-1)   # naik dari RUN 3
    ctx.metering_header(370.0, 585.0, 300.0, "200-MT-6005", dn=300, label_x=450.0)
    ctx.flow_arrow_h(520.0, 300.0, direction=1)
    ctx.text("OUTLET HEADER", 450.0, 307.5, size=1.8)
    ctx.proc += ctx.continuity_box_right(300.0, "200-MT-6005 DN300", "TO LBCV STATION / EXPORT PIPELINE", "DWG: GPF-00-PI-PID-0016")

    # -------------------------------------------------------------------------
    # 7. FAST LOOP SAMPLING + GAS CHROMATOGRAPH + SINYAL GHV KE FQI
    # -------------------------------------------------------------------------
    ctx.fast_loop(105.0, 300.0, 465.0)
    ctx.text("FAST LOOP", 98.5, 385.0, size=1.8)
    ctx.gc_analyzer(
        105.0, 485.0, w=90.0, h=40.0, tag="AT-6090",
        comp_lines=(
            "GAS CHROMATOGRAPH",
            "ONLINE ANALYZER AT-6090",
            "C1-C6+ / CO2 / N2",
            "GHV TO FQI (AGA 8)",
        ),
    )
    # Sinyal GC -> FQI tiap run (break 3 mm pada setiap persilangan proses)
    ctx.sig += dashed(150.0, 470.0, 237.5, 470.0, dash=2.5, gap=1.2)             # ke FQI-611
    ctx.text("GHV", 188.0, 473.5, size=1.8)
    ctx.sig += dashed(118.0, 465.0, 118.0, 349.0, dash=2.5, gap=1.2)             # turun ke FQI-621
    ctx.sig += dashed_brk(118.0, 349.0, 237.5, 349.0, brk=[12.0], dash=2.5, gap=1.2)
    ctx.sig += dashed_brk(92.0, 465.0, 92.0, 210.0, brk=[165.0], dash=2.5, gap=1.2)  # ke FQI-631
    ctx.sig += dashed_brk(92.0, 210.0, 237.5, 210.0, brk=[38.0], dash=2.5, gap=1.2)

    # -------------------------------------------------------------------------
    # 8. SIMPAN MANIFEST TEXTS & SOLIDS untuk cad/apply_text.py
    # -------------------------------------------------------------------------
    out_json = Path(__file__).resolve().parent / "metering_demo.texts.json"
    layers = ctx.export_manifest(out_json)
    return layers


if __name__ == "__main__":
    metering_demo()
