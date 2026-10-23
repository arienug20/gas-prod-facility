---
name: company-cad-standard
description: Aturan drafting perusahaan untuk semua drawing P&ID, piping plan, dan isometric (proyek oil & gas). WAJIB dimuat bersama skill dxf/cad setiap membuat atau merevisi drawing. Mengatur tinggi font Arial per kategori teks, line break pada persilangan garis (major line selalu tampil), lineweight per jenis line, larangan tabrakan teks, dan panah aliran pada setiap line.
license: Proprietary — internal company standard
---

# COMPANY CAD STANDARD — P&ID / PIPING PLAN / ISOMETRIC

Provenance: standar drafting internal perusahaan (manual AutoCAD →
ditranslasikan ke pipeline cadgen/`dxf`). Dimuat SETIAP kali membuat atau
mengubah drawing skematik pipa.

## 1. TEKS — MTEXT, Arial, tinggi 0,5–3,0 (mm pada ukuran kertas)

Perintah perusahaan: *MText → font Arial → height 0.5~3*. Pada pipeline
cadgen: teks **TIDAK digambar sebagai outline** — script menyimpan manifest
`TEXTS`, lalu post-processor `apply_text.py` (bawaan skill dxf hasil patch
perusahaan: `~/.agents/skills/dxf/scripts/apply_text.py`) menulis **entity
MTEXT asli** (style ARIAL, `arial.ttf`, attachment middle-center) pasca-build.
Entity TEXT (single-line) tidak dipakai — perusahaan memakai MTEXT.

| Kategori teks | Tinggi (mm) | Contoh |
|---|---|---|
| Penamaan equipment (tag & nama) | **2,5 – 3,0** | "V-101 3-PHASE SEPARATOR", "P-101", tag instrumen dalam bubble (≥2,0) |
| Nomor line (line number + size) | **1,5 – 2,0** | "100-GO-1002 DN100" |
| Flow from/to (label asal-tujuan) | **1,8 – 2,3** | "TO TANK T-101", "FROM PRODUCTION HEADER" |
| Semua teks lain (notes, dim, BOM, title block) | 0,5 – 3,0 (cap **3,0**) | judul sekat ≤ 3,0; catatan 1,8–2,5 |

Aturan tambahan:
- Label BL yang memuat tujuan + nomor line DIPISAH dua baris/dua teks
  dengan tinggi masing-masing kategori (from/to 1,8–2,3; line number 1,5–2,0).
- Tidak ada teks < 0,5 atau > 3,0 mm.

## 2. PERSILANGAN LINE — BREAK, MAJOR SELALU TAMPIL

Perintah perusahaan: *BREAK/BR → klik segmen yang di-break*. Pada cadgen:
yang di-break = garis MINOR, digambar sebagai dua segmen dengan **gap 3 mm**
di titik persilangan (gap sejajar arah garis minor, terpusat di titik silang).
Garis MAJOR tidak pernah terputus.

Prioritas (yang lebih bawah di-break):
1. Major process line (REF-PROC: line proses utama, header, flare) — TIDAK PERNAH di-break
2. Minor process line (drain, vent, sample, line DN lebih kecil) — break saat bersilang dgn (1) atau sesama (2) — yang lebih kecil yang break
3. Sinyal instrumen (REF-SIG/REF-SIGP) — break saat menyeberang garis proses apa pun
4. Dimensi/leader — break saat menyeberang apapun

Bukan persilangan (tidak di-break): tee/junction (garis menyambung),
terminal ke equipment.

## 3. LINEWEIGHT — BEDA PER JENIS LINE

Perusahaan: lineweight berbeda, terutama major vs minor. Implementasi:
post-process `apply_text.py` (ezdxf; menulis MTEXT **dan** memasang pens
dalam satu pass) SETELAH setiap build — cadgen merender
`LineweightPolicy.ABSOLUTE`, jadi hasilnya terlihat di viewer/snapshot dan
terbawa ke AutoCAD/plot. Script kanonik: `~/.agents/skills/dxf/scripts/
apply_text.py` (skill dxf sudah dipatch perusahaan; salinan proyek:
`cad/apply_text.py`).

