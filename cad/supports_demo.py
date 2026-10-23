"""PIPE SUPPORT & INSULATION STANDARD — GPF-00-PI-STD-0018 Rev A0.

Sheet A3 (420 x 297 mm), origin kiri-bawah.
Blueprint: dokumen/08-plan-pipeline-metering-lbcv-underground.md Bagian V.2-V.3.
Isi:
  1. Tabel katalog 8 tipe pipe support (kode, simbol isometrik, simbol plan,
     fungsi / derajat kebebasan) — MSS SP-58 & ASME B31.3.
  2. Tabel standar shoe height (SH-0/100/150/200 vs ketebalan insulasi)
     + sketsa sepatu pada pipa terinsulasi.
  3. Legend kode kelas insulasi PP/HC/CC/AC/ET/ST + simbol P&ID garis
     selubung ganda berlabel [PP-50] & [ET-HC-40] + simbol batas insulasi
     isometrik (chain line) — ISO 12241 / ASTM C585.

Rantai build (company standard):
  python cad/supports_demo.py --force
  python cad/apply_text.py cad/supports_demo.dxf cad/supports_demo.texts.json
  python cad/validate_cad_rules.py cad/supports_demo.dxf cad/supports_demo.texts.json
  cadgen dxf snapshot cad/supports_demo.dxf cad/supports_demo.png
"""

from __future__ import annotations

from pathlib import Path

from cadgen import dxf

from pid_common import arc as circle_arc, circle
from supports_insulation_common import (
    INSULATION_CLASSES,
    SHOE_HEIGHTS,
    SUPPORT_CATALOG,
    SupInsContext,
    chain_line as si_chain_line,
    line,
    rect,
)


