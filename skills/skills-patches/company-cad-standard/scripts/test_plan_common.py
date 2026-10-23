#!/usr/bin/env python3
"""Comprehensive Smoke Test & Test Suite for plan_common.py.

Exercises 100% of methods and components in PlanContext:
  - Coordinate conversions (P, inv_P, m2mm, mm2m)
  - Furniture: setup_a1_frame, setup_plant_grid, setup_plot_fence, setup_road
  - Equipment: horizontal_vessel, vertical_vessel, storage_tank, equipment_box, pipe_rack
  - Piping & Auto-trimming: plan_pipe_h, plan_pipe_v (with breaks and gaps)
  - Symbols: flow_arrow_plan, elbow_up, elbow_dn, tee_up, tee_dn,
             elbow_90_up, elbow_90_dn, pipe_rack_bay,
             plan_valve_gate (H & V), pipe_support_plan (ANCHOR & GUIDE),
             north_arrow_plan, coord_callout, matchline, battery_limit_arrow
  - Manifest primitives: text, solid_triangle, solid_quad, solid_dot, dimrec
  - Export: export_manifest, get_layers, save_manifest

Standard: ASME B31.3-2022, API STD 650 13th Ed. 2020, API Spec 12J, 8th Ed. (2008), R2023, API STD 521 7th Ed. 2020.
"""

from __future__ import annotations

import math
import os
import subprocess
import sys
from pathlib import Path

# Add current scripts directory to path
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from cadgen import dxf
from plan_common import (
    PlanContext,
    line,
    circle,
    arc,
    rect,
    dashed,
    dashed_circle,
    comp,
)

OUT_DIR = Path("/tmp/aud")
OUT_DXF = OUT_DIR / "plan_test.dxf"
OUT_JSON = OUT_DIR / "plan_test.texts.json"
OUT_PNG = OUT_DIR / "plan_test.png"