| Layer | Lineweight |
|---|---|
| REF-PROC (major process) | **0,50 mm** |
| REF-EQUIP (equipment) | 0,35 mm |
| REF-FRAME | 0,35 mm |
| REF-SYM (valve, simbol, bubble) | 0,25 mm |
| REF-TITLE | 0,25 mm |
| REF-TEXT | 0,18 mm |
| REF-ROAD | 0,18 mm |
| REF-SIG / REF-SIGP / REF-HATCH / REF-FENCE | 0,13 mm |
| REF-GRID / REF-DIM (isometrik — meniru referensi) | 0,09 mm |

**URUTAN WAJIB per drawing**: `python <drawing>.py` → `python apply_text.py
<drawing>.dxf <drawing>.texts.json` → `validate_dxf_file` (0 error) →
snapshot PNG → visual check. Setiap rebuild menimpa .dxf → post-process
WAJIB diulang. (Script lama `apply_pens.py` hanya memasang pens tanpa MTEXT
— tidak dipakai lagi untuk drawing engineering.)

## 4. TABRAKAN TEKS — DILARANG

Teks tidak boleh menabrak line / teks lain / equipment / valve. Verifikasi
visual PNG (subagent dengan kemampuan baca gambar) dengan checklist eksplisit
per kategori; perbaiki dengan memindah teks (bukan menghapus informasi).
Maksimum 3 iterasi per file; temuan sisa wajib dilaporkan.

## 5. ALIRAN — SETIAP LINE WAJIB ADA FLOW

Setiap line proses (P&ID, plan, iso) minimal 1 panah aliran; tambahkan pada:
- tiap perubahan arah (plan/iso),
- tiap ±100 mm panjang gambar (P&ID) / ±15 m (plan),
- semua battery-limit arrow.
Sinyal instrumen tidak diberi panah aliran (bukan aliran proses).

## 7. GAYA ISOMETRIK — STANDAR ISO 6412-2, ISO 10628-2 & REFERENSI FNKT-10 (WAJIB UNTUK ISO)

Sumber acuan: **ISO 6412-2:2017** (*Simplified representation of pipelines — Part 2: Isometric projection*), **ISO 10628-2:2012** (*Graphical symbols for chemical & petrochemical industry*), **ANSI/ISA-5.1-2024**, dan dokumen proyek **`FNKT-10-L0-DWG-007`** (dibedah ulang Modelspace 3D + Viewport `(1, -1, 1)` + Layout 22 Oct 2026). Berlaku untuk SEMUA isometrik piping; plan/P&ID tidak berubah.

- **LARANGAN MUTLAK `POLYFACE` / MESH 3D**: **DILARANG memasukkan mesh 3D (`POLYFACE`) ke dalam DXF isometrik** — gambar isometrik perpipaan adalah proyeksi vektor 2D murni (ukuran file target **~90–150 KB per sheet tunggal**, dan **< 500 KB untuk multi-sheet DXF**).
- **Library Standar Bersama (`iso_common.py`)**: Seluruh script isometrik WAJIB mengimpor `IsoContext` dari `scripts/iso_common.py` (atau `cad/iso_common.py` di folder proyek) agar tata letak furniture 3-kolom, simbol ISO, balon BOM, dan dimensi miring (*oblique*) seragam 100%.

### 7.1 Orientasi Proyeksi (TRUE PIPING ISOMETRIC 30°/150°/90°)
- **Sumbu Timur (+E)**: miring **+30° naik ke kanan-atas**, `EX = (+cos 30°, +sin 30°) = (+0.8660254, +0.5)`. (Barat `WX = -EX = (-0.8660254, -0.5)`).
- **Sumbu Utara (+N)**: miring **+150° naik ke kiri-atas**, `NX = (-cos 30°, +sin 30°) = (-0.8660254, +0.5)`. (Selatan `SX = -NX = (+0.8660254, -0.5)`).
- **Sumbu Vertikal (+UP / -DN)**: **tegak lurus murni (±90°)**, `UX = (0.0, +1.0)`, `DNX = (0.0, -1.0)`.
- **DILARANG menggambar run E-W atau N-S secara horizontal datar (0°)** — garis horizontal 0° hanya boleh dipakai untuk garis rak (*shelf*) anotasi, tabel furniture, atau jika pipa memang berbelok 45° terhadap sumbu plant.

