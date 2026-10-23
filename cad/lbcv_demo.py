"""P&ID GPF-00-PI-PID-0016 Rev A0 — LINE BREAK VALVE STATION.

Sheet A1 (841 x 594 mm), origin kiri-bawah.
Station katup pengaman pipa transmisi gas (ASME B31.8 / API SPEC 6D):
  - MLV ball valve trunnion mounted full-bore PIG-able, body buried,
    stem extension 1.5-2.5 m
  - Aktuator gas-over-oil fail-close otonom (tanpa listrik eksternal)
  - Line break pilot dP/dt (set > 0.5 bar/menit)
  - Emergency hand pump (re-open darurat)
  - Bypass equalizing DN80 dengan 2 katup NC
  - Blowdown stack ganda hulu & hilir dengan katup penutup ganda
  - PT/PI tiap sisi MLV

Standar acuan:
  - ANSI/ISA-5.1-2024 (Instrumentation Symbols and Identification)
  - ISO 10628-2:2012 (Graphical symbols)
  - API SPEC 6D / API RP 1130 / ASME B31.8 & B31.4
  - Referensi perusahaan: SSY-PRO-PID-002 & SSY-PRO-PID-003

Layers:
  REF-FRAME  border lembar, grid referensi, kotak tabel furniture
  REF-TITLE  title block + rev table (ISO 7200 / Company Standard)
  REF-EQUIP  aktuator, stem extension, garis muka tanah
  REF-PROC   line proses, MLV, katup, bypass, blowdown, tap instrumen
  REF-SYM    kotak pilot line break, hand pump, bubble instrumen, legend
  REF-SIG    sinyal sensing pilot (dashed)
  REF-SIGP   konektor hidrolik hand pump
  REF-TEXT   ditulis post-build oleh apply_text.py dari manifest TEXTS (ARIAL)
"""

from __future__ import annotations

from pathlib import Path

from cadgen import dxf
from lbcv_common import LBCVContext
from pid_common import circle, dashed, line, rect


