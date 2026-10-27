# DEPENDENCIES.md — Manifest & Quality Gate gas-prod-facility

Dokumen ini menjelaskan **apa yang dibutuhkan** untuk menjalankan repo,
**kenapa** beberapa hal dibuat opsional, dan **cara memverifikasi** hasil
ubah tanpa merusak mutu.

---

## 1. Ringkasan dependency

| Komponen | Wajib? | Dipakai oleh | Versi teruji |
|---|---|---|---|
| **ezdxf** | **WAJIB** | `validate_cad_rules.py`, `apply_text.py`, `apply_pens.py`, `cadshim.py` | 1.4.3 |
| matplotlib + pillow | Render/QA | `cadshim.snapshot_png` (DXF → PNG) | 3.10.8 / 12.1.0 |
| numpy | QA test | analisis citra pada test | 2.4.1 |
| **cadgen** | **OPSIONAL** | `build123d` (geometri) + `cadgen.dxf` | 0.7.26 |
| **cadcraft-cli** | OPSIONAL | render DXF→PNG/SVG/PDF alternatif | 0.13.0 |
| **GstarCAD** | OPSIONAL | buka DXF & cek visual **manual** | GstarCAD 2026 |
| pytest | CI | quality gate | 9.x |

**Fakta penting:** `ezdxf` adalah satu-satunya dependency pihak ketiga yang
benar-benar diimpor oleh pustaka perusahaan. `validate_cad_rules.py` hanya
butuh `ezdxf` + stdlib, sehingga **linter bisa jalan di CI tanpa cadgen**.

---

## 2. Kenapa `cadgen` dibuat opsional

Sebelumnya `cadgen==0.7.21` adalah ketergantungan keras. Masalahnya:

1. **Sejak 0.7.22 cadgen menarik `cadquery-ocp-novtk`** (kernel OpenCASCADE,
   ratusan MB) **dan `playwright`**. Instalasi di mesin engineer bisa
   menggantung puluhan menit atau gagal.
2. Kode perusahaan hanya memakai **4 primitive** dari `build123d`
   (`Vector`, `Edge.make_line`, `Edge.make_circle`, `Location`, `Compound`)
   dan dekorator `dxf` — bukan CAD kernel penuh.
3. Terbukti: backend `ezdxf` (`cadshim.py`) menghasilkan **geometri identik
   per layer** dan lulus linter **16/16** dengan warning yang sama persis.

Karena itu `cadbackend.py` memilih backend secara berjenjang dan pekerjaan
engineering **tidak pernah terblokir**.

---

## 3. Urutan fallback backend

```
cadgen  →  cadcraft  →  shim (ezdxf)  →  install (pip)  →  gstarcad
```

| Tier | Mampu | Catatan |
|---|---|---|
| `cadgen` | build, export DXF, snapshot, validate | Prioritas utama bila terpasang |
| `cadcraft` | export DXF, snapshot, SVG/PDF, inspect | CLI headless; output bertema gelap |
| `shim` | build, export DXF, snapshot | Jaring pengaman; selalu ada bila `ezdxf` ada |
| `install` | build, export DXF, snapshot | Hanya jalan bila `GPF_CAD_ALLOW_INSTALL=1` |
| `gstarcad` | **buka DXF saja** | GUI: verifikasi visual manual, **bukan** batch |

> **Kenapa `shim` sebelum `install`?** Menunggu instalasi OCC ratusan MB
> sambil pekerjaan menggambar mandek adalah pilihan buruk. Shim sudah
> terbukti benar, jadi dipakai lebih dulu; cadgen tetap tersedia bagi yang
> membutuhkan.

> **Kenapa `gstarcad` paling akhir?** GstarCAD tidak punya CLI headless.
> `doconv.exe` ternyata *Drawing OLE Objects Converter for Microsoft Office*,
> bukan converter drawing. GstarCAD tetap berguna untuk membuka DXF dan
> memeriksa visual secara manual.

### Perintah

```bash
python cadbackend.py list          # status semua tier
python cadbackend.py               # backend aktif
python -c "from cadbackend import resolve; print(resolve(need='build').name)"
```

### Variabel lingkungan

