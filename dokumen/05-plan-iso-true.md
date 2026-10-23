# PLAN EKSEKUSI REVISI A5 — TRUE PIPING ISOMETRIC & TATA LETAK FNKT-10

Dokumen : GPF-00-PI-ISO-0003 / 0004 / 0005 / 0007, Rev A5
Tanggal : 22 Oct 2026
Disusun : PM (Gemini 4 Argon)
Eksekutor: Subagent CAD Executor (Flash)

---

## 1. TUJUAN & KONSEP PERBAIKAN MATANG

Memperbaiki 3 drawing isometrik individual (`cad/iso_go1002.py`, `cad/iso_co1003.py`, `cad/iso_co1004.py`) dan 1 drawing multi-sheet gabungan (`src/export_iso_sheet_dxf.py` → `cad/GPF-00-PI-ISO-0007 SHT 1 - 3.dxf`) agar **100% sesuai konvensi Piping Isometric sejati dan tata letak referensi `FNKT-10-L0-DWG-007`**, serta **menghilangkan seluruh mesh 3D (`POLYFACE`)** sehingga ukuran file DXF sangat kecil (~100–350 KB).

### 1.1 Sistem Sumbu True Piping Isometric (30° / 150° / 90°)
Sesuai kamera Viewport referensi FNKT-10 (`view_direction_vector = (1, -1, 1)`):
- **`EX` (East / Timur, +E)**: `(+0.8660254, +0.5)` → sudut **+30°** (naik ke kanan-atas).
- **`WX` (West / Barat, -E)**: `(-0.8660254, -0.5)` → sudut **-150°** (turun ke kiri-bawah).
- **`NX` (North / Utara, +N)**: `(-0.8660254, +0.5)` → sudut **+150°** (naik ke kiri-atas).
- **`SX` (South / Selatan, -N)**: `(+0.8660254, -0.5)` → sudut **-30°** (turun ke kanan-bawah).
- **`UX` (Up / Atas, +Z)**: `(0.0, +1.0)` → sudut **+90°** (vertikal).
- **`DNX` (Down / Bawah, -Z)**: `(0.0, -1.0)` → sudut **-90°** (vertikal).
- **LARANGAN**: Tidak boleh ada pipa berarah 0° (mendatar) kecuali pipa 45° plan.

### 1.2 Isometric Dimensioning dengan Oblique Extension Lines (`cad/apply_text.py`)
`cad/apply_text.py` telah di-upgrade untuk mendukung field `"oblique"` pada setiap entri `"dims"`:
- Fungsi helper di script drawing:
  ```python
  def dimrec(p1, p2, txt, angle, base, oblique=None):
      d = {"p1": [p1[0], p1[1]], "p2": [p2[0], p2[1]],
           "base": [base[0], base[1]], "angle": angle, "text": txt}
      if oblique is not None:
          d["oblique"] = oblique
      DIMS.append(d)
      return []
  ```
