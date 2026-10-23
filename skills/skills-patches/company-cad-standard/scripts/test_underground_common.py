#!/usr/bin/env python3
"""Light Integration Test for underground_common.py (GPF-00-PM-PLN-0008 V.1).

Membangun showcase semua komponen bawah tanah (REF-PROC-UG, puddle flange,
MIJ, CP test post, cased crossing, trench cross-section) ke /tmp/aud,
menjalankan apply_text.py + validate_cad_rules.py, dan memverifikasi MTEXT.
Exit 0 = lulus.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from cadgen import dxf

import underground_common as uc


@dxf
def test_underground_drawing():
    c = uc.UndergroundContext()

    # Border ringkas
    c.frame += uc.rect(7.0, 6.3, 413.0, 290.7)
    c.text("UNDERGROUND_COMMON COMPONENT TEST", 210.0, 283.0, size=2.5)

    # 1. Rute plan mini: AG proc -> puddle flange -> UG dashed -> casing -> MIJ
    c.sym += [
        uc.line(20.0, 256.5, 20.0, 263.5),
        uc.line(20.0, 256.5, 28.0, 260.0),
        uc.line(28.0, 260.0, 20.0, 263.5),
    ]
    c.proc.append(uc.line(20.0, 260.0, 47.0, 260.0))
    c.flow_arrow_h(30.0, 260.0, layer="REF-PROC")
    c.puddle_flange_plan(50.0, 260.0)
    c.mij_plan(58.0, 260.0, tag="MIJ-T1", tag_dy=-9.5)
    c.ug_pipe_run_h(260.0, 53.0, 220.0, breaks=[(58.0, 3.0)])
    c.flow_arrow_h(100.0, 260.0, layer="REF-PROC-UG")
    c.cp_test_post(120.0, 260.0, tag="TP-T1", dy=6.0, shelf_len=20.0)
    c.cased_road_crossing(180.0, 260.0, half_len=35.0, spacer_step=10.0,
                          vent=True, vent_dx=-30.0, vent_h=10.0, label="")
    c.road_band(168.0, 192.0, 235.0, 285.0, label="")
    c.puddle_flange_section(90.0, 220.0, pipe_r=4.2)
    c.mij_section(104.0, 220.0)
    c.text("SECTION SYMBOLS ABOVE", 97.0, 205.0, size=1.8)
    c.text("TYP. TEST ROUTE (NTS)", 130.0, 244.0, size=1.8)

    # 2. Trench cross-section terdimensi (parametrik, skala kecil)
    c.trench_cross_section(
        x_cl=210.0, y_grade=190.0, x_min=30.0, x_max=390.0, y_min=110.0,
        scale=40.0, cover_m=1.2, pipe_od_mm=168.0, bedding_mm=150.0,
        tape_below_m=0.5, bottom_w_m=1.2, side_slope=1.0,
        pipe_label="DN150 CARRIER (TEST)",
    )

    # 3. UG vertical run + break
    c.ug_pipe_run_v(390.0 - 0.0, 40.0, 100.0)
    c.flow_arrow_v(390.0, 70.0, direction=-1, layer="REF-PROC-UG")

    out_dir = Path("/tmp/aud")
    out_dir.mkdir(parents=True, exist_ok=True)
    return c.export_manifest(out_dir / "test_underground_common.texts.json")


def main() -> int:
    out_dir = Path("/tmp/aud")
    out_dir.mkdir(parents=True, exist_ok=True)
    dxf_dest = out_dir / "test_underground_common.dxf"
    texts_json = out_dir / "test_underground_common.texts.json"

    print("[1/4] Build showcase drawing (cadgen/dxf)...")
    test_underground_drawing()
    built = Path(__file__).resolve().parent / "test_underground_common.dxf"
    if not built.exists():
        built = Path("test_underground_common.dxf")
    if built.exists():
        built.rename(dxf_dest)

    print("[2/4] Stamp REF-PROC-UG pen + apply_text.py...")
    uc.stamp_layer_pens(dxf_dest, {"REF-PROC-UG": uc.UG_PEN})
    apply_text = Path(__file__).resolve().parent / "apply_text.py"
    ret = subprocess.run([sys.executable, str(apply_text), str(dxf_dest), str(texts_json)],
                         capture_output=True, text=True)
    print(" ", ret.stdout.strip() or ret.stderr.strip())
    if ret.returncode != 0:
        print("FAIL: apply_text returncode", ret.returncode)
        return 1

    print("[3/4] validate_cad_rules.py...")
    val = Path(__file__).resolve().parent / "validate_cad_rules.py"
    ret = subprocess.run([sys.executable, str(val), str(dxf_dest), str(texts_json)],
                         capture_output=True, text=True)
    print(ret.stdout)
    if ret.returncode != 0:
        print("FAIL: validate_cad_rules returncode", ret.returncode)
        return 1

    print("[4/4] Verifikasi MTEXT vs manifest (ezdxf)...")
    import ezdxf

    doc = ezdxf.readfile(str(dxf_dest))
    msp = doc.modelspace()
    mtexts = list(msp.query("MTEXT"))
    n_manifest = len(json.loads(texts_json.read_text())["texts"])
    bad = [m for m in mtexts if (m.dxf.style or "").upper() != "ARIAL"
           or not (0.5 <= float(m.dxf.char_height) <= 3.001)]
    single_text = list(msp.query("TEXT"))
    ugr = [l for l in msp.query('LINE[layer=="REF-PROC-UG"]')]
    ugr_pen = {l.dxf.name: l.dxf.lineweight for l in doc.layers
               if l.dxf.name == "REF-PROC-UG"}
    ok = (len(mtexts) == n_manifest and not bad and not single_text
          and len(ugr) > 0 and ugr_pen.get("REF-PROC-UG") == uc.UG_PEN)
    print(f"  MTEXT={len(mtexts)} manifest={n_manifest} bad={len(bad)} "
          f"TEXT={len(single_text)} REF-PROC-UG lines={len(ugr)} pen={ugr_pen}")
    if not ok:
        print("FAIL: verifikasi MTEXT/layer tidak lolos")
        return 1
    print("PASS: test_underground_common")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
