"""Company post-processor for engineering DXF drawings (MTEXT + DIMENSION + SOLID + pens).

Manifest JSON: EITHER a list of text entries (legacy) OR a dict:
  {
    "texts":  [{"t","x","y","h","rot","layer","att"}, ...],
    "dims":   [{"p1":[x,y],"p2":[x,y],"base":[x,y]|none,"angle":deg|0,
                "distance":mm(align mode),"text":"override|<>"}, ...],
    "solids": [{"pts":[[x,y],...3-4], "layer":"REF-SYM"}, ...]
  }

DIMENSION dibuat sebagai entity asli dengan dimstyle GPF-ISO:
closed filled arrow (dimasz=1.6), teks 2.0 aligned DI ATAS garis dimensi
(dimtad=1, dimtih/dimtoh=0), extension gap/overshoot 1.0, desimal 0 (mm).

Idempoten: MTEXT/DIMENSION(REF-DIM)/SOLID(REF-SYM) dari pass sebelumnya
dihapus dulu. Jalankan SETELAH setiap build.

Pemakaian: python apply_text.py <drawing>.dxf <drawing>.manifest.json
"""
import json
import sys
from pathlib import Path

import ezdxf

from cadgen.drawing_checks import validate_dxf_file

PENS = {  # DXF lineweight = mm x 100 (company standard)
    "REF-PROC": 50, "REF-EQUIP": 35, "REF-FRAME": 35, "REF-PROC-UG": 35, "REF-SYM": 25,
    "REF-TITLE": 25, "REF-TEXT": 18, "REF-ROAD": 18,
    "REF-SIG": 13, "REF-SIGP": 13, "REF-HATCH": 13, "REF-DIM": 9,
    "REF-FENCE": 13, "REF-GRID": 9,
}
ARIAL = "ARIAL"
DIMSTY = "GPF-ISO"


def ensure_dimstyle(doc) -> None:
    if DIMSTY in [d.dxf.name for d in doc.dimstyles]:
        return
    ds = doc.dimstyles.add(DIMSTY)
    dd = ds.dxf
    dd.dimblk = ""          # closed filled arrow
    dd.dimtsz = 0.0         # no ticks
    dd.dimasz = 1.6         # panah 0.8x tinggi teks
    dd.dimtxt = 2.0         # tinggi teks dimensi
    dd.dimexo = 1.0         # gap extension line
    dd.dimexe = 1.0         # overshoot extension line
    dd.dimdec = 0           # mm bulat tanpa desimal
    dd.dimtad = 1           # teks DI ATAS garis dimensi
    dd.dimtih = 0           # teks sejajar garis dimensi (inside)
    dd.dimtoh = 0           # ... (outside)
    dd.dimtxsty = ARIAL
    dd.dimclrd = 7
    dd.dimclre = 7
    dd.dimclrt = 7
    dd.dimlfac = 1.0


def main(dxf_path: str, manifest_path: str) -> int:
    raw = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        texts = raw.get("texts", [])
        dims = raw.get("dims", [])
        solids = raw.get("solids", [])
    else:
        texts, dims, solids = raw, [], []
    if not (texts or dims or solids):
        print(f"{manifest_path}: manifest kosong — TIDAK menimpa hasil lama")
        return 1
    for e in texts:
        if not (0.5 <= float(e.get("h", 2.0)) <= 3.0):
            raise SystemExit(
                f"char_height di luar 0.5-3.0 mm: {e.get('h')!r} pada {e.get('t')!r}"
            )

    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()

    if ARIAL not in [s.dxf.name for s in doc.styles]:
        doc.styles.add(ARIAL, font="arial.ttf")
    ensure_dimstyle(doc)

    # idempotency: drop post-processed entities from previous passes
    for mt in list(msp.query("MTEXT")):
        msp.delete_entity(mt)
    for dm in list(msp.query('DIMENSION[layer=="REF-DIM"]')):
        msp.delete_entity(dm)
    for so in list(msp.query('SOLID[layer=="REF-SYM"]')):
        msp.delete_entity(so)

    for e in texts:
        mt = msp.add_mtext(str(e["t"]), dxfattribs={
            "style": ARIAL,
            "char_height": float(e.get("h", 2.0)),
            "attachment_point": int(e.get("att", 5)),
            "layer": str(e.get("layer", "REF-TEXT")),
            "rotation": float(e.get("rot", 0.0)),
        })
        mt.set_location((float(e["x"]), float(e["y"]), 0.0))

    override = {"dimtad": 1, "dimdec": 0, "dimtih": 0, "dimtoh": 0}
    for d in dims:
        p1 = (float(d["p1"][0]), float(d["p1"][1]))
        p2 = (float(d["p2"][0]), float(d["p2"][1]))
        text = str(d.get("text", "<>"))
        if "base" in d and d["base"] is not None:
            base = (float(d["base"][0]), float(d["base"][1]))
            attribs = {"layer": "REF-DIM"}
            if "oblique" in d and d["oblique"] is not None:
                attribs["oblique_angle"] = float(d["oblique"])
            dim = msp.add_linear_dim(
                base=base, p1=p1, p2=p2,
                angle=float(d.get("angle", 0.0)), text=text,
                dimstyle=DIMSTY, override=dict(override),
                dxfattribs=attribs,
            )
        else:
            attribs = {"layer": "REF-DIM"}
            if "oblique" in d and d["oblique"] is not None:
                attribs["oblique_angle"] = float(d["oblique"])
            dim = msp.add_aligned_dim(
                p1=p1, p2=p2, distance=float(d.get("distance", 6.0)),
                text=text, dimstyle=DIMSTY, override=dict(override),
                dxfattribs=attribs,
            )
        dim.render()

    for s in solids:
        pts = [[float(p[0]), float(p[1])] for p in s["pts"]]
        msp.add_solid(pts, dxfattribs={"layer": str(s.get("layer", "REF-SYM"))})

    # ensure manifest layers exist, then pens
    used_layers = sorted(
        {str(e.get("layer", "REF-TEXT")) for e in texts}
        | {"REF-DIM"} | {str(s.get("layer", "REF-SYM")) for s in solids}
    )
    existing = [l.dxf.name for l in doc.layers]
    for name in used_layers:
        if name not in existing:
            doc.layers.add(name)
    applied = 0
    for layer in doc.layers:
        if layer.dxf.name in PENS:
            layer.dxf.lineweight = PENS[layer.dxf.name]
            applied += 1

    doc.saveas(dxf_path)
    errs = [f for f in validate_dxf_file(dxf_path) if f.severity == "error"]
    print(f"{dxf_path}: {len(texts)} MTEXT (ARIAL), {len(dims)} DIMENSION, "
          f"{len(solids)} SOLID, {applied} pens, errors={len(errs)}")
    for f in errs:
        print("  ", f.render())
    return 0 if not errs else 2


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("pemakaian: python apply_text.py <drawing>.dxf <drawing>.manifest.json")
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
