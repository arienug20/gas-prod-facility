"""Post-process: set lineweight per layer (company standard)."""
import sys

import ezdxf

from cadgen.drawing_checks import validate_dxf_file

PENS = {  # DXF lineweight = nilai mm x 100
    "REF-PROC": 50, "REF-EQUIP": 35, "REF-FRAME": 35, "REF-SYM": 25,
    "REF-TITLE": 25, "REF-TEXT": 18, "REF-ROAD": 18,
    "REF-SIG": 13, "REF-SIGP": 13, "REF-HATCH": 13, "REF-DIM": 13,
    "REF-FENCE": 13, "REF-GRID": 9,
}

for path in sys.argv[1:]:
    doc = ezdxf.readfile(path)
    for layer in doc.layers:
        if layer.dxf.name in PENS:
            layer.dxf.lineweight = PENS[layer.dxf.name]
    doc.saveas(path)
    errs = [f for f in validate_dxf_file(path) if f.severity == "error"]
    print(f"{path}: pens applied, errors={len(errs)}")
    for f in errs:
        print("  ", f.render())
