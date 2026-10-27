"""conftest.py — konfigurasi pytest untuk GPF CAD Suite.

Tujuan utama: membuat `import cadgen` SELALU berhasil, tanpa memaksa
memasang paket cadgen asli (kernel OCC + playwright, ratusan MB).

Urutan:
  1. Bila paket `cadgen` asli terpasang          -> pakai apa adanya.
  2. Bila tidak (atau import-nya gagal/timeout)  -> pasang shim ezdxf (cadshim).

Dengan begitu `pytest cad/` berjalan di CI Python-only, dan engineer yang
punya cadgen tetap memakai backend asli.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
if str(REPO / "cad") not in sys.path:
    sys.path.insert(0, str(REPO / "cad"))


def _install_cadgen_if_needed() -> None:
    try:
        import cadgen  # noqa: F401
        return  # paket asli tersedia
    except Exception:
        pass
    try:
        import cadshim  # noqa: PLC0415
    except ImportError:  # pragma: no cover
        return  # tidak ada shim: biarkan test yang membutuhkan gagal sendiri
    cadshim.install()


_install_cadgen_if_needed()
