"""P&ID GPF-00-PI-PID-0020 Rev A0 — GAS BOOSTER COMPRESSION, RECIPROCATING 2x50%.

Sheet A1 (841 x 594 mm), origin kiri-bawah. STANDALONE PACKAGE (di luar
scope GPF-00-DB-0001) — data proses per instruksi PM 26 OCT 2026:
  - NATURAL GAS BOOSTER: suction BL 250 PSIG (17.2 BARG) / 40 C (assumed),
    discharge BL 450 PSIG (31.0 BARG), 10 MMSCFD total, 2 x 50% (train A/B,
    masing-masing 5 MMSCFD). Driver electric motor M (assumed).
  - Train A (band atas, Y=460) & train B (band bawah, Y=240), simetris:
    SDV (ESD FC + solenoid SY) -> PT/PI + TI -> suction scrubber V-21x
    (LG/LT, SIS LAHH/LSLL, PSV tail ke BD, LV drain ke BD) -> suction
    pulsation dampener -> K-21x recip API 618 double-acting (valve
    unloaders 0-50-100 %, lube oil FSL, distance piece purge ke BD) ->
    discharge pulsation dampener -> check valve -> PT/PI + TT/TI ->
    fin-fan aftercooler E-21x (TIC auto-louver) -> discharge header.
  - Spill-back capacity control FV-2101/2201 (FC + FY) dari downstream
    aftercooler kembali ke inlet scrubber.
  - BDV suction & discharge per train + PSV tail + packing purge + LV
    drain -> BD header 080-FL-9031 -> BL TO FLARE KO DRUM.
  - Discharge header -> FE/FT-241 + FIQ -> BL TO SALES PIPELINE 450 PSIG.
  - ESD-2 (SIS): pola pid_v101 — box ESD-2 + diamond di SDV/motor;
    cause & effect di NOTES (3 sinyal SIS utama).

Line numbers (9000-series, PENDING line index registration):
  150-NG-9001 suction header; 150-NG-9002/9003 branch suction A/B;
  100-NG-9011/9012 discharge A/B; 150-NG-9010 discharge header;
  100-NG-9021/9022 spill-back A/B; 080-FL-9031 BD/flare header.

Standar acuan:
  - API STD 618 / ISO 13631 (recip compressor, pulsation DA-3, unloader,
    lube oil FSL, distance piece purge)
  - API STD 661 / ISO 13706 (fin-fan auto louver)
  - ANSI/ISA-5.1-2024, ISO 10628-2:2012, ISO 5457, ISO 7200
  - Referensi perusahaan: SSY-PRO-PID-002 & SSY-PRO-PID-003

Layers:
  REF-FRAME  border lembar, grid referensi, kotak tabel furniture
  REF-TITLE  title block + rev table (ISO 7200 / Company Standard)
  REF-EQUIP  scrubber, kompresor, dampener, fin-fan, bridle
  REF-PROC   line proses, valves, PSV, orifice, BL boxes
  REF-SYM    bubbles instrumen, DCS/SIS, louver, FY, ESD-2, legend
  REF-SIG    signal listrik (dashed)
  REF-SIGP   signal pneumatic (solid + "//")
  REF-HATCH  arsiran 45 deg demister / fin bundle
  REF-TEXT   ditulis post-build oleh apply_text.py dari manifest TEXTS
"""

from __future__ import annotations

from pathlib import Path

from cadgen import dxf
from pid_common import (
    circle,
    dashed,
    dashed_brk,
    line,
    pipe_run_h,
    pipe_run_v,
    pneu,
    rect,
)
from compression_common import CompressionContext

BD_Y = 95.0            # BD/flare header
MID_Y = 345.0          # suction header (kiri) & discharge header (kanan)
BRK = 1.5              # half gap break 3 mm


def _gaps(*specs: tuple[float, float]) -> list[tuple[float, float]]:
    return list(specs)


