#!/usr/bin/env python3
"""Integration Test & Visual QA untuk company-cad-standard air_system_common.py.

Membangun seluruh komponen sistem udara tekan (kompresor screw, aftercooler,
cyclone trap, receiver, filter inline, menara desiccant, PCV, PLC, auto drain,
muffler) dalam satu kanvas terpadu, mengekspor manifest, menjalankan
apply_text.py, mengevaluasi aturan CAD via validate_cad_rules.py, dan
merender visual ke /tmp/aud/test_air_system_common.png.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from cadgen import dxf
import air_system_common as asc
import pid_common as pc


@dxf
def test_air_drawing():
    c = asc.AirSystemContext()

    # 1. Border & Title Frame
    c.frame += pc.rect(10.0, 10.0, 690.0, 290.0)
    c.title += pc.rect(500.0, 20.0, 680.0, 70.0)
    c.text("COMPANY ENGINEERING STANDARD", 590.0, 60.0, size=2.5)
    c.text("AIR_SYSTEM_COMMON V1 COMPONENT SHOWCASE", 590.0, 50.0, size=2.2)
    c.text("DWG NO: GPF-00-PI-PID-0014", 590.0, 38.0, size=2.0)

    # 2. Jalur utama y = 150: intake -> kompresor -> aftercooler -> filter
    c.proc += pc.pipe_run_h(150.0, 40.0, 46.0)
    c.flow_arrow_h(43.0, 150.0, direction=1)
    c.filter_body_h(60.0, 150.0, w=24.0, h=14.0, tag="SF-501", desc="INTAKE FILTER")
    c.proc += pc.pipe_run_h(150.0, 72.0, 117.5)
    c.flow_arrow_h(90.0, 150.0, direction=1)
    c.compressor_screw(140.0, 150.0, tag="K-501")
    c.proc += pc.pipe_run_h(150.0, 162.5, 180.0)
    c.flow_arrow_h(171.0, 150.0, direction=1)
    c.aftercooler_h(200.0, 150.0, w=40.0, h=14.0, tag="E-501")
    c.proc += pc.pipe_run_h(150.0, 220.0, 237.0)
    c.flow_arrow_h(228.0, 150.0, direction=1)
    c.filter_body_h(250.0, 150.0, w=26.0, h=14.0, tag="F-501",
                    desc="PREFILTER 1-3 MICRON", drain=True)
    c.proc += pc.pipe_run_h(150.0, 263.0, 292.0)
    c.flow_arrow_h(272.0, 150.0, direction=1)

    # 3. Cyclone moisture trap (standalone, internally connected)
    c.moisture_trap_cyclone(300.0, 160.0, r=8.0, shell_h=32.0, cone_h=10.0,
                            tag="S-501 MOISTURE TRAP", tag_y=88.0)

    # 4. Receiver + menara desiccant (standalone)
    c.air_receiver_v(350.0, 110.0, 150.0, r=13.0, tag="V-502 WET AIR RECEIVER")
    c.desiccant_tower(400.0, 110.0, 150.0, r=10.0, tag="TOWER A - DRYING", tag_y=181.5)

    # 5. Priority valve PCV pada riser + PLC + muffler + auto drain + orifice
    c.proc += pc.pipe_run_v(450.0, 120.0, 180.0, gaps=[(150.0, 6.5)])
    c.flow_arrow_v(450.0, 120.0, direction=1, size=2.4)
    c.flow_arrow_v(450.0, 180.0, direction=1)
    c.priority_valve_v(450.0, 150.0, tag="PCV-501", tag_pos=(438.0, 150.0), act=1,
                       note="CLOSES AT < 5.5 BARG", note_pos=(436.0, 143.0))
    c.flow_arrow_v(450.0, 132.0, direction=1, size=2.4)
    c.flow_arrow_v(450.0, 174.0, direction=1)
    c.plc_timer(450.0, 200.0, w=16.0, h=8.0, tag="PLC")
    c.sig += pc.dashed(450.0, 196.0, 450.0, 180.0, dash=2.5, gap=1.2)

    c.proc += pc.pipe_run_h(120.0, 500.0, 520.0)
    c.flow_arrow_h(500.0, 120.0, direction=1, size=2.4)
    c.muffler_vent_h(520.0, 120.0)
    c.flow_arrow_h(512.0, 120.0, direction=1)
    c.text("TO ATMOSPHERE", 524.0, 126.0, size=1.8)

    c.auto_drain_v(560.0, 160.0, arrow=True)

    c.proc += pc.pipe_run_h(120.0, 580.0, 620.0)
    c.flow_arrow_h(580.0, 120.0, direction=1, size=2.4)
    c.flow_arrow_h(620.0, 120.0, direction=1)
    c.orifice_plate_v(600.0, 120.0)
    c.flow_arrow_h(590.0, 120.0, direction=1)

    # 6. Registrasi jalur & instrumen + ekspor manifest
    c.register_line("080-IA-5001", spec="A1A", service="Instrument Air", dn=50)
    c.register_line("080-UA-5002", spec="A1A", service="Utility Air", dn=50)

    out_dir = Path("/tmp/aud")
    out_dir.mkdir(parents=True, exist_ok=True)
    c.export_schedules(out_dir / "test_air_system_common.schedules.json")
    return c.export_manifest(out_dir / "test_air_system_common.texts.json")


def run_pipeline():
    script_dir = Path(__file__).resolve().parent
    test_drawing_dxf = script_dir / "test_air_system_common.dxf"
    texts_json = Path("/tmp/aud/test_air_system_common.texts.json")
    png_out = Path("/tmp/aud/test_air_system_common.png")

    # 1. Jalankan test_air_drawing untuk membangun DXF
    print("[1/4] Menjalankan test_air_drawing (cadgen/dxf)...")
    test_air_drawing()

    dxf_dest = Path("/tmp/aud/test_air_system_common.dxf")
    if test_drawing_dxf.exists():
        test_drawing_dxf.rename(dxf_dest)

    # 2. Jalankan apply_text.py bila tersedia
    print("[2/4] Menjalankan apply_text.py...")
    script_dir = Path(__file__).resolve().parent
    apply_text_py = script_dir / "apply_text.py"
    if not apply_text_py.exists():
        apply_text_py = Path("/tmp/aud/apply_text.py")

    if apply_text_py.exists() and dxf_dest.exists() and texts_json.exists():
        ret = subprocess.run(
            [sys.executable, str(apply_text_py), str(dxf_dest), str(texts_json)],
            capture_output=True, text=True,
        )
        print("  apply_text stdout:", ret.stdout.strip())
        if ret.returncode != 0:
            print("  apply_text stderr:", ret.stderr.strip())

    # 3. Jalankan validate_cad_rules.py bila tersedia
    print("[3/4] Menjalankan validate_cad_rules.py...")
    val_py = script_dir / "validate_cad_rules.py"
    if not val_py.exists():
        val_py = Path("/tmp/aud/validate_cad_rules.py")

    if val_py.exists() and dxf_dest.exists():
        cmd = [sys.executable, str(val_py), str(dxf_dest)]
        if texts_json.exists():
            cmd.append(str(texts_json))
        ret = subprocess.run(cmd, capture_output=True, text=True)
        print(ret.stdout)
        if ret.returncode != 0:
            print("  validate_cad_rules stderr:", ret.stderr.strip())

    # 4. Render ke PNG menggunakan ezdxf draw
    print(f"[4/4] Merender visual ke {png_out}...")
    ezdxf_bin = Path(sys.executable).parent / "ezdxf"
    if not ezdxf_bin.exists():
        ezdxf_bin = Path("/home/arienugraha-rei/.local/bin/ezdxf")

    if dxf_dest.exists() and ezdxf_bin.exists():
        ret = subprocess.run(
            [str(ezdxf_bin), "draw", "-o", str(png_out), "--background", "WHITE",
             "--force", str(dxf_dest)],
            capture_output=True, text=True,
        )
        if ret.returncode == 0:
            print(f"  Visual PNG berhasil disimpan: {png_out}")
        else:
            print("  ezdxf draw stderr:", ret.stderr.strip())


if __name__ == "__main__":
    run_pipeline()