def build_test_plan(ctx: PlanContext) -> None:
    """Populate ctx exercising all methods of PlanContext."""
    # 1. Furniture
    ctx.setup_a1_frame(
        doc_no="GPF-00-PI-PLN-9999",
        title="PLAN COMMON FULL SMOKE TEST",
        rev="A0",
        scale_str="1:200 @ A1",
        date_str="23 OCT 2026",
    )
    ctx.setup_plant_grid(e_max=100.0, n_max=60.0, step_m=10.0)
    ctx.setup_plot_fence(0.0, 0.0, 100.0, 60.0)
    ctx.setup_road(8.0, 92.0, n_bot=40.0, n_top=43.0, tag="ACCESS ROAD")

    # 2. Equipment
    ctx.horizontal_vessel(
        e_center=14.0,
        n_center=34.0,
        length_m=7.6,
        diameter_m=2.3,
        tag="V-101",
        desc="3-PHASE SEPARATOR",
    )
    ctx.equipment_box(
        e0=20.5,
        n0=29.0,
        e1=23.5,
        n1=31.5,
        tag="P-101",
        desc="PUMP SKID",
    )
    # E-W Pipe Rack
    ctx.pipe_rack(e0=19.0, e1=58.0, n0=34.0, n1=36.0, bay_m=6.0)
    # N-S Pipe Rack Bay (using alias)
    ctx.pipe_rack_bay(e0=70.0, e1=72.0, n0=22.0, n1=32.0, bay_m=5.0)

    # Vertical vessel
    ctx.vertical_vessel(
        e_center=71.0,
        n_center=46.0,
        diameter_m=2.2,
        tag="V-102",
        desc="FLARE KO DRUM",
    )
    # Storage tank with bund wall and hatch
    ctx.storage_tank(
        e_center=69.0,
        n_center=12.0,
        diameter_m=6.0,
        bund_w_m=14.0,
        bund_l_m=12.0,
        tag="T-101",
        desc="CRUDE STORAGE",
    )

    # 3. Piping runs & auto-trimming
    # Line 1 (Major E-W Header, N=35.0, E=15.0..58.0)
    ctx.plan_pipe_h(n=35.0, e0=15.0, e1=58.0)
    ctx.elbow_up(e=15.0, n=35.0)
    ctx.flow_arrow_plan(e=25.0, n=35.0, ang_deg=0.0)
    ctx.pipe_support_plan(e=38.0, n=35.0, orient="H", tag="PS-101", stype="ANCHOR", dy_mm=12.0)
    ctx.pipe_support_plan(e=48.0, n=35.0, orient="H", tag="PS-102", stype="GUIDE", dy_mm=12.0)

    # Line 2 (Major E-W Header, N=22.0, E=20.0..95.0)
    ctx.plan_pipe_h(n=22.0, e0=20.0, e1=95.0)
    ctx.plan_valve_gate(e=28.0, n=22.0, orient="H", tag="GV-101")
    ctx.flow_arrow_plan(e=55.0, n=22.0, ang_deg=0.0)
    ctx.battery_limit_arrow(e=95.0, n=22.0, direction=1, tag="TO BATTERY LIMIT")

    # Line 3 (Minor N-S branch crossing Line 2 at N=22.0 -> breaks_n=[22.0])
    ctx.plan_pipe_v(e=44.0, n0=35.0, n1=8.0, breaks_n=[22.0])
    ctx.tee_dn(e=44.0, n=35.0, orient_deg=270.0)
    ctx.flow_arrow_plan(e=44.0, n=28.0, ang_deg=270.0)
    ctx.plan_valve_gate(e=44.0, n=16.0, orient="V", tag="GV-102")
    ctx.elbow_dn(e=44.0, n=8.0, orient_deg=90.0)

    # Line 4 testing aliases and additional symbols
    ctx.elbow_90_up(e=20.0, n=22.0)
    ctx.tee_up(e=35.0, n=22.0)
    ctx.elbow_90_dn(e=85.0, n=22.0, orient_deg=180.0)

    # 4. Anotasi & Callouts
    ctx.coord_callout(e=10.2, n=34.0, el_mm=3200, dx_mm=-15.0, dy_mm=12.0)
    ctx.coord_callout(e=71.0, n=47.1, dx_mm=12.0, dy_mm=10.0)
    ctx.north_arrow_plan(x_mm=580.0, y_mm=420.0, r_mm=12.0)
    ctx.matchline(e0=98.0, n0=5.0, e1=98.0, n1=55.0, label="MATCHLINE — SEE DWG GPF-00-PI-PLN-9998")

    # 5. Low-level manifest primitives
    ctx.dimrec(p1=(560.0, 160.0), p2=(660.0, 160.0), txt="20000", angle=0.0)
    ctx.solid_triangle((560.0, 170.0), (565.0, 175.0), (555.0, 175.0), layer="REF-SYM")
    ctx.solid_quad((570.0, 170.0), (575.0, 170.0), (575.0, 175.0), (570.0, 175.0), layer="REF-SYM")
    ctx.solid_dot(585.0, 172.5, r=1.0, layer="REF-SYM")


