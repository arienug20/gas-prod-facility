"""UNDERGROUND PIPING & TRENCH DETAIL — GPF-00-PI-PLN-0017 Rev A0.

Sheet A3 (420 x 297 mm), origin kiri-bawah.
Blueprint: dokumen/08-plan-pipeline-metering-lbcv-underground.md Bagian V.1.
Isi:
  1. TYPICAL TRENCH CROSS-SECTION terdimensi (cover 1.2 m per ASME B31.8,
     sand bedding 150 mm, sand padding, warning tape 500 BGL, backfill 95%
     Standard Proctor, native soil hatch).
  2. MINI PLAN jalur pipa bawah tanah: soil-to-air interface (puddle flange),
     Monolithic Isolation Joint, CP test post, cased road crossing API RP 1102
     (casing spacers + end seals + vent), panah aliran.

Rantai build (company standard):
  python cad/underground_demo.py --force
  python cad/apply_text.py cad/underground_demo.dxf cad/underground_demo.texts.json
  python cad/validate_cad_rules.py cad/underground_demo.dxf cad/underground_demo.texts.json
  cadgen dxf snapshot cad/underground_demo.dxf cad/underground_demo.png

Catatan: design basis (GPF-00-DB-0001) tidak mendefinisikan line transmisi
bawah tanah — jalur pada plan mini diberi label TYPICAL (deviasi tercatat).
"""

from __future__ import annotations

from pathlib import Path

from cadgen import dxf

from underground_common import (
    UG_PEN,
    UndergroundContext,
    circle,
    line,
    rect,
)


