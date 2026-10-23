#!/usr/bin/env python3
"""Lightweight test for compression_common.py (company-cad-standard).

Membangun kanvas showcase seluruh simbol pustaka kompresi, mengekspor
manifest, menjalankan apply_text.py + validate_cad_rules.py, dan memverifikasi:
  1. Registry schedule (equipment/valve/instrument/line) terisi.
  2. Manifest teks memenuhi batas tinggi 0.5-3.0 mm.
  3. Linter perusahaan exit 0 (0 error).

Usage: python test_compression_common.py  (exit 0 = PASS)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from cadgen import dxf
from pid_common import pipe_run_h as pc_pipe_run_h, line as pc_line
import compression_common as cc


@dxf
def test_compression_drawing():
    c = cc.CompressionContext()

    # 0. Line proses dasar untuk simbol inline
    c.proc += pc_pipe_run_h(260.0, 120.0, 200.0)
    c.proc += pc_pipe_run_h(150.0, 170.0, 240.0)
    c.proc += pc_pipe_run_h(90.0, 262.0, 338.0, gaps=[(300.0, 6.2)])
    c.proc += pc_pipe_run_h(120.0, 345.0, 375.0)
    c.proc += [pc_line(262.0, 87.0, 262.0, 93.0), pc_line(338.0, 87.0, 338.0, 93.0),
               pc_line(40.0, 157.0, 40.0, 163.0), pc_line(520.0, 161.0, 520.0, 167.0)]
    c.proc += pc_pipe_run_h(70.0, 60.0, 620.0)       # drain header test
    c.proc += pc_pipe_run_h(60.0, 340.0, 380.0)      # flare header test

    # 1. Kompresor torak + dampener + purge stub (API 618)
    info = c.compressor_reciprocating(150.0, 260.0, tag="K-201",
                                      stage_label="STAGE 1", fsl_loop="205")
    assert info["suction_x"] == 156.0 and info["discharge_x"] == 168.0
    c.pulsation_dampener(156.0, 260.0, tag="PD-201A")

    # 2. Kompresor sentrifugal API 617 (barrel & h-split) + DGS
    c.compressor_centrifugal_617(300.0, 260.0, tag="K-301", casing="BARREL")
    c.compressor_centrifugal_617(420.0, 260.0, tag="K-302", casing="H-SPLIT")

    # 3. Suction scrubber + drain LV otomatis (arah kanan)
    scr = c.suction_scrubber(80.0, 120.0, 200.0, r=16.0, tag="V-301")
    assert scr["drain_x"] == 80.0
    c.proc += pc_pipe_run_h(160.0, 40.0, scr["inlet_x"])   # pipa inlet test
    tee = c.drain_lv_h(80.0, scr["drain_y"], 92.0, 70.0, tag_lv="LV-301")
    assert tee[1] == 70.0

    # 4. Coalescing filter + drain LV (arah kiri)
    f = c.coalescing_filter(560.0, 120.0, 200.0, r=12.0, tag="F-301")
    c.proc += pc_pipe_run_h(164.0, 520.0, f["inlet_x"])    # pipa inlet test
    c.drain_lv_h(560.0, f["drain_y"], 92.0, 70.0, tag_lv="LV-303", dir=-1)

    # 5. Fin-fan + TEMA exchanger
    c.fin_fan_cooler(200.0, 150.0, tag="E-301", hw=22.0, tee_dx=14.0)
    c.shell_tube_tema(400.0, 150.0, tag="E-302", tema="AES")

    # 6. Anti-surge valve + drop BDV
    c.anti_surge_valve_h(300.0, 90.0, tag="ASV-301", fy_no="301")
    c.drop_v(360.0, 60.0, 120.0, breaks=(70.0,), valve_y=100.0, valve_tag="BDV-301")

    # 7. BL box dua arah
    c.bl_box(40.0, 30.0, 70.0, "300-CG-3001 DN100", "FROM STATION", "DWG: X", dir=1)
    c.bl_box(40.0, 500.0, 540.0, "300-CG-3002 DN100", "TO EXPORT", "DWG: Y", dir=-1)

    # Frame minim agar kanvas tidak kosong
    c.frame += __import__("pid_common").rect(20, 15, 823, 579)

    c.register_line("300-CG-3001", spec="150# A1A", service="Test", dn=100)
    out_json = Path(__file__).resolve().parent / "test_compression_common.texts.json"
    return c.export_manifest(out_json)


def main() -> int:
    print("[1/4] Build showcase drawing (cadgen/dxf)...")
    test_compression_drawing()
    dxf_path = Path("test_compression_common.dxf").resolve()
    if not dxf_path.exists():
        # cadgen menulis di cwd script parent — cari
        cand = Path(__file__).resolve().parent / "test_compression_common.dxf"
        dxf_path = cand
    assert dxf_path.exists(), f"DXF tidak dihasilkan: {dxf_path}"
    json_path = dxf_path.with_suffix(".texts.json")
    if not json_path.exists():
        cand = list(dxf_path.parent.glob("test_compression*.texts.json"))
        assert cand, "manifest texts.json tidak ditemukan"
        json_path = cand[0]

    print("[2/4] Verifikasi manifest teks (tinggi 0.5-3.0 mm)...")
    data = json.loads(json_path.read_text(encoding="utf-8"))
    texts = data["texts"] if isinstance(data, dict) else data
    bad = [t for t in texts if not (0.5 <= float(t.get("h", 2.0)) <= 3.0)]
    assert not bad, f"Tinggi teks di luar batas: {bad[:3]}"
    assert len(texts) > 20, "manifest terlalu sedikit"

    print("[3/4] apply_text.py (MTEXT ARIAL + pens)...")
    here = Path(__file__).resolve().parent
    ret = subprocess.run(
        [sys.executable, str(here / "apply_text.py"), str(dxf_path), str(json_path)],
        capture_output=True, text=True,
    )
    print(" ", ret.stdout.strip() or ret.stderr.strip())
    assert ret.returncode == 0, f"apply_text gagal: {ret.stderr}"

    print("[4/4] validate_cad_rules.py (harus 0 error)...")
    ret = subprocess.run(
        [sys.executable, str(here / "validate_cad_rules.py"),
         str(dxf_path), str(json_path)],
        capture_output=True, text=True,
    )
    print(ret.stdout)
    if ret.returncode != 0:
        print(ret.stderr)
    assert ret.returncode == 0, "validate_cad_rules menemukan error"

    print("PASS: test_compression_common")
    return 0


if __name__ == "__main__":
    sys.exit(main())
