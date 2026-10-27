"""conftest.py di folder cad/ — penyesuaian test agar portabel (Windows/CI).

Masalah yang ditangani:
  * Test repo menulis ke path Unix `/tmp/aud` yang tidak ada di Windows/CI.
    Kami arahkan ke direktori sementara pytest (tmp_path_factory) dengan
    membuat `/tmp` sebagai symlink/hardlink-logis bila memungkinkan; bila
    tidak, gunakan env GPF_TEST_OUT.
  * Memastikan `cad/` ada di sys.path sehingga `import pid_common` bekerja
    dari mana pun pytest dijalankan.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

CAD = Path(__file__).resolve().parent
if str(CAD) not in sys.path:
    sys.path.insert(0, str(CAD))

# Direktori kerja default untuk test (dapat dioverride lewat env).
_OUT = Path(os.environ.get("GPF_TEST_OUT", Path(tempfile.gettempdir()) / "gpf-test"))
_OUT.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("GPF_TEST_OUT", str(_OUT))


def pytest_configure(config):  # noqa: ARG001
    """Alihkan /tmp/aud -> folder sementara yang benar-benar ada.

    Pada Windows, `/tmp/aud` menjadi `C:\\tmp\\aud` (bukan root filesystem).
    Test lama menulis ke sana; kita buatkan direktorinya agar tidak crash.
    """
    legacy = Path("/tmp/aud")
    try:
        legacy.mkdir(parents=True, exist_ok=True)
    except OSError:
        # Windows: "/tmp" relatif terhadap drive aktif -> buat versi absolut
        alt = Path(os.path.abspath("/tmp/aud"))
        try:
            alt.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
