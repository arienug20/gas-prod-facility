#!/usr/bin/env python3
"""Smoke Test & Unit Test Suite for alignment_sheet_builder.py.

Unit tests (murni, tanpa build DXF):
  - parse_kp / fmt_kp (format KP 'x+xxx' <-> meter rantai)
  - parse_survey_csv (kolom wajib KP/Northing/Easting/Elevasi + opsional)
  - derive_features (BEND -> Bend, ROAD/RIVER -> Crossing)
  - heading_at (arah rute untuk panah aliran)
  - AlignmentSheetContext: mapping koordinat (kp_x / plan_y / prof_y),
    pipe_elev (BOP = NGL - DOC - OD), clamp tinggi teks manifest,
    band_specs (8 band standar), get_layers (layer kosong dilewati)

E2E smoke (subprocess, rantai build perusahaan):
  build -> apply_text.py -> validate_cad_rules.py (HARUS 0 error) -> snapshot.
  Langkah [1/4] memaksa rebuild cad/alignment_demo.dxf di workspace (satu-
  jalur keluaran model @dxf) — langkah [5/5] WAJIB memulihkan artefak
  workspace ke kondisi terkirim (hasil apply_text + snapshot) agar rantai
  pasca-build tidak pernah tertinggal pada DXF mentah (skill dxf §7:
  rebuild selalu menimpa .dxf -> post-processor diulang).
"""

from __future__ import annotations

import csv
import json
import math
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from alignment_sheet_builder import (  # noqa: E402
    PIPE_OD_M,
    AlignmentSheetContext,
    Bend,
    Crossing,
    SurveyStation,
    derive_features,
    fmt_kp,
    heading_at,
    parse_kp,
    parse_survey_csv,
)

OUT_DIR = Path("/tmp/aud")
OUT_DXF = OUT_DIR / "alignment_test.dxf"
OUT_JSON = OUT_DIR / "alignment_test.texts.json"
OUT_PNG = OUT_DIR / "alignment_test.png"

UVX = ["uvx", "--no-config", "--managed-python", "--python", "3.13",
       "--from", "cadgen==0.7.21"]


def _write_min_csv(path: Path) -> Path:
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["KP", "Northing", "Easting", "Elevasi", "Feature"])
        w.writerow(["0+000", 1000.0, 0.0, 106.2, ""])
        w.writerow(["0+100", 1000.0, 100.0, 107.1, "BEND;COLD;12;R"])
        w.writerow(["0+200", 1002.1, 200.0, 108.4, ""])
        w.writerow(["0+300", 1002.1, 300.0, 107.6, "ROAD;ASPHALT ROAD;OPEN CUT;8"])
    return path


def _mk_ctx(stations) -> AlignmentSheetContext:
    bends, crossings = derive_features(stations)
    return AlignmentSheetContext(stations, bends, crossings, plan_n_ref=1000.0)


