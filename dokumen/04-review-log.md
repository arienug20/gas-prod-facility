# REVIEW LOG — GPF DRAWING PACKAGE (P&ID + ROUTING + ISOS)

Dokumen : GPF-00-QA-0004, Rev A0
Reviewer: PM (AI) — verifikasi independen + koreksi tindak lanjut
Tanggal : 09 Oct 2026
Objek   : GPF-00-PI-PID-0001, GPF-00-PI-PLN-0002, GPF-00-PI-ISO-0003/0004/0005

## 1. Verifikasi independen (oleh PM, bukan oleh eksekutor)

| File | validate_dxf_file | Entity | BBox | TEXT entity | Kesimpulan |
|---|---|---|---|---|---|
| pid_v101.dxf | 0 error | 14.947 | (20,10)-(831,584) A1 | 0 | LULUS |
| routing_plan.dxf | 0 error | 16.560 | (0,0)-(841,594) A1 | 0 | LULUS |
| iso_go1002.dxf | 0 error | 6.028 | (0,0)-(420,297) A3 | 0 | LULUS |
| iso_co1003.dxf | 0 error | 4.765 | (0,0)-(420,297) A3 | 0 | LULUS |
| iso_co1004.dxf | 0 error | 6.263 | (0,0)-(420,297) A3 | 0 | LULUS |

Catatan: bbox (0,0)-… memuat trim-edge ISO 5457 (bagian sah frame).
Semua layer memakai token REF (kontrak skill dxf). Teks seluruhnya outline
bd.Text sesuai kontrak. Verifikasi visual PNG dilakukan subagent glm-5.3-flash
(mendukung baca gambar) dengan iterasi perbaikan — temuan tabrakan label
sudah ditutup semua (lihat laporan eksekusi).

## 2. Temuan review tindak lanjut (pola kutip → masalah → koreksi → status)

| No | Lokasi | Kutipan/temuan | Jenis masalah | Koreksi yang dieksekusi | Status |
|---|---|---|---|---|---|
| 1 | P&ID, sinyal SIS | "Sinyal PT-102/LT-122/LT-132 → ESD-1 hanya di Note 4" | Logika narasi melompat (inisiatif SIS tidak grafis) | 3 rute dashed REF-SIG + label "SIS" digambar ke blok ESD-1 | TUTUP (1 iterasi visual) |
| 2 | ISO-0003 BOM | "4× elbow LR90 DN150" vs geometri 3 belokan | Hitungan tidak konsisten | BOM → "3×" | TUTUP |
| 3 | ISO-0004 BOM | "2× flange WN DN80" vs flange suction DN65 | Hitungan tidak konsisten | BOM → "DN80 (1)/DN65 (1)" | TUTUP |
| 4 | ISO-0005 BOM | "8× elbow LR90 DN80" vs geometri 9 belokan | Hitungan tidak konsisten | BOM → "9×" (K = ujung flange, bukan elbow) | TUTUP |
| 5 | ISO-0005 elevasi | "EL +6.200" vs design basis "+6.15" | Angka tidak konsisten antar-dokumen | Teks → "EL +6.150" | TUTUP |

## 3. Deviasi eksekusi yang diterima (tercatat, non-blocking)

1. P&ID: trim-rect luar (0,0)-(841,594) tidak digambar; border tunggal — diterima.
2. P&ID: grid reference di dalam border — diterima (aturan validasi melarang entity di luar).
3. ISO-0005: segmen AB digambar 36 mm (NTS diperpanjang) demi keterbacaan 3 fitting — diterima, dim teks tetap nilai sesungguhnya (NTS — dimensions govern).
4. ISO-0005: posisi simbol GV-103 digeser dari posisi proporsional murni (diluar arc elbow) — diterima dengan dim tetap benar; catat untuk shop detail.
5. Routing plan: strip notes di bawah sheet (bukan di bawah line-index) — diterima (keterbatasan ruang).
6. FL-1005 memisahkan segmen (13,35)-(15,35) untuk menghindari duplikat geometri identik dengan GO-1002 pada layer sama — diterima (union geometri tetap sesuai manifest).

