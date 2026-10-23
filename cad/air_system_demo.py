"""P&ID GPF-00-PI-PID-0014 Rev A0 — INSTRUMENT & UTILITY AIR SYSTEM.

Sheet A1 (841 x 594 mm), origin kiri-bawah.
Modul roadmap: GPF-00-PM-PLN-0008 Bagian III.2 (air_system_common.py).

Standar acuan:
  - ISO 8573-1 (Kelas udara tekan; Class 1.2.1, PDP <= -40 C)
  - ISA-7.0.01 (Quality Standard for Instrument Air)
  - ASME Sec. VIII Div. 1 (Wet/Dry air receiver)
  - ANSI/ISA-5.1-2024 (Instrumentation Symbols and Identification)
  - ISO 10628-2:2012 (Graphical symbols)

Rangkaian (satu jalur lengkap): intake filter SF-501 -> rotary screw
compressor K-501 -> aftercooler E-501 -> cyclone moisture trap S-501 -> wet
air receiver V-502 (PSV-501) -> prefilter F-501 -> coalescer F-502 ->
twin-tower desiccant dryer DT-501 (tower A drying / tower B regenerating,
PLC-501 timer, purge FO-501, exhaust EV-501) -> dust filter F-503 -> dry air
receiver V-503 (PSV-502) -> priority valve PCV-501 -> bercabang IA
(080-IA-5001) dan UA (080-UA-5002).

Layers:
  REF-FRAME  border lembar, grid referensi, kotak tabel furniture
  REF-TITLE  title block + rev table (ISO 7200 / Company Standard)
  REF-EQUIP  kompresor, cooler, cyclone, receiver, menara dryer, tabel data
  REF-PROC   line proses, filter inline, katup, PCV, orifice, continuity box
  REF-SYM    bubble instrumen, dcs, PLC timer, legenda simbol
  REF-SIG    signal elektrik/PLC (dashed)
  REF-SIGP   signal pneumatic (solid + "//")
  REF-HATCH  arsiran bed desiccant
  REF-TEXT   ditulis post-build oleh apply_text.py dari manifest TEXTS (ARIAL)
"""

from __future__ import annotations

from pathlib import Path

from cadgen import dxf
from air_system_common import AirSystemContext, dome_y_at, head_circle
from pid_common import arc3, dashed, dashed_brk, hatch45, line, pipe_run_h, pipe_run_v, pneu, rect