| Variabel | Arti |
|---|---|
| `GPF_CAD_BACKEND` | Paksa backend (`cadgen`/`cadcraft`/`shim`/`gstarcad`/`install`). Tidak akan fallback diam-diam. |
| `GPF_CAD_ALLOW_INSTALL` | `1` = izinkan `pip install cadgen` otomatis (tier `install`) |
| `GPF_CAD_INSTALL_TIMEOUT` | Timeout instalasi (detik), default 900 |
| `GPF_CADCRAFT_EXE` | Path eksplisit ke `cadcraft-cli.exe` |
| `GPF_GCAD_EXE` | Path eksplisit ke `gcad.exe` |

---

## 4. Quality gate

Satu perintah, dipakai **lokal dan di CI**:

```bash
python tools/quality_gate.py                # sweep linter + pytest
python tools/quality_gate.py --lint-only    # cepat (~40 s)
python tools/quality_gate.py --build        # rebuild -> apply_text -> lint + pytest
python tools/quality_gate.py --json         # keluaran terstruktur (untuk CI)
python tools/quality_gate.py --strict-warnings
```

Yang diperiksa:

1. **environment** — versi Python & backend CAD aktif
2. **hygiene** — laporan file kerja/sisa di `cad/` (mis. `test_opt*.dxf`)
3. **build** (opsional) — `build → apply_text.py` untuk **16 drawing**
4. **lint** — `validate_cad_rules.py` (Check 1–7) pada setiap `*.dxf`
5. **tests** — pytest
6. **coverage** — memastikan 16 sheet wajib benar-benar ada & ter-lint

### Verifikasi bahwa gate benar-benar bekerja (bukti negatif)

```
# rusak lineweight 1 DXF
python -c "import ezdxf; d=ezdxf.readfile('cad/pid_v101.dxf'); \
  [setattr(l.dxf,'lineweight',-3) for l in d.layers]; d.saveas('cad/pid_v101.dxf')"

python tools/quality_gate.py --lint-only
# => HASIL: 18/19 lulus | GAGAL: lint:pid_v101   (exit 1)
```

---

## 5. CI (GitHub Actions)

Workflow: `.github/workflows/quality-gate.yml`

- **Job `gate`** — matrix Python **3.11 / 3.12 / 3.13**; install
  `requirements.txt`, jalankan `ruff` + quality gate, unggah `gate.json`.
- **Job `regression`** — rebuild seluruh 16 drawing lewat backend `ezdxf`,
  apply_text, lint ulang. Membuktikan keluaran deterministik.
- `cadgen` **tidak dipasang** secara default (CI cepat & stabil). Bisa
  diaktifkan lewat input `install_cadgen` atau variabel repo `CADGEN_IN_CI=1`.

**Python 3.14 belum didukung** karena wheel dependency OCC/cadgen belum ada.
Matrix sengaja dibatasi `<3.14` di `pyproject.toml`.

---

## 6. Setup workstation

```bash
git clone https://github.com/arienug20/gas-prod-facility
cd gas-prod-facility
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux:    source .venv/bin/activate
pip install -r requirements.txt
pip install pytest
python tools/quality_gate.py
```

Untuk memakai backend cadgen asli (opsional, lambat):

```bash
pip install -r requirements-cadgen.txt
# Bila instalasi menggantung pada langkah playwright:
pip install cadgen==0.7.26 --no-deps
pip install build123d cadquery-ocp-novtk ezdxf matplotlib pillow shapely
```

---

## 7. Catatan tentang `conftest.py`

`conftest.py` di root menyediakan **shim cadgen otomatis**: bila paket
`cadgen` asli tidak ada, modul tiruan `cadshim` dipasang ke `sys.modules`.
Itulah sebabnya `pytest cad/` berjalan di CI Python-only — sebelum ini,
**11 dari 25 test gagal** karena `ModuleNotFoundError: No module named 'cadgen'`.

`cad/conftest.py` menangani portabilitas: test lama menulis ke `/tmp/aud`
(path Unix) yang tidak ada di Windows; kini direktorinya dibuat otomatis
dan dapat diarahkan lewat `GPF_TEST_OUT`.
