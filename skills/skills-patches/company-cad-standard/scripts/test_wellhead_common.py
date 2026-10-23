#!/usr/bin/env python3
"""Integration Test & Visual QA untuk wellhead_common.py (API SPEC 6A / API RP 14C).

Mengikuti pola cad/test_pid_common.py: membangun kanvas showcase seluruh komponen
pustaka kepala sumur (termasuk positive choke yang tidak dipakai demo), mengekspor
manifest + schedules ke /tmp/aud, menjalankan apply_text.py, memverifikasi aturan
CAD via validate_cad_rules.py (wajib 0 error), dan merender PNG ke /tmp/aud.

Jalankan:
  uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.21 \
      python cad/test_wellhead_common.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from cadgen import dxf

import wellhead_common as wc


@dxf
def test_wellhead_drawing():
    c = wc.WellheadContext()

    # 1. Border & Title Frame (A1 Sheet ISO 5457)
    c.frame += wc.rect(10.0, 10.0, 831.0, 584.0)
    c.title += wc.rect(655.0, 15.0, 823.0, 116.0)
    c.text("WELLHEAD_COMMON V1 COMPONENT SHOWCASE", 739.0, 95.0, size=2.5)
    c.text("API SPEC 6A / ISO 10423 - API RP 14C", 739.0, 80.0, size=2.2)
    c.text("DWG NO: TEST-WELLHEAD-0001", 739.0, 65.0, size=2.0)

    # 2. Baris proses utama y=260 (pipa 68..445, cap tick di kedua ujung):
    #    manual gate H, hydraulic gate H, needle valve, choke adjustable, choke positive
    c.proc += c.valve_gate_manual_h(100.0, 260.0, tag="XV-101")
    c.text("MANUAL GATE H", 100.0, 248.0, size=1.8)

    c.proc += c.valve_gate_hydraulic_h(150.0, 260.0, tag="UV-102", fail="FC")
    c.text("HYDRAULIC GATE H", 150.0, 248.0, size=1.8)

    c.proc += c.valve_needle_h(195.0, 260.0, tag="NV-103")
    c.text("NEEDLE VALVE", 195.0, 250.0, size=1.8)

    c.proc += c.choke_adjustable_h(240.0, 260.0, tag="XOV-104", label="ADJUSTABLE")
    c.proc += c.choke_positive_h(300.0, 260.0, tag="XOV-105", label="POSITIVE")

    c.proc += wc.pipe_run_h(260.0, 68.0, 445.0, gaps=[
        (100.0, 6.2),   # XV-101 flanged w=10
        (150.0, 6.2),   # UV-102 flanged w=10
        (195.0, 3.0),   # NV-103 w=6
        (240.0, 6.5),   # XOV-104 house w=13
        (300.0, 6.5),   # XOV-105 house w=13
    ])
    c.proc += [wc.line(68.0, 255.0, 68.0, 265.0), wc.line(445.0, 255.0, 445.0, 265.0)]
    c.flow_arrow_h(85.0, 260.0, direction=1)
    c.flow_arrow_h(175.0, 260.0, direction=1)
    c.flow_arrow_h(340.0, 260.0, direction=1)
    c.flow_arrow_h(420.0, 260.0, direction=1)

    # Bleeder valve pada tee kecil di atas pipa utama (menempel ujung kanan katup)
    c.proc += wc.pipe_run_v(380.0, 260.0, 268.0)
    c.proc += [wc.line(376.0, 268.0, 380.0, 268.0)]
    c.proc += c.bleeder_valve_h(373.5, 268.0, tag="BV-110")

    # 3. Outlet annulus pada muka casing (rect tertutup) + label
    c.equip += wc.rect(94.0, 150.0, 106.0, 220.0)
    c.proc += c.annulus_outlet_h(
        106.0, 185.0, direction=1, pi_num="101", label="ANNULUS TEST", valve_tag="NV-109"
    )

    # 4. Kolom vertikal x=400: THF -> manual gate V -> hydraulic gate V -> wellbore + SCSSV
    c.equip += c.tubing_head_flange(400.0, 190.0, half_w=17.0)
    c.text("THF", 424.0, 191.5, size=1.8, left=True)

    c.proc += c.valve_gate_manual_v(400.0, 260.0, tag="XV-106")
    c.text("MANUAL GATE V", 424.0, 268.0, size=1.8, left=True)

    c.proc += c.valve_gate_hydraulic_v(400.0, 330.0, tag="UV-107", fail="FC")
    c.text("HYD GATE V", 424.0, 345.0, size=1.8, left=True)

    c.equip += c.wellbore(400.0, y_head_bot=190.0, y_shoe=90.0, scssv_cy=120.0)
    c.proc += c.scssv(400.0, 120.0, tag="SCSSV-108")
    c.text("SCSSV", 424.0, 120.0, size=1.8, left=True)

    # Segmen pipa penghubung kolom vertikal (ujung menempel tick flensa / THF;
    # gap 338..346 = badan kotak aktuator UV-107, garis masuk-keluar kotak)
    c.proc += wc.pipe_run_v(400.0, 193.0, 253.8)
    c.proc += wc.pipe_run_v(400.0, 266.2, 323.8)
    c.proc += wc.pipe_run_v(400.0, 336.2, 338.0)
    c.proc += wc.pipe_run_v(400.0, 346.0, 356.0)
    c.proc += [wc.line(396.0, 356.0, 404.0, 356.0)]
    c.flow_arrow_v(400.0, 225.0, direction=1, size=2.4)
    c.flow_arrow_v(400.0, 295.0, direction=1, size=2.4)

    # 5. Panel ESD + garis proses vertikal + sinyal hidraulik dashed (break 3 mm)
    c.equip += c.panel_box(600.0, 300.0, 680.0, 350.0)
    c.text("ESD PANEL TEST", 640.0, 325.0, size=2.2)
    c.proc += wc.pipe_run_v(560.0, 100.0, 380.0)
    c.proc += [wc.line(554.0, 100.0, 566.0, 100.0), wc.line(554.0, 380.0, 566.0, 380.0)]
    c.flow_arrow_v(560.0, 200.0, direction=1, size=2.4)
    c.text("VERTICAL LINE", 575.0, 150.0, size=1.8, left=True)

    # Sinyal menyeberang pipa vertikal x=560 -> break 3 mm, lalu masuk bubble PI
    c.sig += c.hydraulic_signal([(600.0, 320.0), (520.0, 320.0)], brks=[[40.0]])
    c.sig += c.hydraulic_signal([(520.0, 320.0), (520.0, 326.0)])
    c.sym += c.gauge_pi(520.0, 332.0, num="111")

    # Sinyal kedua tanpa break (uji multi-segmen)
    c.sig += c.hydraulic_signal([(524.0, 90.0), (524.0, 60.0), (600.0, 60.0)])

    # 6. Registrasi line & ekspor
    c.register_line("100-WH-9001", spec="API 6A", service="TEST FLOWLINE", dn=100)
    out_dir = Path("/tmp/aud")
    out_dir.mkdir(parents=True, exist_ok=True)
    c.export_schedules(out_dir / "test_wellhead_common.schedules.json")
    return c.export_manifest(out_dir / "test_wellhead_common.texts.json")


def run_pipeline():
    texts_json = Path("/tmp/aud/test_wellhead_common.texts.json")
    dxf_dest = Path("/tmp/aud/test_wellhead_common.dxf")
    png_out = Path("/tmp/aud/test_wellhead_common.png")
    script_dir = Path(__file__).resolve().parent

    # Pindahkan hasil build (cwd atau folder script) ke /tmp/aud
    import shutil

    for cand in (Path("test_wellhead_common.dxf"), script_dir / "test_wellhead_common.dxf"):
        if cand.exists():
            shutil.move(str(cand), str(dxf_dest))
            break
    if not dxf_dest.exists():
        raise SystemExit(f"DXF hasil build tidak ditemukan: {dxf_dest}")

    # 0. Light asserts terhadap manifest & schedules
    manifest = json.loads(texts_json.read_text(encoding="utf-8"))
    texts = manifest.get("texts", [])
    assert len(texts) > 20, f"manifest texts terlalu sedikit: {len(texts)}"
    for e in texts:
        h = float(e.get("h", 0.0))
        assert 0.5 <= h <= 3.0, f"height di luar 0.5-3.0: {h} pada {e.get('t')!r}"
    schedules = json.loads(
        (Path("/tmp/aud") / "test_wellhead_common.schedules.json").read_text(encoding="utf-8")
    )
    vtypes = {v["type"] for v in schedules["valves"]}
    for expected in (
        "GATE VALVE (MANUAL, API 6A)",
        "GATE VALVE (HYDRAULIC ACTUATOR, FAIL-CLOSE)",
        "NEEDLE VALVE",
        "CHOKE VALVE (ADJUSTABLE, CARBIDE NEEDLE)",
        "CHOKE VALVE (POSITIVE, FIXED BEAN)",
        "BLEEDER VALVE",
    ):
        assert expected in vtypes, f"schedule valves kurang: {expected} (ada: {sorted(vtypes)})"
    etypes = {e["type"] for e in schedules["equipment"]}
    assert any("SCSSV" in t for t in etypes), f"SCSSV belum terdaftar: {sorted(etypes)}"
    itags = {i["tag"] for i in schedules["instruments"]}
    assert "PI-101" in itags and "PI-111" in itags, f"PI belum terdaftar: {sorted(itags)}"
    print(f"[0/4] Light asserts PASS ({len(texts)} texts, "
          f"{len(schedules['valves'])} valves, {len(schedules['equipment'])} equipment)")

    # 1. apply_text.py
    print("[1/4] Menjalankan apply_text.py...")
    ret = subprocess.run(
        [sys.executable, str(script_dir / "apply_text.py"), str(dxf_dest), str(texts_json)],
        capture_output=True, text=True,
    )
    print("  ", ret.stdout.strip())
    if ret.returncode != 0:
        print("  apply_text stderr:", ret.stderr.strip())
        raise SystemExit("apply_text.py gagal")

    # 2. validate_cad_rules.py (wajib 0 error)
    print("[2/4] Menjalankan validate_cad_rules.py...")
    ret = subprocess.run(
        [sys.executable, str(script_dir / "validate_cad_rules.py"), str(dxf_dest), str(texts_json)],
        capture_output=True, text=True,
    )
    print(ret.stdout)
    if ret.returncode != 0:
        raise SystemExit("validate_cad_rules.py FAIL (lihat output di atas)")

    # 3. Snapshot visual (cadgen CLI) - best effort
    print("[3/4] Merender visual ke", png_out, "...")
    ret = subprocess.run(
        ["cadgen", "dxf", "snapshot", str(dxf_dest), str(png_out),
         "--width", "2400", "--height", "1700"],
        capture_output=True, text=True,
    )
    if ret.returncode == 0 and png_out.exists():
        print("  Snapshot tersimpan:", png_out)
    else:
        print("  [WARN] cadgen CLI tidak ditemukan; snapshot dilewati di dalam test "
              "(dijalankan manual di rantai build).", (ret.stderr or "").strip()[:200])

    print("[4/4] TEST WELLHEAD_COMMON SELESAI - PASS")


if __name__ == "__main__":
    test_wellhead_drawing()
    run_pipeline()
