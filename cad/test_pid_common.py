#!/usr/bin/env python3
"""Comprehensive Integration Test & Visual QA for company-cad-standard pid_common.py.

Membangun seluruh komponen peralatan proses, katup, instrumen, dan rakitan macro
dalam satu kanvas terpadu, mengekspor manifest, menjalankan apply_text.py,
mengevaluasi aturan CAD via validate_cad_rules.py, dan merender visual ke /tmp/aud/test_pid_common.png.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from cadgen import dxf
import pid_common as pc


@dxf
def test_pid_drawing():
    c = pc.PIDContext()

    # 1. Border & Title Frame (A1 Sheet ISO 5457)
    c.frame += pc.rect(10.0, 10.0, 831.0, 584.0)
    c.title += pc.rect(655.0, 15.0, 823.0, 116.0)
    c.text("COMPANY ENGINEERING STANDARD", 739.0, 95.0, size=2.5)
    c.text("PID_COMMON V2 COMPONENT SHOWCASE", 739.0, 80.0, size=2.2)
    c.text("DWG NO: GPF-00-PI-PID-0001", 739.0, 65.0, size=2.0)

    # 2. Baris Atas: Katalog Peralatan Proses (y ~ 380..520)
    # (a) Knock-Out Drum V-102 dengan Demister & ISO Cross Plate Vortex Breaker
    c.equip += c.vessel_vertical_ko(cx=80.0, y_bot=380.0, y_top=480.0, r=18.0, tag="V-102", demister=True)

    # (b) Tangki Timbun Atmosferik T-101 (bund=False, P&ID default)
    c.equip += c.storage_tank_atm(cx=200.0, y_bot=380.0, w=48.0, h_shell=36.0, h_roof=8.0, tag="T-101", bund=False)

    # (c) Tangki Timbun T-102 dengan Tanggul Bundwall (bund=True)
    c.equip += c.storage_tank_atm(cx=320.0, y_bot=380.0, w=44.0, h_shell=34.0, h_roof=8.0, tag="T-102", bund=True)

    # (d) Shell & Tube Heat Exchanger E-101 (Channel Spool & Semicircular Heads)
    c.equip += c.heat_exchanger_st(cx=450.0, cy=430.0, length=44.0, r=10.0, tag="E-101")

    # (e) Kompresor Sentrifugal K-101 (Nozzle Suction + Discharge Flanged)
    c.equip += c.compressor_centrifugal(cx=570.0, cy=430.0, r_in=6.0, r_out=9.0, tag="K-101")

    # (f) Pig Launcher PL-101 (aliran ke kanan) & Receiver PR-101 (aliran ke kiri)
    c.equip += c.pig_trap(cx=690.0, cy=465.0, length=36.0, direction=1, tag="PL-101")
    c.equip += c.pig_trap(cx=690.0, cy=395.0, length=36.0, direction=-1, tag="PR-101")

    # 3. Baris Tengah: Jalur Pipa Proses Utama & Katup (y = 260)
    c.proc += c.continuity_box_left(y=260.0, tag="100-GO-1001", desc="GAS FROM WELLHEAD", dwg="GPF-00-PI-PID-0000")

    # Katup & inline fitting di sepanjang jalur utama y=260
    # Reducer: cx=115, FE orifice: cx=150
    c.proc += c.reducer_h(cx=115.0, cy=260.0, w=8.0, h1=5.0, h2=8.0, label="DN150x100")
    c.proc += c.orifice_h(cx=150.0, cy=260.0, tag_fe="FE-101")

    # Control Valve Bypass Station lengkap di cx=240, cy=260
    gap_cv = c.control_valve_station_h(
        cx=240.0,
        cy=260.0,
        cv_tag="PV-101",
        gv_up_tag="GV-101A",
        gv_dn_tag="GV-101B",
        bp_tag="BV-101",
        fail="FC",
        span=56.0,
        bypass_dy=18.0,
    )

    # Check Valve: cx=330
    c.proc += c.valve_check_h(cx=330.0, cy=260.0, w=10.0, h=6.0)
    c.text("NRV-101", 330.0, 253.0, size=1.8)

    # Shutdown Valve (SDV): cx=380
    c.proc += c.sdv_h(cx=380.0, cy=260.0, tag="SDV-101", fail="FC")

    # Angle PSV terpasang pada cabang tee vertikal di x=440, cy=276
    c.proc += c.psv_angle(cx=440.0, cy=276.0, tag="PSV-101", size_str="DN50x80", set_press="SET 25 BARG")
    c.proc += [
        pc.line(440.0, 260.0, 440.0, 276.0 - 9.2),
        pc.line(440.0 + 9.2, 276.0, 460.0, 276.0),  # Pipa discharge PSV ke flare cap
        pc.line(460.0, 273.5, 460.0, 278.5),
    ]

    # Spec Break horizontal: x=495
    c.proc += c.spec_break_h(x=495.0, y=260.0, left_spec="150# A1A", right_spec="300# B1A")

    # Stream Flag PFD: x=555
    c.sym += c.stream_flag_h(x=555.0, y=260.0, stream_no="01", p_barg="18.5", t_degc="38", flow_kgh="28500")

    # Pipa utama y=260 dengan pemotongan gap rapi
    gaps_main = [
        (115.0, 4.0),   # Reducer w=8
        (150.0, 1.2),   # Orifice plate
        gap_cv,         # CV Station (cx=240, hw=28)
        (330.0, 5.0),   # Check valve w=10
        (380.0, 6.2),   # SDV w=10 + flg
        (555.0, 4.0),   # Stream flag diamond r=4
    ]
    c.proc += pc.pipe_run_h(260.0, 68.0, 585.0, gaps=gaps_main)
    c.proc += c.continuity_box_right(y=260.0, tag="100-GO-1002", desc="GAS TO COMPRESSION", dwg="GPF-00-PI-PID-0002")

    # Flow arrows pada jalur utama
    c.proc += c.flow_arrow_h(90.0, 260.0, direction=1)
    c.proc += c.flow_arrow_h(300.0, 260.0, direction=1)
    c.proc += c.flow_arrow_h(470.0, 260.0, direction=1)

    # 4. Baris Bawah: Peralatan Utility, Pompa & Instrumen (y ~ 100..200)
    # (a) Pompa Sentrifugal P-101A & Motor Listrik M-101A
    c.equip += c.pump_centrifugal(cx=100.0, cy=140.0, r=8.0)
    c.equip += c.electric_motor(cx=80.0, cy=140.0, r=5.5, tag="M")
    c.text("P-101A", 100.0, 122.0, size=2.5)

    # Strainer vertikal pada jalur suction pompa dengan cap blind flange
    c.proc += c.strainer_v(cx=100.0, cy=180.0, tag="ST-101")
    c.proc += pc.pipe_run_v(100.0, 148.0, 210.0, gaps=[(180.0, 6.2)])
    c.proc += [pc.line(97.0, 210.0, 103.0, 210.0)]
    c.proc += c.flow_arrow_v(100.0, 160.0, direction=-1)

    # Katup vertikal pada pipa discharge pompa dengan cap blind flange
    c.proc += c.valve_gate_v(cx=135.0, cy=140.0, w=6.0, h=10.0, tag="GV-102")
    c.proc += pc.pipe_run_h(140.0, 108.0, 150.0)
    c.proc += [pc.line(150.0, 137.5, 150.0, 142.5)]

    # (b) Level Bridle Tertutup V-102 LG/LT
    c.level_bridle(
        x_pipe=200.0,
        y_shell_bot=100.0,
        y_tap_bot=120.0,
        y_tap_top=180.0,
        lg_tag="LG-101",
        lt_bpcs=("LT", "101"),
        lt_sis=("LT", "102"),
    )

    # (c) Lingkaran Instrumen ANSI/ISA-5.1
    c.sym += c.bubble(310.0, 140.0, "PT", "101")
    c.sig += pc.dashed(200.0 + 15.0, 140.0, 310.0 - pc.BUBBLE_R, 140.0, dash=2.5, gap=1.2)

    c.sym += c.dcs(360.0, 140.0, "PIC", "101")
    c.sig += pc.dashed(310.0 + pc.BUBBLE_R, 140.0, 360.0 - pc.BUBBLE_R, 140.0, dash=2.5, gap=1.2)

    c.sym += c.sis_box(430.0, 140.0, "PSHH", "101")
    c.sig += pc.dashed(360.0 + pc.BUBBLE_R, 140.0, 430.0 - 8.0, 140.0, dash=2.5, gap=1.2)

    c.sym += c.interlock_diamond(490.0, 140.0, tag="ESD-1", r=5.0)
    c.sig += pc.dashed(430.0 + 8.0, 140.0, 490.0 - 5.0, 140.0, dash=2.5, gap=1.2)

    # (d) Spec Break vertikal pada pipa utility dengan cap ujung atas dan bawah
    c.proc += c.spec_break_v(x=550.0, y=140.0, bot_spec="150# A1A", top_spec="300# B1A")
    c.proc += pc.pipe_run_v(550.0, 90.0, 190.0)
    c.proc += [
        pc.line(547.0, 190.0, 553.0, 190.0),
        pc.line(547.0, 90.0, 553.0, 90.0),
    ]

    # 5. Registrasi Jalur Pipa & Ekspor Manifest
    c.register_line("100-GO-1001", spec="150# A1A", service="Gas Inlet", dn=100)
    c.register_line("100-GO-1002", spec="300# B1A", service="Gas Compression", dn=100)

    out_dir = Path("/tmp/aud")
    out_dir.mkdir(parents=True, exist_ok=True)
    c.export_schedules(out_dir / "test_pid_common.schedules.json")
    return c.export_manifest(out_dir / "test_pid_common.texts.json")


def run_pipeline():
    test_drawing_dxf = Path("test_pid_common.dxf")
    texts_json = Path("/tmp/aud/test_pid_common.texts.json")
    png_out = Path("/tmp/aud/test_pid_common.png")

    # 1. Jalankan test_pid_drawing untuk membangun DXF
    print("[1/4] Menjalankan test_pid_drawing (cadgen/dxf)...")
    test_pid_drawing()

    # Pindahkan / pastikan file DXF di /tmp/aud
    dxf_dest = Path("/tmp/aud/test_pid_common.dxf")
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
            capture_output=True,
            text=True,
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
            [str(ezdxf_bin), "draw", "-o", str(png_out), "--background", "WHITE", "--force", str(dxf_dest)],
            capture_output=True,
            text=True,
        )
        if ret.returncode == 0:
            print(f"  Visual PNG berhasil disimpan: {png_out}")
        else:
            print("  ezdxf draw stderr:", ret.stderr.strip())


if __name__ == "__main__":
    run_pipeline()