def run_unit_tests() -> None:
    print("Running unit tests on alignment_sheet_builder...")

    # --- KP parsing / formatting ---
    assert abs(parse_kp("0+000") - 0.0) < 1e-9
    assert abs(parse_kp("1+900") - 1900.0) < 1e-9
    assert abs(parse_kp("1+050.5") - 1050.5) < 1e-9
    assert abs(parse_kp(750.0) - 750.0) < 1e-9
    assert fmt_kp(0.0) == "0+000"
    assert fmt_kp(1900.0) == "1+900"
    assert fmt_kp(1050.0) == "1+050"
    assert fmt_kp(parse_kp("0+123")) == "0+123"

    # --- CSV parser ---
    csv_path = _write_min_csv(OUT_DIR / "alignment_test_survey.csv")
    stations = parse_survey_csv(csv_path, defaults={"depth_cover": 1.2})
    assert len(stations) == 4, f"4 stasiun diharapkan, dapat {len(stations)}"
    assert stations[0].kp_m == 0.0 and stations[-1].kp_m == 300.0
    assert abs(stations[0].ground_elev - 106.2) < 1e-9
    assert abs(stations[0].depth_cover - 1.2) < 1e-9      # dari defaults
    assert abs(stations[0].wall_thk - 9.5) < 1e-9          # default dataclass
    assert stations[0].grade == "X52" and stations[0].coating == "3LPE"

    # BOP = NGL - DOC - OD
    assert abs(stations[0].pipe_elev - (106.2 - 1.2 - PIPE_OD_M)) < 1e-9

    # --- Feature derivation ---
    bends, crossings = derive_features(stations)
    assert len(bends) == 1 and bends[0].kind == "COLD"
    assert abs(bends[0].deflection_deg - 12.0) < 1e-9 and bends[0].side == "R"
    assert len(crossings) == 1 and crossings[0].kind == "ROAD"
    assert crossings[0].method == "OPEN CUT" and abs(crossings[0].width_m - 8.0) < 1e-9

    # --- Heading (0 = Timur, rute ke timur murni) ---
    assert abs(heading_at(stations, 50.0) - 0.0) < 1e-6
    assert abs(heading_at(stations, 250.0) - 0.0) < 1e-6

    ctx = _mk_ctx(stations)

    # --- Mapping koordinat ---
    assert abs(ctx.kp_x(0.0) - 110.0) < 1e-9               # ch_x0 default
    assert abs(ctx.kp_x(1900.0) - (110.0 + 0.25 * 1900.0)) < 1e-6
    assert abs(ctx.plan_y(1000.0) - 470.0) < 1e-9          # plan_n_ref=1000
    assert abs(ctx.plan_y(1100.0) - 495.0) < 1e-9          # 0.25 mm/m
    assert abs(ctx.prof_y(90.0) - 196.0) < 1e-9            # prof_el0 = 90
    assert abs(ctx.prof_y(100.0) - 236.0) < 1e-9           # 4.0 mm/m (1:250)

    # --- Manifest text: clamp 0.5-3.0 & att ---
    ctx.text("A" * 40, 100.0, 100.0, size=9.9)             # clamp ke 3.0
    ctx.text("b", 100.0, 105.0, size=0.1, left=True)       # clamp ke 0.5
    assert ctx.texts[-2]["h"] == 3.0 and ctx.texts[-1]["h"] == 0.5
    assert ctx.texts[-1]["att"] == 4 and ctx.texts[-2]["att"] == 5

    # --- Band specs: 8 band standar Bagian VI ---
    specs = ctx.band_specs()
    assert len(specs) == 8
    labels = [" ".join(l) for l, _ in specs]
    assert "GROUND ELEV (m)" == labels[0]
    assert "CHAINAGE (KP)" == labels[3]
    assert "WALL THK / GRADE API 5L" == labels[4]
    assert "CLASS LOCATION ASME B31.8" == labels[5]
    assert "COATING" == labels[6]
    assert "SOIL TYPE (USCS)" == labels[7]
    assert specs[3][1](stations[0]) == "0+000"
    assert specs[1][1](stations[0]) == f"{stations[0].pipe_elev:.1f}"

    # --- get_layers: kosong sebelum menggambar, terisi sesudah ---
    assert len(ctx.get_layers()) == 0, "context baru harus tanpa layer"
    ctx.setup_frame()
    layers = ctx.get_layers()
    assert "REF-FRAME" in layers and "REF-TITLE" not in layers

    # --- Simbol manifest solids (flow arrow / bend dot) ---
    ctx2 = _mk_ctx(stations)
    ctx2.setup_frame()
    ctx2.draw_plan_view()
    assert ctx2.solids, "flow arrow & bend harus menghasilkan SOLID manifest"
    assert ctx2.proc, "sumbu pipa harus di REF-PROC"

    print("Unit tests PASSED.")


