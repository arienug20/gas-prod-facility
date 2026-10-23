#!/usr/bin/env python3
"""Integration Test untuk company-cad-standard metering_common.py.

Membangun seluruh komponen stasiun metering (USM, orifice senior dual-chamber,
Coriolis, turbine, DBB, fast loop + GC analyzer, flow computer FQI) dalam satu
kanvas terpadu, mengekspor manifest, menjalankan apply_text.py, mengevaluasi
aturan CAD via validate_cad_rules.py, dan memverifikasi hasil dengan ezdxf
(MTEXT ARIAL 0.5-3.0 mm, tanpa entity TEXT, pens terpasang).

Pemakaian (dari root proyek):
  uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.21 \
      python cad/test_metering_common.py
Exit 0 = seluruh assertion lolos.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import ezdxf

from cadgen import dxf

import metering_common as mc
from pid_common import line


def _cap(x: float, y: float) -> list:
    """Cap 3 mm (garis bantu pendek, exempt dangling) pada ujung pipa test."""
    return [line(x, y - 1.5, x, y + 1.5)]


@dxf
def test_metering_drawing():
    c = mc.MeteringContext()

    # 1. Border & Title Frame (A1 Sheet ISO 5457)
    c.frame += mc.rect(10.0, 10.0, 831.0, 584.0)
    c.title += mc.rect(655.0, 15.0, 823.0, 116.0)
    c.text("METERING_COMMON V1 COMPONENT SHOWCASE", 739.0, 95.0, size=2.5)
    c.text("USM / ORIFICE / CORIOLIS / TURBINE / DBB / GC", 739.0, 80.0, size=2.2)
    c.text("AGA 3/7/9/11 - API MPMS - ISO 5167 - ISO 17089", 739.0, 65.0, size=2.0)

    # 2. Baris 1 (y=480): USM + Orifice Senior + DBB standalone
    c.meter_run_pipe(60.0, 260.0, 480.0, [(150.0, mc.USM_BODY_L / 2.0)])
    c.proc += _cap(60.0, 480.0) + _cap(260.0, 480.0)
    c.flow_arrow_h(90.0, 480.0, direction=1)
    c.flow_arrow_h(230.0, 480.0, direction=1)
    c.usm_meter_run(
        150.0, 480.0, tag="USM-9001", fe_pair=("FT", "901"), fqi_pair=("FQI", "901")
    )

    c.meter_run_pipe(320.0, 540.0, 480.0, [(430.0, mc.METER_BODY_L / 2.0)])
    c.proc += _cap(320.0, 480.0) + _cap(540.0, 480.0)
    c.flow_arrow_h(350.0, 480.0, direction=1)
    c.flow_arrow_h(510.0, 480.0, direction=1)
    c.orifice_meter_run(
        430.0, 480.0, tag="OF-9002", fe_pair=("FT", "902"), fqi_pair=("FQI", "902")
    )

    c.meter_run_pipe(570.0, 650.0, 480.0, [(610.0, mc.DBB_HALF)])
    c.proc += _cap(570.0, 480.0) + _cap(650.0, 480.0)
    c.flow_arrow_h(630.0, 480.0, direction=1)
    c.dbb_valve_h(610.0, 480.0, tag="DBB-9001")

    # 3. Baris 2 (y=330): Coriolis + Turbine + DBB standalone
    c.meter_run_pipe(60.0, 260.0, 330.0, [(150.0, mc.METER_BODY_L / 2.0)])
    c.proc += _cap(60.0, 330.0) + _cap(260.0, 330.0)
    c.flow_arrow_h(90.0, 330.0, direction=1)
    c.flow_arrow_h(230.0, 330.0, direction=1)
    c.coriolis_meter(
        150.0, 330.0, tag="CM-9003",
        ft_pair=("FT", "903"), dt_pair=("DT", "904"), fqi_pair=("FQI", "903"),
    )

    c.meter_run_pipe(320.0, 540.0, 330.0, [(430.0, mc.METER_BODY_L / 2.0)])
    c.proc += _cap(320.0, 330.0) + _cap(540.0, 330.0)
    c.flow_arrow_h(350.0, 330.0, direction=1)
    c.flow_arrow_h(510.0, 330.0, direction=1)
    c.turbine_meter(
        430.0, 330.0, tag="TB-9004", fe_pair=("FT", "905"), fqi_pair=("FQI", "905")
    )

    c.meter_run_pipe(570.0, 650.0, 330.0, [(610.0, mc.DBB_HALF)])
    c.proc += _cap(570.0, 330.0) + _cap(650.0, 330.0)
    c.flow_arrow_h(630.0, 330.0, direction=1)
    c.dbb_valve_h(610.0, 330.0, tag="DBB-9002")

    # 4. Baris 3 (y=180): header + fast loop sampling probe + GC analyzer
    c.metering_header(60.0, 180.0, 180.0, "200-MT-9001", dn=300, label_x=118.0)
    c.proc += _cap(60.0, 180.0)
    c.fast_loop(100.0, 180.0, 265.0)
    c.text("FAST LOOP", 108.0, 240.0, size=1.8, left=True)
    c.gc_analyzer(
        100.0, 285.0, w=90.0, h=40.0, tag="AT-9090",
        comp_lines=(
            "GAS CHROMATOGRAPH",
            "ONLINE ANALYZER AT-9090",
            "C1-C6+ / CO2 / N2",
            "GHV TO FQI (AGA 8)",
        ),
    )

    # 5. Ekspor manifest + schedules
    out_dir = Path(tempfile.gettempdir()) / "aud"
    out_dir.mkdir(parents=True, exist_ok=True)
    c.export_schedules(out_dir / "test_metering_common.schedules.json")
    return c.export_manifest(out_dir / "test_metering_common.texts.json")


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    out_dir = Path(tempfile.gettempdir()) / "aud"
    out_dir.mkdir(parents=True, exist_ok=True)
    texts_json = out_dir / "test_metering_common.texts.json"
    dxf_dest = out_dir / "test_metering_common.dxf"

    # ---- Build DXF (cadgen @dxf) + manifest ----
    print("[1/5] Build DXF via cadgen @dxf...")
    built = script_dir / "test_metering_common.dxf"
    if built.exists():
        built.unlink()
    test_metering_drawing()
    assert built.exists(), f"DXF tidak dibuat di {built}"
    built.rename(dxf_dest)

    # ---- Unit assertion: konteks & manifest ----
    print("[2/5] Assertion konteks MeteringContext...")
    manifest = json.loads(texts_json.read_text(encoding="utf-8"))
    texts = manifest["texts"]
    solids = manifest["solids"]
    assert len(texts) >= 25, f"manifest texts terlalu sedikit: {len(texts)}"
    assert len(solids) >= 10, f"manifest solids terlalu sedikit: {len(solids)}"
    bad_h = [t for t in texts if not (0.5 <= float(t["h"]) <= 3.0)]
    assert not bad_h, f"tinggi teks di luar 0.5-3.0: {bad_h[:3]}"
    # (registrasi diverifikasi via schedules.json)
    sched = json.loads((out_dir / "test_metering_common.schedules.json").read_text(encoding="utf-8"))
    eq_types = " ".join(e["type"] for e in sched["equipment"])
    for kw in ("ULTRASONIC", "CORIOLIS", "TURBINE", "ORIFICE", "GAS CHROMATOGRAPH"):
        assert kw in eq_types, f"equipment '{kw}' tidak teregistrasi"
    valve_types = " ".join(v["type"] for v in sched["valves"])
    assert valve_types.count("DOUBLE BLOCK & BLEED") == 2, "harus 2 DBB teregistrasi"
    line_nos = {ln["line_no"] for ln in sched["lines"]}
    assert "200-MT-9001" in line_nos and "200-SA-6010" in line_nos, f"line list kurang: {line_nos}"
    print(f"      OK: {len(texts)} teks, {len(solids)} solid, "
          f"{len(sched['equipment'])} equipment, {len(sched['valves'])} valve, "
          f"{len(sched['lines'])} line")

    # ---- apply_text.py (MTEXT ARIAL + pens) ----
    print("[3/5] Post-process apply_text.py...")
    ret = subprocess.run(
        [sys.executable, str(script_dir / "apply_text.py"), str(dxf_dest), str(texts_json)],
        capture_output=True, text=True,
    )
    print("      " + (ret.stdout.strip().splitlines() or [""])[-1])
    assert ret.returncode == 0, f"apply_text exit {ret.returncode}: {ret.stderr}"

    # ---- validate_cad_rules.py (0 error) ----
    print("[4/5] Validasi validate_cad_rules.py...")
    ret = subprocess.run(
        [sys.executable, str(script_dir / "validate_cad_rules.py"), str(dxf_dest), str(texts_json)],
        capture_output=True, text=True,
    )
    print("      " + " | ".join(
        ln.strip() for ln in ret.stdout.splitlines() if "Check" in ln
    ))
    assert ret.returncode == 0, (
        f"validate_cad_rules exit {ret.returncode} (harus 0 error)\n{ret.stdout[-2000:]}"
    )

    # ---- Verifikasi ezdxf: MTEXT/TEXT/pens ----
    print("[5/5] Verifikasi ezdxf (MTEXT == manifest, ARIAL, pens, 0 TEXT)...")
    doc = ezdxf.readfile(str(dxf_dest))
    msp = doc.modelspace()
    mtexts = list(msp.query("MTEXT"))
    assert len(mtexts) == len(texts), f"MTEXT {len(mtexts)} != manifest {len(texts)}"
    assert all((m.dxf.style or "").upper() == "ARIAL" for m in mtexts), "ada MTEXT non-ARIAL"
    assert all(0.5 <= float(m.dxf.char_height) <= 3.001 for m in mtexts), "char_height di luar rentang"
    assert len(list(msp.query("TEXT"))) == 0, "ada entity TEXT single-line (terlarang)"
    bad_lw = [l.dxf.name for l in doc.layers
              if l.dxf.name.startswith("REF-") and l.dxf.lineweight <= 0]
    assert not bad_lw, f"layer tanpa lineweight: {bad_lw}"
    print(f"      OK: {len(mtexts)} MTEXT ARIAL, 0 TEXT, pens terpasang")

    print("\nHASIL: PASS - test_metering_common lolos seluruh assertion")
    return 0


if __name__ == "__main__":
    sys.exit(main())
