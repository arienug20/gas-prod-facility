"""MODEL 3D ROUTING PIPING — GAS PRODUCTION FACILITY (GPF).

Satu assembly 3D: equipment primitif (grey) + 3 line pipa utama
(sweep lingkaran sepanjang path 3D; elbow = fillet path radius 1.5D).
Satuan mm — koordinat plant (meter) x 1000. E=+X, N=+Y, UP=+Z.
Sumber koordinat: dokumen/01-design-basis.md (GPF-00-DB-0001 Rev A0)
dan daftar koordinat tugas. Bukan pengganti drawing 2D di cad/.

Build: python src/piping_3d.py  (dari root proyek)
"""
from __future__ import annotations

from cadgen import build123d as bd
from cadgen import srgb
from cadgen import step

# ---------------------------------------------------------------------------
# Konstanta (nilai literal — tracked by value)
# ---------------------------------------------------------------------------

# Pipa: OD (mm) & elbow radius 1.5D
OD_DN100 = 114.3          # 100-GO-1002
OD_DN80 = 88.9            # 080-CO-1003 / 080-CO-1004

# Path pipa (plant mm): [x, y, z] per titik belok
GO_1002_PTS = [
    (15000, 35150, 4150),   # V-101 N2, top shell (CL +3.0 + r 1.15)
    (15000, 35150, 5000),   # riser di atas rack CL +5.0
    (58000, 35000, 5000),   # E sepanjang rack
    (58000, 46000, 6500),   # N, crossing road +6.5
    (70500, 46000, 6500),   # E di atas V-102
    (70500, 46000, 1150),   # turun masuk V-102
]
CO_1003_PTS = [
    (17800, 33200, 2200),   # V-101 N3, head kanan bawah
    (22000, 33200, 2200),   # E 4.2 m
    (22000, 30900, 600),    # turun ke suction P-101 (CL +0.6)
]
CO_1004_PTS = [
    (22800, 30500, 800),    # discharge P-101 (CL +0.8)
    (24000, 30500, 800),    # E 1.2 m (CV-101, GV-102 — tidak dimodelkan)
    (24000, 30500, 5000),   # riser ke rack CL +5.0
    (24000, 34000, 5000),   # N ke rack y=34
    (44000, 34000, 5000),   # E (FE-142 — tidak dimodelkan)
    (44000, 16000, 1200),   # turun panjang ke grade CL +1.2 (sleeper)
    (67000, 16000, 1200),   # E ke dekat T-101
    (67000, 17500, 1200),   # N
    (67000, 17500, 6700),   # riser +6.7
    (67000, 15800, 6700),   # S ke atas nozzle N1
    (67000, 15800, 6200),   # turun ke T-101 N1
]

# Warna (sRGB hex -> channel linear native via cadgen.srgb)
C_V101 = srgb("#9AA3AD")
C_P101 = srgb("#7E8790")
C_V102 = srgb("#A9B2BA")
C_F101 = srgb("#C9C4B8")   # abu hangat — beda tipis dari vessel lain
C_T101 = srgb("#8F979E")
C_BUND = srgb("#B4B8BC")
C_GAS = srgb("#F2D94C")    # kuning — gas (0.95, 0.85, 0.3)
C_OIL = srgb("#66BF66")    # hijau — crude oil (0.4, 0.75, 0.4)


# ---------------------------------------------------------------------------
# Helper (factory biasa — bukan model)
# ---------------------------------------------------------------------------

def _pipe_run(pts: list[tuple[float, float, float]], od: float) -> bd.Part:
    """Sweep lingkaran OD sepanjang polyline 3D dengan elbow fillet 1.5*OD."""
    path = bd.FilletPolyline([bd.Vector(*p) for p in pts], radius=1.5 * od)
    tangent = (bd.Vector(*pts[1]) - bd.Vector(*pts[0])).normalized()
    profile = bd.Plane(origin=bd.Vector(*pts[0]), z_dir=tangent) * bd.Circle(od / 2)
    return bd.sweep(profile, path)


def _flange(
    endpoint: tuple[float, float, float],
    neighbor: tuple[float, float, float],
    od: float,
) -> bd.Solid:
    """Cincin flange: silinder pendek r=OD/2+15, tebal 30, terpusat di endpoint."""
    end = bd.Vector(*endpoint)
    inward = (bd.Vector(*neighbor) - end).normalized()
    plane = bd.Plane(origin=end - inward * 15.0, z_dir=inward)
    return bd.Solid.make_cylinder(od / 2 + 15.0, 30.0, plane)


def _line(label: str, pts, od: float, color) -> list[bd.Shape]:
    """Pipa 1 line + flange di kedua ujungnya (children berlabel & berwarna)."""
    pipe = _pipe_run(pts, od)
    pipe.label = label
    pipe.color = color
    fl_a = _flange(pts[0], pts[1], od)
    fl_a.label = f"{label}-FL-A"
    fl_a.color = color
    fl_b = _flange(pts[-1], pts[-2], od)
    fl_b.label = f"{label}-FL-B"
    fl_b.color = color
    return [pipe, fl_a, fl_b]