@dxf
def plan_test():
    """cadgen model function."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ctx = PlanContext(px0=40.0, py0=40.0, scale=5.0)
    build_test_plan(ctx)
    return ctx.export_manifest(OUT_JSON)


def run_unit_tests() -> None:
    """Run programmatic assertions on PlanContext."""
    print("Running unit tests on PlanContext...")
    ctx = PlanContext(px0=40.0, py0=40.0, scale=5.0)

    # Coordinate transformation test
    x, y = ctx.P(10.0, 20.0)
    assert abs(x - 90.0) < 1e-6 and abs(y - 140.0) < 1e-6, f"P failed: ({x}, {y})"
    e, n = ctx.inv_P(x, y)
    assert abs(e - 10.0) < 1e-6 and abs(n - 20.0) < 1e-6, f"inv_P failed: ({e}, {n})"

    assert abs(ctx.m2mm(2.0) - 10.0) < 1e-6, "m2mm failed"
    assert abs(ctx.mm2m(10.0) - 2.0) < 1e-6, "mm2m failed"

    # Empty layer test: get_layers should NEVER return empty layer
    empty_layers = ctx.get_layers()
    assert len(empty_layers) == 0, f"get_layers on empty context must be empty, got {list(empty_layers.keys())}"

    # After adding a line to REF-PROC, only REF-PROC should be returned
    ctx.plan_pipe_h(n=10.0, e0=0.0, e1=10.0)
    layers_with_pipe = ctx.get_layers()
    assert "REF-PROC" in layers_with_pipe, "REF-PROC must be in layers"
    assert "REF-GRID" not in layers_with_pipe, "REF-GRID must NOT be in layers when empty"
    assert "REF-HATCH" not in layers_with_pipe, "REF-HATCH must NOT be in layers when empty"

    print("Unit tests PASSED.")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # If run by cadgen CLI directly with arguments (like --force)
    if len(sys.argv) > 1 and sys.argv[1] != "--test-runner":
        plan_test()
        return

    # Run unit tests
    run_unit_tests()

    # Run end-to-end smoke test pipeline
    print("\nRunning full smoke test build pipeline...")
    # Step 1: Execute this script with cadgen to generate DXF
    cmd_build = [
        "uvx", "--no-config", "--managed-python", "--python", "3.13",
        "--from", "cadgen==0.7.21", "python", str(Path(__file__).resolve()), "--force"
    ]
    res_build = subprocess.run(cmd_build, cwd=str(OUT_DIR), capture_output=True, text=True)
    if res_build.returncode != 0:
        print("BUILD FAILED:", res_build.stderr or res_build.stdout)
        sys.exit(res_build.returncode)

    # Source cadgen outputs to test_plan_common.dxf next to script
    generated_dxf = SCRIPTS_DIR / "test_plan_common.dxf"
    if not generated_dxf.exists():
        generated_dxf = OUT_DIR / "test_plan_common.dxf"

    if generated_dxf.exists():
        if OUT_DXF.exists():
            OUT_DXF.unlink()
        import shutil
        shutil.move(str(generated_dxf), str(OUT_DXF))
    else:
        print(f"ERROR: Could not find generated DXF at {generated_dxf}")
        sys.exit(1)

    # Step 2: Apply texts and pens via apply_text.py
    apply_text_script = SCRIPTS_DIR / "apply_text.py"
    cmd_apply = [
        "uvx", "--no-config", "--managed-python", "--python", "3.13",
        "--from", "cadgen==0.7.21", "python", str(apply_text_script),
        str(OUT_DXF), str(OUT_JSON)
    ]
    res_apply = subprocess.run(cmd_apply, capture_output=True, text=True)
    if res_apply.returncode != 0:
        print("APPLY_TEXT FAILED:", res_apply.stderr or res_apply.stdout)
        sys.exit(res_apply.returncode)

    # Step 3: Validate CAD rules with validate_cad_rules.py
    validate_script = SCRIPTS_DIR / "validate_cad_rules.py"
    cmd_val = [
        "uvx", "--no-config", "--managed-python", "--python", "3.13",
        "--from", "cadgen==0.7.21", "python", str(validate_script),
        str(OUT_DXF), str(OUT_JSON), "--mode", "plan"
    ]
    res_val = subprocess.run(cmd_val, capture_output=True, text=True)
    print(res_val.stdout)
    if res_val.returncode != 0:
        print("VALIDATE CAD RULES FAILED:", res_val.stderr)
        sys.exit(res_val.returncode)

    # Step 4: Render snapshot PNG
    cmd_snap = [
        "uvx", "--no-config", "--managed-python", "--python", "3.13",
        "--from", "cadgen==0.7.21", "cadgen", "dxf", "snapshot",
        str(OUT_DXF), str(OUT_PNG), "--width", "2400", "--height", "1700"
    ]
    res_snap = subprocess.run(cmd_snap, capture_output=True, text=True)
    if res_snap.returncode != 0:
        print("SNAPSHOT FAILED:", res_snap.stderr or res_snap.stdout)
        sys.exit(res_snap.returncode)

    print(f"\nSUCCESS: plan_test.png rendered to {OUT_PNG}")


if __name__ == "__main__":
    main()
