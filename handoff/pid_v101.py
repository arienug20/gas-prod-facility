"""P&ID GPF-00-PI-PID-0001 Rev A4 — 3-PHASE PRODUCTION SEPARATOR V-101.

Sheet A1 (841 x 594 mm), origin kiri-bawah.
Standar acuan:
  - ANSI/ISA-5.1-2024 (Instrumentation Symbols and Identification)
  - ISO 10628-2:2012 (Diagrams for chemical and petrochemical industry — Graphical symbols)
  - API Spec 12J (Specification for Oil and Gas Separators)
  - API STD 521 (Pressure-relieving and Depressurizing Systems)
  - Referensi Perusahaan: SSY-PRO-PID-002 & SSY-PRO-PID-003

Layers:
  REF-FRAME  border lembar, grid referensi, kotak tabel furniture
  REF-TITLE  title block + rev table (ISO 7200 / Company Standard)
  REF-EQUIP  vessel V-101, internals, saddles, nozzles, bridles, pump casing
  REF-PROC   line proses, valves, check valve, PSV, orifice, continuity boxes
  REF-SYM    bubbles instrumen, dcs shared display, sis logic block / interlock
  REF-SIG    signal listrik (dashed 4.0 / 1.6)
  REF-SIGP   signal pneumatic (solid + "//")
  REF-HATCH  arsiran 45 deg coalescer & demister
  REF-TEXT   ditulis post-build oleh apply_text.py dari manifest TEXTS (ARIAL)
"""

from __future__ import annotations

from pathlib import Path

from cadgen import dxf
from pid_common import (
    BUBBLE_R,
    PIDContext,
    arc,
    arc3,
    circle,
    comp,
    dashed,
    dashed_brk,
    hatch45,
    line,
    pipe_run_h,
    pipe_run_v,
    pneu,
    rect,
)