## 4. Catatan teknik untuk pengembangan (untuk revisi berikutnya)

1. PSV-101: untuk Issue for Construction, tambahkan bypass/car-seal dan
   inlet-outlet isolation policy sesuai praktik operator (API RP 521 §5.10).
2. Exclusion radius flare 13 m adalah asumsi — wajib verifikasi kalkulasi
   radiasi (API 521) sebelum layout dibekukan.
3. Iso belum memuat spes break, test package limit, dan support span mark —
   lengkapi saat detail design.
4. Elevasi GO-1002 di crossing (+6,5) vs slope 1:500 kontinu perlu
   rekonsiliasi di stress/rodding study.
5. Ukuran PSV DN100×150 & header DN150 belum diverifikasi hydraulik —
   blase/sizing calculation terpisah diperlukan.

## 5. Status paket

5/5 drawing: BUILT, tervalidasi 0 error, visual check lolos, koreksi review
tertutup. Paket layak diterbitkan sebagai **A0 — ISSUED FOR REVIEW**
(bukan untuk konstruksi).

---

# ROUND A1 — REVISI PER COMPANY DRAFTING STANDARD (09 Oct 2026)

Pemicu: standar drafting perusahaan (skill baru `company-cad-standard`:
teks Arial per kategori, break persilangan, lineweight per line, larangan
tabrakan teks, flow arrow semua line). Semua drawing direvisi A0 → A1
oleh kedua subagent, lalu diverifikasi independen PM.

## Verifikasi independen (PM)

| File | errors | Entity | BBox | TEXT | Pens perusahaan |
|---|---|---|---|---|---|
| pid_v101 | 0 | 15.528 | (20,10)-(831,584) | 0 | 9/9 layer ✓ |
| routing_plan | 0 | 17.023 | (0,0)-(841,594) | 0 | 11/11 layer ✓ |
| iso_go1002 | 0 | 6.216 | (0,0)-(420,297) | 0 | 8/8 layer ✓ |
| iso_co1003 | 0 | 4.951 | (0,0)-(420,297) | 0 | 7/7 layer ✓ |
| iso_co1004 | 0 | 6.455 | (0,0)-(420,297) | 0 | 7/7 layer ✓ |

## Perubahan A1 (ringkas)

1. **Teks**: equipment 2,5–3,0 (V-101 3,0; bubble 2,0–2,2); line number 1,5–2,0
   (semua 2,0); label from/to dipecah dari nomor line (2,0 + 1,8); judul
   4,0/3,5 → cap 3,0; header sekat 2,5. Tidak ada teks <0,5 atau >3,0.
2. **Break**: P&ID 48 titik (20 sinyal×proses, 27 sinyal×sinyal, 1 proses×proses
   CD di-break terhadap PW); plan: hop diganti gap 3 mm + 2 break CD; iso:
   6 break garis dim/leader. Major line selalu utuh.
3. **Flow arrows**: semua line proses ≥1 panah (P&ID +7 baru; plan 31 panah
   terverifikasi per rute; iso tiap run ≥1).
4. **Lineweight**: apply_pens.py dijalankan pada semua file pasca-build
   (REF-PROC 0,50 … REF-GRID 0,09); terverifikasi di layer table oleh PM;
   subagent mengonfirmasi terlihat di PNG (renderer ABSOLUTE).
5. **Rev**: title block + rev table A1 "REVISED PER COMPANY DRAFTING STANDARD".

## Temuan & deviasi A1

| No | Temuan | Status |
|---|---|---|
| 1 | Design basis §6 masih "Rev A0" saat subagent sudah bump A1 | TUTUP — disinkronkan PM (kalimat rev → A1) |
| 2 | Sliver 1 mm antara 2 break berdekatan di riser x=502 (jarak silang 4 mm) | Diterima — konsekuensi geometri, tidak melanggar aturan |
| 3 | P&ID: gas riser × PSV line (major×major) keduanya utuh | SESUAI ATURAN — sesama major tidak di-break |
| 4 | Plan: CD-1007 di-break terhadap PW-1006 (DN sama) | Diterima — tie-break minor: CD dipilih sebagai minor (drain) |