### 7.2 Dimensi & Oblique Isometric Extension Lines (`"dims"` di Manifest)
- Entity `DIMENSION` dibuat oleh `apply_text.py` (dimstyle `GPF-ISO`): panah **closed filled** (`dimasz=1.6`), teks **DI ATAS garis dimensi** dan **sejajar arah garis** (`dimtad=1, dimtih/dimtoh=0`), extension line gap `1.0` + overshoot `1.0`, **angka mm bulat tanpa satuan** (`"17000"`).
- **Isometric Oblique Extension Lines (`"oblique"` di manifest — WAJIB)**:
  - `apply_text.py` membaca field `"oblique"` dan meneruskannya ke `dxfattribs={"oblique_angle": float(d["oblique"])}` sebelum `dim.render()`.
  - **Run Timur (+E, `angle=30.0`)** ditarik ke bawah (`base` di bawah pipa): gunakan `"angle": 30.0, "oblique": -120.0` → garis ekstensi jatuh vertikal (`-90°`). Bila ditarik ke atas (`base` di atas pipa): gunakan `"angle": 30.0, "oblique": 60.0` → garis ekstensi naik vertikal (`+90°`).
  - **Run Utara (+N, `angle=-30.0`)** ditarik ke bawah (`base` di bawah pipa): gunakan `"angle": -30.0, "oblique": -60.0` → garis ekstensi jatuh vertikal (`-90°`). Bila ditarik ke atas (`base` di atas pipa): gunakan `"angle": -30.0, "oblique": 120.0` → garis ekstensi naik vertikal (`+90°`).
  - **Riser Vertikal (+UP/-DN, `angle=90.0`)** ditarik ke kiri-bawah (`WX`): gunakan `"angle": 90.0, "oblique": 120.0` → garis ekstensi miring sejajar sumbu isometrik `WX/EX` (`30°`).
- **Chained Dimension String**: dimensi berjejer sepanjang satu run harus berbagi titik stasiun (`flange → valve → fitting → orifice → elbow`) dan menggunakan offset `base` yang sama agar segaris lurus.
- Semua dimensi berada di layer `REF-DIM` (lineweight `9` = `0.09 mm` sangat tipis).

### 7.3 Spesifikasi Simbol Komponen Isometrik (ISO 6412-2 & ISO 10628-2)
Semua simbol in-line WAJIB diputar (`rot(..., ang)`) mengikuti sudut arah pipa `u` (`hdg(u)`):
1. **Elbow & Tee**: **Miter siku tajam** — DILARANG menggunakan `ARC` lengkung pada belokan pipa (0 entitas `ARC` pada layer `REF-PROC`).
2. **Gate Valve (`ctx.gate(P, u)`) — ISO 10628-2 & FNKT-10 `block "gate valve"`**:
   - Bentuk **Bowtie (`▷◁`) murni** (2 garis tegak ujung `±hL` + 2 garis silang diagonal sudut-ke-sudut, **TANPA** garis penutup atas/bawah sejajar pipa agar tidak kembar dengan simbol *Pipe Support*), ditambah **2 tick flange `SOLID`** (`tl=0.4, tw=2.0`) di kedua ujung.
3. **Globe / Control Valve (`ctx.globe(P, u, has_actuator=True, act_tag=...)`) — ISO 10628-2 Item 4.1.2**:
   - Bentuk **Bowtie (`▷◁`)** + **bola terisi penuh (*filled dot* `●`, `r=0.65 mm`)** di titik pusat `P` + 2 tick flange `SOLID`.
   - Untuk *Control Valve*: tambahkan *stem* tegak lurus pipa (`5.0 mm`) + kubah diafragma setengah lingkaran (`ARC r=2.2 mm` + garis dasar) sesuai ANSI/ISA-5.1.
4. **Check Valve (`ctx.check_valve(P, u)`) — ISO 10628-2 Item 4.1.6**:
   - Dua garis tegak ujung (`-hL` dan `+hL`) + **garis diagonal *flapper*** dari puncak hulu `(-hL, +hW)` ke bawah hilir `(+hL, -hW)` + **titik engsel terisi penuh (`●`, `r=0.45 mm`)** di puncak hulu `(-hL, +hW)` + **kepala panah `SOLID`** di ujung hilir `(+hL, -hW)` + 2 tick flange `SOLID`.