# =============================================================================
# MODEL UTAMA P&ID REV A0
# =============================================================================
@dxf
def air_system_demo():
    ctx = AirSystemContext()

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
        "1. SCHEMATIC — NOT TO SCALE. NO ORIENTATION IMPLIED.",
        "2. AIR QUALITY PER ISO 8573-1 CL. 1.2.1 (PDP <= -40 C, OIL < 0.01 MG/M3).",
        "   DESIGN PER ISA-7.0.01. SYMBOLS PER ANSI/ISA-5.1-2024 & ISO 10628-2.",
        "3. K-501: OIL-FREE ROTARY SCREW PACKAGE W/ SUCTION FILTER SF-501 AND",
        "   AFTERCOOLER E-501 (CW). CAPACITY CONTROL LOAD/UNLOAD.",
        "4. V-502 & V-503 PER ASME SEC. VIII DIV. 1; PSV-501/502 SET 8.8 BARG.",
        "   V-503 SIZED FOR 30 MIN IA BUFFER AT ZERO COMPRESSOR OUTPUT.",
        "5. DT-501 TWIN-TOWER DESICCANT DRYER: TOWER A DRYING WHILE TOWER B",
        "   REGENERATES (HEATLESS PURGE 5-7% VIA FO-501); SWITCHING VALVES",
        "   GV-502A/B, GV-503A/B AND EXHAUST EV-501 SEQUENCED BY PLC-501 TIMER.",
        "6. AT-501 DEW POINT TRANSMITTER: MAH ALARM IN DCS AT PDP -40 C.",
        "7. PCV-501 PRIORITY SUSTAINING VALVE: CLOSES UA AT < 5.5 BARG SO THE",
        "   REMAINING DRY AIR IS RESERVED 100% FOR INSTRUMENT SAFETY.",
        "8. AUTO DRAIN TRAPS ON S-501, V-502, V-503, F-501..F-503; CONDENSATE TO",
        "   CLOSED DRAIN. LINE NUMBERS PER PIPING LINE INDEX; SPEC A1A CS RF #150.",
    ]
    ny = 556.0
    for ln in notes:
        ctx.text(ln, 659, ny, size=2.0, left=True)
        ny -= 8.3

    # --- 2.2 LEGEND & SYMBOLS (y = 185..435) ---
    ctx.frame.append(line(655, 185, 823, 185))
    ctx.frame.append(line(655, 423, 823, 423))
    ctx.text("LEGEND & SYMBOLS", 739, 429, size=2.5)

    # Process line + flow arrow
    ctx.proc.append(line(660, 420, 685, 420))
    ctx.flow_arrow_h(672, 420, direction=1)
    ctx.text("PROCESS LINE (WITH FLOW ARROW)", 690, 420, size=2.0, left=True)

    # Electric signal / PLC link
    ctx.sig += dashed(660, 410, 685, 410, dash=2.5, gap=1.2)
    ctx.text("ELECTRIC SIGNAL / PLC LINK", 690, 410, size=2.0, left=True)

    # Pneumatic signal
    ctx.sigp += pneu(660, 400, 685, 400)
    ctx.text("PNEUMATIC SIGNAL", 690, 400, size=2.0, left=True)

    # Flow arrow
    ctx.flow_arrow_h(672, 390, direction=1)
    ctx.text("FLOW ARROW (SOLID)", 690, 390, size=2.0, left=True)

    # Valve row (gate, globe, check, PSV, muffler)
    ctx.sym += ctx.valve_gate_h(666, 376, w=8, h=5, flanged=False)
    ctx.sym += ctx.valve_globe_h(684, 376, w=8, h=5, flanged=False)
    ctx.sym += ctx.valve_check_h(702, 376, w=8, h=5)
    ctx.sym += [
        line(724, 371, 724, 376), line(721, 371, 724, 376), line(727, 371, 724, 376),
        line(721, 371, 727, 371), line(724, 376, 724, 381), line(724, 381, 729, 381),
        line(721, 386, 724, 381), line(727, 386, 724, 381),
        line(722, 386, 726, 386),
    ]
    ctx.proc.append(line(740, 376, 749, 376))
    ctx.muffler_vent_h(749, 376)
    ctx.text("GATE", 666, 369, size=1.8)
    ctx.text("GLOBE", 684, 369, size=1.8)
    ctx.text("CHECK", 702, 369, size=1.8)
    ctx.text("PSV", 724, 369, size=1.8)
    ctx.text("MUFFLER", 749, 369, size=1.8)

    # Filter mini (intake / inline)
    ctx.proc += rect(662, 345, 682, 359)
    ctx.proc += [line(666, 345, 670, 359), line(671, 345, 675, 359), line(676, 345, 680, 359)]
    ctx.proc += [line(656, 352, 662, 352), line(682, 352, 688, 352)]
    ctx.text("INTAKE / INLINE FILTER (SF-501, F-501..F-503)", 690, 352, size=2.0, left=True)

    # Cyclone moisture trap mini + auto drain
    ctx.equip += [
        arc3((664, 326), (670, 329), (676, 326)),
        line(664, 314, 664, 326), line(676, 314, 676, 326),
        line(664, 314, 670, 308), line(676, 314, 670, 308),
    ]
    ctx.auto_drain_v(670, 308)
    ctx.text("MOISTURE TRAP (CYCLONE) + AUTO DRAIN", 690, 328, size=2.0, left=True)

    # Air receiver mini
    ctx.equip += [
        arc3((664, 294), (670, 297), (676, 294)),
        line(664, 282, 664, 294), line(676, 282, 676, 294),
        arc3((664, 282), (670, 279), (676, 282)),
    ]
    ctx.text("VERTICAL AIR RECEIVER (ASME SEC. VIII)", 690, 292, size=2.0, left=True)

    # Desiccant tower mini
    ctx.equip += [
        arc3((664, 264), (670, 267), (676, 264)),
        line(664, 252, 664, 264), line(676, 252, 676, 264),
        arc3((664, 252), (670, 249), (676, 252)),
        dashed(664, 261, 676, 261, dash=2.0, gap=1.0),
        dashed(664, 255, 676, 255, dash=2.0, gap=1.0),
    ]
    ctx.hatch += hatch45(665, 255.5, 675, 260.5, spacing=2.5)
    ctx.text("DESICCANT TOWER (TWIN-TOWER DRYER)", 690, 262, size=2.0, left=True)

    # PLC timer mini
    ctx.plc_timer(672, 236, w=16, h=8, tag="PLC")
    ctx.text("PLC SEQUENCE TIMER (TOWER SWITCHING)", 690, 236, size=2.0, left=True)

    # Priority valve mini
    ctx.control_valve_v(668, 218, tag="", act=1)
    ctx.text("PRIORITY VALVE PCV (CLOSES UA < 5.5 BARG)", 690, 218, size=2.0, left=True)

    # Auto drain trap mini
    ctx.auto_drain_v(666, 202, arrow=True)
    ctx.text("AUTO DRAIN TRAP (CONDENSATE)", 690, 200, size=2.0, left=True)

    # Abbreviations
    ctx.text("NC: NORMALLY CLOSED  |  FO: FLOW ORIFICE  |  AT: DEW POINT TRANSM.", 672, 190, size=1.8, left=True)

    # --- 2.3 REFERENCE DRAWINGS (y = 148..185) ---
    ctx.frame.append(line(655, 148, 823, 148))
    ctx.frame.append(line(655, 175, 823, 175))
    ctx.text("REFERENCE DRAWINGS", 739, 180, size=2.2)
    ref_dwgs = [
        ("GPF-00-DB-0001", "DESIGN BASIS — GAS PRODUCTION FACILITY", 169.0),
        ("GPF-00-PI-PID-0001", "P&ID — 3-PHASE SEPARATOR (IA USER)", 163.5),
        ("GPF-00-PI-PID-0012", "P&ID — COOLING WATER SYSTEM", 158.0),
        ("GPF-00-PM-PLN-0008", "ROADMAP — UTILITIES MODULE (PART III.2)", 152.5),
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
        ("A0", "ISSUED FOR REVIEW", "23 OCT 26", "PM", "RE", 139.4),
        ("", "", "", "", "", 134.2),
        ("", "", "", "", "", 129.0),
        ("", "", "", "", "", 123.8),
        ("", "", "", "", "", 118.6),
    ]
    for r_rev, r_desc, r_date, r_chk, r_app, ry in rev_data:
        if r_rev:
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
    ctx.text("INSTRUMENT & UTILITY AIR SYSTEM", 739, 80.0, size=2.5)
    ctx.text("DRAWING NO:", 658, 70.0, size=1.8, left=True)
    ctx.text("GPF-00-PI-PID-0014", 739, 65.5, size=2.8)
    ctx.text("REV:", 658, 56.5, size=1.8, left=True)
    ctx.text("A0", 697, 52.5, size=3.0)
    ctx.text("SCALE:", 742, 56.5, size=1.8, left=True)
    ctx.text("NTS", 781, 52.5, size=2.5)
    ctx.text("DATE:", 658, 44.5, size=1.8, left=True)
    ctx.text("23 OCT 2026", 697, 40.5, size=2.2)
    ctx.text("SHEET:", 742, 44.5, size=1.8, left=True)
    ctx.text("1 OF 1", 781, 40.5, size=2.5)
    ctx.text("DESIGNED:", 658, 32.5, size=1.8, left=True)
    ctx.text("CAD/AI", 697, 29.0, size=2.2)
    ctx.text("DRAWN:", 742, 32.5, size=1.8, left=True)
    ctx.text("GLM-5.3-FLASH", 781, 29.0, size=2.2)
    ctx.text("CHECKED:", 658, 21.5, size=1.8, left=True)
    ctx.text("PM (AI)", 697, 18.5, size=2.2)
    ctx.text("APPROVED:", 742, 21.5, size=1.8, left=True)

    # -------------------------------------------------------------------------
    # 3. TABEL DATA PERALATAN (y = 515..573)
    # -------------------------------------------------------------------------
    # Tabel 1: K-501 (x = 135..375)
    ctx.equip += rect(135, 515, 375, 573)
    ctx.equip.append(line(135, 565, 375, 565))
    ctx.equip.append(line(228, 515, 228, 565))
    ctx.text("EQUIPMENT DATA — AIR COMPRESSOR PACKAGE K-501", 255, 569, size=2.4)
    k501_rows = [
        ("TAG NUMBER", "K-501", 561.0),
        ("SERVICE NAME", "PLANT / INSTRUMENT AIR COMPRESSOR", 553.0),
        ("TYPE", "OIL-FREE ROTARY SCREW + SUCTION FILTER", 545.0),
        ("CAPACITY / DISCH PRESS", "850 NM3/H @ 8.5 BARG", 537.0),
        ("DRIVER", "ELECTRIC MOTOR 90 KW / 400 V / 50 HZ", 529.0),
        ("CODE / STANDARD", "ISO 1217, ISO 8573-1, ASME SEC. VIII (RECEIVERS)", 521.0),
    ]
    for k, (cap, val, ry) in enumerate(k501_rows):
        if k > 0:
            ctx.equip.append(line(135, ry + 4.0, 375, ry + 4.0))
        ctx.text(cap, 138, ry, size=1.8, left=True)
        ctx.text(val, 232, ry, size=2.0, left=True)

    # Tabel 2: DT-501 (x = 395..635)
    ctx.equip += rect(395, 515, 635, 573)
    ctx.equip.append(line(395, 565, 635, 565))
    ctx.equip.append(line(488, 515, 488, 565))
    ctx.text("EQUIPMENT DATA — DESICCANT AIR DRYER DT-501", 515, 569, size=2.4)
    dt501_rows = [
        ("TAG NUMBER", "DT-501 (TOWER A / TOWER B)", 561.0),
        ("SERVICE NAME", "INSTRUMENT AIR DRYER (TWIN-TOWER)", 553.0),
        ("TYPE", "HEATLESS REGENERATING DESICCANT DRYER", 545.0),
        ("CAPACITY / PDP", "850 NM3/H / PDP <= -40 C", 537.0),
        ("QUALITY CLASS", "ISO 8573-1 CLASS 1.2.1 / ISA-7.0.01", 529.0),
        ("CONTROL", "PLC-501 TIMER; GV-502A/B, GV-503A/B, EV-501", 521.0),
    ]
    for k, (cap, val, ry) in enumerate(dt501_rows):
        if k > 0:
            ctx.equip.append(line(395, ry + 4.0, 635, ry + 4.0))
        ctx.text(cap, 398, ry, size=1.8, left=True)
        ctx.text(val, 492, ry, size=2.0, left=True)

    # -------------------------------------------------------------------------
    # 4. BARIS 1 (y = 440): INTAKE -> K-501 -> E-501 -> S-501 -> V-502
    # -------------------------------------------------------------------------
    ctx.text("FROM ATMOSPHERE", 42, 433, size=1.8)
    ctx.flow_arrow_h(46, 440, direction=1)
    ctx.proc += pipe_run_h(440, 46, 52)
    # SF-501 intake filter (pipa berakhir di dinding bodi)
    ctx.filter_body_h(64, 440, w=24, h=14, tag="SF-501", desc="INTAKE FILTER")
    ctx.proc += pipe_run_h(440, 76, 115)
    ctx.flow_arrow_h(88, 440, direction=1)
    # K-501 rotary screw compressor package
    ctx.compressor_screw(137.5, 440, tag="K-501")
    ctx.proc += pipe_run_h(440, 160, 175)
    ctx.flow_arrow_h(168, 440, direction=1)
    # E-501 aftercooler
    ctx.aftercooler_h(195, 440, w=40, h=14, tag="E-501")
    ctx.flow_arrow_v(185, 451, direction=-1, size=2.0)
    ctx.flow_arrow_v(205, 429, direction=-1, size=2.0)
    ctx.proc += pipe_run_h(440, 215, 237)
    ctx.flow_arrow_h(222, 440, direction=1)
    # S-501 cyclone moisture trap (downcomer -> side inlet, top outlet)
    ctx.proc += pipe_run_v(237, 420, 440)
    ctx.proc.append(line(237, 420, 245, 420))
    ctx.moisture_trap_cyclone(253, 432, r=8.0, shell_h=32.0, cone_h=10.0,
                              tag="S-501 MOISTURE TRAP", tag_y=362.0)
    ctx.text("AUTO DRAIN", 264, 377, size=1.8)
    ctx.proc.append(line(253, 438, 253, 440))
    ctx.proc += pipe_run_h(440, 253, 302)
    ctx.text("080-PA-5000 DN50", 280, 445, size=2.0)
    # V-502 wet air receiver + nozzle top
    ctx.air_receiver_v(312, 360, 430, r=14.0, tag="V-502 WET AIR RECEIVER")
    ctx.text("AUTO DRAIN", 324, 344, size=1.8)
    hc502 = head_circle((298, 430), (312, 437), (326, 430))
    ctx.equip += [
        line(300.5, dome_y_at(300.5, hc502), 300.5, 440),
        line(303.5, dome_y_at(303.5, hc502), 303.5, 440),
        line(319, 440, 325, 440),
        line(320.5, dome_y_at(320.5, hc502), 320.5, 440),
        line(323.5, dome_y_at(323.5, hc502), 323.5, 440),
        line(299, 440, 305, 440),
    ]
    # PSV-501 di kepala atas V-502 (vent ke atmosfer)
    ctx.proc.append(line(312, 437, 312, 442.8))
    ctx.proc += ctx.psv_angle(312, 452, tag="PSV-501", size_str="DN50x80", set_press="SET 8.8 BARG")
    ctx.proc += [line(320, 452, 334, 452)]
    ctx.vent_cap_h(334, 452)
    ctx.flow_arrow_h(330, 452, direction=1)
    ctx.text("TO ATMOSPHERE", 334, 458, size=1.8)
    # PI-501 pada shell V-502
    ctx.proc.append(line(298, 410, 276, 410))
    ctx.sym += ctx.bubble(270, 410, "PI", "501")
    # Lanjut ke downcomer baris 2
    ctx.proc += pipe_run_h(440, 322, 352)
    ctx.flow_arrow_h(338, 440, direction=1)
    ctx.proc += pipe_run_v(352, 240, 440)
    ctx.flow_arrow_v(352, 390, direction=-1)
    ctx.flow_arrow_v(352, 300, direction=-1)
    ctx.flow_arrow_v(352, 255, direction=-1)
    ctx.text("080-PA-5000 DN50", 342, 340, size=2.0, rot=90.0)

    # -------------------------------------------------------------------------
    # 5. BARIS 2 (y = 240): F-501 -> F-502 -> DOWNCOMER DRYER
    # -------------------------------------------------------------------------
    ctx.proc += pipe_run_h(240, 352, 369)
    ctx.flow_arrow_h(362, 240, direction=1)
    ctx.filter_body_h(382, 240, w=26, h=14, tag="F-501", desc="PREFILTER 1-3 MICRON", drain=True)
    ctx.flow_arrow_v(382, 229, direction=-1, size=2.0)
    ctx.proc += pipe_run_h(240, 395, 411)
    ctx.flow_arrow_h(403, 240, direction=1)
    ctx.filter_body_h(424, 240, w=26, h=14, tag="F-502",
                      desc="COALESCER OIL < 0.01 MG/M3", drain=True)
    ctx.flow_arrow_v(424, 229, direction=-1, size=2.0)
    ctx.proc += pipe_run_h(240, 437, 456)
    ctx.flow_arrow_h(447, 240, direction=1)
    ctx.proc += pipe_run_v(456, 150, 240)
    ctx.flow_arrow_v(456, 200, direction=-1)
    ctx.flow_arrow_v(456, 165, direction=-1)

    # -------------------------------------------------------------------------
    # 6. DRYER TWIN-TOWER DT-501 (header y = 150, outlet header y = 280)
    # -------------------------------------------------------------------------
    # Header inlet + menara
    ctx.proc += pipe_run_h(150, 456, 526)
    ctx.flow_arrow_h(466, 150, direction=1)
    ctx.flow_arrow_h(508, 150, direction=1)
    ctx.desiccant_tower(478, 185, 255, r=10.0, tag="TOWER A - DRYING", tag_y=308.0)
    ctx.desiccant_tower(526, 185, 255, r=10.0, tag="TOWER B - REGEN.", tag_y=308.0)
    # Katup pengalih bawah (inlet) + riser
    ctx.proc += pipe_run_v(478, 150, 180, gaps=[(162.0, 6.5)])
    ctx.switching_valve_v(478, 162, tag="GV-502A", tag_pos=(466, 162))
    ctx.flow_arrow_v(478, 175, direction=1, size=2.4)
    ctx.proc += pipe_run_v(526, 150, 180, gaps=[(162.0, 6.5)])
    ctx.switching_valve_v(526, 162, tag="GV-502B", tag_pos=(517, 155))
    ctx.flow_arrow_v(526, 175, direction=1, size=2.4)
    # Katup pengalih atas (outlet) + riser
    ctx.proc += pipe_run_v(478, 260, 280, gaps=[(270.0, 6.5)])
    ctx.switching_valve_v(478, 270, tag="GV-503A", tag_pos=(463, 270))
    ctx.flow_arrow_v(478, 277, direction=1, size=2.4)
    ctx.proc += pipe_run_v(526, 260, 280, gaps=[(270.0, 6.5)])
    ctx.switching_valve_v(526, 270, tag="GV-503B", tag_pos=(541, 270))
    ctx.flow_arrow_v(526, 277, direction=1, size=2.4)
    # Exhaust menara B (regenerating): tee -> EV-501 -> muffler -> atmosfer
    ctx.proc += [line(526, 172, 533.5, 172)]
    ctx.proc += ctx.valve_gate_h(540, 172, w=10.0, h=6.0, flanged=True, tag="EV-501")
    ctx.text("EV-501", 540, 163, size=1.8)
    ctx.proc += [line(546.5, 172, 552, 172)]
    ctx.muffler_vent_h(552, 172)
    ctx.flow_arrow_h(531, 172, direction=1)
    ctx.text("TO ATMOSPHERE", 555, 180, size=1.8)
    # Heatless purge: tee header outlet -> GV-504 -> FO-501 -> tower B top
    ctx.proc += pipe_run_v(494, 280, 302, gaps=[(292.0, 6.5)])
    ctx.proc += ctx.valve_gate_v(494, 292, w=6.0, h=10.0, flanged=True, tag="GV-504")
    ctx.text("GV-504", 487, 293.5, size=1.8)
    ctx.proc += pipe_run_h(302, 494, 508)
    ctx.proc += pipe_run_v(508, 262, 302, gaps=[(280.0, 1.5), (290.0, 1.5)])
    ctx.orifice_plate_v(508, 290)
    ctx.text("FO-501", 518, 290, size=1.8)
    ctx.proc += pipe_run_h(262, 508, 526)
    ctx.flow_arrow_v(508, 296, direction=-1, size=2.4)
    ctx.flow_arrow_h(517, 262, direction=-1, size=2.4)
    ctx.text("HEATLESS PURGE", 501, 306, size=1.8)
    # PLC-501 sequence timer + sinyal ke katup pengalih
    ctx.plc_timer(502, 166, w=16, h=8, tag="PLC")
    ctx.text("SEQ TIMER", 502, 156.5, size=1.8)
    ctx.sig += dashed(502, 170, 502, 272, dash=2.5, gap=1.2)
    ctx.sig += dashed(502, 272, 482, 272, dash=2.5, gap=1.2)
    ctx.sig += dashed_brk(502, 272, 522, 272, brk=[6.0], dash=2.5, gap=1.2)
    ctx.sig += dashed(502, 162, 502, 158, dash=2.5, gap=1.2)
    ctx.sig += dashed(502, 158, 482, 158, dash=2.5, gap=1.2)
    ctx.sig += dashed(502, 158, 522, 158, dash=2.5, gap=1.2)
    # Header outlet udara kering
    ctx.proc += pipe_run_h(280, 478, 583)
    ctx.flow_arrow_h(502, 280, direction=1)
    ctx.flow_arrow_h(540, 280, direction=1)
    ctx.flow_arrow_h(575, 280, direction=1)
    ctx.text("080-IA-5001 DN50", 545, 273, size=2.0)
    # AT-501 dew point transmitter + MAH alarm di DCS
    ctx.proc.append(line(556, 280, 556, 290))
    ctx.sym += ctx.bubble(556, 296, "AT", "501")
    ctx.sig += dashed(562, 296, 572, 296, dash=2.5, gap=1.2)
    ctx.sig += dashed(572, 296, 572, 310, dash=2.5, gap=1.2)
    ctx.sig += dashed(572, 310, 578.5, 310, dash=2.5, gap=1.2)
    ctx.sym += ctx.dcs(586, 310, "MAH", "501")
    ctx.text("MAH @ PDP -40 C", 586, 322, size=1.8)
    # F-503 dust filter (0.01-1 micron) pada header outlet
    ctx.filter_body_h(596, 280, w=26, h=14, tag="F-503", drain=True)
    ctx.flow_arrow_v(596, 270, direction=-1, size=2.0)
    ctx.proc += pipe_run_h(280, 609, 612)

    # -------------------------------------------------------------------------
    # 7. V-503 DRY AIR RECEIVER + PSV-502 + PI-502
    # -------------------------------------------------------------------------
    ctx.air_receiver_v(612, 200, 262, r=13.0, tag="V-503 DRY AIR RECEIVER")
    ctx.proc.append(line(612, 268.5, 612, 280))
    # PSV-502 pada kepala atas V-503
    hc503 = head_circle((599, 262), (612, 268.5), (625, 262))
    ctx.proc.append(line(620, dome_y_at(620, hc503), 620, 276.8))
    ctx.proc += ctx.psv_angle(620, 286, tag="PSV-502", size_str="DN50x80", set_press="SET 8.8 BARG")
    ctx.proc += [line(628, 286, 636, 286)]
    ctx.vent_cap_h(636, 286)
    ctx.flow_arrow_h(633, 286, direction=1)
    ctx.text("TO ATMOSPHERE", 637, 293, size=1.8)
    # PI-502 + outlet ke dry header
    ctx.proc.append(line(599, 240, 592, 240))
    ctx.sym += ctx.bubble(586, 240, "PI", "502")
    ctx.proc.append(line(625, 250, 640, 250))
    ctx.flow_arrow_h(632, 250, direction=-1, size=2.4)
    ctx.proc += pipe_run_v(640, 110, 250)
    ctx.flow_arrow_v(640, 180, direction=-1)
    ctx.flow_arrow_v(640, 140, direction=-1)

    # -------------------------------------------------------------------------
    # 8. HEADER DRY + PRIORITY VALVE PCV-501 + CABANG IA / UA
    # -------------------------------------------------------------------------
    ctx.proc += pipe_run_h(110, 72.5, 640)
    ctx.proc += ctx.continuity_box_left(110, "080-IA-5001 DN50", "TO INSTRUMENT AIR HEADER",
                            "DWG: GPF-00-PI-PID-0014")
    ctx.text("080-IA-5001 DN50", 350, 115, size=2.0)
    ctx.flow_arrow_h(600, 110, direction=-1)
    ctx.flow_arrow_h(480, 110, direction=-1)
    ctx.flow_arrow_h(350, 110, direction=-1)
    ctx.flow_arrow_h(150, 110, direction=-1)
    # Cabang UA melalui PCV-501 (menutup UA bila < 5.5 barg)
    ctx.proc += pipe_run_v(580, 110, 204, gaps=[(140.0, 6.5)])
    ctx.priority_valve_v(580, 140, tag="PCV-501", tag_pos=(568, 140), act=1,
                         note="CLOSES AT < 5.5 BARG", note_pos=(558, 127))
    ctx.flow_arrow_v(580, 120, direction=1, size=2.4)
    ctx.flow_arrow_v(580, 190, direction=1)
    ctx.flow_arrow_v(580, 204, direction=1)
    ctx.text("080-UA-5002 DN50", 587, 175, size=2.0, rot=90.0)
    ctx.text("TO UTILITY AIR USERS", 573, 175, size=1.8, rot=90.0)
    # PT-501: pilot tekanan header ke PCV-501
    ctx.proc.append(line(620, 110, 620, 120))
    ctx.sym += ctx.bubble(620, 126, "PT", "501")
    ctx.sig += dashed(620, 132, 620, 140, dash=2.5, gap=1.2)
    ctx.sig += dashed(620, 140, 590.2, 140, dash=2.5, gap=1.2)

    # -------------------------------------------------------------------------
    # 9. REGISTRASI LINE & EKSPOR MANIFEST
    # -------------------------------------------------------------------------
    ctx.register_line("080-PA-5000", spec="A1A", service="Wet Compressed Air", dn=50)
    ctx.register_line("080-IA-5001", spec="A1A", service="Instrument Air", dn=50)
    ctx.register_line("080-UA-5002", spec="A1A", service="Utility Air", dn=50)

    out_json = Path(__file__).resolve().parent / "air_system_demo.texts.json"
    layers = ctx.export_manifest(out_json)
    return layers


if __name__ == "__main__":
    air_system_demo()