## Status akhir

5/5 drawing **A1**: valid 0 error, pens lengkap, visual lolos. Skill
`company-cad-standard` aktif permanen (skill overlay, tidak tertimpa update
text-to-cad) + project AGENTS.md mengikat untuk revisi berikutnya.

---

# ROUND A2 — OUTLINE → MTEXT ASLI (12 Oct 2026)

Pemicu: keluhan user — "teks masih pakai garis, bukan command MTEXT".
Akar masalah: skill `dxf` upstream mewajibkan outline (dirancang untuk
CAM). Solusi permanen: **skill dxf DIPATCH langsung** (sesuai keputusan
user) + post-processor `apply_text.py`.

## Perubahan sistem

| Item | Isi |
|---|---|
| Skill `dxf` (patched) | Kontrak teks dipecah CAM/engineering; seksi "Company standard override" (MTEXT, break, pens, flow, rantai build, revisi); QA MTEXT di Validation; pola manifest di generator-templates.md |
| `~/.agents/skills/dxf/scripts/apply_text.py` | MTEXT ARIAL + pens sekali jalan; idempoten (hapus MTEXT lama → tulis ulang); guard height 0,5–3,0; buat layer manifest bila belum ada |
| `~/skills-patches/` | Backup pristine + patch + `reapply.sh` + README — proteksi dari `npx skills add` yang menimpa |
| Skill `company-cad-standard` | Disinkronkan: §1 MTEXT, §3 rantai apply_text, §6 QA MTEXT |
| Project AGENTS.md + design basis §6/§6a | Rantai build & aturan teks MTEXT |

## Verifikasi independen (PM, 12 Oct)

| File | MTEXT | Manifest | TEXT | errors | Outline sisa | Pens | Visual |
|---|---|---|---|---|---|---|---|
| pid_v101 | 196 | 196 ✓ | 0 | 0 | 0 | 9/9 | 6/6 lolos (flash) |
| routing_plan | 155 | 155 ✓ | 0 | 0 | 0 | 11/11 | lolos (flash) |
| iso_go1002 | 70 | 70 ✓ | 0 | 0 | 0 | 8/8 | lolos (flash) |
| iso_co1003 | 52 | 52 ✓ | 0 | 0 | 0 | 7/7 | lolos (flash) |
| iso_co1004 | 74 | 74 ✓ | 0 | 0 | 0 | 7/7 | lolos (flash) |

Semua style ARIAL; char_height {1,8 … 3,0} sesuai kategori; ukuran DXF
turun ±97% (outline hilang): pid 4,6 MB → 254 KB; routing 5,36 MB → 126 KB.

## Temuan & catatan A2

| No | Temuan | Status |
|---|---|---|
| 1 | Guard `if TEXTS:` pola template tak pernah terisi (build dieksekusi di modul lain) — subagent B menemukan `__cadgen_model__.func()` untuk side-effect manifest | Diterima & didokumentasikan; manifest terisi terbukti (196/155/70/52/74) |
| 2 | Leader/bubble yang tadinya ikut layer REF-TEXT geometri dipindah ke REF-SYM (3 iso) | Sesuai (geometri anotasi tetap ada, teks jadi MTEXT) |
| 3 | Tag valve 2,2 → 2,5 (kategori equipment) pada iso | Sesuai kategori |
| 4 | Minor visual: label FC/N2 berdempet di cluster pump P&ID; "RED 65X80" & cluster G–K iso padat | Minor diterima — teks tetap terbaca; catat untuk B0 IFC |
| 5 | 2× interupsi server selama dispatch — P&ID dirampungkan PM langsung (snapshot + PIL check) + visual oleh subagent flash | Tuntas |

## Status akhir paket

**5/5 drawing Rev A2**: MTEXT asli (perintah perusahaan terpenuhi), Arial,
tinggi per kategori, break persilangan, lineweight major/minor, panah aliran,
valid 0 error, visual lolos. Skill `dxf` resmi versi perusahaan (patched) —
re-apply via `~/skills-patches/reapply.sh` setelah update text-to-cad.

