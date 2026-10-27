# BOM_CHECK.md — Konsistensi Bill of Materials vs Geometri Isometrik

BOM pada lembar isometrik ditulis **tangan** sebagai daftar literal di script
generator. Karena itu ia mudah menyimpang dari geometri yang benar-benar
digambar — dan riwayat proyek membuktikannya.

---

## 1. Akar masalah yang ditutup

Dari `dokumen/04-review-log.md`, **ROUND A2**, temuan #2–#4:

| Lembar | Kutipan temuan | Koreksi (manual) |
|---|---|---|
| ISO-0003 | "4× elbow LR90 DN150" vs geometri **3 belokan** | BOM → "3×" |
| ISO-0004 | "2× flange WN DN80" vs flange suction DN65 | BOM → DN80(1)/DN65(1) |
| ISO-0005 | "8× elbow LR90 DN80" vs geometri **9 belokan** | BOM → "9×" |

Ketiganya ditemukan lewat pembacaan visual manual dan diperbaiki satu per satu.
`tools/bom_extract.py` membuat pemeriksaan itu **otomatis dan deterministik**.

---

## 2. Cara kerja

```
        ┌──────────────────────────┐
DXF ───▶│ 1. hitung belokan dari   │──┐
        │    geometri REF-PROC     │  │
        └──────────────────────────┘  ├──▶ bandingkan ──▶ ERROR bila beda
        ┌──────────────────────────┐  │
        │ 2. parse tabel BOM di    │──┘
        │    kolom kanan lembar    │
        └──────────────────────────┘
```

### 2.1 Menghitung belokan dari geometri

Setiap segmen `LINE` pada layer `REF-PROC` dikumpulkan, lalu ujung yang
berimpit (< 0,35 mm) dikelompokkan menjadi titik sambungan:

| Derajat titik sambungan | Klasifikasi | Dihitung? |
|---|---|---|
| 0–1 segmen | ujung bebas / *dead end* | tidak |
| **2 segmen, arah berubah > 5°** | **elbow** | **ya** |
| 2 segmen, arah sama | kolinear (sambungan lurus) | tidak |
| ≥ 3 segmen | **TEE / cabang** | tidak |

Sudut isometrik sejati berjarak 60°, sehingga ambang 5° aman memisahkan
elbow dari sambungan lurus.

### 2.2 Membaca BOM

Tabel BOM berada di kolom kanan lembar dengan koordinat tetap
(`iso_common.py`): kolom `NO` (x 272–277), `DESCRIPTION` (276–300),
`SIZE` (330–340), `QUANT` (340–360). Baris elbow dikenali dari deskripsi
mengandung `ELL`/`ELBOW`; tee dari `TEE`.

---

## 3. Batasan yang disengaja

Ini penting agar angka yang dilaporkan **jujur**:

| Tidak diverifikasi | Alasan |
|---|---|
| **Panjang pipa (meter)** | Isometrik berskala **NTS**; panjang pada kertas tidak dapat dikonversi ke panjang nyata tanpa tabel vertex |
| **DN per belokan** | DN hanya ada di label teks, tidak tertanam di entitas garis. Perbandingan dilakukan pada **total** belokan per lembar |
| **Flange / gasket / bolt** | Tidak tergambar sebagai entitas geometris yang dapat dihitung andal |

Yang **dapat** dihitung secara deterministik adalah **jumlah belokan**, karena
setiap belokan adalah konsekuensi geometri, bukan anotasi.

---

## 4. Pemakaian

```bash
python tools/bom_extract.py            # laporan
python tools/bom_extract.py --json     # terstruktur (CI)
python tools/bom_extract.py --strict   # warning = gagal
```

Contoh keluaran (kondisi repo saat dokumen ini ditulis):

```
lembar           segmen  belokan elbow BOM tee BOM
--------------------------------------------------
iso_co1003            3        2         2       0
iso_co1004           10        9         9       0
iso_go1002            7        4         4       1
[INFO ] iso_go1002   1 tee di BOM (tidak dihitung sebagai belokan)
HASIL: 0 error, 0 warning
KONSISTEN
```

Ketiganya cocok: CO-1003 (2 = 2), CO-1004 (9 = 9), GO-1002 (4 = 4,
dengan 1 tee yang memang tidak mengubah arah).

---

## 5. Uji negatif

Validator yang selalu hijau tidak berguna. `tools/test_bom_negative.py`
mengubah kuantitas elbow pada **salinan** repo:

```
[PASS] baseline repo bersih (harus exit 0)
[PASS] elbow BOM terlalu sedikit (go1002: 4 -> 3)
[PASS] elbow BOM terlalu banyak (co1004: 9 -> 12)
[PASS] elbow BOM di-nol-kan (co1003: 2 -> 0)
HASIL NEGATIVE TEST BOM: 4/4
```

Keduanya dijalankan otomatis di quality gate (`bom` + `bom-negtest`) dan di CI.

---

## 6. Catatan investigasi (untuk pengembangan lanjutan)

Saat memvalidasi, ekstraktor sempat melaporkan **GO-1002 = 5 belokan**
sedangkan BOM menulis 4. Penelusuran menunjukkan titik `(150.75, 150.00)`
adalah **tee** tempat GO-1002 bertemu tailpipe FL-1005 — bukan elbow.
Logika awal menghitungnya sebagai belokan sehingga muncul ERROR palsu.

Klasifikasi berbasis **derajat titik sambungan** (§2.1) memperbaikinya dan
mengembalikan hasil 4 belokan, sesuai komentar di `cad/iso_go1002.py`
("Elbow at B/D/E/F").

Kandidat peningkatan berikutnya, bila DN per segmen ingin ikut divalidasi:
sisipkan metadata DN ke entitas (XDATA) saat build, sehingga BOM dapat
dihitung penuh **per ukuran** tanpa menebak.
