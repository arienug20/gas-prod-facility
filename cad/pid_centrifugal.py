"""P&ID GPF-00-PI-PID-0021 Rev A0 — NATURAL GAS COMPRESSION, CENTRIFUGAL, 2X50% PARALLEL.

Sheet A1 (841 x 594 mm), origin kiri-bawah. STANDALONE PACKAGE (basis desain
per PM instruction 26 OCT 2026, di luar GPF-00-DB-0001).

Skema: suapan gas lapangan 250 PSIG -> suction header 150-NG-9001 -> 2 x 50%
train (A band atas, B band bawah, identik & simetris). Tiap train:
SDV -> FT/PT/PI/TI -> SUCTION SCRUBBER (API 12J) -> K-30xA sentrifugal API 617
barrel + DGS, motor M -> CV -> PT/TT -> FIN-FAN AFTERCOOLER API 661 (TIC-303/
304 auto louver) -> COALESCING FILTER SEPARATOR -> discharge header 150-NG-9010
-> FE/FT-341 + FIQ -> BL TO SALES PIPELINE 450 PSIG.
Proteksi: loop anti-surge per train (PT/TT suc+dis + FT -> UIC -> ASV fast
opening <= 1 s w/ booster relay FY; recycle 100-NG-9021/9022 ke inlet scrubber),
PSV scrubber + BDV suction/discharge ke BD header 080-FL-9031 -> FLARE KO DRUM.
ESD-3 (SIS): PT-341 PSHH / LSL LSLL scrubber / SURGE UIC -> close SDV + trip M
(cause & effect di NOTE 4).

Penomoran loop instrumen (unik, satu loop satu fungsi):
  train A = seri 301, train B = seri 302; pasangan TT/TIC outlet cooler
  A/B = 303/304 (lihat NOTE 7).

Standar acuan: API STD 617, API STD 661 / ISO 13706, API Spec 12J, API STD 521,
ANSI/ISA-5.1-2024, ISO 10628-2:2012, ISO 5457, ISO 7200.

Layers:
  REF-FRAME  border lembar, grid referensi, kotak tabel furniture
  REF-TITLE  title block + rev table (ISO 7200 / Company Standard)
  REF-EQUIP  vessel, kompresor, fin-fan, coalescer, baseplate
  REF-PROC   line proses, valves, PSV, orifice, BL/continuity boxes
  REF-SYM    bubbles instrumen, DCS/UIC, louver, ESD/SIS box, mini legend
  REF-SIG    signal listrik (dashed 4.0 / 1.6)
  REF-SIGP   signal pneumatic (solid + "//")
  REF-HATCH  arsiran 45 deg demister/coalescer
  REF-TEXT   ditulis post-build oleh apply_text.py dari manifest TEXTS (ARIAL)
"""

from __future__ import annotations

from pathlib import Path

from cadgen import dxf
from pid_common import (
    PIDContext,
    circle,
    dashed,
    dashed_brk,
    hatch45,
    line,
    pipe_run_h,
    pipe_run_v,
    pneu,
    rect,
)
from compression_common import CompressionContext

# Nomor dokumen & data judul
DOC_NO = "GPF-00-PI-PID-0021"
REV = "A0"
DATE_SHORT = "26 OCT 26"
DATE_LONG = "26 OCT 2026"
TITLE_2 = "NATURAL GAS COMPRESSION - CENTRIFUGAL 2 X 50%"