# ---------------------------------------------------------------------------
# Model (satu assembly, parameterless)
# ---------------------------------------------------------------------------

@step(out="../step/piping_3d.step")
def piping_3d():
    # --- V-101: separator horizontal 3-fasa, Ø2300 x 7600, CL (14,34,+3.0)
    v101_shell = bd.Pos(14000, 34000, 3000) * bd.Rot(0, 90, 0) * bd.Cylinder(
        1150.0, 7600.0,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER),
    )
    v101 = (
        v101_shell
        + bd.Pos(10200, 34000, 3000) * bd.Sphere(1150.0)   # head barat
        + bd.Pos(17800, 34000, 3000) * bd.Sphere(1150.0)   # head timur
    )
    v101.label = "V-101"
    v101.color = C_V101

    # --- P-101: pump box 1200x700x600, center (22,30.5), duduk di grade
    p101 = bd.Pos(22000, 30500, 300) * bd.Box(
        1200.0, 700.0, 600.0,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER),
    )
    p101.label = "P-101"
    p101.color = C_P101

    # Nozzle P-101 (stub silinder kecil casing -> titik sambung pipa):
    # suction sisi utara (CL +0.6), discharge sisi timur (CL +0.8) —
    # agar sambungan pipa terbaca, tidak seperti kawat melayang.
    p101_n_suc = bd.Solid.make_cylinder(
        75.0, 55.0,
        bd.Plane(origin=(22000, 30850, 600), z_dir=(0, 1, 0)),
    )
    p101_n_suc.label = "P-101-N-SUC"
    p101_n_suc.color = C_P101
    p101_n_dis = bd.Solid.make_cylinder(
        75.0, 185.0,
        bd.Plane(origin=(22600, 30500, 800), z_dir=(1, 0, 0)),
    )
    p101_n_dis.label = "P-101-N-DIS"
    p101_n_dis.color = C_P101

    # --- V-102: flare KO drum horizontal Ø1600 x 2500, CL (71.25,46,+1.0)
    v102 = bd.Pos(71250, 46000, 1000) * bd.Rot(0, 90, 0) * bd.Cylinder(
        800.0, 2500.0,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.CENTER),
    )
    v102.label = "V-102"
    v102.color = C_V102

    # --- F-101: flare stack vertikal Ø600 x 12000, center (84,46)
    f101 = bd.Pos(84000, 46000, 0) * bd.Cylinder(
        300.0, 12000.0,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )
    f101.label = "F-101"
    f101.color = C_F101

    # --- T-101: tangki vertikal Ø6000 x 6000 + atap kerucut 600, center (69,14)
    t101_shell = bd.Pos(69000, 14000, 0) * bd.Cylinder(
        3000.0, 6000.0,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )
    t101_roof = bd.Pos(69000, 14000, 6000) * bd.Cone(
        3000.0, 0.0, 600.0,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )
    # Nozzle N1 di roof (67,15.8), berdiri dari permukaan cone ke +6.32 m
    # (permukaan cone pada r=2.691 m dari CL ≈ +6.06 m) — agar ujung pipa
    # discharge (+6.2) terbaca masuk nozzle, bukan melayang.
    t101_n1 = bd.Pos(67000, 15800, 6020) * bd.Cylinder(
        100.0, 300.0,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )
    t101 = t101_shell + t101_roof + t101_n1
    t101.label = "T-101"
    t101.color = C_T101

    # --- Bund T-101: 4 dinding box t=300, h=1000, rect (62,8)-(76,20) m
    w_s = bd.Pos(69000, 8150, 0) * bd.Box(
        14000.0, 300.0, 1000.0,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )
    w_n = bd.Pos(69000, 19850, 0) * bd.Box(
        14000.0, 300.0, 1000.0,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )
    w_w = bd.Pos(62150, 14000, 0) * bd.Box(
        300.0, 11400.0, 1000.0,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )
    w_e = bd.Pos(75850, 14000, 0) * bd.Box(
        300.0, 11400.0, 1000.0,
        align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
    )
    bund = w_s + w_n + w_w + w_e
    bund.label = "T-101_BUND"
    bund.color = C_BUND

    # --- Pipa (warna per service)
    children: list[bd.Shape] = [
        v101, p101, p101_n_suc, p101_n_dis, v102, f101, t101, bund,
    ]
    children += _line("100-GO-1002", GO_1002_PTS, OD_DN100, C_GAS)
    children += _line("080-CO-1003", CO_1003_PTS, OD_DN80, C_OIL)
    children += _line("080-CO-1004", CO_1004_PTS, OD_DN80, C_OIL)

    return bd.Compound(children=children, label="piping_3d")


if __name__ == "__main__":
    piping_3d()
