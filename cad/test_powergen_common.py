#!/usr/bin/env python3
"""Lightweight Integration Test for company-cad-standard powergen_common.py.

Membangun kanvas showcase berisi seluruh simbol pustaka pembangkit listrik
(coalescing filter, preheater electric, dual PCV station, gas admission valve,
fin-fan radiator, engine-alternator skid, exhaust system, expansion tank,
electrical interface), mengekspor manifest, menjalankan apply_text.py +
validate_cad_rules.py via subprocess, lalu memverifikasi schedule registry.

Jalankan: uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.21 \
          python cad/test_powergen_common.py
Exit 0 = seluruh assertion lolos dan linter PASS (0 error).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from cadgen import dxf
from pid_common import pipe_run_h, pipe_run_v, rect
import powergen_common as pg


@dxf
def test_powergen_drawing():
    c = pg.PowerGenContext()

    # 1. Border & frame (A1 sheet ISO 5457)
    c.frame += rect(10.0, 10.0, 831.0, 584.0)

    # 2. Coalescing filter FG-401 (drain GV-402 internal) -> preheater E-401
    c.proc += c.coalescing_filter_v(80.0, 160.0, 240.0, r=13.0, tag="FG-401")
    c.proc += pipe_run_v(80.0, 246.5, 258.0)                 # apex -> atas
    c.proc += pipe_run_h(258.0, 80.0, 154.0)                 # ke kanan
    c.proc += pipe_run_v(154.0, 234.0, 258.0)                # turun ke flange nozzle atas
    c.proc += pipe_run_v(154.0, 190.0, 206.0)                # nozzle bawah -> funnel
    c.proc += [pc_line(150.0, 190.0, 158.0, 190.0)]          # funnel cap
    c.proc += pipe_run_h(190.0, 154.0, 250.0)                # ke riser jalur PCV
    c.proc += c.fuel_preheater_electric(180.0, 220.0, tag="E-401")

    # 3. Dual PCV station (worker + monitor) + gas admission valve
    c.proc += pipe_run_v(250.0, 190.0, 220.0)                # naik ke jalur PCV
    c.proc += pipe_run_h(220.0, 250.0, 380.0,
                         gaps=[(270.0, 6.2), (300.0, 6.2), (360.0, 6.2)])
    c.dual_pcv_station(220.0, 270.0, 300.0, pic_y=280.0)
    c.proc += c.gas_admission_valve_h(360.0, 220.0, tag="GA-401")
    c.proc += [pc_line(380.0, 216.0, 380.0, 224.0)]          # blind cap ujung

    # 4. Fin-fan radiator + package pump
    c.proc += c.fin_fan_radiator(250.0, 40.0, 300.0, 80.0, tag="HX-401", label="JW RAD")
    c.proc += pipe_run_h(60.0, 300.0, 333.0)                 # suction dari panel
    c.proc += c.package_pump(340.0, 60.0, r=7.0)
    c.proc += pipe_run_h(60.0, 347.0, 365.0)                 # discharge
    c.proc += [pc_line(365.0, 56.0, 365.0, 64.0)]            # blind cap ujung

    # 5. Engine-alternator skid + exhaust system (kanan; riser di atas blok)
    c.proc += c.engine_alternator_skid(
        x0=470.0, yb=80.0, bw=60.0, bh=55.0, alt_cx=565.0, alt_r=20.0,
        coupling=12.0, skid_x0=455.0, skid_x1=635.0, yskid=45.0,
        dampers=(465.0, 545.0, 625.0), tag="GE-G1",
    )
    c.proc += pipe_run_v(510.0, 135.0, 150.0)
    c.proc += c.exhaust_bellows_v(510.0, 150.0, 162.0, w=12.0)
    c.proc += pipe_run_v(510.0, 162.0, 168.0)
    c.proc += c.exhaust_silencer_arrestor_v(510.0, 168.0, 215.0, w=18.0, tag="")
    c.text("EXH-SIL-401", 525.0, 186.0, size=1.8, left=True)
    c.text("SILENCER + SPARK ARRESTOR", 525.0, 180.0, size=1.8, left=True)
    c.schedule_equipment.append({
        "tag": "EXH-SIL-401",
        "type": "EXHAUST SILENCER + SPARK ARRESTOR (NFPA 37)",
        "x": 510.0, "y": 191.5,
    })
    c.proc += pipe_run_v(510.0, 215.0, 240.0)
    c.proc += c.exhaust_stack_cap(510.0, 240.0, w=14.0, label="RAIN CAP")

    # 6. Expansion tank JW + LT di cabang riser ber-cap
    c.proc += c.expansion_tank_lt(400.0, 140.0, 416.0, 170.0,
                                  branch=(416.0, 155.0, 428.0, 155.0))
    c.proc += pipe_run_v(428.0, 130.0, 180.0)
    c.proc += [pc_line(424.0, 130.0, 432.0, 130.0),
               pc_line(424.0, 180.0, 432.0, 180.0)]

    # 7. Electrical interface (GCB/CT/PT/panel)
    c.electrical_interface(cable_x=620.0, y_bus=200.0, alt_x=585.0, y_alt=107.5)

    # 8. Registrasi & manifest
    c.register_line("080-FG-4001", spec="150# A1A", service="Fuel Gas", dn=50)
    c.register_line("080-JW-4004", spec="150# A1A", service="Jacket Water", dn=80)

    out_dir = Path("/tmp/aud")
    out_dir.mkdir(parents=True, exist_ok=True)
    data = c.export_schedules(out_dir / "test_powergen_common.schedules.json")
    # Assertions ringan terhadap auto-registry
    assert len(data["equipment"]) >= 6, f"equipment kurang: {len(data['equipment'])}"
    assert len(data["valves"]) >= 4, f"valves kurang: {len(data['valves'])}"
    assert len(data["instruments"]) >= 5, f"instruments kurang: {len(data['instruments'])}"
    assert data["lines"][0]["line_no"] == "080-FG-4001"
    return c.export_manifest(out_dir / "test_powergen_common.texts.json")


def pc_line(x1, y1, x2, y2):
    """Garis pendek (cap/nozzle) untuk test showcase."""
    from cadgen import build123d as bd
    return bd.Edge.make_line(bd.Vector(x1, y1, 0), bd.Vector(x2, y2, 0))


def run_pipeline():
    dxf_dest = Path("/tmp/aud/test_powergen_common.dxf")
    texts_json = Path("/tmp/aud/test_powergen_common.texts.json")
    script_dir = Path(__file__).resolve().parent

    print("[1/4] Membangun showcase drawing powergen_common...")
    test_powergen_drawing()
    staged = script_dir / "test_powergen_common.dxf"
    if staged.exists():
        if dxf_dest.exists():
            dxf_dest.unlink()
        staged.rename(dxf_dest)
    assert dxf_dest.exists(), "DXF test tidak dihasilkan"

    print("[2/4] apply_text.py...")
    ret = subprocess.run(
        [sys.executable, str(script_dir / "apply_text.py"), str(dxf_dest), str(texts_json)],
        capture_output=True, text=True,
    )
    print(" ", ret.stdout.strip()[-400:])
    assert ret.returncode == 0, f"apply_text gagal: {ret.stderr[-400:]}"

    print("[3/4] validate_cad_rules.py...")
    ret = subprocess.run(
        [sys.executable, str(script_dir / "validate_cad_rules.py"),
         str(dxf_dest), str(texts_json)],
        capture_output=True, text=True,
    )
    print(ret.stdout[-3000:])
    assert ret.returncode == 0, "validate_cad_rules menemukan error"

    print("[4/4] PASS: schedules + manifest + linter bersih.")


if __name__ == "__main__":
    run_pipeline()