# =============================================================================
# MODEL UTAMA P&ID REV A4
# =============================================================================
@dxf
def pid_v101():
    ctx = PIDContext()

    # -------------------------------------------------------------------------
    # 1. BORDER LEMBAR A1 & GRID REFERENSI (ISO 5457)
    # -------------------------------------------------------------------------
    ctx.frame += rect(10, 7, 831, 587)      # Outer border
    ctx.frame += rect(20, 15, 823, 579)     # Inner border

    dx_col = (823.0 - 20.0) / 12.0      # 66.9167 mm per zona kolom
    for k in range(1, 12):
        x = 20.0 + dx_col * k
        ctx.frame += [line(x, 7, x, 15), line(x, 579, x, 587)]
    for i in range(12):
        cx = 20.0 + dx_col * (i + 0.5)
        ctx.text(str(i + 1), cx, 11.0, size=2.5)
        ctx.text(str(i + 1), cx, 583.0, size=2.5)

    dy_row = (579.0 - 15.0) / 8.0       # 70.5 mm per zona baris
    for k in range(1, 8):
        y = 15.0 + dy_row * k
        ctx.frame += [line(10, y, 20, y), line(823, y, 831, y)]
    for i in range(8):
        cy = 579.0 - dy_row * (i + 0.5)  # Baris A di atas -> H di bawah
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
        "1. SCHEMATIC — NOT TO SCALE. NO ORIENTATION IMPLIED.",
        "2. LINE DESIGNATION PER PIPING LINE INDEX. PIPE SPEC CLASS A1A (CS RF #150).",
        "3. INSTRUMENT SYMBOLS & TAGGING PER ANSI/ISA-5.1-2024.",
        "   DIAGRAM CONTENT PER ISO 10628-2:2012 & ISO 15519-2:2015.",
        "4. ESD-1 (SIS) CAUSE & EFFECT: PT-102 PSHH/PSLL & LT-122 LSHH/LSLL",
        "   -> CLOSE SDV-101, CLOSE LV-121, TRIP P-101. LT-132 LSHH/LSLL",
        "   -> CLOSE LV-131. SEE CAUSE & EFFECT CHART GPF-00-IN-SCH-0001.",
        "5. PSV-101 SET PRESSURE = 17.2 BARG PER V-101 MAWP / DATASHEET.",
        "   RELIEF SYSTEM SIZED PER API STD 521.",
        "6. ALARMS PAH/PAL/LAH/LAL IMPLEMENTED IN BPCS DCS FROM PT-101,",
        "   LT-121, LT-131.",
        "7. FLARE HEADER 100-FL-1005 SLOPE 1:500 TO KO DRUM — NO POCKETS.",
        "8. SIZES/DIMENSIONS FOR CLARITY ONLY — REFER TO PIPING LINE INDEX.",
        "9. EQUIPMENT DESIGN: V-101 PER API SPEC 12J & ASME SEC. VIII DIV. 1;",
        "   P-101 PER API 610; T-101 PER API STD 650.",
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

    # Electric signal
    ctx.sig += dashed(660, 397, 685, 397)
    ctx.text("ELECTRIC SIGNAL (BPCS / SIS)", 690, 397, size=2.0, left=True)

    # Pneumatic signal
    ctx.sigp += pneu(660, 381, 685, 381)
    ctx.text("PNEUMATIC SIGNAL", 690, 381, size=2.0, left=True)

    # Continuity arrow
    ctx.proc += [
        line(660, 362, 680, 362), line(680, 362, 685, 365),
        line(685, 365, 680, 368), line(680, 368, 660, 368), line(660, 368, 660, 362),
    ]
    ctx.text("CONTINUITY ARROW (BATTERY LIMIT)", 690, 365, size=2.0, left=True)

    # Field instrument
    ctx.sym.append(circle(672, 348, 5.0))
    ctx.sym.append(line(667, 348, 677, 348))
    ctx.text("FIELD INSTRUMENT", 690, 348, size=2.0, left=True)

    # DCS shared display
    ctx.sym += [
        line(666, 325, 678, 325), line(678, 325, 678, 337),
        line(678, 337, 666, 337), line(666, 337, 666, 325),
        circle(672, 331, 5.0), line(666, 331, 678, 331),
    ]
    ctx.text("DCS SHARED DISPLAY / CONTROL", 690, 331, size=2.0, left=True)

    # SIS logic block / interlock
    ctx.sym += [
        line(666, 308, 678, 308), line(678, 308, 678, 320),
        line(678, 320, 666, 320), line(666, 320, 666, 308),
        line(666, 314, 672, 320), line(672, 320, 678, 314),
        line(678, 314, 672, 308), line(672, 308, 666, 314),
    ]
    ctx.text("SIS LOGIC SOLVER / INTERLOCK", 690, 314, size=2.0, left=True)

    # Valves row
    ctx.sym += ctx.valve_gate_h(668, 292, w=8, h=5, flanged=False)
    ctx.sym += ctx.valve_globe_h(695, 292, w=8, h=5, flanged=False)
    ctx.sym += ctx.valve_check_h(722, 292, w=8, h=5)
    # Mini PSV
    ctx.sym += [
        line(750, 287, 750, 292), line(747, 287, 750, 292), line(753, 287, 750, 292), line(747, 287, 753, 287),
        line(750, 292, 755, 292), line(750, 292, 755, 289), line(750, 292, 755, 295), line(755, 289, 755, 295),
        line(750, 292, 750, 297), line(748, 297, 752, 297),
    ]
    ctx.text("GATE", 668, 283, size=1.8)
    ctx.text("GLOBE", 695, 283, size=1.8)
    ctx.text("CHECK", 722, 283, size=1.8)
    ctx.text("PSV", 750, 283, size=1.8)

    # Centrifugal pump + motor
    ctx.sym += [
        circle(666, 268, 3.5),
        line(669.5, 268, 673.5, 268),
        circle(678, 268, 4.5),
        line(678, 272.5, 685, 272.5),
    ]
    ctx.text("M", 666, 268, size=2.0)
    ctx.text("CENTRIFUGAL PUMP & MOTOR", 690, 268, size=2.0, left=True)

    # Concentric reducer & orifice
    ctx.sym += ctx.reducer_h(668, 250, w=6, h1=2.5, h2=4.5, label="")
    ctx.sym += [line(679, 246, 679, 254), line(681, 246, 681, 254)]
    ctx.text("REDUCER / ORIFICE PLATE", 690, 250, size=2.0, left=True)

    # Normally Closed Gate Valve
    ctx.sym += ctx.valve_gate_h(672, 233, w=8, h=5, nc=True, flanged=False)
    ctx.text("NC = NORMALLY CLOSED VALVE", 690, 233, size=2.0, left=True)

    # Abbreviations
    ctx.text("STANDARD ABBREVIATIONS:", 659, 216, size=1.9, left=True)
    ctx.text("FC: FAIL CLOSED        | CSO: CAR SEALED OPEN", 659, 206, size=1.8, left=True)
    ctx.text("LO: LOCKED OPEN       | TW:  THERMOWELL", 659, 197, size=1.8, left=True)
    ctx.text("NC: NORMALLY CLOSED   | VB:  VORTEX BREAKER", 659, 188, size=1.8, left=True)

    # --- 2.3 REFERENCE DRAWINGS (y = 148..185) ---
    ctx.frame.append(line(655, 148, 823, 148))
    ctx.frame.append(line(655, 175, 823, 175))
    ctx.text("REFERENCE DRAWINGS", 739, 180, size=2.2)
    ref_dwgs = [
        ("GPF-00-DB-0001", "DESIGN BASIS — GAS PRODUCTION FACILITY", 169.0),
        ("GPF-00-PI-PLN-0002", "PIPING PLAN — SEPARATOR AREA", 163.5),
        ("GPF-00-PI-ISO-0003", "PIPING ISOMETRIC — 100-PF-1001 / GO-1002", 158.0),
        ("GPF-00-PI-ISO-0004", "PIPING ISOMETRIC — 080-CO-1003 / CO-1004", 152.5),
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
        ("A4", "ADDED GV-103; REFACTORED TO PID_COMMON; LINTER FIXES", "23 OCT 26", "PM", "RE", 139.4),
        ("A3", "UPGRADED TO FULL ISA-5.1 / ISO 10628-2 P&ID", "23 OCT 26", "PM", "RE", 134.2),
        ("A2", "TEXT CONVERTED TO MTEXT PER STANDARD", "12 OCT 26", "PM", "RE", 129.0),
        ("A1", "REVISED PER COMPANY DRAFTING STANDARD", "09 OCT 26", "PM", "RE", 123.8),
        ("A0", "ISSUED FOR REVIEW", "09 OCT 26", "PM", "RE", 118.6),
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
    # Company / Consultant header
    ctx.text("GAS PRODUCTION FACILITY — ONSHORE FIELD", 739, 108.5, size=2.8)
    ctx.text("PM OIL & GAS SURFACE FACILITY", 739, 102.5, size=2.2)
    ctx.text("REKAYASA ENGINEERING", 739, 98.0, size=2.0)
    # Drawing title
    ctx.text("PIPING & INSTRUMENTATION DIAGRAM", 739, 87.0, size=2.8)
    ctx.text("3-PHASE PRODUCTION SEPARATOR V-101", 739, 80.0, size=2.5)
    # Drawing number
    ctx.text("DRAWING NO:", 658, 70.0, size=1.8, left=True)
    ctx.text("GPF-00-PI-PID-0001", 739, 65.5, size=2.8)
    # Metadata rows
    ctx.text("REV:", 658, 56.5, size=1.8, left=True)
    ctx.text("A4", 697, 52.5, size=3.0)
    ctx.text("SCALE:", 742, 56.5, size=1.8, left=True)
    ctx.text("NTS", 781, 52.5, size=2.5)

    ctx.text("DATE:", 658, 44.5, size=1.8, left=True)
    ctx.text("23 OCT 2026", 697, 40.5, size=2.2)
    ctx.text("SHEET:", 742, 44.5, size=1.8, left=True)
    ctx.text("1 OF 1", 781, 40.5, size=2.5)

    ctx.text("DESIGNED:", 658, 32.5, size=1.8, left=True)
    ctx.text("CAD/FEED", 697, 29.0, size=2.2)
    ctx.text("DRAWN:", 742, 32.5, size=1.8, left=True)
    ctx.text("CAD TEAM", 781, 29.0, size=2.2)

    ctx.text("CHECKED:", 658, 21.5, size=1.8, left=True)
    ctx.text("PM (AI)", 697, 18.5, size=2.2)
    ctx.text("APPROVED:", 742, 21.5, size=1.8, left=True)
    ctx.text("ENG MGR", 781, 18.5, size=2.2)

    # -------------------------------------------------------------------------
    # 3. EQUIPMENT DATA TABLES DI BAGIAN ATAS (y = 515..573)
    # -------------------------------------------------------------------------
    # Tabel 1: V-101 (x = 135..375)
    ctx.equip += rect(135, 515, 375, 573)
    ctx.equip.append(line(135, 565, 375, 565))
    ctx.equip.append(line(228, 515, 228, 565))
    ctx.text("EQUIPMENT DATA — 3-PHASE PRODUCTION SEPARATOR V-101", 255, 569, size=2.4)
    v101_rows = [
        ("TAG NUMBER", "V-101", 561.0),
        ("SERVICE NAME", "3-PHASE PRODUCTION SEPARATOR", 553.0),
        ("SIZE (ID x S/S)", "2300 MM (ID) x 7600 MM (S/S) HORIZONTAL", 545.0),
        ("DESIGN PRESS / TEMP", "17.2 BARG / 60 °C", 537.0),
        ("OPER. PRESS / TEMP", "10.0 BARG / 40 °C", 529.0),
        ("MATERIAL / CODE", "CS ASTM A516 GR.70 / ASME SEC. VIII & API SPEC 12J", 521.0),
    ]
    for k, (cap, val, ry) in enumerate(v101_rows):
        if k > 0:
            ctx.equip.append(line(135, ry + 4.0, 375, ry + 4.0))
        ctx.text(cap, 138, ry, size=1.8, left=True)
        ctx.text(val, 232, ry, size=2.0, left=True)

    # Tabel 2: P-101 (x = 395..635)
    ctx.equip += rect(395, 515, 635, 573)
    ctx.equip.append(line(395, 565, 635, 565))
    ctx.equip.append(line(488, 515, 488, 565))
    ctx.text("EQUIPMENT DATA — CRUDE OIL TRANSFER PUMP P-101", 515, 569, size=2.4)
    p101_rows = [
        ("TAG NUMBER", "P-101", 561.0),
        ("SERVICE NAME", "CRUDE OIL TRANSFER PUMP", 553.0),
        ("TYPE / STANDARD", "HORIZONTAL CENTRIFUGAL / API 610", 545.0),
        ("DESIGN PRESS / TEMP", "17.2 BARG / 60 °C", 537.0),
        ("SUCTION / DISCH.", "10.0 BARG / 13.5 BARG (OPERATING 40 °C)", 529.0),
        ("MATERIAL / DRIVER", "CS A216-WCB / ELECTRIC MOTOR (M)", 521.0),
    ]
    for k, (cap, val, ry) in enumerate(p101_rows):
        if k > 0:
            ctx.equip.append(line(395, ry + 4.0, 635, ry + 4.0))
        ctx.text(cap, 398, ry, size=1.8, left=True)
        ctx.text(val, 492, ry, size=2.0, left=True)

    # -------------------------------------------------------------------------
    # 4. LEVEL DIAGRAM TABLE UNTUK V-101 (x = 25..110, y = 145..205)
    # -------------------------------------------------------------------------
    ctx.equip += rect(25, 145, 110, 205)
    ctx.equip.append(line(25, 197, 110, 197))
    ctx.equip.append(line(72, 145, 72, 197))
    ctx.text("V-101 LEVEL SETTING", 67.5, 201, size=2.2)
    lvl_rows = [
        ("HHLL (LSHH)", "1850 MM", 193.0),
        ("HLL (LAH)", "1650 MM", 185.0),
        ("NLL", "1350 MM", 177.0),
        ("LLL (LAL)", "900 MM", 169.0),
        ("LLLL (LSLL)", "650 MM", 161.0),
        ("WEIR HEIGHT", "1500 MM", 153.0),
    ]
    for k, (cap, val, ry) in enumerate(lvl_rows):
        if k > 0:
            ctx.equip.append(line(25, ry + 4.0, 110, ry + 4.0))
        ctx.text(cap, 27, ry, size=1.8, left=True)
        ctx.text(val, 75, ry, size=2.0, left=True)

    # -------------------------------------------------------------------------
    # 5. SIS LOGIC SOLVER ESD-1 MAIN SYMBOL (x = 70, y = 475)
    # -------------------------------------------------------------------------
    ctx.sym += rect(58, 463, 82, 487)
    ctx.sym += [
        line(58, 475, 70, 487), line(70, 487, 82, 475),
        line(82, 475, 70, 463), line(70, 463, 58, 475),
    ]
    ctx.text("ESD", 70, 477.5, size=2.2)
    ctx.text("1", 70, 472.5, size=2.2)
    ctx.text("SIS LOGIC SOLVER", 70, 458.0, size=1.9)
    ctx.text("(SEE NOTE 4)", 70, 453.5, size=1.8)

    # -------------------------------------------------------------------------
    # 6. BEJANA V-101 & INTERNALS (API SPEC 12J)
    # -------------------------------------------------------------------------
    # Shell silinder & heads (x = 135..435, y = 250..340, CL = 295)
    ctx.equip += [
        line(135, 250, 435, 250),
        line(135, 340, 435, 340),
    ]
    ctx.equip.append(arc3((135, 250), (123, 295), (135, 340)))
    ctx.equip.append(arc3((435, 250), (447, 295), (435, 340)))
    ctx.equip += dashed(135, 250, 135, 340)
    ctx.equip += dashed(435, 250, 435, 340)

    # Saddle supports (x = 165 fixed, x = 352 sliding, y = 235..250)
    for sx, is_fixed in ((165, True), (352, False)):
        ctx.equip += [
            line(sx - 10, 250, sx - 13, 235),
            line(sx + 10, 250, sx + 13, 235),
            line(sx - 15, 235, sx + 15, 235),
        ]
        ctx.text("FIXED SADDLE" if is_fixed else "SLIDING SADDLE", sx, 230, size=1.8)

    # Internals
    # 1. Inlet Deflector Baffle di depan N1
    ctx.equip.append(arc3((140, 275), (143, 295), (140, 315)))
    ctx.text("INLET BAFFLE", 150, 322, size=1.8)

    # 2. Plate Coalescer Pack (x = 175..235, y = 265..325)
    ctx.equip += rect(175, 265, 235, 325)
    ctx.hatch += hatch45(175, 265, 235, 325, spacing=3.5)
    ctx.text("PLATE COALESCER", 205, 259, size=2.0)

    # 3. Weir Plate (x = 335, y = 250..305)
    ctx.equip.append(line(335, 250, 335, 305))
    ctx.text("WEIR", 335, 310, size=2.0)

    # 4. Liquid levels (di-break bersih tanpa memotong internals, standpipe, & instrumen)
    ctx.equip += dashed(142, 275, 172, 275)
    ctx.equip += dashed(238, 275, 273, 275)
    ctx.text("OIL / WATER INTERFACE", 255, 278, size=1.8)

    ctx.equip += dashed(142, 300, 172, 300)
    ctx.equip += dashed(238, 300, 273, 300)
    ctx.text("OIL LEVEL (NLL)", 255, 303, size=1.8)

    ctx.equip += dashed(338, 286, 369, 286)
    ctx.equip += dashed(427, 286, 444, 286)
    ctx.text("OIL LEVEL", 353, 289, size=1.8)

    # 5. Demister Pad di bawah N2 (x = 380..430, y = 320..335)
    ctx.equip += rect(380, 320, 430, 335)
    ctx.hatch += hatch45(380, 320, 430, 335, spacing=3.0)
    ctx.text("DEMISTER PAD", 405, 315, size=2.0)

    # 6. Vortex Breakers di N4 (x=255) dan N3 (x=430)
    for vx in (255, 430):
        ctx.equip += [
            line(vx - 4, 253, vx + 4, 253),
            line(vx, 250, vx, 256),
        ]
        ctx.text("VB", vx, 259, size=1.8)

    # Flanged Nozzles N1..N6
    # N1 inlet DN150 (head kiri, y=295)
    ctx.equip += [
        line(123, 295, 115, 295),
        line(115, 289, 115, 301), line(116.2, 289, 116.2, 301),
    ]
    ctx.text("N1 DN150", 115, 305, size=2.0)

    # N2 gas outlet DN100 (top, x=400)
    ctx.equip += [
        line(400, 340, 400, 350),
        line(395, 350, 405, 350), line(395, 351.2, 405, 351.2),
    ]
    ctx.text("N2 DN100", 386, 356, size=2.0)

    # N5 PSV inlet DN100 (top, x=155)
    ctx.equip += [
        line(155, 340, 155, 350),
        line(150, 350, 160, 350), line(150, 351.2, 160, 351.2),
    ]
    ctx.text("N5 DN100", 141, 356, size=2.0)

    # N4 water outlet DN50 (bottom, x=255)
    ctx.equip += [
        line(255, 250, 255, 240),
        line(251, 240, 259, 240), line(251, 238.8, 259, 238.8),
    ]
    ctx.text("N4 DN50", 242, 242, size=2.0)

    # N6 drain DN50 (bottom shell, x=408 — terhubung utuh ke shell bawah y=250)
    ctx.equip += [
        line(408, 250, 408, 240),
        line(404, 240, 412, 240), line(404, 238.8, 412, 238.8),
    ]
    ctx.text("N6 DN50", 418, 242, size=2.0)

    # N3 oil outlet DN80 (bottom shell kanan, x=430 — terhubung utuh ke shell bawah y=250)
    ctx.equip += [
        line(430, 250, 430, 240),
        line(425, 240, 435, 240), line(425, 238.8, 435, 238.8),
    ]
    ctx.text("N3 DN80", 444, 242, size=2.0)

    # -------------------------------------------------------------------------
    # 7. LEVEL BRIDLES & INSTRUMEN LEVEL (TERHUBUNG PENUH TANPA STUB MELAYANG)
    # -------------------------------------------------------------------------
    # Interface / Water Level Standpipe (x = 278, terhubung ke shell bawah y=250 s/d y=308)
    ctx.equip += [
        line(278, 250, 278, 308),
        # Top & Bottom bridle taps dengan isolation gate valve menuju LG-133 (x = 290)
        line(278, 308, 281.5, 308),
        ctx.valve_gate_h(284.0, 308, w=5.0, h=3.2, flanged=False),
        line(286.5, 308, 290, 308),
        line(278, 262, 281.5, 262),
        ctx.valve_gate_h(284.0, 262, w=5.0, h=3.2, flanged=False),
        line(286.5, 262, 290, 262),
        # Drain valve di bawah shell (y = 250 turun ke y = 236)
        line(278, 250, 278, 245.5),
        ctx.valve_gate_v(278, 243.0, w=3.2, h=5.0, flanged=False),
        line(278, 240.5, 278, 236.0),
        line(276, 236.0, 280, 236.0),
    ]
    # LG-133 Sight Glass Column (x = 290..293, y = 262..308)
    ctx.sym += [
        line(290, 262, 290, 308), line(293, 262, 293, 308),
        line(290, 262, 293, 262), line(290, 308, 293, 308),
    ]
    ctx.text("LG-133", 291.5, 313, size=2.0)
    # LT-131 (BPCS) — sinyal dari sisi kanan LG-133 (x = 293) ke bubble (x = 298)
    ctx.sym += ctx.bubble(304, 275, "LT", "131")
    ctx.sig += dashed(293, 275, 298, 275)
    # LT-132 (SIS) — sinyal dari sisi kanan LG-133 (x = 293) ke bubble (x = 298)
    ctx.sym += ctx.bubble(304, 295, "LT", "132")
    ctx.sig += dashed(293, 295, 298, 295)
    ctx.sym += ctx.sis_box(322, 295, "LAHH", "LALL")
    ctx.sig += dashed(310, 295, 314, 295)
    ctx.text("TO ESD-1", 322, 306, size=1.8)

    # Oil Level Standpipe (x = 374, terhubung ke shell bawah y=250 s/d y=306, bebas dari SLIDING SADDLE x=352)
    ctx.equip += [
        line(374, 250, 374, 306),
        # Top & Bottom bridle taps dengan isolation gate valve menuju LG-123 (x = 386)
        line(374, 306, 377.5, 306),
        ctx.valve_gate_h(380.0, 306, w=5.0, h=3.2, flanged=False),
        line(382.5, 306, 386, 306),
        line(374, 262, 377.5, 262),
        ctx.valve_gate_h(380.0, 262, w=5.0, h=3.2, flanged=False),
        line(382.5, 262, 386, 262),
        # Drain valve di bawah shell (y = 250 turun ke y = 236)
        line(374, 250, 374, 245.5),
        ctx.valve_gate_v(374, 243.0, w=3.2, h=5.0, flanged=False),
        line(374, 240.5, 374, 236.0),
        line(372, 236.0, 376, 236.0),
    ]
    # LG-123 Sight Glass Column (x = 386..389, y = 262..306)
    ctx.sym += [
        line(386, 262, 386, 306), line(389, 262, 389, 306),
        line(386, 262, 389, 262), line(386, 306, 389, 306),
    ]
    ctx.text("LG-123", 387.5, 311, size=2.0)
    # LT-121 (BPCS) — sinyal dari sisi kanan LG-123 (x = 389) ke bubble (x = 394)
    ctx.sym += ctx.bubble(400, 275, "LT", "121")
    ctx.sig += dashed(389, 275, 394, 275)
    # LT-122 (SIS) — sinyal dari sisi kanan LG-123 (x = 389) ke bubble (x = 394)
    ctx.sym += ctx.bubble(400, 295, "LT", "122")
    ctx.sig += dashed(389, 295, 394, 295)
    ctx.sym += ctx.sis_box(418, 295, "LAHH", "LALL")
    ctx.sig += dashed(406, 295, 410, 295)
    ctx.text("TO ESD-1", 418, 306, size=1.8)

    # -------------------------------------------------------------------------
    # 8. INSTRUMEN PUNCAK BEJANA (y = 380)
    # -------------------------------------------------------------------------
    top_inst = [
        ("PT", "101", 195.0),
        ("TT", "111", 225.0),
        ("TI", "112", 250.0),
        ("PT", "102", 285.0),
        ("PI", "103", 315.0),
    ]
    for top_t, bot_t, tx in top_inst:
        ctx.proc.append(line(tx, 340, tx, 374))
        ctx.sym += ctx.bubble(tx, 380, top_t, bot_t)

    ctx.text("TW", 230.0, 355.0, size=1.8)  # Thermowell tag di sebelah kanan riser TT-111
    # SIS function box di atas PT-102
    ctx.sym += ctx.sis_box(285, 400, "PAHH", "PALL")
    ctx.sig += dashed(285, 386, 285, 392)
    ctx.text("TO ESD-1", 285, 410, size=1.8)
    # TI-111 DCS display di atas TT-111
    ctx.sym += ctx.dcs(225, 450, "TI", "111")
    ctx.sig += dashed_brk(225, 386, 225, 442.5, brk=[44.0])  # Cross PSV line y=430
    ctx.text("TAH", 237, 450, size=1.8)

    # -------------------------------------------------------------------------
    # 9. PIPA PROSES LINTAS LEMBAR (6 LINE UTAMA DENGAN TRIMMING KETAT)
    # -------------------------------------------------------------------------

    # --- LINE 1: 100-PF-1001 (Inlet Separator, y = 295) ---
    ctx.proc += ctx.continuity_box_left(295, "100-PF-1001 DN150", "FROM PRODUCTION HEADER", "DWG: GPF-00-PI-PLN-0002")
    # Pipa dari x=72.5 ke x=115, gap untuk SDV-101 di x=94 (hw=5.0)
    ctx.proc += pipe_run_h(295, 72.5, 115.0, gaps=[(94.0, 5.0)])
    ctx.proc += ctx.sdv_h(94.0, 295.0, tag="SDV-101", fail="FC")
    ctx.sym += ctx.interlock_diamond(94.0, 321.0, tag="ESD-1")
    ctx.sig += dashed(94.0, 307.5, 94.0, 316.0)
    ctx.flow_arrow_h(108.0, 295.0, direction=1)

    # --- LINE 2: 100-FL-1005 (PSV-101 Tail ke Flare, y = 430) ---
    # Riser dari N5 (155, 351.2) ke PSV-101 (155, 430)
    ctx.proc += pipe_run_v(155.0, 351.2, 422.0, gaps=[(380.0, 5.0)])
    ctx.proc += ctx.valve_gate_v(155.0, 380.0, w=6.0, h=10.0, flanged=True)
    ctx.text("GV-105", 168.0, 382.0, size=2.0)
    ctx.text("CSO", 168.0, 377.5, size=1.8)
    ctx.proc += ctx.psv_angle(155.0, 430.0, tag="PSV-101", size_str="DN100x150", set_press="SET 17.2 BARG")
    # Horizontal run dari PSV outlet (x=163) ke continuity box (x=585); gap 3 mm di riser N2 (x=400)
    ctx.proc += pipe_run_h(430.0, 163.0, 585.0, gaps=[(400.0, 1.5)])
    ctx.proc += ctx.continuity_box_right(430.0, "100-FL-1005 DN150", "TO FLARE HEADER (PSV-101 TAIL)", "DWG: GPF-00-PI-ISO-0003")
    ctx.flow_arrow_h(250.0, 430.0, direction=1)
    ctx.flow_arrow_h(560.0, 430.0, direction=1)
    ctx.text("100-FL-1005 DN150", 350.0, 434.0, size=2.0)

    # --- LINE 3: 100-GO-1002 / 100-FL-1005 (Gas Outlet ke Flare, y = 455) ---
    # Riser dari N2 (400, 351.2) ke y=455
    ctx.proc += pipe_run_v(400.0, 351.2, 455.0)
    # Horizontal run y=455: PV-101 (440, hw=5), GV-141 (475, hw=5), FE-141 (515, hw=1.2), Reducer (545, hw=4)
    ctx.proc += pipe_run_h(455.0, 400.0, 585.0, gaps=[(440.0, 5.0), (475.0, 5.0), (515.0, 1.2), (545.0, 4.0)])
    ctx.proc += ctx.control_valve_h(440.0, 455.0)
    ctx.text("PV-101", 440.0, 447.0, size=2.2)
    ctx.text("FC", 440.0, 442.5, size=1.8)
    # Loop PIC-101
    ctx.sym += ctx.dcs(440.0, 492.0, "PIC", "101")
    ctx.sym += rect(436.0, 470.0, 444.0, 476.0)
    ctx.text("FY", 440.0, 474.2, size=1.8)
    ctx.text("101", 440.0, 471.5, size=1.8)
    ctx.sig += dashed(440.0, 484.5, 440.0, 476.0)
    ctx.sigp += pneu(440.0, 470.0, 440.0, 462.5, spacing=3.0)
    # Sinyal dari PT-101 (195, 386) ke PIC-101 (440, 492)
    ctx.sig += dashed_brk(195.0, 386.0, 195.0, 492.0, brk=[44.0])  # Cross PSV line y=430
    ctx.sig += dashed(195.0, 492.0, 432.5, 492.0)

    # GV-141
    ctx.proc += ctx.valve_gate_h(475.0, 455.0, w=10.0, h=6.0, flanged=True)
    ctx.text("GV-141", 475.0, 465.0, size=2.2)

    # Orifice FE-141 + FT-141 + FI-141
    ctx.proc += ctx.orifice_h(515.0, 455.0, tag_fe="FE-141")
    ctx.sig += dashed(515.0, 461.0, 515.0, 470.0)
    ctx.sym += ctx.bubble(515.0, 474.0, "FT", "141")
    ctx.sig += dashed(515.0, 480.0, 515.0, 484.5)
    ctx.sym += ctx.dcs(515.0, 492.0, "FI", "141")

    # Concentric Reducer DN100x150
    ctx.proc += ctx.reducer_h(545.0, 455.0, w=8.0, h1=5.0, h2=8.0, label="DN100x150")

    ctx.proc += ctx.continuity_box_right(455.0, "100-FL-1005 DN150", "TO FLARE HEADER", "DWG: GPF-00-PI-ISO-0003")
    ctx.flow_arrow_h(415.0, 455.0, direction=1)
    ctx.flow_arrow_h(570.0, 455.0, direction=1)
    ctx.text("100-GO-1002 DN100", 416.0, 460.0, size=2.0)
    ctx.text("100-FL-1005 DN150", 565.0, 460.0, size=2.0)

    # --- LINE 4: 050-PW-1006 (Produced Water ke Treatment, y = 210) ---
    # Riser dari N4 (255, 238.8) turun ke y=210
    ctx.proc += pipe_run_v(255.0, 210.0, 238.8)
    # Horizontal run y=210: GV-131 (295, hw=5), LV-131 (325, hw=5), FE-143 (365, hw=1.2), Cross CO-1003 (490, hw=1.5)
    ctx.proc += pipe_run_h(210.0, 255.0, 585.0, gaps=[(295.0, 5.0), (325.0, 5.0), (365.0, 1.2), (490.0, 1.5)])
    ctx.proc += ctx.valve_gate_h(295.0, 210.0, w=10.0, h=6.0, flanged=True)
    ctx.text("GV-131", 295.0, 220.0, size=2.2)

    ctx.proc += ctx.control_valve_h(325.0, 210.0)
    ctx.text("LV-131", 325.0, 202.0, size=2.0)
    ctx.text("FC", 325.0, 197.5, size=1.8)
    # Loop LIC-131
    ctx.sym += ctx.dcs(325.0, 240.0, "LIC", "131")
    ctx.sym += rect(321.0, 222.0, 329.0, 228.0)
    ctx.text("FY", 325.0, 226.2, size=1.8)
    ctx.text("131", 325.0, 223.5, size=1.8)
    ctx.sig += dashed(325.0, 232.5, 325.0, 228.0)
    ctx.sigp += pneu(325.0, 222.0, 325.0, 217.5, spacing=3.0)
    # Interlock ESD-1 pada LV-131
    ctx.sym += ctx.interlock_diamond(338.0, 225.0, tag="ESD-1")
    ctx.sig += dashed(329.0, 225.0, 333.0, 225.0)
    # Sinyal LT-131 ke LIC-131 (break di shell bawah y=250: 269-250=19)
    ctx.sig += dashed_brk(304.0, 269.0, 304.0, 240.0, brk=[19.0])
    ctx.sig += dashed(304.0, 240.0, 317.5, 240.0)

    # Orifice FE-143 + FT-143 + FI-143
    ctx.proc += ctx.orifice_h(365.0, 210.0, tag_fe="FE-143")
    ctx.sig += dashed(365.0, 204.0, 365.0, 196.0)
    ctx.sym += ctx.bubble(365.0, 190.0, "FT", "143")
    ctx.sig += dashed(365.0, 184.0, 365.0, 181.5)
    ctx.sym += ctx.dcs(365.0, 174.0, "FI", "143")

    ctx.proc += ctx.continuity_box_right(210.0, "050-PW-1006 DN50", "TO PRODUCED WATER TREATMENT", "DWG: GPF-00-PI-ISO-0005")
    ctx.flow_arrow_h(420.0, 210.0, direction=1)
    ctx.flow_arrow_h(560.0, 210.0, direction=1)
    ctx.text("050-PW-1006 DN50", 450.0, 215.0, size=2.0)

    # --- LINE 5: 050-CD-1007 (Closed Drain ke Drain System, y = 175) ---
    # Riser dari N6 (408, 238.8) turun ke y=175; cross PW-1006 di y=210 (gap 3 mm)
    ctx.proc += pipe_run_v(408.0, 175.0, 238.8, gaps=[(210.0, 1.5)])
    # Horizontal run y=175: GV-104 NC (448, hw=5), Cross CO-1003 (490, hw=1.5)
    ctx.proc += pipe_run_h(175.0, 408.0, 585.0, gaps=[(448.0, 5.0), (490.0, 1.5)])
    ctx.proc += ctx.valve_gate_h(448.0, 175.0, w=10.0, h=6.0, nc=True, flanged=True)
    ctx.text("GV-104", 448.0, 184.0, size=2.2)
    ctx.text("NC", 448.0, 167.0, size=2.0)
    ctx.text("NORMALLY CLOSED", 448.0, 162.0, size=1.8)

    ctx.proc += ctx.continuity_box_right(175.0, "050-CD-1007 DN50", "TO CLOSED DRAIN SYSTEM", "DWG: GPF-00-PI-ISO-0005")
    ctx.flow_arrow_h(530.0, 175.0, direction=1)
    ctx.text("050-CD-1007 DN50", 530.0, 180.0, size=2.0)

    # --- LINE 6: 080-CO-1003 (Suction Pompa P-101) & 080-CO-1004 (Discharge ke Tank) ---
    # CO-1003: dari N3 (430, 238.8) turun ke y=225, ke x=490, lalu turun ke pompa
    ctx.proc += pipe_run_v(430.0, 225.0, 238.8)
    ctx.proc += pipe_run_h(225.0, 430.0, 490.0)
    # Suction riser vertikal x=490: GV-101 (145, hh=5), ST-101 (125, hh=5), flange pompa di y=104
    # Cross PW-1006 (y=210) & CD-1007 (y=175) -> garis proses CO-1003 utuh (minor di-break di PW & CD)
    ctx.proc += pipe_run_v(490.0, 104.0, 225.0, gaps=[(145.0, 5.0), (125.0, 5.0)])
    ctx.proc += ctx.valve_gate_v(490.0, 145.0, w=6.0, h=10.0, flanged=True)
    ctx.text("GV-101", 503.0, 145.0, size=2.2)

    ctx.proc += ctx.strainer_v(490.0, 125.0, tag="ST-101")
    ctx.flow_arrow_v(490.0, 195.0, direction=-1)
    ctx.text("080-CO-1003 DN80", 501.0, 195.0, size=2.0, rot=90.0)

    # Pompa Sentrifugal P-101 & Electric Motor M
    ctx.proc += ctx.pump_centrifugal(490.0, 95.0, r=7.0)
    ctx.proc += ctx.electric_motor(465.0, 95.0, r=5.0, tag="M")
    ctx.proc.append(line(470.0, 95.0, 483.0, 95.0))  # Shaft
    ctx.text("P-101", 490.0, 80.0, size=2.5)

    # Trip dari ESD-1 ke Motor M
    ctx.sym += ctx.interlock_diamond(465.0, 110.0, tag="ESD-1")
    ctx.sig += dashed(465.0, 105.0, 465.0, 100.0)
    ctx.text("TRIP", 465.0, 102.5, size=1.8)

    # CO-1004 Discharge (y = 102 tangensial dari puncak pompa):
    # Rangkaian spasi presisi (jarak antar tick >= 4 mm, FE-142 tegak lurus di bawah FT/FI, panah >= 6 mm dari tick, GV-103 bebas dari x=585):
    # CV-101 (501.2, hw=5), GV-102 (517.7, hw=5), LV-121 (534.2, hw=5), FE-142 (550.7, hw=1.2), GV-103 (575.0, hw=5)
    ctx.proc += pipe_run_h(102.0, 490.0, 585.0, gaps=[(501.2, 5.0), (517.7, 5.0), (534.2, 5.0), (550.7, 1.2), (575.0, 5.0)])

    # CV-101 Check Valve (ticks: 495.0 .. 507.4, clearance ke flange pompa 494.0 = 1.0 mm bebas crossing)
    ctx.proc += ctx.valve_check_h(501.2, 102.0, w=10.0, h=6.0)
    ctx.text("CV-101", 501.2, 111.0, size=2.2)

    # GV-102 Gate Valve (ticks: 511.5 .. 523.9, clearance ke CV-101 = 4.1 mm >= 4 mm)
    ctx.proc += ctx.valve_gate_h(517.7, 102.0, w=10.0, h=6.0, flanged=True)
    ctx.text("GV-102", 517.7, 111.0, size=2.2)

    # LV-121 Control Valve (ticks: 528.0 .. 540.4, clearance ke GV-102 = 4.1 mm >= 4 mm)
    ctx.proc += ctx.control_valve_h(534.2, 102.0)
    ctx.text("LV-121", 534.2, 93.5, size=2.0)
    ctx.text("FC", 534.2, 89.0, size=1.8)

    # Loop LIC-121 & FY-121 di atas LV-121
    ctx.sym += ctx.dcs(534.2, 138.0, "LIC", "121")
    ctx.sym += rect(530.2, 120.0, 538.2, 126.0)
    ctx.text("FY", 534.2, 124.2, size=1.8)
    ctx.text("121", 534.2, 121.5, size=1.8)
    ctx.sig += dashed(534.2, 130.5, 534.2, 126.0)
    ctx.sigp += pneu(534.2, 120.0, 534.2, 114.5, spacing=3.0)

    # Interlock ESD-1 pada LV-121
    ctx.sym += ctx.interlock_diamond(521.2, 123.0, tag="ESD-1")
    ctx.sig += dashed(526.2, 123.0, 530.2, 123.0)

    # Sinyal LT-121 ke LIC-121 via y=65 dengan break pada shell (250), PW (210) & CO (102)
    ctx.sig += dashed_brk(400.0, 269.0, 400.0, 65.0, brk=[19.0, 59.0])
    ctx.sig += dashed(400.0, 65.0, 542.5, 65.0)
    ctx.sig += dashed_brk(542.5, 65.0, 542.5, 138.0, brk=[37.0])  # break di CO-1004 y=102
    ctx.sig += dashed(542.5, 138.0, 541.7, 138.0)

    # Orifice FE-142 (ticks: 548.2 .. 553.2, clearance ke LV-121 = 7.8 mm >= 4 mm)
    # FE-142 TEGAK LURUS di bawah FT-142 dan FI-142 (sinyal lurus vertikal, TANPA jog)
    ctx.proc += ctx.orifice_h(550.7, 102.0, tag_fe="")
    ctx.text("FE-142", 550.7, 93.5, size=1.8)
    ctx.sig += dashed(550.7, 108.0, 550.7, 116.0)
    ctx.sym += ctx.bubble(550.7, 122.0, "FT", "142")
    ctx.sig += dashed(550.7, 128.0, 550.7, 130.5)
    ctx.sym += ctx.dcs(550.7, 138.0, "FI", "142")

    # Panah aliran CO-1004 di segmen pipa terbuka (base: 559.2, tip: 562.8, size: 2.4)
    # Jarak ke tick kanan FE-142 (553.2) = 6.0 mm (>= 6 mm)
    # Jarak ke tick kiri GV-103 (568.8) = 6.0 mm (>= 6 mm)
    ctx.flow_arrow_h(562.8, 102.0, direction=1, size=2.4)

    # GV-103 Gate Valve flanged (ticks: 568.8 .. 581.2, gap ke kontinuitas x=585 = 3.8 mm bebas)
    ctx.proc += ctx.valve_gate_h(575.0, 102.0, w=10.0, h=6.0, flanged=True)
    ctx.text("GV-103", 575.0, 93.5, size=2.2)

    # Kotak kontinuitas keluar ke tangki T-101
    ctx.proc += ctx.continuity_box_right(102.0, "080-CO-1004 DN80", "TO CRUDE OIL STORAGE TANK T-101", "DWG: GPF-00-PI-ISO-0005")
    ctx.text("080-CO-1004 DN80", 510.0, 86.0, size=2.0)

    # Simpan manifest TEXTS & SOLIDS untuk cad/apply_text.py
    out_json = Path(__file__).resolve().parent / "pid_v101.texts.json"
    layers = ctx.export_manifest(out_json)
    return layers


if __name__ == "__main__":
    pid_v101()