@dxf
def pid_recip_booster():
    ctx = CompressionContext()

    # =========================================================================
    # 1. BORDER LEMBAR A1 & GRID REFERENSI (ISO 5457)
    # =========================================================================
    ctx.frame += rect(10, 7, 831, 587)
    ctx.frame += rect(20, 15, 823, 579)

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

    # =========================================================================
    # 2. KOLOM FURNITURE KANAN (x = 655..823)
    # =========================================================================
    ctx.frame.append(line(655, 15, 655, 579))

    # --- 2.1 NOTES (y = 435..579) ---
    ctx.frame.append(line(655, 435, 823, 435))
    ctx.frame.append(line(655, 567, 823, 567))
    ctx.text("NOTES", 739, 573, size=2.5)
    notes = [
        "1. SCHEMATIC - NOT TO SCALE. NO ORIENTATION IMPLIED.",
        "2. DESIGN DATA (PER PM INSTRUCTION 26 OCT 2026): NATURAL GAS BOOSTER;",
        "   SUCTION 250 PSIG (17.2 BARG) / 40 C (ASSUMED); DISCHARGE 450 PSIG",
        "   (31.0 BARG); 10 MMSCFD TOTAL, 2 X 50% PARALLEL TRAINS A/B",
        "   (5 MMSCFD EACH). DRIVER: ELECTRIC MOTOR (M, ASSUMED).",
        "3. STANDALONE PACKAGE - OUTSIDE GPF-00-DB-0001 SCOPE.",
        "4. ESD-2 (SIS) CAUSE & EFFECT:",
        "   (1) LT-2108/2208 LAHH OR LSLL (SUCTION SCRUBBER) -> CLOSE",
        "       SDV-2102/2202 + TRIP K-21A/B.",
        "   (2) PT-241 PAHH (DISCHARGE HEADER) -> CLOSE SDV-2102/2202 +",
        "       TRIP K-21A/B + OPEN BDV-21A2/B2.",
        "   (3) FSL-2109/2209 LSL (CYLINDER LUBE OIL) -> TRIP K-21A/B.",
        "   SEE CAUSE & EFFECT CHART (PENDING REGISTRATION).",
        "5. LINE NUMBERS 9000-SERIES PENDING PIPING LINE INDEX REGISTRATION.",
        "6. COMPRESSORS K-21A/B PER API STD 618, DOUBLE-ACTING; CAPACITY",
        "   CONTROL BY VALVE UNLOADERS 0-50-100 % AND SPILL-BACK FV-2101/2201",
        "   (FAIL CLOSED) RETURNING TO SUCTION SCRUBBER INLET.",
        "7. PULSATION DAMPENERS PD-21A1/A2, PD-21B1/B2 PER API 618 DESIGN",
        "   APPROACH 3 ON SUCTION AND DISCHARGE OF EACH TRAIN.",
        "8. FIN-FAN E-21A/B PER API STD 661 / ISO 13706; TIC-2101/2201",
        "   MODULATES AUTO LOUVERS FROM TT-2101/2201 (OUTLET).",
        "9. CYLINDER LUBE OIL FORCE-FED; FSL LSL TRIPS DRIVER. DISTANCE",
        "   PIECE PACKING PURGED TO BD HEADER 080-FL-9031.",
        "10. PSV-21A/B TAIL TO 080-FL-9031 (TO FLARE KO DRUM). SET PRESSURE",
        "    PER VESSEL DATASHEET (VALUE INDICATIVE - ASSUMED).",
        "11. INSTRUMENT SYMBOLS & TAGGING PER ANSI/ISA-5.1-2024; DIAGRAM",
        "    CONTENT PER ISO 10628-2:2012.",
    ]
    ny = 560.0
    for ln in notes:
        ctx.text(ln, 659, ny, size=2.0, left=True)
        ny -= 4.9

    # --- 2.2 LEGEND & SYMBOLS (y = 185..423) ---
    ctx.frame.append(line(655, 185, 823, 185))
    ctx.frame.append(line(655, 423, 823, 423))
    ctx.text("LEGEND & SYMBOLS", 739, 429, size=2.5)

    ctx.proc += [line(660, 413, 685, 413)]
    ctx.flow_arrow_h(676, 413, direction=1)
    ctx.text("PROCESS LINE", 695, 413, size=1.8, left=True)

    ctx.sig += dashed(660, 399, 685, 399)
    ctx.text("ELECTRIC SIGNAL (BPCS / SIS)", 695, 399, size=1.8, left=True)

    ctx.sigp += pneu(660, 385, 685, 385)
    ctx.text("PNEUMATIC SIGNAL", 695, 385, size=1.8, left=True)

    ctx.proc += [
        line(660, 366, 680, 366), line(680, 366, 685, 369),
        line(685, 369, 680, 372), line(680, 372, 660, 372), line(660, 372, 660, 366),
    ]
    ctx.text("CONTINUITY ARROW (BATTERY LIMIT)", 695, 369, size=1.8, left=True)

    ctx.sym.append(circle(672, 352, 5.0))
    ctx.sym.append(line(667, 352, 677, 352))
    ctx.text("FIELD INSTRUMENT", 695, 352, size=1.8, left=True)

    ctx.sym += [
        line(666, 331, 678, 331), line(678, 331, 678, 343),
        line(678, 343, 666, 343), line(666, 343, 666, 331),
        circle(672, 337, 5.0), line(666, 337, 678, 337),
    ]
    ctx.text("DCS SHARED DISPLAY / CONTROL", 695, 337, size=1.8, left=True)

    ctx.sym += [
        line(666, 314, 678, 314), line(678, 314, 678, 326),
        line(678, 326, 666, 326), line(666, 326, 666, 314),
        line(666, 320, 672, 326), line(672, 326, 678, 320),
        line(678, 320, 672, 314), line(672, 314, 666, 320),
    ]
    ctx.text("SIS LOGIC SOLVER / INTERLOCK", 695, 320, size=1.8, left=True)

    ctx.sym += ctx.valve_gate_h(668, 298, w=8, h=5, flanged=False)
    ctx.sym += ctx.valve_globe_h(695, 298, w=8, h=5, flanged=False)
    ctx.sym += ctx.valve_check_h(722, 298, w=8, h=5)
    ctx.text("GATE / GLOBE / CHECK VALVE", 695, 289, size=1.8, left=True)

    ctx.sym += [
        line(750, 293, 750, 298), line(747, 293, 750, 298), line(753, 293, 750, 298),
        line(747, 293, 753, 293),
        line(750, 298, 755, 298), line(750, 298, 755, 295), line(750, 298, 755, 301),
        line(755, 295, 755, 301),
        line(750, 298, 750, 303), line(748, 303, 752, 303),
    ]
    ctx.text("PRESSURE SAFETY VALVE (PSV)", 695, 272, size=1.8, left=True)

    # Control valve + FY booster (spill-back type)
    ctx.sym += ctx.control_valve_h(668, 254, w=8, h=5, tag="")
    ctx.sym += rect(664.5, 266, 671.5, 271.5)
    ctx.text("FY", 668, 269.5, size=1.6)
    ctx.sigp += pneu(668, 266, 668, 263.8, spacing=2.4)
    ctx.text("CONTROL VALVE + FY (FC)", 695, 256, size=1.8, left=True)

    # Valve unloader mini
    ctx.sym += rect(664, 243, 672, 248)
    ctx.text("VALVE UNLOADER 0-50-100 %", 695, 245.5, size=1.8, left=True)

    # Auto drain LV mini
    ctx.sym += ctx.valve_gate_v(668, 230, w=5, h=8, flanged=False)
    ctx.text("AUTO DRAIN LV + LEVEL LOOP (LIC)", 695, 230, size=1.8, left=True)

    ctx.text("STANDARD ABBREVIATIONS:", 659, 216, size=1.9, left=True)
    ctx.text("FC: FAIL CLOSED        | CSO: CAR-SEAL OPEN", 659, 207, size=1.8, left=True)
    ctx.text("NC: NORMALLY CLOSED    | BDV: BLOWDOWN VALVE", 659, 199, size=1.8, left=True)
    ctx.text("SY: SOLENOID VALVE     | FSL: FLOW SWITCH LOW", 659, 191, size=1.8, left=True)

    # --- 2.3 REFERENCE DRAWINGS (y = 148..185) ---
    ctx.frame.append(line(655, 148, 823, 148))
    ctx.frame.append(line(655, 175, 823, 175))
    ctx.text("REFERENCE DRAWINGS", 739, 180, size=2.2)
    ref_dwgs = [
        ("GPF-00-PI-PID-0020", "THIS DRAWING - GAS BOOSTER COMPRESSION (STANDALONE)", 169.0),
        ("GPF-00-PI-PID-0012", "P&ID GAS COMPRESSION PACKAGE 2-STAGE (REFERENCE)", 163.5),
        ("GPF-00-PM-PLN-0008", "ROADMAP AI-CAD SUITE (BAGIAN II KOMPRESI)", 158.0),
        ("(PENDING)", "PIPING LINE INDEX - 9000-SERIES REGISTRATION", 152.5),
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
        ("A0", "ISSUED FOR REVIEW", "26 OCT 26", "PM", "RE", 118.6),
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
    ctx.text("GAS BOOSTER COMPRESSION (RECIP 2 X 50%)", 739, 80.0, size=2.2)
    ctx.text("DRAWING NO:", 658, 70.0, size=1.8, left=True)
    ctx.text("GPF-00-PI-PID-0020", 739, 65.5, size=2.8)
    ctx.text("REV:", 658, 56.5, size=1.8, left=True)
    ctx.text("A0", 697, 52.5, size=3.0)
    ctx.text("SCALE:", 742, 56.5, size=1.8, left=True)
    ctx.text("NTS", 781, 52.5, size=2.5)
    ctx.text("DATE:", 658, 44.5, size=1.8, left=True)
    ctx.text("26 OCT 2026", 697, 40.5, size=2.2)
    ctx.text("SHEET:", 742, 44.5, size=1.8, left=True)
    ctx.text("1 OF 1", 781, 40.5, size=2.5)
    ctx.text("DESIGNED:", 658, 32.5, size=1.8, left=True)
    ctx.text("CAD/FEED", 697, 29.0, size=2.2)
    ctx.text("DRAWN:", 742, 32.5, size=1.8, left=True)
    ctx.text("GLM-5.3-FLASH", 781, 29.0, size=2.2)
    ctx.text("CHECKED:", 658, 21.5, size=1.8, left=True)
    ctx.text("PM (AI)", 697, 18.5, size=2.2)
    ctx.text("APPROVED:", 742, 21.5, size=1.8, left=True)

    # =========================================================================
    # 3. COMMON: SUCTION HEADER + DISCHARGE HEADER + BD HEADER + ESD-2 BOX
    # =========================================================================

    # --- 3.1 Suction BL + header 150-NG-9001 + riser split A/B ---
    ctx.proc += ctx.bl_box(
        y=MID_Y, x0=25.0, x1=68.0, dir=1,
        tag="150-NG-9001 DN150",
        desc="FROM FIELD GAS SUPPLY 250 PSIG",
        dwg="",
    )
    ctx.proc += pipe_run_h(MID_Y, 72.5, 105.0)
    ctx.proc += pipe_run_v(105.0, 240.0, 460.0)
    ctx.flow_arrow_h(95.0, MID_Y, direction=1, size=2.4)
    ctx.flow_arrow_v(105.0, 420.0, direction=1, size=2.4)
    ctx.flow_arrow_v(105.0, 300.0, direction=-1, size=2.4)

    # --- 3.2 Discharge header 150-NG-9010 + FE/FT-241 + FIQ + BL sales ---
    ctx.proc += pipe_run_h(MID_Y, 558.0, 605.0, gaps=_gaps((592.0, 1.25)))
    ctx.proc += pipe_run_v(558.0, MID_Y, 460.0)          # downleg train A
    ctx.proc += pipe_run_v(574.0, 240.0, MID_Y)          # downleg train B
    ctx.proc += ctx.orifice_h(592.0, MID_Y, tag_fe="")
    ctx.text("FE-241", 592.0, 337.0, size=1.8)
    ctx.sig += dashed(592.0, 351.0, 592.0, 355.0)
    ctx.sym += ctx.bubble(592.0, 361.0, "FT", "241")
    ctx.sig += dashed(592.0, 367.0, 592.0, 369.5)
    ctx.sym += ctx.dcs(592.0, 377.0, "FIQ", "241")
    # PT-241 + SIS PAHH/PALL (discharge header PSHH -> ESD-2, NOTE 4)
    ctx.proc += [line(564.0, MID_Y, 564.0, 355.0)]
    ctx.sym += ctx.bubble(564.0, 361.0, "PT", "241")
    ctx.sym += ctx.sis_box(564.0, 377.0, "PAHH", "PALL")
    ctx.sig += dashed(564.0, 367.0, 564.0, 369.0)
    ctx.text("TO ESD-2", 566.0, 389.5, size=1.8)
    ctx.flow_arrow_h(580.0, MID_Y, direction=1, size=2.0)
    ctx.flow_arrow_v(558.0, 400.0, direction=-1, size=2.4)
    ctx.flow_arrow_v(574.0, 290.0, direction=-1, size=2.4)
    # Downleg discharge per train tetap line per-train sampai titik gabung di
    # header; 150-NG-9010 hanya untuk header jual (BL sales).
    ctx.text("100-NG-9011 DN100", 552.0, 400.0, size=1.8, rot=90.0)
    ctx.text("100-NG-9012 DN100", 568.0, 290.0, size=1.8, rot=90.0)
    ctx.proc += ctx.bl_box(
        y=MID_Y, x0=605.0, x1=645.0, dir=1,
        tag="150-NG-9010 DN150",
        desc="TO SALES PIPELINE 450 PSIG",
        dwg="",
    )

    # --- 3.3 BD / flare header 080-FL-9031 (y = 95) ---
    ctx.proc += pipe_run_h(BD_Y, 65.0, 605.0)
    ctx.proc += [line(65.0, 92.0, 65.0, 98.0)]
    ctx.proc += ctx.bl_box(
        y=BD_Y, x0=605.0, x1=645.0, dir=1,
        tag="080-FL-9031 DN80",
        desc="TO FLARE KO DRUM",
        dwg="",
    )
    for ax in (100.0, 160.0, 300.0, 450.0, 560.0):
        ctx.flow_arrow_h(ax, BD_Y, direction=1, size=2.4)
    ctx.text("080-FL-9031 DN80", 330.0, 101.0, size=1.8)

    # --- 3.4 ESD-2 SIS logic box (pola pid_v101) ---
    ctx.sym += rect(40, 528, 64, 552)
    ctx.sym += [
        line(40, 540, 52, 552), line(52, 552, 64, 540),
        line(64, 540, 52, 528), line(52, 528, 40, 540),
    ]
    ctx.text("ESD", 52, 542.5, size=2.2)
    ctx.text("2", 52, 537.5, size=2.2)
    ctx.text("SIS LOGIC SOLVER", 52, 523.0, size=1.9)
    ctx.text("(SEE NOTE 4)", 52, 518.0, size=1.8)

    # =========================================================================
    # 4. TRAIN A (Y = 460) & TRAIN B (Y = 240)
    # =========================================================================
    for Y, sfx, ipfx, ipfx2, loop, ln_br, ln_dis, ln_sb, dx_leg, sb_y, wells_dis in (
        (460.0, "A", "210", "211", "2101", "150-NG-9002 DN150",
         "100-NG-9011 DN100", "100-NG-9021 DN100", 558.0, 390.0,
         (436.0, 454.0, 472.0)),
        (240.0, "B", "220", "221", "2201", "150-NG-9003 DN150",
         "100-NG-9012 DN100", "100-NG-9022 DN100", 574.0, 170.0,
         (430.0, 448.0, 466.0)),
    ):
        cyc = Y - 13.0                     # compressor shaft line
        y_bot, y_top = Y - 25.0, Y + 45.0  # scrubber shell
        det_y = Y + 64.0                   # gas outlet detour
        apex = y_bot - 8.0                 # bottom head apex
        drain_y = apex - 6.2               # drain flange
        fv_x = 360.0 if sfx == "A" else 368.0
        tag_sdv, tag_pt, tag_pi, tag_ti = f"{ipfx}2", f"{ipfx}3", f"{ipfx}4", f"{ipfx}5"
        tag_lg, tag_lt, tag_ltsis, tag_fsl = f"{ipfx}6", f"{ipfx}7", f"{ipfx}8", f"{ipfx}9"
        tag_ptd, tag_pid, tag_ttd = f"{ipfx2}0", f"{ipfx2}1", f"{ipfx2}2"

        # --- 4.1 Suction: line + SDV + PT/PI + TI ---
        ctx.proc += pipe_run_h(Y, 105.0, 207.0, gaps=_gaps((130.0, 6.2)))
        ctx.proc += ctx.sdv_h(130.0, Y, tag=f"SDV-{tag_sdv}", fail="FC")
        ctx.sym += ctx.interlock_diamond(130.0, Y + 27.0, tag="ESD-2")
        ctx.sig += dashed(130.0, Y + 22.0, 130.0, Y + 12.5)
        ctx.text("SY", 138.5, Y + 13.2, size=1.8)
        for wx, tt, tl in ((150.0, "PT", tag_pt), (167.0, "PI", tag_pi),
                           (184.0, "TI", tag_ti)):
            ctx.proc += [line(wx, Y, wx, Y + 10.0)]
            ctx.sym += ctx.bubble(wx, Y + 16.0, tt, tl)
        ctx.sig += dashed(184.0, Y + 22.0, 184.0, Y + 24.5)
        ctx.sym += ctx.dcs(184.0, Y + 32.0, "TI", tag_ti)
        if sfx == "A":
            # Label branch hisap train A diriser vertikal (pola train B) agar
            # bebas dome aktuator SDV-2102.
            ctx.text(ln_br, 100.0, 420.0, size=1.8, rot=90.0)
        else:
            ctx.text(ln_br, 100.0, 300.0, size=1.8, rot=90.0)
        for ax in (117.0, 158.0, 250.0, 300.0):
            ctx.flow_arrow_h(ax, Y, direction=1, size=2.4)

        # --- 4.2 Suction scrubber V-21x + bridle + SIS + PSV + LV ---
        ctx.suction_scrubber(225.0, y_bot, y_top, r=16.0,
                             tag=f"V-21{sfx}", service="SUCTION SCRUBBER",
                             inlet_y=Y)
        # Level taps -> LG + LT (BPCS -> LIC -> LV) + LT (SIS LAHH/LSLL)
        y_tap_t, y_tap_b = Y + 18.0, Y - 14.0
        ctx.equip += [
            line(241.0, y_tap_t, 246.5, y_tap_t),
            ctx.valve_gate_h(249.0, y_tap_t, w=5.0, h=3.2, flanged=False),
            line(251.5, y_tap_t, 262.0, y_tap_t),
            line(241.0, y_tap_b, 246.5, y_tap_b),
            ctx.valve_gate_h(249.0, y_tap_b, w=5.0, h=3.2, flanged=False),
            line(251.5, y_tap_b, 262.0, y_tap_b),
        ]
        ctx.sym += [
            line(262.0, y_tap_b, 262.0, y_tap_t), line(265.0, y_tap_b, 265.0, y_tap_t),
            line(262.0, y_tap_b, 265.0, y_tap_b), line(262.0, y_tap_t, 265.0, y_tap_t),
        ]
        ctx.text(f"LG-{tag_lg}", 263.5, y_tap_t + 5.0, size=2.0)
        ctx.sym += ctx.bubble(274.0, Y - 7.0, "LT", tag_lt)
        ctx.sig += dashed(265.0, Y - 7.0, 268.0, Y - 7.0, dash=2.0, gap=1.2)
        ctx.sym += ctx.bubble(274.0, Y + 11.0, "LT", tag_ltsis)
        ctx.sig += dashed(265.0, Y + 11.0, 268.0, Y + 11.0, dash=2.0, gap=1.2)
        ctx.sym += ctx.sis_box(290.0, Y + 11.0, "LAHH", "LSLL")
        ctx.sig += dashed(280.0, Y + 11.0, 282.0, Y + 11.0, dash=2.5, gap=1.2)
        ctx.text("TO ESD-2", 300.0, Y + 24.0, size=1.8, left=True)
        # LIC + signal ke LV
        ctx.sym += ctx.dcs(274.0, Y - 27.0, "LIC", tag_lt)
        ctx.sig += dashed(274.0, Y - 13.0, 274.0, Y - 19.5, dash=2.0, gap=1.2)
        if sfx == "A":
            ctx.sig += dashed_brk(274.0, Y - 34.5, 274.0, Y - 88.0, brk=[35.5])
            ctx.sig += dashed(274.0, Y - 88.0, 200.0, Y - 88.0)
            ctx.sig += dashed(200.0, Y - 88.0, 200.0, Y - 95.0)
        else:
            ctx.sig += dashed(274.0, Y - 34.5, 274.0, Y - 45.0)
            ctx.sig += dashed(274.0, Y - 45.0, 225.0, Y - 45.0)
            ctx.sig += dashed(225.0, Y - 45.0, 225.0, Y - 50.0)
        # PSV-21x + tail ke BD header (tag manual — posisi library menabrak
        # koridor drop LV setelah reroute)
        ctx.proc += pipe_run_v(218.6, y_top + 13.2, Y + 70.0)
        ctx.proc += ctx.psv_angle(218.6, Y + 78.0, tag="",
                                  size_str="", set_press="")
        ctx.schedule_valves.append({
            "tag": f"PSV-21{sfx}", "type": "PRESSURE SAFETY VALVE (PSV)",
            "orientation": "ANGLE", "x": 218.6, "y": round(Y + 78.0, 3),
            "size": "DN50x80", "set_press": "SET 19.6 BARG"})
        # Blok label PSV di kiri simbol; train B lebih kiri (x=178) agar bbox
        # bebas drop LV-21A di x=200 sekaligus bebas segitiga/flange PSV.
        psv_lbl_x = 195.0 if sfx == "A" else 178.0
        ctx.text(f"PSV-21{sfx}", psv_lbl_x, Y + 70.0, size=2.2, left=True)
        ctx.text("DN50x80", psv_lbl_x, Y + 65.5, size=1.8, left=True)
        ctx.text("SET 19.6 BARG", psv_lbl_x, Y + 61.0, size=1.8, left=True)
        ctx.proc += pipe_run_h(Y + 78.0, 227.8, 243.0)
        if sfx == "A":
            ctx.proc += pipe_run_h(566.0, 85.0, 243.0)
            ctx.proc += pipe_run_v(243.0, Y + 78.0, 566.0)
            ctx.proc += pipe_run_v(85.0, BD_Y, 566.0, gaps=_gaps((MID_Y, BRK)))
            ctx.flow_arrow_v(243.0, 550.0, direction=1, size=1.6)
            ctx.flow_arrow_h(150.0, 566.0, direction=-1, size=2.0)
            ctx.flow_arrow_v(85.0, 450.0, direction=-1, size=2.4)
            ctx.flow_arrow_v(85.0, 250.0, direction=-1, size=2.4)
        else:
            # Tail PSV-21B pola PSV-21A (Note 10: tail ke 080-FL-9031): keluar
            # kanan, naik di x=243 sampai y=370 (di atas ujung spring cy+16),
            # balik kiri, turun di x=92 ke BD header; break 3 mm pada garis
            # minor ini di silang riser hisap (105), drop BDV-21A1 (112) dan
            # drop LV-21A (200), serta di silang header hisap y=345.
            ctx.proc += pipe_run_h(370.0, 92.0, 243.0,
                                   gaps=_gaps((105.0, BRK), (112.0, BRK),
                                              (200.0, BRK)))
            ctx.proc += pipe_run_v(243.0, Y + 78.0, 370.0)
            ctx.proc += pipe_run_v(92.0, BD_Y, 370.0,
                                   gaps=_gaps((MID_Y, BRK)))
            ctx.flow_arrow_v(243.0, 345.0, direction=1, size=1.6)
            ctx.flow_arrow_h(170.0, 370.0, direction=-1, size=2.0)
            ctx.flow_arrow_v(92.0, 200.0, direction=-1, size=2.4)
        # LV drain ke BD header
        lv_vy = Y - 100.0 if sfx == "A" else 185.0
        if sfx == "A":
            # drop dari drain flange, jog kiri di y=410 ke x=200 (koridor bebas
            # dari vessel train B), lalu turun ke BD header dengan break di
            # y=390/240/170 dan gate valve LV-21A di y=360. Silang tail
            # PSV-21B di y=370 di-break pada garis tail (yang lebih kecil).
            ctx.proc += pipe_run_v(225.0, drain_y, 410.0)
            ctx.proc += [line(225.0, 410.0, 200.0, 410.0)]
            ctx.proc += pipe_run_v(200.0, BD_Y, 410.0,
                                   gaps=_gaps((390.0, BRK), (240.0, BRK),
                                              (170.0, BRK),
                                              (lv_vy, 5.0)))
            ctx.flow_arrow_v(225.0, 415.0, direction=-1, size=2.4)
            ctx.flow_arrow_h(214.0, 410.0, direction=-1, size=2.0)
            ctx.flow_arrow_v(200.0, 400.0, direction=-1, size=2.4)
            ctx.flow_arrow_v(200.0, 375.0, direction=-1, size=2.4)
            ctx.flow_arrow_v(200.0, 250.0, direction=-1, size=2.4)
            ctx.flow_arrow_v(200.0, 200.0, direction=-1, size=2.4)
            ctx.flow_arrow_v(200.0, 120.0, direction=-1, size=2.4)
        else:
            ctx.proc += pipe_run_v(225.0, drain_y, 130.0,
                                   gaps=_gaps((170.0, BRK), (lv_vy, 5.0)))
            ctx.proc += [line(225.0, 130.0, 240.0, 130.0)]
            ctx.proc += pipe_run_v(240.0, BD_Y, 130.0)
            ctx.flow_arrow_h(232.0, 130.0, direction=1, size=2.0)
            ctx.flow_arrow_v(240.0, 112.0, direction=-1, size=2.4)
        ctx.proc += ctx.valve_gate_v(200.0 if sfx == "A" else 225.0, lv_vy,
                                     w=6.0, h=10.0, flanged=False,
                                     tag=f"LV-21{sfx}")
        if sfx == "A":
            ctx.text(f"LV-21{sfx}", 208.0, 380.0, size=1.8, left=True)
        else:
            ctx.text(f"LV-21{sfx}", 233.0, 205.0, size=1.8, left=True)
        if sfx == "B":
            ctx.flow_arrow_v(225.0, 150.0, direction=-1, size=2.4)

        # --- 4.3 Gas outlet detour + kompresor K-21x + dampeners + purge ---
        ctx.proc += pipe_run_v(231.4, y_top + 13.2, det_y)
        ctx.proc += pipe_run_h(det_y, 231.4, 270.0)
        ctx.proc += pipe_run_v(270.0, Y, det_y)
        ctx.flow_arrow_v(231.4, Y + 61.0, direction=1, size=1.6)
        ctx.flow_arrow_h(250.0, det_y, direction=1, size=2.0)
        ctx.flow_arrow_v(270.0, Y + 35.0, direction=-1, size=2.4)

        k = ctx.compressor_reciprocating(355.0, Y, tag=f"K-21{sfx}",
                                         stage_label="VALVE UNLOADERS",
                                         fsl_loop=tag_fsl)
        ctx.pulsation_dampener(361.0, Y, tag="")
        ctx.pulsation_dampener(373.0, Y, tag="")
        ctx.schedule_equipment.append({
            "tag": f"PD-21{sfx}1", "type": "PULSATION DAMPENER (API 618 DA-3)",
            "x": 361.0, "y": round(Y, 3)})
        ctx.schedule_equipment.append({
            "tag": f"PD-21{sfx}2", "type": "PULSATION DAMPENER (API 618 DA-3)",
            "x": 373.0, "y": round(Y, 3)})
        ctx.text(f"PD-21{sfx}1", 361.0, Y + 25.0, size=2.5)
        ctx.text(f"PD-21{sfx}2", 373.0, Y + 30.0, size=2.5)
        ctx.sym += ctx.interlock_diamond(290.0, cyc, tag="ESD-2")
        ctx.sig += dashed(295.0, cyc, 304.0, cyc)
        # Distance piece purge ke BD header
        if sfx == "A":
            ctx.proc += pipe_run_v(352.0, k["purge_y"], 420.0)
            ctx.proc += pipe_run_h(420.0, 352.0, 440.0, gaps=_gaps((400.0, BRK)))
            ctx.proc += pipe_run_v(440.0, BD_Y, 420.0,
                                   gaps=_gaps((390.0, BRK), (240.0, BRK),
                                              (170.0, BRK), (125.0, 5.0)))
            ctx.proc += ctx.valve_gate_v(440.0, 125.0, w=6.0, h=10.0, flanged=False)
            ctx.flow_arrow_v(352.0, 432.0, direction=-1, size=2.0)
            ctx.flow_arrow_h(376.0, 420.0, direction=1, size=2.0)
            ctx.flow_arrow_v(440.0, 300.0, direction=-1, size=2.4)
            ctx.flow_arrow_v(440.0, 200.0, direction=-1, size=2.4)
            ctx.flow_arrow_v(440.0, 110.0, direction=-1, size=2.4)
            ctx.text("PURGE", 356.0, 433.0, size=1.8, left=True)
        else:
            ctx.proc += pipe_run_v(352.0, BD_Y, k["purge_y"],
                                   gaps=_gaps((170.0, BRK), (140.0, 5.0)))
            ctx.proc += ctx.valve_gate_v(352.0, 140.0, w=6.0, h=10.0, flanged=False)
            ctx.flow_arrow_v(352.0, 200.0, direction=-1, size=2.0)
            ctx.flow_arrow_v(352.0, 120.0, direction=-1, size=2.4)
            # PURGE di kanan riser x=352, bebas box FY-2201 (y 186..192) dan
            # bebas teks tag K-21B (x <= 349).
            ctx.text("PURGE", 356.5, 218.0, size=1.8, left=True)

        # --- 4.4 Discharge: check valve + PT/PI + TT/TI + fin-fan ---
        ctx.proc += pipe_run_h(Y, 270.0, 490.0, gaps=_gaps((415.0, 6.2)))
        ctx.proc += ctx.valve_check_h(415.0, Y, w=10.0, h=6.0)
        ctx.text(f"CV-21{sfx}", 415.0, Y + 11.0, size=1.8)
        for wx, (tt, tl) in zip(wells_dis,
                                (("PT", tag_ptd), ("PI", tag_pid), ("TT", tag_ttd))):
            ctx.proc += [line(wx, Y, wx, Y + 10.0)]
            ctx.sym += ctx.bubble(wx, Y + 16.0, tt, tl)
        ctx.sig += dashed(wells_dis[2], Y + 22.0, wells_dis[2], Y + 24.5)
        ctx.sym += ctx.dcs(wells_dis[2], Y + 32.0, "TI", tag_ttd)
        ctx.text(ln_dis, 445.0 if sfx == "A" else 505.0, Y - 6.5, size=1.8)
        for ax in (391.0, 427.0, 480.0):
            ctx.flow_arrow_h(ax, Y, direction=1, size=2.0)

        ctx.fin_fan_cooler(510.0, Y, tag=f"E-21{sfx}", tee_dx=20.0)
        ctx.text(f"E-21{sfx} AFTERCOOLER (FIN-FAN)", 510.0, Y + 57.0, size=2.5)
        # TT outlet -> TIC -> auto louver (dashed)
        ctx.proc += pipe_run_h(Y, 530.0, dx_leg)
        ctx.proc += [line(548.0, Y, 548.0, Y + 10.0)]
        ctx.sym += ctx.bubble(548.0, Y + 16.0, "TT", loop)
        ctx.sig += dashed(548.0, Y + 22.0, 548.0, Y + 24.5)
        ctx.sym += ctx.dcs(548.0, Y + 32.0, "TIC", loop)
        ctx.sig += dashed(540.5, Y + 32.0, 521.0, Y + 32.0)
        ctx.flow_arrow_h(542.5, Y, direction=1, size=2.0)
        ctx.flow_arrow_v(dx_leg, 400.0 if sfx == "A" else 290.0,
                         direction=-1, size=2.4)

        # --- 4.5 Spill-back capacity control ---
        ctx.proc += pipe_run_v(537.0, sb_y, Y)
        ctx.proc += pipe_run_h(sb_y, 194.0, 537.0, gaps=_gaps((fv_x, 6.2)))
        ctx.proc += pipe_run_v(194.0, sb_y, Y)
        ctx.proc += ctx.control_valve_h(fv_x, sb_y, w=10.0, h=6.0, tag=f"FV-{loop}")
        ctx.sym += rect(fv_x - 4.0, sb_y + 16.0, fv_x + 4.0, sb_y + 22.0)
        ctx.text("FY", fv_x, sb_y + 20.0, size=1.8)
        ctx.text(loop, fv_x, sb_y + 17.4, size=1.8)
        ctx.sigp += pneu(fv_x, sb_y + 16.0, fv_x, sb_y + 12.5, spacing=3.0)
        ctx.text(f"FV-{loop}", fv_x, sb_y - 10.0, size=1.8)
        ctx.text("FC", fv_x, sb_y - 14.5, size=1.8)
        lbl_x = 254.0 if sfx == "A" else 282.0
        ctx.text("CAPACITY CONTROL (SPILL-BACK)", lbl_x, sb_y + 6.0, size=1.8)
        ctx.text(ln_sb, lbl_x, sb_y - 6.0, size=1.8)
        ctx.flow_arrow_v(537.0, sb_y + 35.0, direction=-1, size=2.4)
        ctx.flow_arrow_h(480.0, sb_y, direction=-1, size=2.4)
        ctx.flow_arrow_h(280.0, sb_y, direction=-1, size=2.4)
        ctx.flow_arrow_v(194.0, sb_y + 40.0, direction=1, size=2.4)

        # --- 4.6 BDV suction & discharge ke BD header ---
        bdv_sx = 112.0 if sfx == "A" else 141.0
        bdv_svy = 155.0 if sfx == "A" else 185.0
        brk_s = [(240.0, BRK)] if sfx == "A" else []
        ctx.proc += pipe_run_v(bdv_sx, BD_Y, Y,
                               gaps=_gaps(*brk_s, (bdv_svy, 5.0)))
        ctx.proc += ctx.valve_gate_v(bdv_sx, bdv_svy, w=6.0, h=10.0, nc=True,
                                     flanged=False, tag=f"BDV-21{sfx}1")
        ctx.text(f"BDV-21{sfx}1", bdv_sx + 8.0, bdv_svy, size=1.8, left=True)
        ctx.text("NC", bdv_sx + 8.0, bdv_svy - 4.7, size=1.8, left=True)
        if sfx == "A":
            ctx.flow_arrow_v(bdv_sx, 300.0, direction=-1, size=2.4)
            ctx.flow_arrow_v(bdv_sx, 200.0, direction=-1, size=2.4)
            ctx.flow_arrow_v(bdv_sx, 130.0, direction=-1, size=2.4)
        else:
            ctx.flow_arrow_v(bdv_sx, 215.0, direction=-1, size=2.4)
            ctx.flow_arrow_v(bdv_sx, 130.0, direction=-1, size=2.4)

        bdv_dx = 400.0 if sfx == "A" else 458.0
        bdv_dvy = 135.0 if sfx == "A" else 150.0
        brk_d = [(390.0, BRK), (240.0, BRK), (170.0, BRK)] if sfx == "A" \
            else [(170.0, BRK)]
        ctx.proc += pipe_run_v(bdv_dx, BD_Y, Y,
                               gaps=_gaps(*brk_d, (bdv_dvy, 5.0)))
        ctx.proc += ctx.valve_gate_v(bdv_dx, bdv_dvy, w=6.0, h=10.0, nc=True,
                                     flanged=False, tag=f"BDV-21{sfx}2")
        ctx.text(f"BDV-21{sfx}2", bdv_dx + 8.0, bdv_dvy, size=1.8, left=True)
        ctx.text("NC", bdv_dx + 8.0, bdv_dvy - 4.7, size=1.8, left=True)
        if sfx == "A":
            ctx.flow_arrow_v(bdv_dx, 435.0, direction=-1, size=2.4)
            ctx.flow_arrow_v(bdv_dx, 300.0, direction=-1, size=2.4)
            ctx.flow_arrow_v(bdv_dx, 200.0, direction=-1, size=2.4)
            ctx.flow_arrow_v(bdv_dx, 110.0, direction=-1, size=2.4)
        else:
            ctx.flow_arrow_v(bdv_dx, 220.0, direction=-1, size=2.4)
            ctx.flow_arrow_v(bdv_dx, 110.0, direction=-1, size=2.4)

    # --- 4.7 Sinyal SIS scrubber A -> ESD-2 (rute atas, break di 85/243) ---
    ctx.sig += dashed(290.0, 479.0, 290.0, 558.0)
    ctx.sig += dashed_brk(52.0, 558.0, 290.0, 558.0, brk=[33.0, 191.0])
    ctx.sig += dashed(52.0, 558.0, 52.0, 552.0)

    # =========================================================================
    # 5. REGISTRI LINE & EXPORT MANIFEST
    # =========================================================================
    ctx.register_line("150-NG-9001", spec="150# A1A", service="Suction header", dn=150)
    ctx.register_line("150-NG-9002", spec="150# A1A", service="Suction train A", dn=150)
    ctx.register_line("150-NG-9003", spec="150# A1A", service="Suction train B", dn=150)
    ctx.register_line("100-NG-9011", spec="300# B1A", service="Discharge train A", dn=100)
    ctx.register_line("100-NG-9012", spec="300# B1A", service="Discharge train B", dn=100)
    ctx.register_line("150-NG-9010", spec="300# B1A", service="Discharge header", dn=150)
    ctx.register_line("100-NG-9021", spec="300# B1A", service="Spill-back train A", dn=100)
    ctx.register_line("100-NG-9022", spec="300# B1A", service="Spill-back train B", dn=100)
    ctx.register_line("080-FL-9031", spec="150# A1A", service="BD/flare header", dn=80)

    out_json = Path(__file__).resolve().parent / "pid_recip_booster.texts.json"
    layers = ctx.export_manifest(out_json)
    return layers


if __name__ == "__main__":
    pid_recip_booster()