- **Aturan Sudut Dimensi & Oblique** agar garis ekstensi sejajar sumbu isometrik (membentuk bidang isometrik rapi seperti FNKT-10):
  1. **Run arah +E (`EX`, sudut +30°)**:
     - Taruh dimensi di bawah pipa (`base = addp(p1, (0.0, -dist))`), dengan `angle = 30.0`, `oblique = -120.0` (sehingga `ext_line_angle = 30 - 120 = -90°` vertikal ke bawah!).
     - Atau di atas pipa (`base = addp(p1, (0.0, +dist))`), `angle = 30.0`, `oblique = 60.0` (`ext_line_angle = +90°` vertikal ke atas).
  2. **Run arah +N (`NX`, sudut +150° atau -30°)**:
     - Untuk teks terbaca dari bawah, gunakan `angle = -30.0` (sama garisnya dengan 150°), `p1` di ujung kiri-atas dan `p2` di ujung kanan-bawah:
       - Bila ditarik vertikal ke bawah (`base = addp(p1, (0.0, -dist))`): `angle = -30.0`, `oblique = -60.0` (`ext_line_angle = -30 - 60 = -90°` vertikal ke bawah!).
       - Bila ditarik vertikal ke atas (`base = addp(p1, (0.0, +dist))`): `angle = -30.0`, `oblique = 120.0` (`ext_line_angle = +90°` vertikal ke atas).
  3. **Run Riser Vertikal (`UX` / `DNX`, sudut 90°)**:
     - Taruh `p1` di titik bawah, `p2` di titik atas, `angle = 90.0`.
     - Jika ditarik ke arah kiri-bawah (`-EX`): `base = addp(p1, mulp(WX, dist))`, `oblique = 120.0` (`ext_line_angle = 90 + 120 = 210° = -150°` sejajar `WX`).
     - Jika ditarik ke arah kanan-atas (`+EX`): `base = addp(p1, mulp(EX, dist))`, `oblique = -60.0` (`ext_line_angle = 90 - 60 = 30°` sejajar `EX`).
     - Jika ditarik ke arah kiri-atas (`+NX`): `base = addp(p1, mulp(NX, dist))`, `oblique = 60.0` (`ext_line_angle = 90 + 60 = 150°` sejajar `NX`).

### 1.3 Tata Letak Furniture Lembar A3 (420 × 297 mm) Persis FNKT-10
Buat satu modul/fungsi `fnkt_furniture(sheet_no, line_no, service, press_temp_des, press_temp_op, bom_groups, notes, rev_desc)` yang seragam di ketiga file:
- **Border Luar**: `rect(2.0, 1.3, 418.0, 295.7)` & **Border Dalam**: `rect(7.0, 6.3, 413.0, 290.7)` (di dalam kanvas A3 `0..420 × 0..297` agar `validate_dxf_file` 0 error dan bbox di dalam `420×297`).
- **Grid Ticks & Labels**:
  - Horizontal `1..12` di antara `x=7.0..413.0` (tiap `33.833 mm`), tick di border atas (`y=290.7..295.7`) dan bawah (`y=1.3..6.3`), teks angka `1..12` tinggi `1.6 mm`.
  - Vertikal `A..H` (8 zona dari atas ke bawah) di antara `y=6.3..290.7` (tiap `35.55 mm`), tick di kiri (`x=2.0..7.0`) dan kanan (`x=413.0..418.0`), teks huruf `A..H` tinggi `1.6 mm`.
- **Kompas Isometrik (North Arrow) di Kiri-Atas `(cx=25.3, cy=271.2)`**:
  - Panah utama menunjuk arah **`NX` (+150°, kiri-atas)** sepanjang `11 mm` menuju `(15.8, 276.7)` dengan sayap bintang 4-arah isometrik (`NX`, `SX`, `EX`, `WX`) + setengah bagian di-solid (`solidrec`) + huruf **`N`** (`h=2.5`, rot=`60.0`) di ujung kiri-atas `(13.5, 278.0)`.
- **Kolom 1 Atas — Tabel NDT & Data Line (`x = 195.4..271.5, y = 236.4..290.7`, pembagi kolom di `x = 235.1`)**:
  - 12 baris tinggi `4.525 mm`:
    1. `NDT :` | (kosong)
    2. `RADIOGRAPHY TEST (RT)` | `100%`
    3. `ULTRASONOGRAPHY (UT)` | `100%`
    4. `MAGNETIC PARTICLE TEST (MT)` | `NOTE 3`
    5. `DYE PENETRANT TEST (PT)` | `NOTE 3`
    6. `SERVICE LINE` | `<service>`
    7. `CODE` | `ASME B31.3`
    8. `LINE NUMBER` | `<line_no>`
    9. `PIPING CLASS` | `A1A`
    10. `DESIGN TEMPERATURE` | `60 °C`
    11. `DESIGN PRESSURE` | `17.2 BARG`
    12. `OPERATING TEMP / PRESS` | `40 °C / 10.0 BARG`
  - Semua teks tinggi `1.4 mm` (`att=4` di kolom kiri `x=196.8`, `att=5` di kolom kanan `x=253.3`).