5. **Concentric Reducer (`ctx.reducer(P, u, L=2.6, W1=1.2, W2=2.2)`) — ISO 6412-2 §6.4**:
   - **Trapesium konsentris tertutup** (4 garis: sisi kecil `W1`, sisi besar `W2`, dan 2 garis tirus penghubung) yang berotasi sejajar arah pipa `u`.
6. **Y-Strainer (`ctx.strainer(P, u)`) — ISO 10628-2**:
   - Bodi persegi panjang sejajar pipa + kantong cabang Y miring ke bawah-hilir dengan garis saringan (*mesh*) di dalamnya + 2 tick flange `SOLID`.
7. **Orifice Flange & Transmitter (`ctx.orifice(P, u, tag="FT-xxx", lead_dir=UX)`)**:
   - Dua garis pelat orifice tegak lurus pipa (`half=3.8–4.0 mm`, jarak `±0.8 mm`) + garis *instrument lead* dari tepi pelat ke tepi lingkaran balon instrumen (`r=3.6 mm` agar teks `FT-141` tidak menyentuh lingkaran).
8. **Shop / Field Weld (`ctx.sw(P, u)`) — ISO 6412-2 §5.2 & FNKT-10 `block G$C1084F77C`**:
   - **Titik las bulat terisi penuh (*filled weld dot* `●`, `r=0.8 mm`)** tepat pada garis pipa + teks `"SW"`.
9. **Pipe Support (`ctx.pipe_support(P, u, tag, stype)`) — FNKT-10 `block "Support 1"`**:
   - Kotak tertutup miring sejajar pipa (`3.6×1.4 mm`) dengan silang diagonal `X` (`☒`) + garis leader ke rak horizontal (*shelf*) + teks 2 baris (`PS-001` / `RESTING` atau `GUIDE`).
10. **Part Callout Balloons (`ctx.part_bubble` & `ctx.stacked_bubbles`)**:
    - Setiap jenis item BOM WAJIB ditunjuk oleh lingkaran balon (`r=1.85 mm`, Ø3.7 mm) berisi nomor urut BOM (`1`..`15`) dengan garis leader yang berhenti tepat di tepi lingkaran. Untuk sambungan *flange*, gunakan `stacked_bubbles` berderet 3 lingkaran (`[flange, gasket, bolt]`).
11. **Line Callout (`ctx.line_callout`) & Continuation (`ctx.continuation`)**:
    - *Line Callout*: panah `SOLID` menunjuk titik pipa + leader miring + rak horizontal + teks 2 baris (`<LINE NO>` / `BOP.EL. +xxxx`).
    - *Continuation*: garis pipa putus-putus (*dashed line*) sepanjang `12–22 mm` selepas flange batas + teks 3 baris (`CONT. TO/FROM ...`, `DRW NO. ...`, `SHEET x OF y`).

### 7.4 Furnitur Lembar A3 (420×297 mm) — TATA LETAK 3-KOLOM PERSIS FNKT-10
- Border luar `(2, 1.3)–(422, 298.3)` & border dalam `(7, 6.3)–(417, 293.3)` dengan grid `1–12` (horizontal) dan `A–H` (vertikal). Area gambar pipa di sebelah kiri: `x = 7..271.5`, `y = 6.3..293.3` (untuk `x = 195.4..271.5` di bawah tabel NDT `y = 6.3..236.4`).
- **Kompas Isometrik (North Arrow)** di kiri-atas `(x ≈ 25, y ≈ 271)`: bintang 4-arah isometrik dengan panah utama menunjuk **miring 150° (kiri-atas, arah +N)** dan huruf **`N`** di ujung panah kiri-atas (persis FNKT-10).
- **Kolom 1 Atas — Tabel NDT & Line Data (`x = 195.4..271.5, y = 236.4..290.7`, garis tengah `x = 235.1`)**:
  - 4 baris atas: `NDT :` → `RADIOGRAPHY TEST (RT)` | `100%`, `ULTRASONOGRAPHY (UT)` | `100%`, `MAGNETIC PARTICLE TEST (MT)` | `NOTE 3`, `DYE PENETRANT TEST (PT)` | `NOTE 3`.
  - 7 baris bawah: `SERVICE LINE`, `CODE` (`ASME B31.3`), `LINE NUMBER`, `PIPING CLASS` (`A1A`), `DESIGN TEMPERATURE`, `DESIGN PRESSURE`, `OPERATING TEMP / PRESS`.