---

# ROUND A3 — RESTYLE ISOMETRIK PER REFERENSI FNKT-10 (13 Oct 2026)

Pemicu: user memberi referensi gambar proyek asli (Downloads/"Piping 3.zip",
"PIPING 1.zip" — FNKT-10, berisi iso DXF 20 sheet). Permintaan: isometrik
meniru referensi, terutama **cara memberi dimensi, bentuk panah, cara
memberi simbol**.

## Analisis referensi (programatik + visual subagent)

| Aspek referensi | Hasil analisis |
|---|---|
| Dimensi | Entity DIMENSION asli (413 aligned/linear), style GUMI: panah closed filled (dimasz 0,65 ≈ 0,8× teks), teks DI ATAS garis sejajar arah 30°/150°, ext gap/overshoot 0,4, mm bulat tanpa satuan, dimension string bersambung |
| Elevasi | Teks 2 baris "BOP.EL. ±xxxx" di bawah line number (bukan dim vertikal) |
| Elbow | Miter siku tajam — 0 entitas ARC di modelspace |
| Flow arrow | Segitiga SOLID terisi menempel run (66 buah/20 sheet) |
| Simbol | Weld dot terisi, flange 2 tick persegi, valve kotak-X, support "PS-xxx PAD" |
| Lembar | Kompas 4-arah kiri-atas, BOM strip vertikal kanan-atas, tabel data line + NDE tengah-atas, title block urutan rev→project→approval→title, "SHEET x OF y", CONT. TO/FROM |

## Perubahan sistem (permanen)

1. `apply_text.py` **v2** (skill + project + patch copy): manifest dict
   `{"texts","dims","solids"}` → menulis MTEXT + **DIMENSION asli**
   (dimstyle GPF-ISO: dimblk='' closed filled, dimasz 1,6, dimtxt 2,0,
   dimtad 1, dimtih/dimtoh 0, dimexo/exe 1,0, dimdec 0) + **SOLID**
   (flow arrow, weld dot) — idempoten.
2. Skill `company-cad-standard`: **§7 GAYA ISOMETRIK** baru (14 aturan,
   sumber FNKT-10) + §8 QA butir 9 (DIM/SOLID/ARC/furnitur) + PENS
   REF-DIM 0,09 (meniru referensi).