# =============================================================================
# SATU TRAIN (A = band atas, B = band bawah; L = y line proses train)
# =============================================================================
def build_train(ctx: CompressionContext, sfx: str, loop: int, L: float, is_a: bool) -> None:
    """Menggambar satu train kompresi lengkap pada band y=L.

    Geometri relatif terhadap L (line proses):
      yd   = L-6   discharge line
      yr   = L-80  recycle line (A: 376, B: 148)
      UIC  = (403, L-52); ASV di asv_x (A: 255, B: 285)
    """
    yd = L - 6.0
    yr = L - 80.0
    asv_x = 290.0 if is_a else 285.0
    tag = lambda n: f"{n}-{loop}"  # noqa: E731

    # ------------------------------------------------------------------
    # 1. SUCTION BRANCH (header x=62 -> scrubber inlet stub x=218)
    # ------------------------------------------------------------------
    # SDV-3x1 (ESD, fail close, solenoid SY)
    ctx.proc += pipe_run_h(L, 62.0, 218.0, gaps=[(95.0, 6.2), (128.0, 1.2)])
    ctx.proc += ctx.sdv_h(95.0, L, tag=tag("SDV"), fail="FC")
    ctx.sym += ctx.interlock_diamond(95.0, L + 24.0, tag="ESD-3")
    ctx.sig += dashed(95.0, L + 12.5, 95.0, L + 19.0)
    ctx.flow_arrow_h(78.0, L, direction=1, size=2.2)
    if is_a:
        ctx.text("150-NG-9002 DN150", 75.0, L + 7.0, size=1.8)
    else:
        ctx.text("150-NG-9003 DN150", 95.0, L - 17.0, size=1.8)

    # FE-3x1 orifice + FT-3x1 (untuk anti-surge) + PT + PI + TI
    ctx.proc += ctx.orifice_h(128.0, L, tag_fe="")
    ctx.sym += ctx.bubble(128.0, L - 16.0, "FT", str(loop))
    ctx.proc += [line(128.0, L, 128.0, L - 10.0)]
    ctx.sig += dashed(128.0, L - 22.0, 128.0, L - 38.0)
    ctx.text(f"FE-{loop}", 120.0, L - 9.0, size=1.8, rot=90.0)
    ctx.proc += [line(148.0, L, 148.0, L - 10.0)]
    ctx.sym += ctx.bubble(148.0, L - 16.0, "PT", str(loop))
    ctx.sig += dashed(148.0, L - 22.0, 148.0, L - 42.0)
    ctx.proc += [line(162.0, L, 162.0, L + 6.0)]
    ctx.sym += ctx.bubble(162.0, L + 12.0, "TI", str(loop))
    ctx.proc += [line(178.0, L, 178.0, L + 6.0)]
    ctx.sym += ctx.bubble(178.0, L + 12.0, "PI", str(loop))
    # Train B: panah pertama digeser ke x=84 agar tidak menutup break 3 mm
    # pada drop drain x=75 yang melintasi garis hisap train B (QA finding 4).
    ctx.flow_arrow_h(78.0 if is_a else 84.0, L, direction=1, size=2.2)
    for ax in (115.0, 155.0, 190.0, 207.0):
        ctx.flow_arrow_h(ax, L, direction=1, size=2.2)

    # BD suction tap (BDV train) — drop ke BD sub-header (A: y=350, B: y=142)
    y_bd_hdr = 350.0 if is_a else 142.0
    x_bd_suc = 140.0 if is_a else 112.0
    bd_suc_brks = []  # persilangan sinyal di-break pada sinyalnya (bus UIC)
    ctx.proc += pipe_run_v(x_bd_suc, y_bd_hdr, L, gaps=bd_suc_brks)
    ctx.flow_arrow_v(x_bd_suc, L - 15.0, direction=-1, size=2.2)
    ctx.flow_arrow_v(x_bd_suc, L - 60.0, direction=-1, size=2.2)

    # ------------------------------------------------------------------
    # 2. SUCTION SCRUBBER V-30xA (API 12J) + bridle LT/LG + SIS LAHH/LSLL
    # ------------------------------------------------------------------
    scr = ctx.suction_scrubber(
        240.0, L - 60.0, L + 55.0, r=20.0, tag=f"V-301{sfx}",
        service="SUCTION SCRUBBER", inlet_y=L,
    )

    # Level bridle manual (standpipe + taps + LG + 2 LT + SIS box)
    y_arc = (L - 60.0) - 10.0 + 25.0 - 21.9  # head arc di x=252
    x_sp, y_tapb, y_tapt = 252.0, L - 54.0, L - 4.0
    ctx.equip += [
        line(x_sp, y_arc, x_sp, y_tapt),
        line(x_sp, y_tapt, x_sp + 3.5, y_tapt),
        ctx.valve_gate_h(x_sp + 6.0, y_tapt, w=5.0, h=3.2, flanged=False),
        line(x_sp + 8.5, y_tapt, x_sp + 12.0, y_tapt),
        line(x_sp, y_tapb, x_sp + 3.5, y_tapb),
        ctx.valve_gate_h(x_sp + 6.0, y_tapb, w=5.0, h=3.2, flanged=False),
        line(x_sp + 8.5, y_tapb, x_sp + 12.0, y_tapb),
    ]
    ctx.sym += [
        line(x_sp + 12.0, y_tapb, x_sp + 12.0, y_tapt),
        line(x_sp + 15.0, y_tapb, x_sp + 15.0, y_tapt),
        line(x_sp + 12.0, y_tapb, x_sp + 15.0, y_tapb),
        line(x_sp + 12.0, y_tapt, x_sp + 15.0, y_tapt),
    ]
    ctx.text(f"LG-30{1 if is_a else 2}", x_sp + 13.5, y_tapt + 5.0, size=2.0)
    # LT (level ke DCS) ditempatkan DI ATAS kedua bus sinyal UIC (L-38/L-42)
    # agar dashed tidak menembus interior bubble (QA finding 3); LSL (SIS)
    # tetap di dekat tap bawah dan melayani kotak LAHH/LSLL.
    y_lt1, y_lt2 = L - 28.0, y_tapt - 11.0
    ctx.sym += ctx.bubble(x_sp + 28.0, y_lt1, "LT", str(loop))
    ctx.sig += dashed_brk(x_sp + 15.0, y_lt1, x_sp + 22.0, y_lt1, brk=[(272.0 - x_sp - 15.0)])
    ctx.sym += ctx.bubble(x_sp + 28.0, y_lt2, "LSL", str(loop))
    ctx.sig += dashed_brk(x_sp + 15.0, y_lt2, x_sp + 22.0, y_lt2, brk=[(272.0 - x_sp - 15.0)])
    ctx.sym += ctx.sis_box(x_sp + 46.0, y_lt2, "LAHH", "LSLL")
    ctx.sig += dashed(x_sp + 34.0, y_lt2, x_sp + 38.0, y_lt2)
    y_toesd = (y_lt2 + 11.0) if is_a else (y_lt2 - 13.0)
    ctx.text("TO ESD-3", x_sp + 46.0, y_toesd, size=1.8)

    # PSV-30xA (stub atas sudah digambar pustaka; valve + isolasi CSO)
    y_psv = L + 84.0
    ctx.proc += pipe_run_v(232.0, L + 68.2, y_psv - 8.0, gaps=[(L + 72.5, 2.6)])
    ctx.proc += ctx.valve_gate_v(232.0, L + 72.5, w=3.2, h=5.0, flanged=False)
    ctx.text("CSO", 238.0, L + 72.5, size=1.8)
    ctx.proc += ctx.psv_angle(
        232.0, y_psv, tag=f"PSV-30{1}{sfx}", size_str="DN80x150", set_press="SET 34.5 BARG"
    )
    # Tail PSV ke kanan lalu drop gabungan x=272
    ctx.proc += [line(241.2, y_psv, 272.0, y_psv)]
    y_tee = (L + 84.0) if is_a else 319.0
    if is_a:
        ctx.proc += pipe_run_v(272.0, 319.0, 534.0, gaps=[(526.0, 1.5), (370.0, 1.5), (350.0, 1.5)])
        ctx.flow_arrow_h(255.0, 534.0, direction=1, size=2.0)
        ctx.flow_arrow_v(272.0, 490.0, direction=-1, size=2.2)
    else:
        ctx.proc += pipe_run_v(272.0, 95.0, 319.0, gaps=[(313.0, 1.5), (155.0, 1.5), (142.0, 1.5)])
        ctx.flow_arrow_h(255.0, 319.0, direction=1, size=2.0)
        ctx.flow_arrow_v(272.0, 290.0, direction=-1, size=2.2)
        ctx.flow_arrow_v(272.0, 240.0, direction=-1, size=2.2)
        ctx.flow_arrow_v(272.0, 180.0, direction=-1, size=2.2)
        ctx.flow_arrow_v(272.0, 120.0, direction=-1, size=2.2)
    _ = y_tee, scr

    # Drain LV bawah scrubber
    if is_a:
        ctx.proc += pipe_run_v(240.0, 356.0, 373.8, gaps=[(370.0, 1.5)])
        ctx.proc += pipe_run_h(356.0, 75.0, 240.0, gaps=[(150.0, 6.2), (140.0, 1.5)])
        ctx.proc += ctx.control_valve_h(150.0, 356.0, tag="LV-301")
        ctx.text("LV-301", 150.0, 344.0, size=1.8)
        ctx.proc += pipe_run_v(75.0, 95.0, 356.0, gaps=[(235.0, 1.5)])
        ctx.flow_arrow_v(240.0, 366.0, direction=-1, size=2.0)
        ctx.flow_arrow_h(110.0, 356.0, direction=-1, size=2.0)
        ctx.flow_arrow_v(75.0, 320.0, direction=-1, size=2.2)
        ctx.flow_arrow_v(75.0, 200.0, direction=-1, size=2.2)
        ctx.flow_arrow_v(75.0, 130.0, direction=-1, size=2.2)
    else:
        ctx.drain_lv_h(
            240.0, L - 76.2, 128.0, 95.0, tag_lv="LV-303", breaks1=(142.0, 155.0)
        )
        ctx.flow_arrow_v(240.0, 145.0, direction=-1, size=2.0)
        ctx.flow_arrow_v(258.0, 115.0, direction=-1, size=2.2)

    # ------------------------------------------------------------------
    # 3. KOMPRESOR SENTRIFUGAL K-30xA (API 617 BARREL + DGS), driver M
    # ------------------------------------------------------------------
    ctx.compressor_centrifugal_617(
        330.0, L, r_in=5.0, r_out=8.0, tag="", casing="BARREL", driver="M"
    )
    # Konektor pendek shaft/kopling ke dinding casing (pustaka menyisakan gap)
    ctx.equip += [line(320.0, L, 322.5, L), line(345.0, L, 346.6, L)]
    ctx.text(f"K-30{1}{sfx}", 330.0, L - 20.0, size=2.5)
    ctx.text("DRY GAS SEAL (DGS)", 330.0, L - 26.0, size=1.8)

    # Gas outlet scrubber -> kompresor (masuk dinding kiri barrel di L+7)
    y_gas_h = L + 76.0 if is_a else L + 78.0
    ctx.proc += pipe_run_v(248.0, L + 68.2, y_gas_h)
    ctx.proc += pipe_run_h(y_gas_h, 248.0, 300.0)
    ctx.proc += pipe_run_v(300.0, L + 7.0, y_gas_h)
    ctx.proc += pipe_run_h(L + 7.0, 300.0, 320.0)
    ctx.flow_arrow_h(260.0, y_gas_h, direction=1, size=2.2)
    ctx.flow_arrow_v(300.0, y_gas_h - 15.0, direction=-1, size=2.2)
    ctx.flow_arrow_h(310.0, L + 7.0, direction=1, size=2.0)

    # ------------------------------------------------------------------
    # 4. DISCHARGE (yd = L-6): CV -> PT/TT -> tap ASV -> FIN-FAN -> coalescer
    # ------------------------------------------------------------------
    ctx.proc += pipe_run_h(yd, 340.0, 435.0, gaps=[(376.0, 6.2)])
    ctx.proc += ctx.valve_check_h(376.0, yd, w=10.0, h=6.0)
    ctx.proc += pipe_run_h(yd, 475.0, 497.8)
    ctx.proc += [line(396.0, yd, 396.0, yd + 10.0)]
    ctx.sym += ctx.bubble(396.0, yd + 16.0, "PT", str(loop))
    ctx.proc += [line(410.0, yd, 410.0, yd + 10.0)]
    ctx.sym += ctx.bubble(410.0, yd + 16.0, "TT", str(loop))
    for ax in (360.0, 388.0, 403.0, 427.0):
        ctx.flow_arrow_h(ax, yd, direction=1, size=2.2)
    ctx.text(f"100-NG-901{1 if is_a else 2} DN100", 370.0, L + 6.0, size=1.8)

    # FIN-FAN AFTERCOOLER E-301A/B + TIC auto louver (pasangan TT/TIC-303/304)
    ctx.fin_fan_cooler(455.0, yd, tag=f"E-30{1}{sfx}", hw=25.0, tee_dx=20.0)
    ctx.text(
        f"E-30{1}{sfx} AFTERCOOLER (FIN-FAN)", 455.0, yd + 57.0, size=2.5
    )
    ctx.proc += [line(492.0, yd, 492.0, yd + 10.0)]
    ttc = "303" if is_a else "304"  # loop khusus pasangan TT/TIC outlet cooler
    ctx.sym += ctx.bubble(492.0, yd + 16.0, "TT", ttc)
    ctx.sym += ctx.bubble(492.0, yd + 34.0, "TIC", ttc)
    ctx.sig += dashed(492.0, yd + 22.0, 492.0, yd + 28.0)
    ctx.sig += dashed(486.0, yd + 34.0, 478.5, yd + 34.0)

    # Coalescing filter separator F-30xA
    f = ctx.coalescing_filter(
        515.0, L - 45.0, L + 30.0, r=14.0, tag=f"F-30{1}{sfx}", inlet_y=yd
    )
    _ = f
    ctx.proc += pipe_run_v(515.0, L + 43.2, L + 56.0)
    ctx.proc += pipe_run_h(L + 56.0, 515.0, 560.0)
    ctx.flow_arrow_h(535.0, L + 56.0, direction=1, size=2.0)
    ctx.flow_arrow_h(550.0, L + 56.0, direction=1, size=2.0)

    # Drain LV coalescer
    if is_a:
        ctx.proc += pipe_run_v(515.0, 381.0, 391.8)
        ctx.proc += pipe_run_h(381.0, 515.0, 540.0, gaps=[(528.0, 6.2)])
        ctx.proc += ctx.control_valve_h(528.0, 381.0, tag="LV-302")
        ctx.text("LV-302", 528.0, 369.0, size=1.8)
        ctx.proc += pipe_run_v(540.0, 95.0, 381.0, gaps=[(291.0, 1.5)])
        ctx.flow_arrow_v(515.0, 387.0, direction=-1, size=2.0)
        ctx.flow_arrow_v(540.0, 340.0, direction=-1, size=2.2)
        ctx.flow_arrow_v(540.0, 180.0, direction=-1, size=2.2)
        ctx.flow_arrow_v(540.0, 120.0, direction=-1, size=2.2)
    else:
        ctx.drain_lv_h(515.0, L - 58.2, 132.0, 95.0, tag_lv="LV-304")
        ctx.flow_arrow_v(515.0, 165.0, direction=-1, size=2.0)
        ctx.flow_arrow_v(533.0, 115.0, direction=-1, size=2.2)

    # ------------------------------------------------------------------
    # 5. LOOP ANTI-SURGE: recycle yr, ASV-3x1 + FY, UIC-3x1, sinyal
    # ------------------------------------------------------------------
    ctx.proc += pipe_run_v(175.0, yr, L)
    ctx.proc += pipe_run_h(yr, 175.0, 420.0, gaps=[(asv_x, 6.2)])
    ctx.proc += pipe_run_v(420.0, yr, yd)
    ctx.flow_arrow_v(175.0, yr + 22.0, direction=1, size=2.2)
    for ax in (190.0, 230.0, 300.0, 340.0):
        if abs(ax - asv_x) > 10.0:
            ctx.flow_arrow_h(ax, yr, direction=-1, size=2.2)
    ctx.text(f"100-NG-902{1 if is_a else 2} DN100",
             305.0 if is_a else 300.0, yr + 6.0, size=1.8)

    # ASV (globe FC, fast opening) + FY booster — pustaka taruh di REF-SYM
    ctx.anti_surge_valve_h(asv_x, yr, tag="", fail="", fy_no=str(loop))
    ctx.text(tag("ASV"), asv_x, yr - 21.0, size=2.2)
    ctx.text("FC", asv_x, yr - 25.5, size=1.8)

    # UIC-3x1 anti-surge controller
    y_uic = L - 52.0
    ctx.sym += ctx.dcs(403.0, y_uic, "UIC", str(loop))
    ctx.text("ANTI-SURGE CONTROLLER", 403.0, L - 67.0, size=1.8)
    ctx.text("SURGE O/P TO ESD-3", 403.0, (L - 88.0) if is_a else 138.0, size=1.5)

    # Sinyal masukan UIC: FT & PT suction (bus bawah), PT/TT discharge (atas)
    # Break di setiap vertikal proses/equip yang dilintasi bus sinyal.
    x_wall = (140.0, 175.0, 220.0, 252.0, 260.0, 264.0, 267.0, 272.0, 350.0)
    x_wall_b = (175.0, 220.0, 252.0, 260.0, 264.0, 267.0, 272.0, 350.0, 356.0)
    ft_brks = sorted(x - 128.0 for x in (x_wall if is_a else x_wall_b))
    pt_brks = sorted(x - 148.0 for x in (x_wall if is_a else x_wall_b))
    ctx.sig += dashed_brk(128.0, L - 38.0, 396.0, L - 38.0, brk=ft_brks)
    ctx.sig += dashed(396.0, L - 38.0, 396.0, L - 44.5)
    ctx.sig += dashed_brk(148.0, L - 42.0, 410.0, L - 42.0, brk=pt_brks)
    ctx.sig += dashed(410.0, L - 42.0, 410.0, L - 44.5)
    ctx.sig += dashed_brk(396.0, yd + 10.0, 396.0, L - 44.5, brk=[10.0])
    ctx.sig += dashed_brk(410.0, yd + 10.0, 410.0, L - 44.5, brk=[10.0])

    # Sinyal keluaran UIC -> FY (ASV)
    uom = yr + 19.0
    if is_a:
        ctx.sig += dashed(403.0, L - 59.5, 403.0, uom)
        ctx.sig += dashed_brk(403.0, uom, asv_x + 4.0, uom, brk=[53.0])
    else:
        ctx.sig += dashed_brk(395.5, y_uic, 311.0, y_uic, brk=[39.5, 45.5])
        ctx.sig += dashed(311.0, y_uic, 311.0, uom)
        ctx.sig += dashed(311.0, uom, asv_x + 4.0, uom)

    # Trip motor oleh ESD-3
    ctx.sym += ctx.interlock_diamond(311.0, L + 20.0, tag="ESD-3")
    ctx.sig += dashed_brk(311.0, L + 5.0, 311.0, L + 15.0, brk=[2.0])
    ctx.text("TRIP", 322.0, L + 20.0, size=1.8)

    # ------------------------------------------------------------------
    # 6. BDV-3x1 suction & discharge -> BD header 080-FL-9031
    # ------------------------------------------------------------------
    if is_a:
        ctx.proc += pipe_run_h(350.0, x_bd_suc, 350.0)  # sub-header y=350
        ctx.proc += pipe_run_v(
            350.0, 95.0, yd,
            gaps=[(339.0, 2.5), (370.0, 1.5), (229.0, 1.5),
                  (155.0, 1.5), (142.0, 1.5)],
        )
        ctx.proc += ctx.valve_gate_v(350.0, 339.0, w=3.2, h=5.0, tag="BDV-301")
        ctx.text("BDV-301", 364.0, 339.0, size=1.8)
        ctx.text("FC", 364.0, 334.5, size=1.8)
        ctx.flow_arrow_h(250.0, 350.0, direction=1, size=2.0)
        ctx.flow_arrow_v(350.0, 300.0, direction=-1, size=2.2)
        ctx.flow_arrow_v(350.0, 180.0, direction=-1, size=2.2)
    else:
        # Suction tap x=112 sudah digambar; horizontal BD train B + drop x=356
        ctx.proc += pipe_run_h(142.0, x_bd_suc, 356.0)
        ctx.proc += pipe_run_v(356.0, 95.0, 142.0, gaps=[(128.0, 2.5)])
        ctx.proc += pipe_run_v(356.0, 142.0, yd, gaps=[(155.0, 1.5)])
        ctx.proc += ctx.valve_gate_v(356.0, 128.0, w=3.2, h=5.0, tag="BDV-302")
        ctx.text("BDV-302", 370.0, 128.0, size=1.8)
        ctx.text("FC", 370.0, 123.5, size=1.8)
        ctx.flow_arrow_h(250.0, 142.0, direction=1, size=2.0)
        ctx.flow_arrow_v(356.0, 112.0, direction=-1, size=2.2)


