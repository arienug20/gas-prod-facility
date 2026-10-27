# TOOLS.md — Alat QA Tambahan (Title Block, Revision Diff, Export Excel)

Tiga alat pelengkap. Semuanya ikut dijalankan di **quality gate** dan **CI**.

| Alat | Fungsi | Exit code |
|---|---|---|
| `tools/titleblock_check.py` | Verifikasi field title block per ISO 7200:2004 | 1 bila ada error |
| `tools/revdiff.py` | Bandingkan isi drawing antar revisi git | 2 bila input salah |
| `tools/export_xlsx.py` | Ekspor BOM/line list/register ke Excel | 0 |
| `tools/test_tools.py` | Uji ketiganya (8 kasus) | 1 bila ada gagal |

---

## 1. `titleblock_check.py` — ISO 7200:2004

### Field yang diperiksa

**Wajib (ERROR)** — 7 field:

| Field | Acuan | Bentuk sah di repo |
|---|---|---|
| `legal_owner` | §4.1 | `PT …`, `COMPANY`, `CONSULTANT` |
| `identification_number` | §4.1 | `GPF-NN-XX-XXX-NNNN` |
| `date_of_issue` | §4.1 | `26 OCT 2026`, `09 OCT 26` |
| `revision_index` | §4.1 | sel `A0`…`Z9` atau `REV: A3` |
| `sheet_number` | §4.1 | `SHEET: 1 OF 1` **atau** `SHEET:` + `1 OF 1` (dua teks) |
| `title` | §4.1 | `P&ID`, `PIPING PLAN`, `ISOMETRIC`, … |
| `sheet_size` | §4.2 / ISO 5457 | dari **geometri** (lihat di bawah) |

**Dianjurkan (WARN)** — 4 field: `responsible_dept`, `approval`, `status`,
`scale`.

### Tiga jebakan yang ditangani

**a. Field terbagi dua MTEXT.** Di repo ini label dan nilainya sering
dipisah menjadi dua entity:

```
teks 1: "SHEET:"      teks 2: "1 OF 1"
```

Pencocokan yang hanya menerima `"SHEET: 1 OF 1"` akan melaporkan field
hilang padahal ada.

**b. Ukuran lembar vs sel revisi sama-sama "A1".** Token `A0`/`A1` dipakai
sebagai **ukuran lembar** *dan* **sel revisi**. Karena itu ukuran lembar
ditentukan dari **geometri**, bukan teks:

| Lembar | Extents border terukur | Terdeteksi |
|---|---|---|
| A1 | 821,0 × 580,0 mm (841−20, 594−14) | A1 |
| A3 | 416,0 × 294,4 mm | A3 |

Toleransi 45 mm memisahkan A1 dari A2 (selisih ~200 mm), cukup longgar
untuk border namun cukup ketat untuk menolak tebakan.

> Catatan teknis: `ezdxf` **tidak** menyediakan `Entity.bbox()` secara
> default. Extents dihitung manual dari titik entity.

**c. Format tanggal 2 digit.** `09 OCT 26` sah; regex yang mensyaratkan
4 digit tahun akan melaporkan tanggal hilang.

### Temuan yang muncul saat implementasi

Registri awal menulis `underground_demo` dan `supports_demo` sebagai **A1**,
padahal geometrinya **A3** (416×294,4). Registri yang dikoreksi — bukan
drawing.

---

## 2. `revdiff.py` — perbandingan revisi

Membandingkan `cad/<sheet>.texts.json` antar dua revisi git dan
mengelompokkan: **ADDED**, **REMOVED**, **MOVED** (>0,5 mm), serta *noise*.

```bash
python tools/revdiff.py                              # semua, HEAD~1 -> HEAD
python tools/revdiff.py pid_v101
python tools/revdiff.py --all 69b5bb4 3811477
python tools/revdiff.py pid_v101 HEAD~3 HEAD --json
```

Contoh keluaran nyata:

```
--- pid_v101  [A4 -> A5]
  + 4 teks ditambahkan:
      + 26 OCT 26
      + TRIP LABEL OFFSET PER LINTER OPT-3 (SIG-TEXT RULE)
  ~ 24 teks dipindah:
      ~ REV    dx=+0.00 dy=+0.80
  = 120 teks tidak berubah
```

Hasil ini **cocok** dengan `04-review-log.md` ROUND OPT-3 (pid_v101 → A5,
"TRIP LABEL OFFSET PER LINTER OPT-3").

### Tiga jebakan yang ditangani

**a. Teks duplikat pada posisi berbeda.** Nomor grid `1`…`12` muncul **dua
kali** (tepi atas y=11, tepi bawah y=583). Pemetaan tunggal `{teks: posisi}`
membuang kemunculan kedua dan melaporkan "dipindah" palsu sepanjang tinggi
lembar (~572 mm). Pencocokan kini **per-entry**, dipasangkan ke posisi
terdekat yang belum terpakai.

**b. Argumen tertukar.** `--all <old> <new>` sempat dibaca sebagai
`<sheet> <old>`, sehingga `git show` gagal dan diff menjadi palsu
(16/16 lembar "berubah" padahal manifest identik).

**c. Nama lembar/revisi salah harus GAGAL.** Sebelumnya nama yang salah
tuli diperlakukan sebagai nama lembar, manifest tidak ditemukan, lalu alat
melaporkan *"tidak ada perubahan"* — kesimpulan yang menyesatkan. Kini
divalidasi lebih awal dan keluar dengan **exit 2**.

---

## 3. `export_xlsx.py` — Excel untuk procurement & QA

```bash
python tools/export_xlsx.py                       # dist/gpf-register.xlsx
python tools/export_xlsx.py -o laporan.xlsx
```

Tujuh sheet: **BOM per Lembar**, **Komponen Gabungan** (pivot lintas lembar),
**Equipment Register**, **Line List**, **Instrument Index**,
**Register Dokumen**, **Ringkasan**.

Isi aktual: 42 baris BOM, 31 komponen unik, 9 equipment, 7 line,
23 instrumen, 16 dokumen.

### Prinsip: hanya ekspor yang dapat dibuktikan

| Diekspor | Tidak diekspor |
|---|---|
| BOM dari tabel lembar isometrik | **Panjang pipa nyata** — isometrik berskala NTS, tidak dapat dikonversi tanpa tabel vertex |
| Line list & instrument index dari design basis | Harga / material take-off berbayar |
| Register dokumen dari `documents.json` | Angka hasil tebakan |

Baris tanpa tag pada tabel equipment (pipe rack, access road, fence, tank
bund) diberi label `(non-tag)` agar tidak dihitung sebagai peralatan
ber-tag.

---

## 4. Uji negatif

```
[PASS] titleblock: repo bersih exit 0
[PASS] titleblock: tanggal dihapus -> exit 1
[PASS] titleblock: ukuran registri salah -> exit 1
[PASS] revdiff: rentang sama -> exit 0
[PASS] revdiff: revisi salah -> exit 2
[PASS] revdiff: lembar salah -> exit 2
[PASS] export_xlsx: menghasilkan berkas
[PASS] export_xlsx: sheet & data lengkap
HASIL TOOLS TEST: 8/8
```

---

## 5. Status quality gate

```
HASIL: 26/26 lulus
SEMUA GATE LULUS
```

Langkah: environment, hygiene, consistency, bom, **titleblock**, lint 16 DXF,
consistency-negtest, bom-negtest, **tools-test**, tests.