def run_e2e_smoke() -> None:
    """Rantai build perusahaan utk dataset demo penuh (20 stasiun KP)."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("\n[1/4] Build DXF (alignment_demo model, output test)...")
    demo_py = SCRIPTS_DIR / "alignment_demo.py"
    res = subprocess.run(
        UVX + ["python", str(demo_py), "--force"],
        cwd=str(SCRIPTS_DIR.parent), capture_output=True, text=True,
    )
    if res.returncode != 0:
        print("BUILD FAILED:", res.stdout or res.stderr)
        sys.exit(res.returncode)
    src_dxf = SCRIPTS_DIR / "alignment_demo.dxf"
    src_json = SCRIPTS_DIR / "alignment_demo.texts.json"
    assert src_dxf.exists() and src_json.exists(), "DXF/manifest demo tidak ditemukan"

    # Salinan test terpisah agar artefak demo tidak diganggu
    import shutil
    shutil.copyfile(src_dxf, OUT_DXF)
    shutil.copyfile(src_json, OUT_JSON)

    print("[2/4] apply_text.py (MTEXT ARIAL + pens)...")
    res = subprocess.run(
        UVX + ["python", str(SCRIPTS_DIR / "apply_text.py"), str(OUT_DXF), str(OUT_JSON)],
        capture_output=True, text=True,
    )
    print("  ", (res.stdout or res.stderr).strip())
    if res.returncode != 0:
        sys.exit(res.returncode)

    print("[3/4] validate_cad_rules.py (HARUS 0 error)...")
    res = subprocess.run(
        UVX + ["python", str(SCRIPTS_DIR / "validate_cad_rules.py"),
               str(OUT_DXF), str(OUT_JSON)],
        capture_output=True, text=True,
    )
    print(res.stdout)
    if res.returncode != 0:
        print("VALIDATE FAILED:", res.stderr)
        sys.exit(res.returncode)

    print("[4/4] Snapshot PNG...")
    res = subprocess.run(
        UVX + ["cadgen", "dxf", "snapshot", str(OUT_DXF), str(OUT_PNG),
               "--width", "2400", "--height", "1700"],
        capture_output=True, text=True,
    )
    if res.returncode != 0:
        print("SNAPSHOT FAILED:", res.stdout or res.stderr)
        sys.exit(res.returncode)
    print(f"  saved snapshot: {OUT_PNG}")

    # [5/5] Pulihkan artefak demo workspace: langkah [1/4] menimpa
    # cad/alignment_demo.dxf dengan build mentah (keluaran model @dxf selalu
    # saudari script). Salin kembali DXF hasil apply_text yang barusan
    # divalidasi 0 error + PNG snapshot-nya, agar workspace tidak pernah
    # tertinggal DXF tanpa post-process (MTEXT/pens/SOLID manifest).
    print("[5/5] Restore workspace demo artifact (processed DXF + PNG)...")
    shutil.copyfile(OUT_DXF, src_dxf)
    shutil.copyfile(OUT_PNG, SCRIPTS_DIR / "alignment_demo.png")
    res = subprocess.run(
        UVX + ["python", str(SCRIPTS_DIR / "validate_cad_rules.py"),
               str(src_dxf), str(src_json)],
        capture_output=True, text=True,
    )
    status = res.stdout.strip().splitlines()[-1] if res.stdout.strip() else ""
    print(f"  workspace re-validate: {status}")
    if res.returncode != 0:
        print("WORKSPACE VALIDATE FAILED:", res.stderr)
        sys.exit(res.returncode)

    print(f"\nSUCCESS: {OUT_PNG}")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if len(sys.argv) > 1 and sys.argv[1] != "--test-runner":
        # Mode build langsung: delegasi ke demo model (pola test_plan_common)
        from cadgen import dxf as _dxf  # noqa: F401
        import alignment_demo
        alignment_demo.alignment_demo()
        return

    run_unit_tests()
    run_e2e_smoke()


if __name__ == "__main__":
    main()