3. PENGEUALIAN dim riser vertikal: dipertahankan sebagai dim (850, 4200,
   dst.) untuk kejelasan fabrikasi; elevasi tetap anotasi BOP.EL. —
   keputusan PM, dicatat sebagai penyempurnaan aturan §7 ("dim run
   vertikal boleh; elevasi titik tetap teks").

## Verifikasi independen (PM, 13 Oct)

| File | MTEXT/man | DIM/man | SOLID/man | err | dimstyle | ARC run | Rev |
|---|---|---|---|---|---|---|---|
| iso_go1002 | 110/110 | 8/8 | 11/11 | 0 | GPF-ISO | 0 | A3 |
| iso_co1003 | 93/93 | 4/4 | 6/6 | 0 | GPF-ISO | 0 | A3 |
| iso_co1004 | 110/110 | 10/10 | 11/11 | 0 | GPF-ISO | 0 | A3 |

Dim text contoh: go1002 string `17000+8000+10000` (=35000); co1004
`1200|4200|3500|20000|3800|23000|1500|5500|1700|500`. Visual check flash
lolos (2–3 iterasi/file): panah closed filled, teks di atas garis, miter,
kompas, BOM vertikal, tabel data line.

## Temuan A3

| No | Temuan | Status |
|---|---|---|
| 1 | Dim dipecah per stasiun fitting agar teks tidak menimpa valve (17000+8000+10000) | Diterima — jumlah tetap konsisten |
| 2 | 2 ARC sisa di co1004 = simbol valve (bukan run) | Diterima — §7 melarang arc RUN |
| 3 | Minor: "+6.5 ROAD CROSSING" dilalui garis dim tipis; note 6 mepet kotak NOTE | Minor diterima (B0) |

## Status akhir

3/3 isometrik **A3** mengikuti gaya referensi FNKT-10; P&ID & plan tetap
A2. Sistem: gaya referensi sudah menjadi aturan permanen di skill —
isometrik berikutnya otomatis mengikuti.

---

# ROUND A4 — ORIENTASI ISO & SIMBOL VALVE PER REFERENSI (15 Oct 2026)

Pemicu: user — "lambang valve disesuaikan dengan isometric; cara pandang
view isometric referensi lebih benar".

## Analisis referensi (programatik + visual)

| Bukti | Hasil |
|---|---|
| Sudut LINE layer pipa (bucket 15°) | 0° (49) & 90° (24) dominan → **konvensi piping iso** (satu sumbu plan datar), bukan true isometric |
| Blok `gate valve` FNKT-10 | Kotak 2,85×1,59 (rasio 1,8:1) + diagonal X penuh sudut-ke-sudut + 2 tick flange 0,21×1,59 HATCHED di ujung; total 3,7 unit; mengikuti arah run |
| Visual (subagent flash) | Run E-W datar sempurna; N-S miring ±30°; valve kotak-X IKUT DIROTASI sejajar run; flow arrow mengikuti run |

## Perubahan

1. Skill `company-cad-standard` §7: aturan orientasi (u_E=(1,0) datar,
   u_N=(0.866,0.5) miring 30° naik kanan-atas, u_UP=(0,1)) + spesifikasi
   simbol valve terorientasi (kotak+X+flange SOLID, rotasi mengikuti run;
   globe/check bowtie dirotasi; flow arrow sejajar run).
2. 3 iso di-rebuild dengan transform baru + valve terorientasi; rev
   A3 → **A4** "ISO ORIENTATION & VALVE SYMBOL PER REFERENCE".
3. (Konteks) text-to-cad di-update ke **0.7.21** (14 Oct); patch perusahaan
   di-merge ulang (upstream hanya mengubah pin); viewer di-restart 0.7.21.

## Verifikasi independen (PM, 15 Oct)

| File | MTEXT/man | DIM/man | SOLID/man | err | dimstyle | Sudut run | Rev |
|---|---|---|---|---|---|---|---|
| iso_go1002 | 114/114 | 8/8 | 13/13 | 0 | GPF-ISO | 0°/30°/±90° | A4 |
| iso_co1003 | 97/97 | 4/4 | 8/8 | 0 | GPF-ISO | 0°/−90° | A4 |
| iso_co1004 | 114/114 | 10/10 | 15/15 | 0 | GPF-ISO | 0°/30°/±90° | A4 |

Visual (flash): kotak valve miring sejajar run + flange tick terisi
(shoelace 0,8 mm²), flow arrow sejajar run, dim string rapi.

## Temuan A4

| No | Temuan | Status |
|---|---|---|
| 1 | co1004 D→E tergambar campuran E+UP (14,04°) — konsekuensi vertex table lama yang menggabungkan dua leg dalam satu segmen; dim text tetap benar per leg | Diterima sementara (NTS, dim govern) — catat untuk B0: pecah menjadi 2 leg murni |
| 2 | Anchor start digeser (konsekuensi bbox orientasi baru) | Diterima |
| 3 | Label "+6.5 ROAD CROSSING" perlu geser 1 iterasi | TUTUP |

## Status akhir

3/3 isometrik **A4** (orientasi konvensi piping iso + valve terorientasi);
P&ID & plan A2; runtime cadgen 0.7.21; patch perusahaan utuh.

---

# ROUND 3D — MODEL 3D ROUTING + RENDER ISOMETRIK (20 Oct 2026)

Pemicu: user — "isometric masih XY, belum murni 3D". Klarifikasi teknis:
DXF 2D tidak dapat memuat 3DSOLID/ACIS baru (kontrak ezdxf); referensi
FNKT-10 memuat 761 3DSOLID yang dibuat di AutoCAD/Plant. Solusi sesuai
alur kerja proyek nyata: **3D model (STEP) + render isometrik dari kamera
3D**, dengan DXF iso tetap sebagai gambar berdimensi.

## Deliverable baru

| File | Isi |
|---|---|
| `src/piping_3d.py` | Model assembly 3D (mm): 6 equipment + 3 line pipa (sweep, elbow fillet 1,5D) + 6 flange + 2 stub nozzle P-101 |
| `step/piping_3d.step` | STEP assembly, **17 leaves berlabel**, 283 kB |
| `render/render_iso.png` / `render_top.png` | Overview isometrik & top (1600×1200) |
| `render/closeup_gas.png` / `closeup_suction.png` / `closeup_discharge.png` | Close-up multi-panel resolusi tinggi, tabung 15–51 px ber-shading |

Koordinat & elevasi dari design basis (plant m × 1000). Warna: gas kuning,
oil hijau, equipment abu.

## QA builder (deterministik)

- STEP `read_scene` = 17 leaves berlabel; bbox 9050..84300 / 8000..46800 /
  0..12000 mm ✓
- Elbow: face torus GO=4, CO-1003=1, CO-1004=9 — **persis jumlah belokan**,
  radius major 1,5×OD, minor = r pipa ✓
- Volume pipa ≈ π·r²·L nominal (0,744/0,043/0,490 vs 0,747/0,043/0,493 m³) ✓
- Pipa mendarat benar: gas → V-102 (menembus atap), suction → top P-101
  (via stub N-SUC), discharge → stub N-DIS → nozzle N1 T-101 (+6,15 m) ✓

## QA visual (flash, 2 putaran)

- Putaran 1: "belum murni 3D" — tabung 1–2 px pada render full-plant
  (zoom, bukan geometri). Putaran 2: close-up per line, tabung 15–51 px,
  shading terang/gelap terlihat, elbow membulat terkonfirmasi ✓
- Artefak terkonfirmasi sah: "loop kotak" T-101 = pendekatan N1 zigzag per
  design basis; "segitiga" P-101 = superposisi proyeksi — dibereskan stub.

## Temuan & catatan

| No | Temuan | Status |
|---|---|---|
| 1 | Kamera snapshot CLI auto-fit seluruh model (tidak bisa partial framing) | Diatasi via render hi-res + crop panel |
| 2 | 3DSOLID tidak dapat ditulis ke DXF oleh toolchain | Didokumentasikan — 3D deliverable = STEP + render; DXF = 2D berdimensi |
| 3 | Ground plane/bayangan/label belum ada di render | Catatan peningkatan berikutnya |

## Status akhir

Deliverable 3D: STEP 17 komponen + 5 render (overview + 3 close-up + top),
semua terverifikasi. Paket lengkap kini: 5 drawing DXF (P&ID A2, plan A2,
3 iso A4) + model 3D STEP + render.

---

# ROUND FNKT-FORMAT — DXF MULTI-SHEET FORMAT FNKT-10 (21 Oct 2026)

Pemicu: user — "render bagus; kalau format isometric CAD susah yah?" lalu
"formatnya ikut dokumen ini (FNKT-10-L0-DWG-007)".

## Solusi

File **`cad/GPF-00-PI-ISO-0007 SHT 1 - 3.dxf`** (30,4 MB) — format dokumen
FNKT-10: satu file multi-layout, **model space = mesh 3D** (17 POLYFACE/
POLYLINE — ACIS tak dapat ditulis toolchain, mesh = analog sah), **3 layout
"SHEET x OF 3"** berisi viewport isometrik (view_direction_vector
(0.69,0.55,0.48)) mengarah ke masing-masing line + furniture lengkap:
border ganda + grid 1-12/A-F, title block urutan FNKT (rev table A0–A4 →
PROJECT → COMPANY → CONSULTANT → approval → TITLE → DRAWING NUMBER|SHEET|
REV A4|SCALE NTS), BOM vertikal (GO: 9 baris; CO-1003: 6; CO-1004: 8),
NOTE, LEGEND, tabel data line + NDE (ASME B31.3). Teks MTEXT ARIAL
1,4–2,5 mm. Script: `src/export_iso_sheet_dxf.py`.

## QA

- Programatik: 3 sheet layouts, mesh 17 polyline, 432 MTEXT (heights
  1,4–2,5), 6 viewport (3 milik kita + 3 viewport aktif bawaan layout),
  view_direction & target per line terpasang.
- Visual (flash) putaran 1: 2 temuan parah — LEGEND menimpa tabel revisi;
  teks CONT. menimpa PROJECT. Putaran 2: **LULUS** (4 blok kolom kanan
  terpisah, BOM 9 baris dengan TEE & REDUCER pecah, tanpa tabrakan parah;
  sisa kosmetik: tick garis kecil di margin kanan).

## Temuan & catatan

| No | Temuan | Status |
|---|---|---|
| 1 | ezdxf VIEWPORT: atribut bernama `view_direction_vector` (bukan view_direction); MeshBuilder: `render_polyface` (bukan render) | TUTUP — API dipelajari & dipakai |
| 2 | Layout1 bawaan tidak dapat dihapus sebelum layout lain ada | TUTUP — urutan: buat sheets dulu, hapus belakangan |
| 3 | SIGNATURE/NAME/DATE approval kosong | Disengaja (issue for review) — isi sebelum IFC |
| 4 | Tick garis kecil tak berlabel di margin kanan | Kosmetik — B0 |

## Status akhir

`GPF-00-PI-ISO-0007 SHT 1 - 3.dxf` LULUS QA: format FNKT-10, isometrik 3D
per sheet via viewport. Cara pakai: buka di AutoCAD → tab layout SHEET n →
visual style **Conceptual/Shaded** → orbit di dalam viewport. Rebuild:
`python src/export_iso_sheet_dxf.py`.

---

# ROUND A5 — TRUE PIPING ISOMETRIC (30°/150°/90°), OBLIQUE DIMS, FULL FNKT-10 FURNITURE & PENGHAPUSAN POLYFACE (22 Oct 2026)

Pemicu: evaluasi PM atas keluhan user bahwa format isometrik model sebelumnya belum ideal ("masih belum betul-betul sesuai isometrik") dan ukuran file terlalu besar (30,4 MB akibat 133.017 segitiga `POLYFACE`).

## Root Cause Analysis (Evaluasi Metodologi Review)

| No | Lokasi | Kutipan / Implementasi Lama (Salah) | Jenis Masalah | Penjelasan | Rekomendasi & Koreksi (Rev A5) |
|---|---|---|---|---|---|
| 1 | `iso_go1002.py`, `iso_co1003.py`, `iso_co1004.py`, `SKILL.md` §7 | `EX = (1.0, 0.0)` (pipa East–West digambar datar 0° horizontal); `NX = (0.866, 0.5)` (+30°) | Teknis/Klaim salah (Proyeksi salah) | Model sebelumnya membaca koordinat WCS 3D mentah pada referensi `FNKT-10-L0-DWG-007` tanpa memproyeksikannya lewat kamera `VIEWPORT` (`view_direction_vector = (1, -1, 1)`). Pada proyeksi isometrik sejati, sumbu `+E` tampak miring **+30°** (`(+0.866, +0.5)`), sumbu `+N` miring **+150°** (`(-0.866, +0.5)`), dan `+UP` **+90°** (`(0, 1)`). Pipa tidak pernah digambar datar 0°. | Seluruh isometrik dibangun ulang memakai **True Piping Isometric** (`EX = (+cos 30°, +sin 30°)`, `NX = (-cos 30°, +sin 30°)`, `UX = (0, 1)`), 0 garis pipa horizontal 0°. Juga memperbaiki cacat sudut 14,04° pada segmen D–E di `iso_co1004`. |
| 2 | `apply_text.py` & `iso_*.py` | Garis ekstensi `DIMENSION` tegak lurus biasa terhadap pipa (tidak sejajar sumbu isometrik) | Format/struktur | Pada gambar isometrik teknik, garis ekstensi dimensi (*extension lines*) harus dimiringkan (*oblique*) mengikuti bidang sumbu isometrik (vertikal ±90° untuk pipa horizontal ±30°, atau ±30°/150° untuk riser vertikal). | Menambahkan dukungan atribut `"oblique"` (`dxfattribs={"oblique_angle": ...}`) di `apply_text.py`. Semua dimensi horizontal menggunakan `oblique = ±120°/±60°` (ekstensi jatuh vertikal) dan riser vertikal menggunakan `oblique = 120°`. |
| 3 | `GPF-00-PI-ISO-0007 SHT 1 - 3.dxf` & `step/piping_3d_mesh.dxf` | Menyuntikkan 133.017 face `POLYFACE` (30,4 MB) ke modelspace isometrik | Format/struktur & Performa | Isometrik perpipaan adalah gambar kerja fabrikasi berdimensi vektor 2D murni, bukan dump mesh 3D yang membengkakkan file hingga 30 MB tanpa dimensi di viewport. | **Menghapus permanen** `step/piping_3d_mesh.dxf` dan `src/export_mesh_dxf.py`. Membangun ulang `src/export_iso_sheet_dxf.py` menggunakan geometri vektor 2D True Isometric (`POLYFACE = 0`, ukuran turun 98,4% dari 30,4 MB menjadi **477,9 KB**). |
| 4 | Furniture Sheet (`iso_*.py`) | Hanya 1 kolom kanan sempit (x=335..410); BOM ringkas 6–9 baris tanpa kategori; North Arrow kompas 2D | Format/struktur | Referensi `FNKT-10-L0-DWG-007` menggunakan **3 kolom furniture penuh** (x=196..412): Kolom 1 (x=196..272) untuk tabel NDT + Line Data di bagian atas; Kolom 2 (x=272..350) penuh dari atas ke bawah untuk **Bill of Materials** berkategori (`PIPE` dalam meter, `FITTING`, `FLANGE`, `GASKET`, `BOLT`, `VALVE`); Kolom 3 (x=350..412) untuk `NOTE`, `LEGEND`, `REFERENCE DOCUMENT`, `REV TABLE` *bottom-up* (A0 di bawah → A5 di atas), `PROJECT/COMPANY/CONSULTANT`, `APPROVAL`, `ISOMETRIC DRAWING`, dan `DRAWING NUMBER / SHT / REV triangle / SCALE`. North Arrow berupa panah bintang 3D isometrik miring ke arah **N = +150°**. | Membuat modul bersama `cad/iso_common.py` yang mengimplementasikan tata letak 3 kolom persis `FNKT-10`, North Arrow isometrik +150°, balon nomor part (`part_bubble` & `stacked_bubbles` untuk flange+gasket+bolt), simbol Pipe Support (`PS-xxx RESTING/GUIDE`), simbol instrumen + balon transmitter (`FT-141`, `FT-142`), dan *line callout* berpanah. |

## Verifikasi Independen PM (22 Oct 2026)

| File | Ukuran | POLYFACE | MTEXT | DIM (Oblique) | SOLID | Validation Errors | Rev |
|---|---|---|---|---|---|---|---|
| `cad/iso_go1002.dxf` | **108,5 KB** | 0 | 264 | 8 | 21 | **0** | A5 |
| `cad/iso_co1003.dxf` | **92,4 KB** | 0 | 238 | 5 | 18 | **0** | A5 |
| `cad/iso_co1004.dxf` | **123,9 KB** | 0 | 273 | 13 | 32 | **0** | A5 |
| `cad/GPF-00-PI-ISO-0007 SHT 1 - 3.dxf` | **477,9 KB** | 0 | 775 | 26 | 71 | **0** | A5 |

## Status Akhir

Seluruh deliverable isometrik (**Rev A5**) telah memenuhi standar **True Piping Isometric** sesuai referensi `FNKT-10-L0-DWG-007`, bebas `POLYFACE` (ukuran < 500 KB), lulus validasi deterministik (`0 errors`), dan lulus pemeriksaan visual PM tanpa tabrakan teks/simbol.