# =============================================================================
# MODEL UTAMA P&ID REV A0
# =============================================================================
@dxf
def pid_centrifugal():
    ctx = CompressionContext()

    # -------------------------------------------------------------------------
    # 1. BORDER LEMBAR A1 & GRID REFERENSI (ISO 5457)
    # -------------------------------------------------------------------------
    ctx.frame += rect(10, 7, 831, 587)
    ctx.frame += rect(20, 15, 823, 579)

    dx_col = (823.0 - 20.0) / 12.0
    for k in range(1, 12):
        x = 20.0 + dx_col * k
        ctx.frame += [line(x, 7, x, 15), line(x, 579, x, 587)]
    for i in range(12):
        cx = 20.0 + dx_col * (i + 0.5)
        ctx.text(str(i + 1), cx, 11.0, size=2.5)
        ctx.text(str(i + 1), cx, 583.0, size=2.5)

    dy_row = (579.0 - 15.0) / 8.0
    for k in range(1, 8):
        y = 15.0 + dy_row * k
        ctx.frame += [line(10, y, 20, y), line(823, y, 831, y)]
    for i in range(8):
        cy = 579.0 - dy_row * (i + 0.5)
        ctx.text("ABCDEFGH"[i], 15.0, cy, size=2.5)
        ctx.text("ABCDEFGH"[i], 827.0, cy, size=2.5)

    # -------------------------------------------------------------------------
    # 2. KOLOM FURNITURE KANAN (x = 655..823)
    # -------------------------------------------------------------------------
    ctx.frame.append(line(655, 15, 655, 579))

    # --- 2.1 NOTES (y = 435..579) ---
    ctx.frame.append(line(655, 435, 823, 435))
    ctx.frame.append(line(655, 567, 823, 567))
    ctx.text("NOTES", 739, 573, size=2.5)
    notes = [
        "1. NATURAL GAS COMPRESSION, CENTRIFUGAL 2 X 50% PARALLEL (TRAIN A / B).",
        "   DESIGN DATA: SUCTION 250 PSIG (17.2 BARG) / 40 DEG C AT BATTERY LIMIT;",
        "   DISCHARGE 450 PSIG (31.0 BARG) AT BATTERY LIMIT. FLOW 10 MMSCFD TOTAL,",
        "   5 MMSCFD PER TRAIN, SINGLE STAGE PER TRAIN (COMPRESSION RATIO 1.8).",
        "2. STANDALONE PACKAGE - OUTSIDE GPF-00-DB-0001 SCOPE. ALL PROCESS DATA",
        "   PER PM INSTRUCTION DATED 26 OCT 2026.",
        "3. LINE NUMBERS 9000-SERIES PENDING LINE INDEX REGISTRATION.",
        "4. ESD-3 (SIS) CAUSE & EFFECT: PT-341 PSHH (DISCHARGE HEADER 150-NG-9010)",
        "   OR LSL-301/LSL-302 LSLL (SCRUBBER V-301A/B) OR UIC-301/302 SURGE TRIP:",
        "   CLOSE SDV-301/302 AND TRIP MOTORS K-301A / K-301B (SEE ESD-3 DIAMONDS).",
        "5. COMPRESSORS K-301A/B PER API STD 617: SINGLE-STAGE BARREL CASING WITH",
        "   DRY GAS SEALS (DGS), DRIVER: ELECTRIC MOTOR (M).",
        "6. ANTI-SURGE: UIC-301/302 COMPUTE MARGIN TO SURGE LIMIT LINE FROM PT/TT",
        "   SUCTION AND DISCHARGE PLUS FT-301/302; OPENS ASV-301/302 (FAST OPENING",
        "   <= 1 s WITH BOOSTER RELAY FY). RECYCLE 100-NG-9021/9022 TO SCRUBBER INLET.",
        "7. AFTERCOOLERS E-301A/B FIN-FAN PER API STD 661 / ISO 13706; TIC-303/304",
        "   MODULATES AUTO LOUVERS FROM TT-303/304 (COOLER OUTLET).",
        "8. SCRUBBERS V-301A/B PER API SPEC 12J; COALESCING FILTER SEPARATORS",
        "   F-301A/B. AUTO DRAINS LV-301..LV-304 TO BD HEADER 080-FL-9031.",
        "9. PSV-301A/B SET 34.5 BARG; RELIEF AND BDV-301/302 BLOWDOWN TO FLARE KO",
        "   DRUM PER API STD 521.",
        "10. INSTRUMENT SYMBOLS PER ANSI/ISA-5.1-2024; CONTENT PER ISO 10628-2:2012.",
        "11. SCHEMATIC - NOT TO SCALE. NO ORIENTATION IMPLIED.",
    ]
    ny = 562.0
    for ln in notes:
        ctx.text(ln, 659, ny, size=1.8, left=True)
        ny -= 5.3

    # --- 2.2 LEGEND & SYMBOLS (y = 195..435) ---
    ctx.frame.append(line(655, 195, 823, 195))
    ctx.frame.append(line(655, 423, 823, 423))
    ctx.text("LEGEND & SYMBOLS", 739, 429, size=2.5)

    ctx.proc += [line(660, 425, 685, 425)]
    ctx.flow_arrow_h(676, 425, direction=1)
    ctx.text("PROCESS LINE", 700, 425, size=1.8, left=True)

    ctx.sig += dashed(660, 411, 685, 411)
    ctx.text("ELECTRIC SIGNAL (BPCS / SIS)", 700, 411, size=1.8, left=True)

    ctx.sigp += pneu(660, 397, 685, 397)
    ctx.text("PNEUMATIC SIGNAL", 700, 397, size=1.8, left=True)

    ctx.proc += [
        line(660, 378, 678, 378), line(678, 378, 683, 383),
        line(683, 383, 678, 388), line(678, 388, 660, 388), line(660, 388, 660, 378),
    ]
    ctx.text("BATTERY LIMIT / CONTINUITY ARROW", 700, 383, size=1.8, left=True)

    ctx.sym += [circle(672, 369, 5.0), line(667, 369, 677, 369)]
    ctx.text("FIELD INSTRUMENT", 700, 369, size=1.8, left=True)

    ctx.sym += [
        line(666, 349, 678, 349), line(678, 349, 678, 361),
        line(678, 361, 666, 361), line(666, 361, 666, 349),
        circle(672, 355, 5.0), line(667, 355, 677, 355),
    ]
    ctx.text("DCS SHARED DISPLAY / CONTROL", 700, 355, size=1.8, left=True)

    ctx.sym += [
        line(666, 335, 678, 335), line(678, 335, 678, 347),
        line(678, 347, 666, 347), line(666, 347, 666, 335),
        line(666, 341, 672, 347), line(672, 347, 678, 341),
        line(678, 341, 672, 335), line(672, 335, 666, 341),
    ]
    ctx.text("SIS LOGIC SOLVER / INTERLOCK", 700, 341, size=1.8, left=True)

    ctx.sym += ctx.valve_gate_h(663, 327, w=8, h=5, flanged=False)
    ctx.sym += ctx.valve_globe_h(677, 327, w=8, h=5, flanged=False)
    ctx.sym += ctx.valve_check_h(691, 327, w=8, h=5)
    ctx.text("GATE / GLOBE / CHECK VALVE", 700, 327, size=1.8, left=True)

    ctx.sym += [
        line(667, 312, 672, 317), line(677, 312, 672, 317), line(667, 312, 677, 312),
        line(672, 317, 672, 321), line(669.5, 321, 674.5, 321), line(670, 323, 674, 323),
    ]
    ctx.text("PRESSURE SAFETY VALVE (PSV)", 700, 316, size=1.8, left=True)

    ctx.sym += ctx.control_valve_h(672, 296, w=8, h=5, tag="")
    ctx.text("CONTROL VALVE / AUTO DRAIN LV", 700, 296, size=1.8, left=True)

    ctx.sym += ctx.control_valve_h(706, 270, w=8, h=5, tag="")
    ctx.sym += rect(702, 286, 710, 292)
    ctx.text("FY", 706, 290.2, size=1.8)
    ctx.text("30x", 706, 287.8, size=1.8)
    ctx.sigp += pneu(706, 286, 706, 282.5, spacing=3.0)
    ctx.text("ANTI-SURGE VALVE ASV (FAST OPEN <= 1 s)", 726, 270, size=1.8, left=True)

    ctx.compressor_centrifugal_617(
        cx=678, cy=258, r_in=3.5, r_out=5.5, tag="", casing="BARREL", driver="M"
    )
    ctx.text("CENTRIFUGAL COMPRESSOR (API STD 617, DGS)", 700, 258, size=1.8, left=True)

    ctx.text("FC: FAIL CLOSED      |  CSO: CAR-SEAL OPEN", 659, 240, size=1.8, left=True)
    ctx.text("NC: NORMALLY CLOSED  |  BDV: BLOWDOWN VALVE", 659, 232, size=1.8, left=True)
    ctx.text("DGS: DRY GAS SEAL    |  UIC: ANTI-SURGE CONTROLLER", 659, 224, size=1.8, left=True)
    ctx.text("SLL: SURGE LIMIT LINE |  LV: AUTO DRAIN VALVE", 659, 216, size=1.8, left=True)

    # --- 2.3 REFERENCE DRAWINGS (y = 148..195) ---
    ctx.frame.append(line(655, 148, 823, 148))
    ctx.frame.append(line(655, 175, 823, 175))
    ctx.text("REFERENCE DRAWINGS", 739, 180, size=2.2)
    ref_dwgs = [
        ("GPF-00-DB-0001", "DESIGN BASIS (NOTE 2 - STANDALONE SCOPE)", 169.0),
        ("GPF-00-PI-PID-0001", "P&ID 3-PHASE PRODUCTION SEPARATOR V-101", 163.5),
        ("GPF-00-PI-PID-0012", "P&ID GAS COMPRESSION PACKAGE (RECIP, REF)", 158.0),
        ("GPF-00-PM-PLN-0008", "ROADMAP AI-CAD SUITE (COMPRESSION LIBRARY)", 152.5),
    ]
    for doc_no, doc_title, ry in ref_dwgs:
        ctx.text(f"{doc_no} : {doc_title}", 659, ry, size=1.8, left=True)

    # --- 2.4 REVISION TABLE (y = 116..148) ---
    ctx.title += [
        line(655, 116, 823, 116),
        line(655, 142.0, 823, 142.0),
        line(655, 136.8, 823, 136.8),
        line(655, 131.6, 823, 131.6),
        line(655, 126.4, 823, 126.4),
        line(655, 121.2, 823, 121.2),
        line(675, 116, 675, 148),
        line(763, 116, 763, 148),
        line(795, 116, 795, 148),
        line(809, 116, 809, 148),
    ]
    ctx.text("REV", 665, 145.0, size=1.8)
    ctx.text("DESCRIPTION", 719, 145.0, size=1.8)
    ctx.text("DATE", 779, 145.0, size=1.8)
    ctx.text("CHK", 802, 145.0, size=1.8)
    ctx.text("APP", 816, 145.0, size=1.8)
    rev_data = [
        ("A0", "ISSUED FOR REVIEW", DATE_SHORT, "PM", "RE", 118.6),
    ]
    for r_rev, r_desc, r_date, r_chk, r_app, ry in rev_data:
        ctx.text(r_rev, 665, ry, size=1.8)
        ctx.text(r_desc, 678, ry, size=1.8, left=True)
        ctx.text(r_date, 779, ry, size=1.8)
        ctx.text(r_chk, 802, ry, size=1.8)
        ctx.text(r_app, 816, ry, size=1.8)

    # --- 2.5 TITLE BLOCK (y = 15..116) ---
    ctx.title += [
        line(655, 96, 823, 96),
        line(655, 74, 823, 74),
        line(655, 60, 823, 60),
        line(655, 48, 823, 48),
        line(655, 36, 823, 36),
        line(655, 25, 823, 25),
        line(739, 15, 739, 60),
    ]
    ctx.text("GAS PRODUCTION FACILITY - ONSHORE FIELD", 739, 108.5, size=2.8)
    ctx.text("PM OIL & GAS SURFACE FACILITY", 739, 102.5, size=2.2)
    ctx.text("REKAYASA ENGINEERING", 739, 98.0, size=2.0)
    ctx.text("PIPING & INSTRUMENTATION DIAGRAM", 739, 87.0, size=2.8)
    ctx.text(TITLE_2, 739, 80.0, size=2.5)
    ctx.text("DRAWING NO:", 658, 70.0, size=1.8, left=True)
    ctx.text(DOC_NO, 739, 65.5, size=2.8)
    ctx.text("REV:", 658, 56.5, size=1.8, left=True)
    ctx.text(REV, 697, 52.5, size=3.0)
    ctx.text("SCALE:", 742, 56.5, size=1.8, left=True)
    ctx.text("NTS", 781, 52.5, size=2.5)
    ctx.text("DATE:", 658, 44.5, size=1.8, left=True)
    ctx.text(DATE_LONG, 697, 40.5, size=2.2)
    ctx.text("SHEET:", 742, 44.5, size=1.8, left=True)
    ctx.text("1 OF 1", 781, 40.5, size=2.5)
    ctx.text("DESIGNED:", 658, 32.5, size=1.8, left=True)
    ctx.text("CAD/FEED", 697, 29.0, size=2.2)
    ctx.text("DRAWN:", 742, 32.5, size=1.8, left=True)
    ctx.text("GLM-5.3-FLASH", 781, 29.0, size=2.2)
    ctx.text("CHECKED:", 658, 21.5, size=1.8, left=True)
    ctx.text("PM (AI)", 697, 18.5, size=2.2)
    ctx.text("APPROVED:", 742, 21.5, size=1.8, left=True)

    # -------------------------------------------------------------------------
    # 3. COMMON: SUCTION HEADER + BL, FLARE HEADER + BL, DISCHARGE HEADER + SALES
    # -------------------------------------------------------------------------
    # Suction header vertikal x=62 (BL feed di y=175)
    ctx.bl_box(
        y=175.0, x0=30.0, x1=57.5, dir=1,
        tag="150-NG-9001 DN150",
        desc="FROM FIELD GAS SUPPLY",
        dwg="250 PSIG",
    )
    ctx.proc += pipe_run_v(62.0, 175.0, 450.0)
    for ay in (250.0, 300.0, 400.0):
        ctx.flow_arrow_v(62.0, ay, direction=1, size=2.2)
    ctx.text("150-NG-9001 DN150", 54.0, 300.0, size=1.8, rot=90.0)

    # Discharge header vertikal x=560 + cabang sales
    ctx.proc += pipe_run_v(560.0, 291.0, 506.0)
    ctx.flow_arrow_v(560.0, 350.0, direction=1, size=2.2)
    ctx.flow_arrow_v(560.0, 460.0, direction=1, size=2.2)
    ctx.text("150-NG-9010 DN150", 554.0, 370.0, size=1.8, rot=90.0)

    ctx.proc += pipe_run_h(506.0, 560.0, 598.0, gaps=[(580.0, 1.2)])
    ctx.proc += ctx.orifice_h(580.0, 506.0, tag_fe="FE-341")
    ctx.sig += dashed(580.0, 512.0, 580.0, 514.0)
    ctx.sym += ctx.bubble(580.0, 520.0, "FT", "341")
    ctx.sig += dashed(580.0, 526.0, 580.0, 528.5)
    ctx.sym += ctx.dcs(580.0, 536.0, "FIQ", "341")
    ctx.bl_box(
        y=506.0, x0=598.0, x1=638.0, dir=1,
        tag="150-NG-9010 DN150",
        desc="TO SALES PIPELINE",
        dwg="450 PSIG",
    )
    ctx.flow_arrow_h(570.0, 506.0, direction=1, size=2.2)
    ctx.flow_arrow_h(590.0, 506.0, direction=1, size=2.2)

    # PT-341 PSHH discharge header -> ESD-3
    ctx.proc += [line(560.0, 480.0, 566.0, 480.0)]
    ctx.sym += ctx.bubble(572.0, 480.0, "PT", "341")
    ctx.sig += dashed(578.0, 480.0, 584.0, 480.0)
    ctx.sym += ctx.sis_box(592.0, 480.0, "PAHH", "")
    ctx.text("TO ESD-3", 592.0, 491.0, size=1.8)

    # BD / flare header y=95 -> FLARE KO DRUM
    ctx.proc += pipe_run_h(95.0, 40.0, 568.0)
    ctx.proc += [line(40.0, 92.0, 40.0, 98.0)]
    ctx.bl_box(
        y=95.0, x0=568.0, x1=606.0, dir=1,
        tag="080-FL-9031 DN80",
        desc="TO FLARE KO DRUM",
        dwg="DWG: GPF-00-PI-PID-0001",
    )
    for ax in (60.0, 150.0, 250.0, 330.0, 450.0, 550.0):
        ctx.flow_arrow_h(ax, 95.0, direction=1, size=2.2)
    ctx.text("080-FL-9031 DN80", 300.0, 101.0, size=1.8)

    # -------------------------------------------------------------------------
    # 4. SIS LOGIC SOLVER ESD-3 (kotak utama, pola pid_v101)
    # -------------------------------------------------------------------------
    ctx.sym += rect(60, 531, 100, 555)
    ctx.sym += [
        line(60, 543, 80, 555), line(80, 555, 100, 543),
        line(100, 543, 80, 531), line(80, 531, 60, 543),
    ]
    ctx.text("ESD", 80, 549.0, size=2.2)
    ctx.text("3", 80, 537.5, size=2.2)
    ctx.text("SIS LOGIC SOLVER", 80, 526.0, size=1.9)
    ctx.text("(SEE NOTE 4)", 80, 521.5, size=1.8)

    # -------------------------------------------------------------------------
    # 5. TRAIN A (band atas) & TRAIN B (band bawah)
    # -------------------------------------------------------------------------
    build_train(ctx, "A", 301, 450.0, is_a=True)
    build_train(ctx, "B", 302, 235.0, is_a=False)

    # -------------------------------------------------------------------------
    # 6. REGISTRI LINE & EXPORT MANIFEST
    # -------------------------------------------------------------------------
    for ln, dn, svc, spec in [
        ("150-NG-9001", 150, "NG suction header", "150# A1A"),
        ("150-NG-9002", 150, "NG suction train A", "150# A1A"),
        ("150-NG-9003", 150, "NG suction train B", "150# A1A"),
        ("100-NG-9011", 100, "NG discharge train A", "300# B1A"),
        ("100-NG-9012", 100, "NG discharge train B", "300# B1A"),
        ("150-NG-9010", 150, "NG discharge header", "300# B1A"),
        ("100-NG-9021", 100, "Anti-surge recycle A", "300# B1A"),
        ("100-NG-9022", 100, "Anti-surge recycle B", "300# B1A"),
        ("080-FL-9031", 80, "BD/flare to KO drum", "150# A1A"),
    ]:
        ctx.register_line(ln, spec=spec, service=svc, dn=dn)

    out_json = Path(__file__).resolve().parent / "pid_centrifugal.texts.json"
    layers = ctx.export_manifest(out_json)
    return layers


if __name__ == "__main__":
    pid_centrifugal()