- **Kolom 2 — Tabel BILL OF MATERIALS Vertikal Penuh (`x = 271.5..349.5, y = 6.3..290.7`)**:
  - Header1 (`y = 286.5..290.7`): `BILL OF MATERIALS` (`h=1.6`).
  - Header2 (`y = 281.5..286.5`): `NO` (`271.5..276.5`) | `DESCRIPTION` (`276.5..331.5`) | `SIZE` (`331.5..340.5`) | `QUANT` (`340.5..349.5`).
  - Garis vertikal kolom dari `y = 6.3` sampai `y = 286.5`, dan garis horizontal baris setiap `5.5 mm` dari `y = 281.5` turun sampai `y = 6.3` (persis grid BOM FNKT-10!).
  - Isi BOM dikelompokkan dengan sub-header kategori (`PIPE`, `FITTING`, `FLANGE`, `GASKET`, `BOLT`, `VALVE`) dengan tinggi teks `1.35 mm` zodat tidak ada teks yang menabrak garis kolom!
- **Kolom 3 Kanan — NOTE, LEGEND, REF DOC, REV TABLE & TITLE BLOCK (`x = 349.5..413.0, y = 6.3..290.7`)**:
  - `y = 231.7..290.7`: Kotak **NOTE** (header `NOTE` di `y=288.0`, isi 5 butir teks `h=1.35`).
  - `y = 144.7..231.7`: Kotak **LEGEND** (header `LEGEND` di `y=229.0`, simbol grafik + label: `PIPE SUPPORT`, `SHOP WELD`, `FLANGE`, `VALVE`, `FLOW ARROW`).
  - `y = 121.3..144.7`: Tabel **REFERENCE DOCUMENT** (`GPF-00-PI-PID-0001` | `P&ID SEPARATOR V-101`, `GPF-00-PI-PLN-0002` | `PIPING PLAN`, `GPF-00-DB-0001` | `DESIGN BASIS`).
  - `y = 96.4..121.3`: **Tabel Revisi** (`NO | REV | DESCRIPTION | DATE | REMARK` di baris bawah `y=96.4..100.0`, lalu baris revisi `A0` s/d `A5` disusun dari bawah ke atas seperti FNKT-10, tinggi teks `1.25 mm`).
  - `y = 85.1..96.4`: `PROJECT` (`GAS PRODUCTION FACILITY - ONSHORE FIELD`).
  - `y = 68.3..85.1`: `COMPANY` (`PM OIL & GAS SURFACE FACILITY`).
  - `y = 53.3..68.3`: `CONSULTANT` (`REKAYASA ENGINEERING`).
  - `y = 30.7..53.3`: **Approval Grid** (`DRAWN | CHECKED | APPROVED` + `SIGNATURE / NAME / DATE`).
  - `y = 16.7..30.7`: **TITLE** (`ISOMETRIC DRAWING` / `<line_no>` / `<service>`, tinggi `1.6–1.8 mm`).
  - `y = 6.3..16.7`: **DRAWING NUMBER** (`GPF-00-PI-ISO-000x`) | **SHEET** (`01 OF 03`) | **REV** (`A5` di dalam segitiga) | **SCALE** (`NTS`).

### 1.4 Elemen Simbol pada Area Gambar Pipa (`x = 12..265`)
1. **Part Callout Balloons (`part_bubble(P, target_pt, item_no)` atau `stacked_bubbles(P_target, dir_vec, item_nos)`)**:
   - Lingkaran `r = 1.9 mm` (layer `REF-SYM`) dengan teks angka `item_no` (`h = 1.5 mm`) di pusatnya, dihubungkan dengan garis leader tipis dari tepi lingkaran ke titik komponen pada pipa.
   - Untuk sambungan flange, gunakan `stacked_bubbles` berisi nomor item `[flange, gasket, bolt]` (mis. `[6, 7, 8]`) persis seperti FNKT-10!