@dxf
def underground_demo():
    ctx = UndergroundContext()

    # -------------------------------------------------------------------------
    # 1. FURNITUR LEMBAR A3 (border, grid, NOTES, LEGEND, REF DOC, REV, TITLE)
    # -------------------------------------------------------------------------
    notes = [
        "1. UG PROCESS LINE REF-PROC-UG DASHED 0.35 MM.",
        "2. COVER 1.0-1.2 M ASME B31.8; 1.5 M ROAD XING.",
        "3. SAND BEDDING 150 MM + PADDING; TAPE 300-500 BGL.",
        "4. BACKFILL COMPACTED TO 95% STD. PROCTOR.",
        "5. CASED CROSSING API RP 1102 - SPACERS/SEALS/VENT.",
        "6. MIJ + CP TEST POST PER NACE SP0169.",
        "7. TYPICAL DETAIL - NTS. DIMENSIONS IN MM.",
    ]
    ref_docs = [
        ("GPF-00-DB-0001", "DESIGN BASIS"),
        ("GPF-00-PI-PID-0001", "P&ID SEPARATOR V-101"),
        ("GPF-00-PM-PLN-0008", "DEVELOPMENT ROADMAP REV A2"),
    ]
    legend = ctx.setup_a3_furniture(
        doc_no="GPF-00-PI-PLN-0017",
        title_lines=["UNDERGROUND PIPING &", "TRENCH DETAIL"],
        notes=notes,
        ref_docs=ref_docs,
    )

    # --- Legenda kolom kanan (simbol contoh, y = 224..171.5 step 7.5) ---
    rows = [224.0, 216.5, 209.0, 201.5, 194.0, 186.5, 179.0, 171.5]
    # 1. UG process line (dashed)
    ctx.ug_segment((340.0, rows[0]), (362.0, rows[0]))
    ctx.text("UG PROCESS LINE (DASHED)", 366.0, rows[0], size=1.5, left=True)
    # 2. Above-ground process line + flow arrow
    ctx.sym += [line(340.0, rows[1], 362.0, rows[1])]
    ctx.solid_triangle((358.0, rows[1]), (352.0, rows[1] + 1.5), (352.0, rows[1] - 1.5),
                       layer="REF-SYM")
    ctx.text("ABOVE-GROUND PROCESS LINE", 366.0, rows[1], size=1.5, left=True)
    # 3. MIJ
    ctx.mij_plan(351.0, rows[2], w=4.0, h=6.0, tag="")
    ctx.text("MONOLITHIC ISOLATION JOINT", 366.0, rows[2], size=1.5, left=True)
    # 4. Puddle flange
    ctx.puddle_flange_plan(351.0, rows[3], r_out=3.6, r_in=2.0)
    ctx.sym += [line(347.0, rows[3], 355.0, rows[3])]
    ctx.text("SOIL-TO-AIR INTERFACE (PUDDLE FLANGE)", 366.0, rows[3], size=1.5, left=True)
    # 5. CP test post
    ctx.sym += [rect(348.0, rows[4] - 1.8, 354.0, rows[4] + 1.8)]
    ctx.text("CP TEST POST (NACE SP0169)", 366.0, rows[4], size=1.5, left=True)
    # 6. Cased crossing
    ctx.sym += [
        line(340.0, rows[5] - 2.0, 362.0, rows[5] - 2.0),
        line(340.0, rows[5] + 2.0, 362.0, rows[5] + 2.0),
    ]
    ctx.solid_quad((340.0, rows[5] - 2.0), (341.6, rows[5] - 2.0),
                   (341.6, rows[5] + 2.0), (340.0, rows[5] + 2.0), layer="REF-SYM")
    ctx.text("CASED CROSSING (API RP 1102)", 366.0, rows[5], size=1.5, left=True)
    # 7. Vent
    ctx.sym += [line(351.0, rows[6] - 3.0, 351.0, rows[6] + 2.0)]
    ctx.sym += [circle(351.0, rows[6] + 3.6, 1.4)]
    ctx.text("CASING VENT PIPE", 366.0, rows[6], size=1.5, left=True)
    # 8. Warning tape
    ctx.sym += [
        line(340.0, rows[7] - 0.7, 362.0, rows[7] - 0.7),
        line(340.0, rows[7] + 0.7, 362.0, rows[7] + 0.7),
    ]
    ctx.text("WARNING TAPE (300-500 MM BGL)", 366.0, rows[7], size=1.5, left=True)

    # -------------------------------------------------------------------------
    # 2. TYPICAL TRENCH CROSS-SECTION TERDIMENSI (y = 155..290)
    # -------------------------------------------------------------------------
    ctx.trench_cross_section(
        x_cl=171.0, y_grade=272.0, x_min=12.0, x_max=330.0, y_min=190.0,
        scale=50.0, cover_m=1.2, pipe_od_mm=168.0, bedding_mm=150.0,
        pad_side_m=0.20, pad_top_m=0.20, tape_below_m=0.50,
        bottom_w_m=1.20, side_slope=1.0,
        pipe_label="DN150 CARRIER PIPE (3LPE)",
    )
    ctx.text("TYPICAL TRENCH CROSS-SECTION", 171.0, 163.0, size=2.8)
    ctx.text("DIMENSIONS IN MM - TYPICAL DETAIL", 171.0, 159.0, size=1.8)
    ctx.text("COVER MIN. 1.5 M AT ROAD CROSSING (API RP 1102)", 171.0, 155.4,
             size=1.8)

    # -------------------------------------------------------------------------
    # 3. MINI PLAN — TYPICAL UNDERGROUND ROUTE (y = 25..150)
    # -------------------------------------------------------------------------
    ctx.frame += rect(12.0, 25.0, 330.0, 150.0)
    ctx.text("MINI PLAN - TYPICAL UNDERGROUND ROUTE (NTS)", 171.0, 145.0, size=2.6)

    ry = 95.0  # sumbu rute
    # Battery limit kiri + label
    ctx.sym += [
        line(20.0, ry - 3.5, 20.0, ry + 3.5),
        line(20.0, ry - 3.5, 28.0, ry),
        line(28.0, ry, 20.0, ry + 3.5),
    ]
    ctx.text("FROM FACILITY / ABOVE GROUND", 14.0, 86.5, size=1.8, left=True)

    # Di atas tanah (REF-PROC) sampai soil-to-air interface
    ctx.proc.append(line(28.0, ry, 52.0, ry))
    ctx.flow_arrow_h(38.0, ry, direction=1, layer="REF-PROC")

    # Soil-to-air interface: puddle flange (cincin ganda)
    ctx.puddle_flange_plan(55.0, ry, r_out=5.0, r_in=3.0)
    ctx.sym += [
        line(55.0, ry + 5.0, 55.0, ry + 13.0),
        line(55.0, ry + 13.0, 77.0, ry + 13.0),
    ]
    ctx.text("SOIL-TO-AIR INTERFACE", 56.0, ry + 15.8, size=1.8, left=True)
    ctx.text("PUDDLE FLANGE (WATER STOP)", 56.0, ry + 10.6, size=1.8, left=True)

    # Rute bawah tanah (dashed REF-PROC-UG) dengan break di kedua MIJ
    ctx.ug_pipe_run_h(ry, 58.0, 293.0, breaks=[(66.0, 3.0)])
    ctx.ug_pipe_run_h(ry, 299.0, 301.5)
    ctx.flow_arrow_h(95.0, ry, direction=1, layer="REF-PROC-UG")
    ctx.flow_arrow_h(145.0, ry, direction=1, layer="REF-PROC-UG")
    ctx.flow_arrow_h(280.0, ry, direction=1, layer="REF-PROC-UG")

    # MIJ-01 di batas tanah/udara pemutus arus proteksi katodik
    ctx.mij_plan(66.0, ry, tag="MIJ-01", tag_dy=-9.5)

    # CP test post
    ctx.cp_test_post(110.0, ry, tag="TP-01", dy=6.0, shelf_len=22.0)

    # Label line typical
    ctx.text("TYP. UG LINE -\nSEE PIPELINE LINE INDEX", 148.0, ry + 9.0, size=1.8)
    ctx.text("UG ROUTE BCL EL. -1.200 (TYP.)", 145.0, 70.0, size=1.8)

    # Cased road crossing (casing + spacers + end seals + vent) & band jalan
    ctx.cased_road_crossing(
        cx=215.0, cy=ry, half_len=50.0, casing_half=3.0, spacer_step=12.0,
        vent=True, vent_dx=-47.0, vent_h=12.0,
        label="CASED ROAD CROSSING (API RP 1102)", label_dy=-11.5,
    )
    ctx.road_band(176.0, 254.0, 55.0, 135.0, label="")
    ctx.text("ACCESS ROAD", 219.0, 70.0, size=1.8, rot=90.0)

    # Soil-to-air interface kedua + MIJ-02 + battery limit kanan
    ctx.puddle_flange_plan(296.0, ry, r_out=5.0, r_in=3.0)
    ctx.mij_plan(304.5, ry, tag="MIJ-02", tag_dy=-9.5)
    ctx.proc.append(line(306.0, ry, 320.0, ry))
    ctx.flow_arrow_h(313.0, ry, direction=1, layer="REF-PROC")
    ctx.sym += [
        line(320.0, ry - 3.5, 320.0, ry + 3.5),
        line(320.0, ry - 3.5, 328.0, ry),
        line(328.0, ry, 320.0, ry + 3.5),
    ]
    ctx.text("TO PIPELINE", 313.0, 80.0, size=1.8)

    # Simpan manifest TEXTS/DIMS/SOLIDS + layer
    out_json = Path(__file__).resolve().parent / "underground_demo.texts.json"
    return ctx.export_manifest(out_json)


if __name__ == "__main__":
    underground_demo()
    _dxf = Path(__file__).resolve().parent / "underground_demo.dxf"
    # REF-PROC-UG 0.35 mm (Bagian V.1) — di luar PENS apply_text.py
    print(f"stamped REF-PROC-UG pen={UG_PEN} on {_dxf.name}")
