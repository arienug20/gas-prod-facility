"""cadbackend.py - Resolver backend CAD untuk proyek gas-prod-facility.

Menggantikan ketergantungan keras pada `cadgen`. Urutan pemilihan backend
(dapat di-override lewat env GPF_CAD_BACKEND):

    cadgen      Paket resmi cadgen (build123d + dxf + drawing_checks).
    cadcraft    CADCraft CLI (DXF read/write, PNG/SVG/PDF export, headless).
    gstarcad    GstarCAD - HANYA untuk verifikasi visual manual / interaktif.
    install     Tidak ada backend -> coba `pip install cadgen` (ada timeout).
    shim        Shim ezdxf murni (cadshim.py) - selalu tersedia selama ada
                ezdxf; dipakai sebagai jaring pengaman terakhir.

Filosofi: pekerjaan engineering TIDAK PERNAH terblokir. Setiap tier yang
gagal dicatat lalu dilanjutkan ke tier berikutnya.

Pemakaian umum:

    from cadbackend import resolve, build_dxf, snapshot, validate

    be = resolve()                 # -> Backend(name=..., version=..., path=...)
    print(be.summary())
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# --------------------------------------------------------------------------- config
ENV_PREFER = "GPF_CAD_BACKEND"        # paksa backend tertentu (nama tier)
ENV_ALLOW_INSTALL = "GPF_CAD_ALLOW_INSTALL"   # "1" untuk mengizinkan auto-install
ENV_INSTALL_TIMEOUT = "GPF_CAD_INSTALL_TIMEOUT"

DEFAULT_ORDER = ("cadgen", "cadcraft", "shim", "install", "gstarcad")
# PENTING: `shim` (ezdxf) sengaja berada SEBELUM `install` dan `gstarcad`.
# Alasan: shim terbukti mampu build->apply_text->linter 16/16 PASS, sedangkan
# GstarCAD tidak punya CLI headless dan `pip install cadgen` bisa menggantung
# berjam-jam (dependency OCC + playwright). Pekerjaan engineering tidak boleh
# menunggu instalasi raksasa atau aplikasi GUI. GstarCAD tetap tersedia
# sebagai alat verifikasi visual manual (lihat cadbackend.py list).
CADGEN_PIN = "cadgen>=0.7.21,<0.8"     # 0.7.26 = rilis terbaru saat resolver ditulis

# Lokasi kandidat CADCraft CLI (portable/normal/msi)
CADCRAFT_CANDIDATES = (
    Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "cadcraft" / "cadcraft-cli.exe",
    Path(r"C:\Program Files\CADCraft\cadcraft-cli.exe"),
    Path(r"C:\Program Files (x86)\CADCraft\cadcraft-cli.exe"),
)
GSTARCAD_CANDIDATES = (
    Path(r"C:\Program Files\Gstarsoft\GstarCAD2026\gcad.exe"),
    Path(r"C:\Program Files\Gstarsoft\GstarCAD2025\gcad.exe"),
)


@dataclass
class Backend:
    name: str
    version: str = ""
    path: str = ""
    capabilities: set[str] = field(default_factory=set)
    notes: list[str] = field(default_factory=list)

    def has(self, cap: str) -> bool:
        return cap in self.capabilities

    def summary(self) -> str:
        caps = ", ".join(sorted(self.capabilities)) or "-"
        loc = f"  [{self.path}]" if self.path else ""
        ver = f" {self.version}" if self.version else ""
        return f"backend={self.name}{ver}  capabilities={caps}{loc}"


# --------------------------------------------------------------------------- probes
def _probe_module(mod: str, timeout: float = 0.0) -> tuple[bool, str]:
    """Cek modul terpasang TANPA mengimpornya (import cadgen bisa menggantung)."""
    # Modul yang sudah ada di sys.modules (simulasi/hot-reload) dianggap ada.
    root = mod.split(".")[0]
    if root in sys.modules:
        m = sys.modules.get(mod) or sys.modules.get(root)
        return m is not None, str(getattr(m, "__version__", ""))
    try:
        spec = importlib.util.find_spec(mod)
    except (ImportError, ValueError, ModuleNotFoundError):
        return False, ""
    if spec is None:
        return False, ""
    ver = ""
    try:
        from importlib.metadata import version
        ver = version(root)
    except Exception:
        ver = ""
    return True, ver


def _run_import_check(mod: str, timeout: float) -> bool:
    """Import sungguhan berbatas waktu (aman dari hang akibat OCC/playwright).

    Bila modul sudah ter-load di proses ini (simulasi, hot-reload, atau backend
    dipanggil dari dalam proses yang sama), pakai hasil proses-ini lebih dulu —
    subprocess baru tidak akan melihat modul yang di-inject ke sys.modules.
    """
    if mod in sys.modules:
        return True
    try:
        r = subprocess.run(
            [sys.executable, "-c", f"import {mod}"],
            capture_output=True, timeout=timeout,
        )
        return r.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def _probe_cadgen() -> Backend | None:
    ok, ver = _probe_module("cadgen")
    if not ok:
        return None
    notes: list[str] = []
    # cadgen menarik build123d + OCP; import bisa lama -> batasi waktu.
    if not _run_import_check("cadgen.drawing_checks", timeout=120):
        notes.append("`import cadgen.drawing_checks` gagal/timeout (dependency "
                     "OCC/playwright kemungkinan belum lengkap)")
        return Backend("cadgen", ver, capabilities={"metadata_only"}, notes=notes)
    return Backend(
        "cadgen", ver,
        capabilities={"build", "export_dxf", "snapshot", "validate"},
        notes=notes,
    )


def _find_exe(cands, name: str) -> Path | None:
    # 1) eksplisit via env
    env = os.environ.get(f"GPF_{name.upper()}_EXE")
    if env and Path(env).is_file():
        return Path(env)
    # 2) PATH
    which = shutil.which(name)
    if which:
        return Path(which)
    # 3) lokasi kandidat
    for c in cands:
        if str(c) and Path(c).is_file():
            return Path(c)
    return None


def _probe_cadcraft() -> Backend | None:
    exe = _find_exe(CADCRAFT_CANDIDATES, "cadcraft-cli")
    if exe is None:
        return None
    ver = ""
    try:
        r = subprocess.run([str(exe), "--version"], capture_output=True,
                           text=True, timeout=30)
        ver = (r.stdout or r.stderr).strip().splitlines()[0].replace(
            "cadcraft-cli", "").strip()
    except Exception as exc:  # pragma: no cover
        return Backend("cadcraft", "", str(exe), {"open_dxf"},
                       [f"version check gagal: {exc}"])
    return Backend(
        "cadcraft", ver, str(exe),
        capabilities={"export_dxf", "snapshot", "convert_dwg", "export_svg",
                      "export_pdf", "inspect", "open_dxf"},
        notes=["renderer PNG tema gelap; tidak memvalidasi aturan perusahaan"],
    )


def _probe_gstarcad() -> Backend | None:
    exe = _find_exe(GSTARCAD_CANDIDATES, "gcad")
    if exe is None:
        return None
    return Backend(
        "gstarcad", "", str(exe),
        capabilities={"open_dxf", "manual_visual_check"},
        notes=[
            "TIDAK punya CLI headless untuk snapshot (doconv.exe hanya OLE "
            "converter untuk Microsoft Office) - hanya untuk verifikasi visual "
            "manual / interaktif di workstation engineer",
        ],
    )


PROBES = {
    "cadgen": _probe_cadgen,
    "cadcraft": _probe_cadcraft,
    "gstarcad": _probe_gstarcad,
}


# --------------------------------------------------------------------------- install
def try_install_cadgen(allow: bool | None = None) -> Backend | None:
    """Pasang cadgen bila diizinkan. Selalu punya timeout agar tidak menggantung.

    catatan: cadgen>=0.7.22 menarik cadquery-ocp-novtk (OCC, ratusan MB) +
    playwright, sehingga instalasi bisa sangat lama. Itulah alasan timeout wajib.
    """
    if allow is None:
        allow = os.environ.get(ENV_ALLOW_INSTALL, "0") == "1"
    if not allow:
        return None
    timeout = int(os.environ.get(ENV_INSTALL_TIMEOUT, "900"))
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", CADGEN_PIN],
            check=True, timeout=timeout,
        )
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return None
    importlib.invalidate_caches()
    return _probe_cadgen()


# --------------------------------------------------------------------------- shim
def _shim_dir() -> Path:
    env = os.environ.get("GPF_SHIM_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent


def _probe_shim() -> Backend | None:
    ok, ver = _probe_module("ezdxf")
    if not ok:
        return None
    shim = _shim_dir() / "cadshim.py"
    if not shim.is_file():
        return None
    return Backend(
        "shim", f"ezdxf {ver}", str(shim),
        capabilities={"build", "export_dxf", "snapshot"},
        notes=["jaring pengaman terakhir; lihat capabilitas backend lain"],
    )


# --------------------------------------------------------------------------- resolve
def resolve(prefer: str | None = None, order=None,
            need: str | None = None) -> Backend:
    """Kembalikan backend pertama yang tersedia (dan mampu `need`).

    need: kapabilitas yang wajib, mis. "build", "snapshot", "export_dxf".
          Backend yang terdeteksi tetapi tidak mampu akan dilewati, sehingga
          GstarCAD (GUI, tanpa snapshot headless) tidak pernah terpilih untuk
          pekerjaan batch.
    """
    order = tuple(order) if order else DEFAULT_ORDER
    forced = prefer or os.environ.get(ENV_PREFER, "")

    if forced:
        if forced not in DEFAULT_ORDER:
            raise ValueError(f"{ENV_PREFER}={forced!r} tidak dikenal; "
                             f"pilihan: {', '.join(DEFAULT_ORDER)}")
        be = _probe_named(forced)
        if be is None:
            raise RuntimeError(
                f"Backend {forced!r} dipaksa lewat {ENV_PREFER} tetapi tidak "
                f"tersedia di mesin ini.")
        if need and not be.has(need):
            raise RuntimeError(
                f"Backend {forced!r} dipaksa tetapi tidak mendukung "
                f"kapabilitas {need!r} (dimiliki: {sorted(be.capabilities)}).")
        return be

    skipped: list[str] = []
    for name in order:
        be = _probe_named(name)
        if be is None:
            continue
        if need and not be.has(need):
            skipped.append(f"{name} (tidak punya {need})")
            continue
        if skipped:
            be.notes.append("dilewati: " + "; ".join(skipped))
        return be
    raise RuntimeError(
        "Tidak ada backend CAD yang tersedia"
        + (f" untuk kapabilitas {need!r}" if need else "")
        + ". Terperiksa: " + ", ".join(skipped or list(order)))


def _probe_named(name: str) -> Backend | None:
    if name == "install":
        return try_install_cadgen()
    if name == "shim":
        return _probe_shim()
    fn = PROBES.get(name)
    return fn() if fn else None


# --------------------------------------------------------------------------- API
def snapshot(dxf: Path, png: Path, width=2400, height=1700,
             backend: Backend | None = None) -> Backend:
    """Render DXF -> PNG dengan backend terbaik yang mendukung snapshot."""
    be = backend or resolve()
    if be.name == "cadcraft" and be.path:
        subprocess.run([be.path, "convert", str(dxf), str(png),
                        "--view", "extents"], check=True)
        return be
    if be.name == "shim" and be.path:
        sys.path.insert(0, str(Path(be.path).parent))
        import cadshim  # noqa: PLC0415
        cadshim.snapshot_png(Path(dxf), Path(png), width, height)
        return be
    if be.name == "cadgen":
        subprocess.run(["cadgen", "dxf", "snapshot", str(dxf), str(png),
                        "--width", str(width), "--height", str(height)],
                       check=True)
        return be
    # cadcraft/gstarcad tidak bisa snapshot headless -> turun ke backend lain
    fallback = resolve(order=[n for n in DEFAULT_ORDER if n != be.name])
    return snapshot(dxf, png, width, height, backend=fallback)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"-h", "--help", "info"}:
        try:
            be = resolve()
            print(be.summary())
            for n in be.notes:
                print("  note:", n)
            return 0
        except RuntimeError as exc:
            print("ERROR:", exc)
            return 1
    if argv[0] == "list":
        for name in DEFAULT_ORDER:
            try:
                be = _probe_named(name)
            except Exception as exc:  # pragma: no cover
                print(f"{name:<10} ERR {exc}")
                continue
            print(f"{name:<10} {'OK  ' if be else 'MISS'} "
                  f"{(be.summary() if be else '')}")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