# =============================================================================
# MODEL UTAMA P&ID REV A0
# =============================================================================
@dxf
def lbcv_demo():
    ctx = LBCVContext()

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
        "1. MLV PER API SPEC 6D: BALL VALVE, TRUNNION MOUNTED, FULL BORE (PIG-ABLE).",
        "   MLV BODY BURIED WITH STEM EXTENSION 1.5 - 2.5 M TO GRADE LEVEL.",
        "2. ACTUATION: GAS-OVER-OIL. LINE PRESSURE GAS ACCUMULATOR DRIVES HYDRAULIC",
        "   CLOSING - FAIL-CLOSE WITHOUT EXTERNAL POWER.",
        "3. LINE BREAK PILOT (dP/dt): CLOSES MLV ON PRESSURE DROP > 0.5 BAR/MIN.",
        "4. EMERGENCY HAND PUMP PROVIDED TO RE-OPEN MLV AFTER PIPELINE INSPECTION.",
        "5. EQUALIZING BYPASS DN80 WITH TWO NC VALVES - EQUALIZE PRESSURE ACROSS MLV",
        "   BEFORE OPENING.",
        "6. BLOWDOWN STACKS U/S & D/S WITH DOUBLE BLOCK VALVES, SIZED PER API STD 521.",
        "7. PT/PI ON EACH SIDE OF MLV FOR STATION MONITORING AND PILOT SENSING.",
        "8. DESIGN CODES: ASME B31.8 (GAS) / ASME B31.4 (LIQUID), API RP 1130 (LPCM).",
        "9. INSTRUMENT SYMBOLS PER ANSI/ISA-5.1-2024; DIAGRAM PER ISO 10628-2:2012.",
        "10. SEE DESIGN BASIS GPF-00-DB-0001. ANY CONFLICT: DESIGN BASIS GOVERNS.",
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
    ctx.text("ELECTRIC SIGNAL (INSTRUMENT)", 690, 397, size=2.0, left=True)

    # Main Line Valve (ball trunnion)
    ctx.sym += ctx.ball_valve_mlv_h(672, 381, w=12, h=6)
    ctx.text("MAIN LINE VALVE (API 6D)", 690, 381, size=2.0, left=True)

    # Gas-over-oil actuator
    ctx.sym += rect(668, 361, 686, 369)
    ctx.sym.append(line(668, 365, 686, 365))
    ctx.text("GAS-OVER-OIL ACTUATOR", 690, 365, size=2.0, left=True)

    # Line break pilot
    ctx.sym += rect(668, 345, 684, 353)
    ctx.text("LINE BREAK PILOT (dP/dt)", 690, 349, size=2.0, left=True)

    # Emergency hand pump
    ctx.sym += rect(668, 329, 682, 337)
    ctx.text("EMERGENCY HAND PUMP", 690, 333, size=2.0, left=True)

    # Blowdown stack (double valve)
    ctx.sym += [
        line(672, 309, 672, 317),
        line(667, 317, 677, 317),
        line(669, 311.5, 675, 311.5),
        line(669, 314.5, 675, 314.5),
    ]
    ctx.text("BLOWDOWN STACK (DOUBLE VALVE)", 690, 313, size=2.0, left=True)

    # Equalizing bypass
    ctx.sym.append(line(664, 301, 680, 301))
    ctx.sym += ctx.valve_gate_h(672, 301, w=7, h=4.4, nc=True, flanged=False)
    ctx.text("EQUALIZING BYPASS (NORM. CLOSED)", 690, 301, size=2.0, left=True)

    # Grade line (buried)
    ctx.sym += dashed(664, 285, 684, 285)
    ctx.text("GRADE LINE (MLV BODY BURIED)", 690, 285, size=2.0, left=True)

    # Normally Closed Gate Valve
    ctx.sym += ctx.valve_gate_h(672, 269, w=8, h=5, nc=True, flanged=False)
    ctx.text("NC = NORMALLY CLOSED VALVE", 690, 269, size=2.0, left=True)

    # Field instrument
    ctx.sym.append(circle(672, 253, 5.0))
    ctx.sym.append(line(667, 253, 677, 253))
    ctx.text("FIELD INSTRUMENT", 690, 253, size=2.0, left=True)

    # Abbreviations
    ctx.text("STANDARD ABBREVIATIONS:", 659, 216, size=1.9, left=True)
    ctx.text("FC: FAIL CLOSED    | NC: NORMALLY CLOSED    | CSO: CAR-SEAL OPEN", 659, 206, size=1.8, left=True)
    ctx.text("MLV: MAIN LINE VALVE | BD: BLOWDOWN | HP: HAND PUMP | BP: BYPASS", 659, 197, size=1.8, left=True)
    ctx.text("U/S: UPSTREAM | D/S: DOWNSTREAM | dP/dt: RATE OF PRESSURE DROP", 659, 188, size=1.8, left=True)

    # --- 2.3 REFERENCE DOCUMENTS (y = 148..185) ---
    ctx.frame.append(line(655, 148, 823, 148))
    ctx.frame.append(line(655, 175, 823, 175))
    ctx.text("REFERENCE DOCUMENTS", 739, 180, size=2.2)
    ref_docs = [
        ("GPF-00-DB-0001", "DESIGN BASIS - GAS PRODUCTION FACILITY", 169.0),
        ("GPF-00-PM-PLN-0008", "ROADMAP - PIPELINE, METERING & LBCV (REV A2)", 163.5),
        ("GPF-00-PI-ISO-0007", "PIPING ISOMETRIC - TRANSMISSION PIPELINE", 158.0),
    ]
    for doc_no, doc_title, ry in ref_docs:
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
        ("A0", "ISSUED FOR REVIEW", "23 OCT 26", "PM", "", 118.6),
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
    ctx.text("GAS PRODUCTION FACILITY - ONSHORE FIELD", 739, 108.5, size=2.8)
    ctx.text("PM OIL & GAS SURFACE FACILITY", 739, 102.5, size=2.2)
    ctx.text("REKAYASA ENGINEERING", 739, 98.0, size=2.0)
    # Drawing title
    ctx.text("PIPING & INSTRUMENTATION DIAGRAM", 739, 87.0, size=2.8)
    ctx.text("LINE BREAK VALVE STATION", 739, 80.0, size=2.5)
    # Drawing number
    ctx.text("DRAWING NO:", 658, 70.0, size=1.8, left=True)
    ctx.text("GPF-00-PI-PID-0016", 739, 65.5, size=2.8)
    # Metadata rows
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
    # 3. TABEL DATA STATION DI BAGIAN ATAS (y = 515..573)
    # -------------------------------------------------------------------------
    # Tabel 1: Station Data (x = 135..375)
    ctx.equip += rect(135, 515, 375, 573)
    ctx.equip.append(line(135, 565, 375, 565))
    ctx.equip.append(line(228, 515, 228, 565))
    ctx.text("LINE BREAK VALVE STATION - STATION DATA", 255, 569, size=2.4)
    st_rows = [
        ("CODE / STANDARD", "ASME B31.8 (GAS) / API SPEC 6D", 561.0),
        ("LINE NO. (U/S - D/S)", "300-ML-7001 / 300-ML-7002", 553.0),
        ("SIZE / CLASS LOCATION", "DN600 / CLASS LOC. 2 (ASME B31.8)", 545.0),
        ("MLV TYPE", "BALL VALVE, TRUNNION, FULL BORE (PIG-ABLE)", 537.0),
        ("STEM EXTENSION", "1.5 - 2.5 M (BODY BURIED)", 529.0),
        ("DESIGN PRESS / TEMP", "99.0 BARG / 45 DEG C", 521.0),
    ]
    for k, (cap, val, ry) in enumerate(st_rows):
        if k > 0:
            ctx.equip.append(line(135, ry + 4.0, 375, ry + 4.0))
        ctx.text(cap, 138, ry, size=1.8, left=True)
        ctx.text(val, 232, ry, size=2.0, left=True)

    # Tabel 2: MLV Actuation & Protection Data (x = 395..635)
    ctx.equip += rect(395, 515, 635, 573)
    ctx.equip.append(line(395, 565, 635, 565))
    ctx.equip.append(line(488, 515, 488, 565))
    ctx.text("MLV ACTUATION & PROTECTION DATA", 515, 569, size=2.4)
    ac_rows = [
        ("ACTUATOR", "GAS-OVER-OIL, FAIL-CLOSE (AUTONOMOUS)", 561.0),
        ("LINE BREAK PILOT", "dP/dt SENSING, SET > 0.5 BAR/MIN", 553.0),
        ("HAND PUMP", "EMERGENCY RE-OPEN (HYDRAULIC)", 545.0),
        ("BYPASS", "DN80 EQUALIZING, 2 GLOBE VALVES NC", 537.0),
        ("BLOWDOWN", "STACKS U/S & D/S, DOUBLE BLOCK VALVE", 529.0),
        ("EXTERNAL POWER", "NONE - OPERATED BY LINE PRESSURE", 521.0),
    ]
    for k, (cap, val, ry) in enumerate(ac_rows):
        if k > 0:
            ctx.equip.append(line(395, ry + 4.0, 635, ry + 4.0))
        ctx.text(cap, 398, ry, size=1.8, left=True)
        ctx.text(val, 492, ry, size=2.0, left=True)

    # -------------------------------------------------------------------------
    # 4. STATION LBCV LENGKAP (garis utama y = 300, MLV di x = 250)
    # -------------------------------------------------------------------------
    # Battery limit kiri & kanan
    ctx.proc += ctx.continuity_box_left(
        300.0, "300-ML-7001 DN600", "FROM CUSTODY METERING STATION", "PER PIPELINE LINE LIST"
    )
    ctx.proc += ctx.continuity_box_right(
        300.0, "300-ML-7002 DN600", "TO SALES PIPELINE (DOWNSTREAM)", "PER PIPELINE LINE LIST"
    )
    ctx.lbcv_station_h(72.5, 585.0, 300.0)

    # -------------------------------------------------------------------------
    # 5. SIMPAN MANIFEST TEXTS & SOLIDS untuk cad/apply_text.py
    # -------------------------------------------------------------------------
    out_json = Path(__file__).resolve().parent / "lbcv_demo.texts.json"
    layers = ctx.export_manifest(out_json)
    return layers


if __name__ == "__main__":
    lbcv_demo()
