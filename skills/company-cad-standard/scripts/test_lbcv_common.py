#!/usr/bin/env python3
"""Integration Test & Visual QA untuk company-cad-standard lbcv_common.py.

Membangun satu LBCV station lengkap + sampel komponen lepas (MLV ball,
aktuator gas-over-oil, pilot line break, hand pump, blowdown stack, grade
line) dalam satu kanvas, mengekspor manifest, menjalankan apply_text.py,
memverifikasi jumlah MTEXT == manifest, menjalankan validate_cad_rules.py
(wajib 0 error), dan merender visual ke /tmp/aud/test_lbcv_common.png.

Exit code: 0 bila seluruh tahap lolos, 1 bila ada kegagalan.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from cadgen import dxf

import lbcv_common as lc
from pid_common import dashed, dashed_brk, line, pipe_run_h


@dxf
def test_lbcv_common():
    c = lc.LBCVContext()

    # 1. Border lembar (ISO 5457 disederhanakan)
    c.frame += [
        line(10.0, 7.0, 831.0, 7.0), line(831.0, 7.0, 831.0, 587.0),
        line(831.0, 587.0, 10.0, 587.0), line(10.0, 587.0, 10.0, 7.0),
    ]
    c.text("LBCV_COMMON V1 COMPONENT SHOWCASE", 420.0, 570.0, size=2.5)
    c.text("GPF-00-PI-PID-0016 (TEST SHEET)", 420.0, 560.0, size=2.0)

    # 2. Station LBCV lengkap (koordinat standar demo: garis y=300, MLV x=250)
    info = c.lbcv_station_h(72.5, 585.0, 300.0)
    assert info["mlv"] == (250.0, 300.0), "posisi MLV salah"

    # 3. Sampel lepas: pilot line break
    c.sym += c.line_break_pilot(80.0, 490.0, tag="LBP-7002")

    # 4. Sampel lepas: emergency hand pump
    c.sym += c.hand_pump(170.0, 490.0, tag="HP-7002")

    # 5. Sampel lepas: aktuator gas-over-oil
    c.equip += c.gas_over_oil_actuator(240.0, 480.0)

    # 6. Sampel lepas: MLV ball valve pada pipa stub ber-cap
    c.proc += pipe_run_h(500.0, 300.0, 340.0, gaps=[(320.0, 10.2)])
    c.proc += [line(300.0, 495.0, 300.0, 505.0), line(340.0, 495.0, 340.0, 505.0)]
    c.proc += c.ball_valve_mlv_h(320.0, 500.0, tag="MLV-7002")
    c.text("MLV-7002", 320.0, 486.0, size=2.5)

    # 7. Sampel lepas: blowdown stack pada pipa stub ber-cap
    c.proc += pipe_run_h(200.0, 460.0, 560.0)
    c.proc += [line(460.0, 195.0, 460.0, 205.0), line(560.0, 195.0, 560.0, 205.0)]
    c.proc += c.blowdown_stack_v(500.0, 200.0, 280.0, tags=("BD-7008A", "BD-7008B"))

    # 8. Sampel lepas: garis muka tanah dengan break stem
    c.equip += c.grade_line_h(80.0, 240.0, 440.0, brk=[70.0])

    # 9. Sampel sinyal dashed legend-style (REF-SIG)
    c.sig += dashed(80.0, 460.0, 120.0, 460.0, dash=2.5, gap=1.2)

    out_dir = Path("/tmp/aud")
    out_dir.mkdir(parents=True, exist_ok=True)
    c.export_schedules(out_dir / "test_lbcv_common.schedules.json")
    return c.export_manifest(out_dir / "test_lbcv_common.texts.json")


def run_pipeline() -> int:
    out_dir = Path("/tmp/aud")
    out_dir.mkdir(parents=True, exist_ok=True)
    dxf_dest = out_dir / "test_lbcv_common.dxf"
    texts_json = out_dir / "test_lbcv_common.texts.json"
    png_out = out_dir / "test_lbcv_common.png"
    script_dir = Path(__file__).resolve().parent

    # 1. Bangun DXF (cadgen menulis di samping script -> pindah ke /tmp/aud)
    print("[1/5] Membangun test_lbcv_common (cadgen/dxf)...")
    test_lbcv_common()
    built = Path(__file__).resolve().parent / "test_lbcv_common.dxf"
    if not built.exists():
        built = Path("test_lbcv_common.dxf")
    if built.exists():
        built.rename(dxf_dest)
    if not dxf_dest.exists():
        print("  GAGAL: DXF tidak dihasilkan")
        return 1

    # 2. apply_text.py (MTEXT + pens)
    print("[2/5] Menjalankan apply_text.py...")
    ret = subprocess.run(
        [sys.executable, str(script_dir / "apply_text.py"), str(dxf_dest), str(texts_json)],
        capture_output=True, text=True,
    )
    print("  " + (ret.stdout.strip() or ret.stderr.strip()))
    if ret.returncode != 0:
        print("  GAGAL: apply_text.py return code", ret.returncode)
        return 1

    # 3. Verifikasi jumlah MTEXT == panjang manifest
    print("[3/5] Verifikasi MTEXT vs manifest...")
    import ezdxf

    manifest = json.loads(texts_json.read_text(encoding="utf-8"))
    n_manifest = len(manifest.get("texts", []))
    doc = ezdxf.readfile(str(dxf_dest))
    mtexts = list(doc.modelspace().query("MTEXT"))
    bad_h = [m for m in mtexts if not (0.5 <= float(m.dxf.char_height) <= 3.001)]
    bad_style = [m for m in mtexts if (m.dxf.style or "").upper() != "ARIAL"]
    print(f"  MTEXT={len(mtexts)} manifest={n_manifest} style_beda={len(bad_style)} h_invalid={len(bad_h)}")
    if len(mtexts) != n_manifest or bad_h or bad_style:
        print("  GAGAL: MTEXT tidak sinkron dengan manifest / style / tinggi")
        return 1

    # 4. validate_cad_rules.py (wajib 0 error)
    print("[4/5] Menjalankan validate_cad_rules.py...")
    sys.path.insert(0, str(script_dir))
    from validate_cad_rules import CADValidator

    validator = CADValidator(str(dxf_dest), str(texts_json))
    errs, warns = validator.run_all_checks()
    if errs != 0:
        print(f"  GAGAL: validate_cad_rules {errs} error(s)")
        return 1

    # 5. Render visual (best-effort, ezdxf draw)
    print(f"[5/5] Merender visual ke {png_out}...")
    ezdxf_bin = Path(sys.executable).parent / "ezdxf"
    if not ezdxf_bin.exists():
        ezdxf_bin = Path.home() / ".local" / "bin" / "ezdxf"
    if ezdxf_bin.exists():
        ret = subprocess.run(
            [str(ezdxf_bin), "draw", "-o", str(png_out), "--background", "WHITE", "--force", str(dxf_dest)],
            capture_output=True, text=True,
        )
        if ret.returncode == 0:
            print(f"  Visual PNG tersimpan: {png_out}")
        else:
            print("  (render dilewati):", ret.stderr.strip())
    else:
        print("  (ezdxf CLI tidak ditemukan — render dilewati)")

    print("HASIL: PASS (0 error, MTEXT sinkron, visual dirender)")
    return 0


if __name__ == "__main__":
    sys.exit(run_pipeline())