@dxf
def supports_demo():
    ctx = SupInsContext()

    # -------------------------------------------------------------------------
    # 1. FURNITUR LEMBAR A3
    # -------------------------------------------------------------------------
    notes = [
        "1. SUPPORT TYPES PER MSS SP-58 & ASME B31.3.",
        "2. SHOE HEIGHT PER INSULATION THICKNESS (TABLE).",
        "3. INSULATION CLASSES PER ISO 12241 / ASTM C585.",
        "4. MIN. CLEARANCE 100 MM FROM OUTER CLADDING.",
        "5. ISO BOM: INSULATED AREA (M2) + TRACING (M).",
        "6. THIS STANDARD SHEET IS NOT TO SCALE.",
    ]
    ref_docs = [
        ("GPF-00-DB-0001", "DESIGN BASIS"),
        ("GPF-00-PI-PID-0001", "P&ID SEPARATOR V-101"),
        ("GPF-00-PM-PLN-0008", "DEVELOPMENT ROADMAP REV A2"),
    ]
    ctx.setup_a3_furniture(
        doc_no="GPF-00-PI-STD-0018",
        title_lines=["PIPE SUPPORT &", "INSULATION STANDARD"],
        notes=notes,
        ref_docs=ref_docs,
    )

    # --- Legenda kolom kanan (simbol contoh, y = 226..193 step 11) ---
    lg = [
        (226.0, "PIPE SUPPORT (ISO SYMBOL)"),
        (215.0, "PIPE SUPPORT (PLAN SYMBOL)"),
        (204.0, "INSULATION JACKET [CLASS-THK]"),
        (193.0, "INSULATION BREAK (CHAIN LINE)"),
    ]
    # 1. Iso support: resting di atas stub pipa
    ctx.sym += [line(340.0, lg[0][0], 362.0, lg[0][0])]
    ctx.iso_res(351.0, lg[0][0])
    ctx.text(lg[0][1], 366.0, lg[0][0], size=1.5, left=True)
    # 2. Plan support: anchor di atas stub pipa
    ctx.sym += [line(340.0, lg[1][0], 362.0, lg[1][0])]
    ctx.plan_anc(351.0, lg[1][0])
    ctx.text(lg[1][1], 366.0, lg[1][0], size=1.5, left=True)
    # 3. Jacket insulasi mini
    ctx.pid_insulation_jacket(340.0, 362.0, lg[2][0], cls="PP", thk_mm=50,
                              label_dy=3.6, jacket_half=1.8)
    ctx.text(lg[2][1], 366.0, lg[2][0], size=1.5, left=True)
    # 4. Chain line batas insulasi mini
    ctx.sym += [line(340.0, lg[3][0], 362.0, lg[3][0])]
    ctx.sym += si_chain_line(351.0, lg[3][0] - 3.4, 351.0, lg[3][0] + 3.4)
    ctx.text(lg[3][1], 366.0, lg[3][0], size=1.5, left=True)

    # -------------------------------------------------------------------------
    # 2. TABEL KATALOG 8 TIPE SUPPORT (x = 12..330, y = 164..288)
    # -------------------------------------------------------------------------
    tx0, tx1 = 12.0, 330.0
    ty_top, ty_bot = 288.0, 164.0
    col_code, col_iso, col_plan = 42.0, 100.0, 160.0
    ctx.frame += rect(tx0, ty_bot, tx1, ty_top)
    ctx.frame.append(line(tx0, 280.0, tx1, 280.0))
    for cx_ in (col_code, col_iso, col_plan):
        ctx.frame.append(line(cx_, ty_bot, cx_, ty_top))
    ctx.text("CODE", 27.0, 283.5, size=2.0)
    ctx.text("ISO SYMBOL", 71.0, 283.5, size=2.0)
    ctx.text("PLAN SYMBOL", 130.0, 283.5, size=2.0)
    ctx.text("TYPE / FUNCTION - DEGREES OF FREEDOM", 245.0, 283.5, size=2.0)

    row_h = 14.5
    for i, item in enumerate(SUPPORT_CATALOG):
        ry = 280.0 - (i + 0.5) * row_h
        if i > 0:
            ctx.frame.append(line(tx0, 280.0 - i * row_h, tx1, 280.0 - i * row_h))
        ctx.text(item["code"], 27.0, ry + 2.4, size=2.5)
        ctx.text(item["name"], 27.0, ry - 2.6, size=1.4)
        # Stub pipa contoh pada sel simbol; VSP/CSP/TRN plan menggantikan pipa
        if item["code"] != "TRN":
            ctx.sym += [line(62.0, ry, 80.0, ry)]
        if item["code"] not in ("TRN", "VSP", "CSP"):
            ctx.sym += [line(119.0, ry, 141.0, ry)]
        # Simbol isometrik
        ctx.draw_iso_support(item["code"], 71.0, ry)
        # Simbol plan
        ctx.draw_plan_support(item["code"], 130.0, ry)
        # Fungsi / derajat kebebasan
        ctx.text(item["func"], 164.0, ry, size=1.6, left=True)

    # -------------------------------------------------------------------------
    # 3. TABEL SHOE HEIGHT (x = 12..160, y = 108..150) + SKETSA SEPATU
    # -------------------------------------------------------------------------
    ctx.frame += rect(12.0, 108.0, 160.0, 150.0)
    ctx.frame.append(line(12.0, 143.0, 160.0, 143.0))
    ctx.frame.append(line(60.0, 108.0, 60.0, 143.0))
    ctx.frame.append(line(132.0, 108.0, 132.0, 143.0))
    ctx.text("PIPE SHOE HEIGHT (SH) SELECTION", 86.0, 146.5, size=2.0)
    ctx.text("SH CODE", 36.0, 140.2, size=1.8)
    ctx.text("INSULATION THICKNESS", 96.0, 140.2, size=1.8)
    ctx.text("SH", 146.0, 140.2, size=1.8)
    ry = 134.9
    for code, desc, sh in SHOE_HEIGHTS:
        ctx.text(code, 36.0, ry, size=1.8)
        ctx.text(desc, 64.0, ry, size=1.8, left=True)
        ctx.text(f"{sh} MM", 146.0, ry, size=1.8)
        ry -= 7.0

    # Sketsa sepatu pada pipa terinsulasi (x = 175..330, y = 108..150)
    ctx.frame += rect(175.0, 108.0, 330.0, 150.0)
    ctx.text("TYPICAL SHOE ON INSULATED PIPE", 252.5, 146.5, size=2.0)
    sx, sy = 235.0, 128.0
    ctx.sym += [
        # base + shoe
        line(sx - 22.0, 112.0, sx + 22.0, 112.0),
        line(sx - 7.0, 121.4, sx - 9.0, 112.0),
        line(sx + 7.0, 121.4, sx + 9.0, 112.0),
        line(sx - 7.0, 121.4, sx + 7.0, 121.4),
        # pipa
        line(sx - 11.0, sy, sx + 11.0, sy),
    ]
    ctx.sym.append(circle(sx, sy, 6.6))
    # insulasi: arc atas putus-putus (tidak menembus sepatu di bawah pipa)
    for a in range(12, 169, 22):
        ctx.sym.append(circle_arc(sx, sy, 9.4, a, a + 13))
    ctx.sym += [
        line(sx + 9.4, sy + 3.4, sx + 30.0, sy + 12.0),
        line(sx + 30.0, sy + 12.0, sx + 52.0, sy + 12.0),
    ]
    ctx.text("INSULATION", sx + 31.0, sy + 14.6, size=1.8, left=True)
    ctx.dimrec((sx + 16.0, 121.4), (sx + 16.0, 112.0), "SH", angle=90.0,
               base=(sx + 24.0, 121.4))
    ctx.sym += [line(sx + 9.0, 112.0, sx + 24.0, 112.0)]
    ctx.text("WEAR PAD / SHOE", 196.0, 116.0, size=1.8, left=True)

    # -------------------------------------------------------------------------
    # 4. LEGEND KODE INSULASI + SIMBOL P&ID & ISO (x = 12..330, y = 12..100)
    # -------------------------------------------------------------------------
    ctx.frame += rect(12.0, 12.0, 330.0, 100.0)
    ctx.text("INSULATION CLASS CODES & SYMBOLS (ISO 12241 / ASTM C585)",
             171.0, 96.0, size=2.2)
    ctx.frame.append(line(12.0, 92.0, 140.0, 92.0))
    ctx.frame.append(line(40.0, 40.0, 40.0, 92.0))
    ctx.text("CODE", 26.0, 94.0, size=1.8)
    ctx.text("DESCRIPTION", 44.0, 94.0, size=1.8, left=True)
    ry = 85.0
    for code, desc in INSULATION_CLASSES:
        ctx.text(code, 26.0, ry, size=1.8)
        ctx.text(desc, 44.0, ry, size=1.8, left=True)
        ry -= 9.0

    # Sampel simbol P&ID: jacket [PP-50]
    ctx.pid_insulation_jacket(160.0, 250.0, 80.0, cls="PP", thk_mm=50)
    ctx.text("P&ID: INSULATION JACKET - [CLASS-THK]", 205.0, 72.0, size=1.8)
    # Sampel simbol P&ID: tracing [ET-HC-40]
    ctx.pid_insulation_jacket(160.0, 250.0, 58.0, cls="ET-HC", thk_mm=40)
    ctx.text("P&ID: ELECTRIC TRACING + HEAT CONSERVATION", 205.0, 50.0, size=1.8)
    # Sampel simbol iso: batas insulasi (chain line)
    ctx.iso_insulation_break(205.0, 30.0, label="INSULATION BREAK",
                             pipe_layer="REF-SYM")
    ctx.text("ISO: CHAIN LINE AT INSULATION LIMIT", 205.0, 19.5, size=1.8)

    # Simpan manifest + layer
    out_json = Path(__file__).resolve().parent / "supports_demo.texts.json"
    return ctx.export_manifest(out_json)


if __name__ == "__main__":
    supports_demo()