- **Kolom 2 — Tabel BILL OF MATERIALS Vertikal Penuh (`x = 271.5..349.5, y = 6.3..290.7`)**:
  - Kolom: `NO` (`271.5..275.9`) | `DESCRIPTION` (`275.9..331.8`) | `SIZE` (`331.8..340.7`) | `QUANT` (`340.7..349.5`).
  - Dikelompokkan dengan sub-header kategori seperti FNKT-10: **`PIPE`** (kuantitas dalam `M`), **`FITTING`** (`EA`), **`FLANGE`** (`EA`), **`GASKET`** (`EA`), **`BOLT`** (`EA`), **`VALVE`** (`EA`).
- **Kolom 3 Kanan — NOTE, LEGEND, REFERENCE DOC, REV TABLE & TITLE BLOCK (`x = 349.5..413.0, y = 6.3..290.7`)**:
  - `y = 231.7..290.7`: **NOTE** (mm, NTS, Pipe spec A1A, Field welds SW, slope/service).
  - `y = 144.7..231.7`: **LEGEND** (simbol ISO + label `PIPE SUPPORT`, `SHOP WELD / SW`, `FLANGE CONNECTION`, `VALVE`, `FLOW ARROW`, `CONTINUATION LINE`).
  - `y = 121.3..144.7`: **REFERENCE DOCUMENT** (`GPF-00-PI-PID-0001` P&ID, `GPF-00-PI-PLN-0002` Piping Plan, `GPF-00-DB-0001` Design Basis).
  - `y = 96.4..121.3`: **Tabel Revisi** (`NO | REV | DESCRIPTION | DATE | REM`, urutan baris *bottom-up* dari bawah ke atas A0→A5 seperti FNKT-10).
  - `y = 53.3..96.4`: **PROJECT** (`GAS PRODUCTION FACILITY - ONSHORE FIELD`), **COMPANY**, **CONSULTANT**.
  - `y = 30.7..53.3`: **APPROVAL** (`DRAWN | CHECKED | APPROVED`).
  - `y = 16.7..30.7`: **TITLE** (`ISOMETRIC DRAWING` / `<LINE NUMBER>` / `<SERVICE>`).
  - `y = 6.3..16.7`: **DRAWING NUMBER** | **SHT** (`01/03`) | **REV** (`A5` dalam segitiga) | **SCALE** (`NTS`).

## 8. QA CHECKLIST (sebelum menyatakan selesai)

1. **MTEXT**: jumlah entity MTEXT == panjang manifest `<drawing>.texts.json`;
   semua style ARIAL; char_height 0,5–3,0 dan sesuai kategori §1; entity
   TEXT (single-line) = 0; tidak ada outline bd.Text tersisa (REF-TEXT di
   geometri kosong, teks hanya sebagai MTEXT di layer REF-TEXT).
2. Semua persilangan garis proses/sinyal: minor ter-break gap 3 mm, major utuh.
3. Pens terpasang (lineweight layer ≠ default; major terlihat lebih tebal di PNG).
4. Tidak ada tabrakan teks.
5. Setiap line proses ≥1 panah aliran.
6. validate_dxf_file = 0 error; bbox dalam border.
7. Snapshot dirender ULANG setelah post-process; visual check membaca PNG
   final (MTEXT harus terbaca — bukti render).
8. Revisi drawing: bump REV (A1→A2 dst.) + baris rev table + keterangan
   perubahan.
9. **Isometrik (khusus §7)**: jumlah DIMENSION == panjang `"dims"` manifest,
   semua dimstyle GPF-ISO (panah closed filled, teks aligned di atas garis),
   tanpa ARC di run pipa (miter), jumlah SOLID == manifest `"solids"`
   (flow arrow + weld dot), furnitur lembar §7 lengkap (kompas, BOM
   vertikal, tabel data line + NDE, LEGEND, note mm).