2. **Pipe Supports (`pipe_support(P, u_run, tag, stype, offset_vec)`)**:
   - Kotak tipis miring (`3.2 × 1.2 mm`) bersilang diagonal menempel pada pipa + garis leader putus/solid ke teks 2 baris: `PS-00x` / `RESTING` (atau `GUIDE`).
3. **Callout Line Number + BOP.EL. dengan Leader Berpanah (`line_callout(P_pipe, P_elbow, line_str, bop_str)`)**:
   - Garis leader dari titik atas pipa `P_pipe` naik vertikal ke `P_elbow` lalu mendatar sepanjang `22 mm`, dilengkapi panah segitiga solid kecil (`solidrec`) di ujung yang menyentuh pipa, dan teks 2 baris `line_str` (`h=1.8`) + `bop_str` (`h=1.8`) di atas garis mendatar.
4. **Continuation Pipe Dashed (`dashed_line(p1, p2)`)**:
   - Di luar flange batas awal/akhir (dan cabang tee), gambar pipa lanjutan sepanjang `14 mm` dengan garis putus-putus (`dash 2.2 mm, gap 1.2 mm` di layer `REF-SYM`) + teks 3 baris `CONT. FROM/TO DRW NO. ... / <EQUIPMENT NOZZLE> / SHEET x OF 03`.

---

## 2. DETAIL GEOMETRI PER SHEET (TRUE ISOMETRIC)

### 2.1 ISO-1: `cad/iso_go1002.py` (`GPF-00-PI-ISO-0003`, Sheet 01 OF 03)
- **Rute True Isometric** (semua segmen murni mengikuti `UX`, `EX` (+30°), `NX` (+150°), `DNX` (-90°)):
  - Titik `A = (78.0, 92.0)` (V-101 N2 Flange DN100, `BOP.EL. +4150`)
  - `A → B`: naik vertikal (`UX`) sejauh `16.0 mm` (dim: `"850"`) → `B = (78.0, 108.0)` (`BOP.EL. +5000`).
  - `B → C`: arah Timur (`EX`, +30°) sejauh `84.0 mm` (35 m):
    - `P_PS1` di `18.0 mm` (`PS-001 RESTING`)
    - `P_PV` di `36.0 mm` (`PV-101` Globe Control Valve DN100, dim B→PV: `"17000"`)
    - `P_GV` di `56.0 mm` (`GV-141` Gate Valve DN150/100, dim PV→GV: `"8000"`)
    - `P_FE` di `72.0 mm` (`FE-141` Orifice + `FT-141` bubble)
    - `C = addp(B, mulp(EX, 84.0)) = (150.746, 150.0)` (Tee + Reducer DN100×150, dim GV→C: `"10000"`).
  - Cabang Tee di `C`: ke arah Utara (`NX`, +150°) sejauh `15.0 mm` (`P_BR`), disambung garis putus-putus + label `CONT. TO PSV-101 TAIL / DRW NO. GPF-00-PI-PID-0001`.
  - `C → D`: lanjut arah Timur (`EX`, +30°) sejauh `22.0 mm` (dim C→D: `"8000"`) → `D = addp(C, mulp(EX, 22.0)) = (169.799, 161.0)`. Support `PS-002 GUIDE` di tengah C–D.
  - `D → E`: belok arah Utara (`NX`, +150° kiri-atas!) sejauh `36.0 mm` (dim D→E: `"11000"`) → `E = addp(D, mulp(NX, 36.0)) = (138.622, 179.0)`. Melintasi `ROAD CROSSING EL +6.5` di tengah D–E.
  - `E → F`: belok arah Timur (`EX`, +30° kanan-atas) sejauh `34.0 mm` (dim E→F: `"12500"`) → `F = addp(E, mulp(EX, 34.0)) = (168.067, 196.0)`. Support `PS-003 RESTING` di tengah E–F.
  - `F → G`: turun vertikal (`DNX`, -90°) sejauh `26.0 mm` (dim G→F: `"3850"`) → `G = (168.067, 170.0)` (V-102 N1 Flange DN150, `BOP.EL. +1150`).
