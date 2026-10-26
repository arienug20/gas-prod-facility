"""Export multi-sheet isometric DXF (Rev A6) without POLYFACE 3D mesh.

GPF-00-PI-ISO-0007 SHT 1 - 3 Rev A6:
- 3 Paper Space Layouts ("SHEET 1 OF 3", "SHEET 2 OF 3", "SHEET 3 OF 3")
- Modelspace: 3 sheets arranged side-by-side at X = 0, 500, 1000 mm
- 2D Viewport per layout pointing to corresponding sheet in Modelspace
- 100% 2D vector geometry (MTEXT + DIMENSION + SOLID + Lineweights)
- File size < 500 KB (POLYFACE = 0)

Usage:
  cd ~/gas-prod-facility && uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.21 python src/export_iso_sheet_dxf.py
"""
from __future__ import annotations

import os
from pathlib import Path
import ezdxf
from ezdxf.addons.importer import Importer
from cadgen.drawing_checks import validate_dxf_file

OUT_PATH = "cad/GPF-00-PI-ISO-0007 SHT 1 - 3.dxf"

SHEETS = [
    ("SHEET 1 OF 3", "cad/iso_go1002.dxf", 0.0),
    ("SHEET 2 OF 3", "cad/iso_co1003.dxf", 500.0),
    ("SHEET 3 OF 3", "cad/iso_co1004.dxf", 1000.0),
]


def round_coordinates(e, ndigits: int = 2) -> None:
    """Trim excessive floating point precision to optimize DXF file size."""
    k = e.dxftype()
    if k == "LINE":
        e.dxf.start = (round(e.dxf.start.x, ndigits), round(e.dxf.start.y, ndigits), 0.0)
        e.dxf.end = (round(e.dxf.end.x, ndigits), round(e.dxf.end.y, ndigits), 0.0)
    elif k == "CIRCLE":
        e.dxf.center = (round(e.dxf.center.x, ndigits), round(e.dxf.center.y, ndigits), 0.0)
        e.dxf.radius = round(e.dxf.radius, ndigits)
    elif k == "MTEXT":
        e.dxf.insert = (round(e.dxf.insert.x, ndigits), round(e.dxf.insert.y, ndigits), 0.0)
    elif k == "SOLID":
        e.dxf.vtx0 = (round(e.dxf.vtx0.x, ndigits), round(e.dxf.vtx0.y, ndigits), 0.0)
        e.dxf.vtx1 = (round(e.dxf.vtx1.x, ndigits), round(e.dxf.vtx1.y, ndigits), 0.0)
        e.dxf.vtx2 = (round(e.dxf.vtx2.x, ndigits), round(e.dxf.vtx2.y, ndigits), 0.0)
        e.dxf.vtx3 = (round(e.dxf.vtx3.x, ndigits), round(e.dxf.vtx3.y, ndigits), 0.0)
    elif k == "DIMENSION":
        for attr in ("defpoint", "defpoint2", "defpoint3", "defpoint4", "text_midpoint"):
            if e.dxf.hasattr(attr):
                val = e.dxf.get(attr)
                e.dxf.set(attr, (round(val.x, ndigits), round(val.y, ndigits), 0.0))


def main() -> int:
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 4  # mm
    doc.layers.add("VIEWPORTS", color=7)

    msp = doc.modelspace()

    for name, src_path, off_x in SHEETS:
        if not Path(src_path).exists():
            raise FileNotFoundError(f"Source drawing not found: {src_path}")
        src = ezdxf.readfile(src_path)

        # 1. Paper Space Layout
        lay = doc.layouts.new(name)
        lay.page_setup(size=(420.0, 297.0), margins=(0, 0, 0, 0), units="mm")
        imp_lay = Importer(src, doc)
        imp_lay.import_entities(src.modelspace(), lay)
        imp_lay.finalize()

        # 2. 2D Viewport in layout pointing to Modelspace offset
        lay.add_viewport(
            center=(210.0, 148.5),
            size=(420.0, 297.0),
            view_center_point=(off_x + 210.0, 148.5),
            view_height=297.0,
            dxfattribs={"layer": "VIEWPORTS", "status": 1}
        )

        # 3. Model Space (arranged side-by-side)
        n_before = len(msp)
        imp_msp = Importer(src, doc)
        imp_msp.import_entities(src.modelspace(), msp)
        imp_msp.finalize()
        if off_x != 0.0:
            for e in list(msp)[n_before:]:
                e.translate(off_x, 0.0, 0.0)

    # Remove default unused layout
    if "Layout1" in doc.layouts:
        doc.layouts.delete("Layout1")

    # Round floating point precision to keep file size well under 500 KB
    for lay in doc.layouts:
        for e in lay:
            round_coordinates(e, ndigits=2)
    for blk in doc.blocks:
        for e in blk:
            round_coordinates(e, ndigits=2)

    doc.saveas(OUT_PATH)

    # Verification and Statistics
    chk = ezdxf.readfile(OUT_PATH)
    msp_chk = chk.modelspace()
    poly_count = len(msp_chk.query("POLYFACE"))
    mtext_total = len(msp_chk.query("MTEXT"))
    dim_total = len(msp_chk.query("DIMENSION"))
    solid_total = len(msp_chk.query("SOLID"))
    vp_total = sum(len(lay.query("VIEWPORT")) for lay in chk.layouts if lay.name != "Model")
    sheet_count = len([l for l in chk.layouts if l.name != "Model"])
    sz_bytes = os.path.getsize(OUT_PATH)

    print(f"Exported: {OUT_PATH}")
    print(f"  Sheets (layouts): {sheet_count} (plus Modelspace)")
    print(f"  Modelspace entities: {len(msp_chk)}")
    print(f"  MTEXT: {mtext_total}, DIMENSION: {dim_total}, SOLID: {solid_total}, VIEWPORTS: {vp_total}")
    print(f"  POLYFACE count: {poly_count} (target = 0)")
    print(f"  File size: {sz_bytes} bytes ({sz_bytes / 1024:.1f} KB, target < 500 KB)")

    findings = validate_dxf_file(OUT_PATH)
    errors = [f for f in findings if f.severity == "error"]
    print(f"  Validation findings: {len(findings)} total, {len(errors)} errors")
    for f in errors:
        print("    ", f.render())

    return 0 if not errors and poly_count == 0 and sz_bytes < 500 * 1024 else 1


if __name__ == "__main__":
    raise SystemExit(main())
