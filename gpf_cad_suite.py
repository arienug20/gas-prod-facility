"""gpf_cad_suite — stub paket untuk metadata dependency.

Logika CAD perusahaan berada di `cad/` dan dijalankan langsung dari repo
(bukan sebagai paket terpasang). Modul ini hanya memastikan `pip install .`
menghasilkan distribusi yang sah sehingga dependency dapat di-resolve oleh
CI tanpa memaksa memindahkan struktur repo.
"""

__version__ = "1.0.0"
__all__ = ["__version__"]