- Periksa koordinat: semua X berada di `55..192` (< `195.4` batas tabel NDT!) dan Y berada di `70..225` — **100% bebas dari tabel NDT dan BOM!**

### 2.2 ISO-2: `cad/iso_co1003.py` (`GPF-00-PI-ISO-0004`, Sheet 02 OF 03)
- **Rute True Isometric**:
  - Di [01-design-basis.md](file:///home/arienugraha-rei/gas-prod-facility/dokumen/01-design-basis.md#L87): N3 `(17.8, 33.2, +2.2)` → Timur 4.2 m ke `(22.0, 33.2, +2.2)` → Selatan 2.3 m ke `(22.0, 30.9, +2.2)` → Turun 1.6 m ke P-101 suction `(22.0, 30.9, +0.6)`.
  - Titik `A = (55.0, 145.0)` (V-101 N3 Flange DN80, `BOP.EL. +2200`).
  - `A → B`: arah Timur (`EX`, +30° kanan-atas) sejauh `84.0 mm` (4.2 m):
    - `P_GV` di `34.0 mm` (`GV-101` Gate Valve DN80, dim A→GV: `"1700"`)
    - `P_ST` di `64.0 mm` (`ST-101` Y-Strainer DN80, dim GV→ST: `"1600"`)
    - `B = addp(A, mulp(EX, 84.0)) = (127.746, 187.0)` (dim ST→B: `"900"`).
  - `B → B2`: arah Selatan (`SX`, -30° kanan-bawah) sejauh `40.0 mm` (2.3 m, dim B→B2: `"2300"`) → `B2 = addp(B, mulp(SX, 40.0)) = (162.387, 167.0)`. Support `PS-101 RESTING` di tengah B–B2.
  - `B2 → C`: turun vertikal (`DNX`, -90°) sejauh `44.0 mm` (1.6 m, dim C→B2: `"1600"`) → `C = (162.387, 123.0)` (P-101 Suction Flange DN65, `BOP.EL. +0600`), dengan `RED DN80×65` di tengah B2–C.
  - Sekarang `iso_co1003` adalah **gambar isometrik 3D sejati** dengan 3 sumbu (`+E`, `-N`, `-UP`) yang sangat jelas dan proporsional!

### 2.3 ISO-3: `cad/iso_co1004.py` (`GPF-00-PI-ISO-0005`, Sheet 03 OF 03)
- **Rute True Isometric** (memperbaiki bug segmen miring D–E dan elevasi `+6150`):
  - Titik `A = (42.0, 95.0)` (P-101 Discharge Flange DN65, `BOP.EL. +0800`).
  - `A → B`: arah Timur (`EX`, +30°) sejauh `36.0 mm` (dim: `"1200"`, memuat `CV-101`, `GV-102`, `RED 65×80`) → `B = (73.177, 113.0)`.
  - `B → C`: naik vertikal (`UX`, +90°) sejauh `28.0 mm` (dim: `"4200"`) → `C = (73.177, 141.0)` (`BOP.EL. +5000`).
  - `C → D`: belok arah Utara (`NX`, +150° kiri-atas) sejauh `18.0 mm` (dim: `"3500"`) → `D = (57.588, 150.0)`.
  - `D → E`: belok arah Timur (`EX`, +30° kanan-atas, **murni +30° tanpa kemiringan liar 14°!**) sejauh `52.0 mm` (dim D→FE: `"10000"`, FE→E: `"10000"`, memuat `FE-142` & `FT-142` serta `PS-201 RESTING`) → `E = (102.622, 176.0)`.
  - `E → F`: turun vertikal (`DNX`, -90°) sejauh `26.0 mm` (dim: `"3800"`) dan arah Selatan ke grade sleeper → `F = (102.622, 150.0)` (`BOP.EL. +1200`).
  - `F → G`: arah Timur (`EX`, +30° kanan-atas) sejauh `62.0 mm` (dim F→LV: `"4000"`, LV→GV3: `"17000"`, GV3→G: `"2000"`, memuat `LV-121`, `PS-202 RESTING`, `GV-103`) → `G = (156.315, 181.0)`.
  - `G → H`: belok arah Utara (`NX`, +150° kiri-atas) sejauh `15.0 mm` (dim: `"1500"`) → `H = (143.325, 188.5)`.
  - `H → I`: naik vertikal (`UX`, +90°) sejauh `30.0 mm` (dim: `"5500"`, memuat `PS-203 GUIDE`) → `I = (143.325, 218.5)` (`BOP.EL. +6700`).
  - `I → J`: arah Selatan (`SX`, -30° kanan-bawah menuju roof nozzle) sejauh `16.0 mm` (dim: `"1700"`) → `J = (157.181, 210.5)`.
  - `J → K`: turun vertikal (`DNX`, -90°) sejauh `12.0 mm` (dim: `"550"`) → `K = (157.181, 198.5)` (T-101 N1 Flange DN80, `BOP.EL. +6150`).

---

## 3. MULTI-SHEET DXF TANPA POLYFACE (`src/export_iso_sheet_dxf.py`)

Ubah `src/export_iso_sheet_dxf.py` agar **TIDAK LAGI membaca `piping_3d.step` dan TIDAK menulis `POLYFACE` mesh**.
Sebaliknya, `src/export_iso_sheet_dxf.py` menyalin seluruh geometri vektor 2D + MTEXT + DIMENSION + SOLID + Lineweights dari ketiga file (`cad/iso_go1002.dxf`, `cad/iso_co1003.dxf`, `cad/iso_co1004.dxf`) secara langsung ke dalam:
- 3 Paper Space Layouts (`SHEET 1 OF 3`, `SHEET 2 OF 3`, `SHEET 3 OF 3`) **DAN** disusun berjejer rapi di `Model` space (dengan offset X = `0`, `500`, `1000` mm + Viewport 2D di tiap Sheet yang menyorot masing-masing sheet).
- Hasilnya:
  1. Baik pengguna membuka tab `Model` maupun tab `SHEET 1 OF 3`..`SHEET 3 OF 3` di AutoCAD atau CAD Viewer, **gambar isometrik langsung tampil utuh lengkap dengan dimensi, balon BOM, valve, dan title block**.
  2. Ukuran file `cad/GPF-00-PI-ISO-0007 SHT 1 - 3.dxf` turun drastis dari **30,4 MB** menjadi **< 400 KB**!

---

## 4. PROSEDUR QA WAJIB (OLEH SUBAGENT & DIVERIFIKASI PM)

1. Jalankan build chain untuk ketiga iso:
   - `python cad/iso_go1002.py && python cad/apply_text.py cad/iso_go1002.dxf cad/iso_go1002.texts.json`
   - `python cad/iso_co1003.py && python cad/apply_text.py cad/iso_co1003.dxf cad/iso_co1003.texts.json`
   - `python cad/iso_co1004.py && python cad/apply_text.py cad/iso_co1004.dxf cad/iso_co1004.texts.json`
   - `python src/export_iso_sheet_dxf.py`
2. Render snapshot PNG untuk ketiga iso (`cadgen dxf snapshot ... --appearance light`).
3. Cek deterministik:
   - `validate_dxf_file` = 0 error.
   - Ukuran semua file `.dxf` < 500 KB (`POLYFACE` = 0).
   - Sudut garis pada layer `REF-PROC` hanya `±30°`, `±150°`, dan `±90°` (0 garis horizontal 0°!).
4. Cek visual PNG: pastikan tidak ada tabrakan teks, balon nomor BOM terbaca jelas, garis ekstensi dimensi sejajar sumbu isometrik, dan tabel 3-kolom FNKT-10 rapi.
5. Sinkronkan hasil ke folder `handoff/` dan perbarui `handoff-antigravity.zip`.
