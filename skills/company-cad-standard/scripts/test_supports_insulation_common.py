#!/usr/bin/env python3
"""Light Integration Test for supports_insulation_common.py (GPF-00-PM-PLN-0008 V.2-V.3).

Membangun showcase 8 tipe simbol support (iso + plan), tabel shoe height,
jacket insulasi P&ID berlabel, dan simbol batas insulasi isometrik ke
/tmp/aud, menjalankan apply_text.py + validate_cad_rules.py, memverifikasi
MTEXT dan konsistensi katalog. Exit 0 = lulus.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from cadgen import dxf

import supports_insulation_common as si


@dxf
def test_supports_drawing():
    c = si.SupInsContext()

    c.frame += si.rect(7.0, 6.3, 413.0, 290.7)
    c.text("SUPPORTS_INSULATION_COMMON COMPONENT TEST", 210.0, 283.0, size=2.5)

    # 1. Delapan simbol isometrik (baris atas, stub pipa di REF-SYM)
    for i, item in enumerate(si.SUPPORT_CATALOG):
        x = 30.0 + i * 48.0
        if item["code"] != "TRN":
            c.sym.append(si.line(x - 11.0, 250.0, x + 11.0, 250.0))
        c.draw_iso_support(item["code"], x, 250.0)
        c.text(item["code"], x, 236.0, size=2.0)

    # 2. Delapan simbol plan (baris kedua; VSP/CSP/TRN menggantikan pipa)
    for i, item in enumerate(si.SUPPORT_CATALOG):
        x = 30.0 + i * 48.0
        if item["code"] not in ("VSP", "CSP", "TRN"):
            c.sym.append(si.line(x - 11.0, 210.0, x + 11.0, 210.0))
        c.draw_plan_support(item["code"], x, 210.0)

    # 3. Jacket insulasi P&ID: PP-50 dan ET-HC-40
    c.pid_insulation_jacket(60.0, 180.0, 170.0, cls="PP", thk_mm=50)
    c.pid_insulation_jacket(240.0, 360.0, 170.0, cls="ET-HC", thk_mm=40)
    c.text("P&ID SAMPLES", 210.0, 182.0, size=1.8)

    # 4. Simbol batas insulasi isometrik
    c.iso_insulation_break(210.0, 130.0, label="INSULATION BREAK",
                           pipe_layer="REF-SYM")

    # 5. Data katalog & shoe height konsisten
    assert [it["code"] for it in si.SUPPORT_CATALOG] == [
        "ANC", "RES", "GUI", "STP", "HNG", "VSP", "CSP", "TRN"]
    assert si.shoe_height_for_insulation(0) == ("SH-0", 0)
    assert si.shoe_height_for_insulation(50) == ("SH-100", 100)
    assert si.shoe_height_for_insulation(80) == ("SH-150", 150)
    assert si.shoe_height_for_insulation(120) == ("SH-200", 200)
    c.text("SHOE HEIGHT: SH-0/100/150/200 VS INSULATION 0/<=50/60-100/>100 MM",
           210.0, 100.0, size=1.8)

    out_dir = Path("/tmp/aud")
    out_dir.mkdir(parents=True, exist_ok=True)
    return c.export_manifest(out_dir / "test_supports_insulation_common.texts.json")


def main() -> int:
    out_dir = Path("/tmp/aud")
    out_dir.mkdir(parents=True, exist_ok=True)
    dxf_dest = out_dir / "test_supports_insulation_common.dxf"
    texts_json = out_dir / "test_supports_insulation_common.texts.json"

    print("[1/4] Build showcase drawing (cadgen/dxf)...")
    test_supports_drawing()
    built = Path(__file__).resolve().parent / "test_supports_insulation_common.dxf"
    if not built.exists():
        built = Path("test_supports_insulation_common.dxf")
    if built.exists():
        built.rename(dxf_dest)

    print("[2/4] apply_text.py...")
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
    ok = len(mtexts) == n_manifest and not bad and not single_text
    print(f"  MTEXT={len(mtexts)} manifest={n_manifest} bad={len(bad)} "
          f"TEXT={len(single_text)}")
    if not ok:
        print("FAIL: verifikasi MTEXT tidak lolos")
        return 1
    print("PASS: test_supports_insulation_common")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
