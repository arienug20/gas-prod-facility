# PLAN EKSEKUSI P&ID REV A3 — STANDAR ANSI/ISA-5.1-2024, ISO 10628-2:2012, API RP 12J & REFERENSI P&ID PERUSAHAAN

Dokumen : `dokumen/06-plan-pid-true.md`
Target  : `cad/pid_v101.py` → `cad/pid_v101.dxf` & `cad/pid_v101.png` (`GPF-00-PI-PID-0001 Rev A3`)
Ukuran  : Sheet A1 Landscape (`841 × 594 mm`)

---

## 1. Tujuan & Filosofi Desain P&ID Rev A3

Merombak `cad/pid_v101.py` dari skematik konseptual kasar menjadi **Engineering P&ID Oil & Gas (FEED/EPC Grade)** yang mengadopsi tata letak, simbol, dan kelengkapan informasi dari dokumen referensi P&ID perusahaan (`SSY-PRO-PID-002 Legend & Symbols` dan `SSY-PRO-PID-003 Horizontal Separator P&ID`) serta standar **ANSI/ISA-5.1-2024**, **ISO 10628-2:2012**, **API RP 12J**, dan **API STD 521**, dengan tetap menjaga **100% konsistensi tag equipment, line number, dan instrument index** terhadap `dokumen/01-design-basis.md`.

---

## 2. Tata Letak Lembar A1 (`841 × 594 mm`)

### 2.1 Border & Grid Referensi
- **Outer Border**: `(10, 7)` hingga `(831, 587)`
- **Inner Border**: `(20, 15)` hingga `(823, 579)`
- **Grid Kolom Horizontal (`1` s/d `12`)**: 12 zona lebar `66.917 mm` (`x = 20..823`), teks di pita atas (`y = 583`) dan pita bawah (`y = 11`).
- **Grid Baris Vertikal (`A` s/d `H`)**: 8 zona tinggi `70.5 mm` (`y = 15..579`, `A` di atas → `H` di bawah), teks di pita kiri (`x = 15`) dan pita kanan (`x = 827`).

### 2.2 Zona Gambar Utama vs Zona Furniture Kanan
- **Kolom Furniture Kanan (`x = 655..823, y = 15..579`)**:
  - `y = 435..579`: **NOTES** (9 butir catatan proses, SIS C&E, relief API 521, slope 1:500, standar acuan).
  - `y = 185..435`: **LEGEND & SYMBOLS** (menampilkan simbol proses, sinyal listrik, sinyal pneumatik, *Continuity Arrow*, *Field Instrument*, *DCS Shared Display*, *SIS Logic / Interlock (Diamond-in-Box)*, *Gate Valve*, *Globe Valve (Filled Dot)*, *Check Valve*, *Spring-Loaded PSV*, *Centrifugal Pump*, *Spec Break*, dan singkatan `FC / NC / CSO / LO / TW`).
  - `y = 148..185`: **REFERENCE DRAWINGS** (`GPF-00-PI-PLN-0002` Piping Plan, `GPF-00-PI-ISO-0003..0005` Piping Isometrics, `GPF-00-DB-0001` Design Basis).
  - `y = 116..148`: **REVISION TABLE (Bottom-Up)** (`REV | DESCRIPTION | DATE | CHK'D | APP'D`, baris `A0` di bawah → `A3` di atas: `"A3 | UPGRADED TO FULL ISA-5.1 / ISO 10628-2 P&ID STANDARD | 23 OCT 26"`).
  - `y = 15..116`: **TITLE BLOCK** (Project: `GAS PRODUCTION FACILITY — ONSHORE FIELD`, Company: `PM OIL & GAS SURFACE FACILITY`, Consultant: `REKAYASA ENGINEERING`, Title: `PIPING & INSTRUMENTATION DIAGRAM / 3-PHASE PRODUCTION SEPARATOR V-101`, Drawing No: `GPF-00-PI-PID-0001`, Scale: `NTS`, Sheet: `1 OF 1`, Rev: `A3` dalam segitiga/kotak bersih **tanpa teks panjang yang menabrak garis!**).

### 2.3 Equipment Data Tables di Bagian Atas Area Gambar (`y = 515..573`)
Seperti pada `SSY-PRO-PID-003` (Grid 4–9 baris A), tampilkan **2 Tabel Data Equipment** di bagian paling atas kanvas proses:
1. **Tabel Kiri (`x = 135..375, y = 515..573`) — `V-101` Equipment Data Block**:
   - `TAG NO` : `V-101`
   - `SERVICE NAME` : `3-PHASE PRODUCTION SEPARATOR`
   - `SIZE (ID x S/S)` : `2300 MM (ID) x 7600 MM (S/S) HORIZONTAL`
   - `DESIGN PRESS / TEMP` : `17.2 BARG / 60 °C`
   - `OPER. PRESS / TEMP` : `10.0 BARG / 40 °C`
   - `MATERIAL / CODE` : `CS ASTM A516 GR.70 / ASME SEC. VIII DIV.1 & API RP 12J`
2. **Tabel Kanan (`x = 395..635, y = 515..573`) — `P-101` Equipment Data Block**:
   - `TAG NO` : `P-101`
   - `SERVICE NAME` : `CRUDE OIL TRANSFER PUMP`
   - `TYPE / RATED` : `HORIZONTAL CENTRIFUGAL / API 610`
   - `DESIGN PRESS / TEMP` : `17.2 BARG / 60 °C`
   - `SUCTION / DISCH. PRESS` : `10.0 BARG / 13.5 BARG (OPERATING 40 °C)`
   - `MATERIAL / DRIVER` : `CS A216-WCB / ELECTRIC MOTOR (M)`

---

## 3. Spesifikasi Simbol & Trimming Garis Pipa (ISO 10628-2 & ANSI/ISA-5.1)

### 3.1 Aturan Mutlak Trimming Pipa (`add_segmented_pipe`)
- **DILARANG KERAS** menggambar garis pipa proses menembus bagian dalam simbol *valve*, *orifice*, *reducer*, atau *pump*!
- Buat helper `pipe_run_h(y, x_start, x_end, gaps=[(x_c1, half_w1), ...])` dan `pipe_run_v(x, y_start, y_end, gaps=[(y_c1, half_h1), ...])` yang secara otomatis memotong (*trim*) segmen pipa di setiap bukaan komponen in-line (`[cx - hw, cx + hw]`).
- Semua panah aliran proses (`flow_arrow_h`, `flow_arrow_v`) WAJIB menggunakan segitiga `SOLID` terisi penuh (melalui manifest `"solids"` di `apply_text.py`), bukan dua garis terbuka `>`.

### 3.2 Katalog Simbol Katup, Fitting, & Equipment (ISO 10628-2 & `SSY-PRO-PID-002`)
1. **Gate Valve (`valve_gate_h(cx, cy, w=10, h=6, nc=False)` & `valve_gate_v`)**:
   - Dua segitiga berhadapan (*bowtie* `▷◁`) + batang *stem* T-handle pendek di tengah (`3.5 mm`).
   - Bila `nc=True` (*Normally Closed* seperti `GV-104`): kedua segitiga *bowtie* diisi `SOLID` hitam + teks `"NC"`.
   - Tambahkan tick *flange* vertikal pendek di kiri-kanan katup (`cx ± (w/2 + 1.2)`).
2. **Globe / Control Valve (`valve_globe_h(cx, cy, w=10, h=6)` & `control_valve_h`)**:
   - *Bowtie* `▷◁` dengan **bola tengah terisi penuh (`SOLID` dot `●`, `r=1.3 mm`)**.
   - Untuk *Control Valve* (`PV-101`, `LV-121`, `LV-131`): tambahkan batang *stem* vertikal (`6 mm`) + kubah diafragma setengah lingkaran (`r=4.5 mm` + alas datar) + label `"FC"` (*Fail Closed*).
3. **Shutdown Valve (`sdv_h(cx, cy, tag="SDV-101")`)**:
   - *Gate Valve* `▷◁` + batang *stem* ke aktuator piston/diafragma + kotak solenoid `S` (`SY-101`) di samping *stem* dengan jalur pneumatik + indikator posisi `ZSO-101` / `ZSC-101` seperti pada `SSY-PRO-PID-003`.
4. **Check Valve (`valve_check_h(cx, cy, w=10, h=6)`)**:
   - Sesuai `SSY-PRO-PID-002` & ISO 10628-2: dua garis tegak ujung (`cx - w/2`, `cx + w/2`), garis diagonal dari puncak kiri `(cx - w/2, cy + h/2)` ke bawah kanan `(cx + w/2, cy - h/2)`, **titik engsel `SOLID` (`●`, `r=0.9 mm`)** di puncak kiri, dan **kepala panah `SOLID`** di ujung bawah kanan.
5. **Spring-Loaded Angle PSV (`psv_angle(cx, cy)`)**:
   - Sesuai ISO 10628-2 & `SSY-PRO-PID-002`: katup sudut (*angle valve*) terdiri dari segitiga vertikal di bawah `(cx, cy - 6)..(cx, cy)` dan segitiga horizontal di kanan `(cx, cy)..(cx + 6, cy)`, ditambah batang vertikal ke atas dengan simbol pegas zig-zag (`spring`) + panah lurus miring + label `"PSV-101"`, `"DN100x150"`, `"SET = 17.2 BARG"`, dan *inlet isolation gate valve* dengan label `"CSO"` (*Car Sealed Open*).
6. **Concentric Reducer (`reducer_h(cx, cy, w=6, h1=3, h2=5, label="DN100x150")`)**:
   - Trapesium tertutup simetris (4 garis) + teks ukuran di atasnya, dengan pipa ter-trim di `cx ± w/2`.
7. **Orifice Plate with Flange Taps (`orifice_h(cx, cy, tag_fe="FE-141")`)**:
   - Dua garis vertikal paralel (`cx - 1.2`, `cx + 1.2`, tinggi `±5.5 mm`) dengan celah pipa ter-trim di tengah (`2.4 mm`) + titik sadap (*taps*) kiri-kanan yang naik ke balon transmitter `FT-141` / `FT-142` / `FT-143`.
8. **Y-Strainer (`strainer_v(cx, cy)`)**:
   - Kotak/trapesium saringan pada pipa vertikal `080-CO-1003` dengan kantong *blowdown* miring sesuai ISO 10628-2.
9. **Centrifugal Pump + Electric Motor (`pump_centrifugal(cx, cy)`)**:
   - Sesuai `SSY-PRO-PID-002` Hal. 3 (`CENTRIFUGAL PUMP` + `ELECTRIC MOTOR`):
     - Lingkaran badan pompa (`r=7.0 mm`) dengan kaki tumpuan trapesium di bawah (`cy - 7.0` ke `cy - 10.5`).
     - Pipa *suction* masuk horizontal ke **pusat/sisi kiri lingkaran** (dilengkapi *flange*), dan pipa *discharge* keluar **tangensial dari puncak lingkaran ke arah kanan** (`y = cy + 7.0`).
     - Di sebelah kiri pompa dihubungkan poros (*shaft* garis ganda/tunggal) ke lingkaran **Electric Motor (`M`, `r=5.0 mm`)** yang menerima sinyal `TRIP` dari `ESD-1`.
10. **Continuity Arrow Box (Battery Limit Arrow — `continuity_box_left` & `continuity_box_right`)**:
    - Sesuai `SSY-PRO-PID-002` Hal. 2 (`CONTINUITY ARROW`): kotak panah poligon memanjang (`lebar 48 mm × tinggi 11 mm` dengan ujung lancip searah aliran) di tepi kiri (`x = 28..76`) dan tepi kanan (`x = 585..635`).
    - Di dalam kotak tertulis nomor gambar referensi (`GPF-00-PI-PLN-0002` / `GPF-00-PI-ISO-0003`), dan tepat di atas/bawah kotak tertulis asal/tujuan aliran (`FROM PRODUCTION HEADER`, `TO FLARE HEADER`, `TOPRODUCED WATER TREATMENT`, `TO CLOSED DRAIN`, `TO STORAGE TANK T-101`).

---

## 4. Detail Bejana `V-101` & Level Bridle / Level Diagram

### 4.1 Geometri Bejana `V-101` (`x = 135..435, y = 250..340`)
- Dinding silinder horizontal (`x = 135..435, y = 250..340`, tinggi `90 mm`, panjang `300 mm`) + 2 *ellipsoidal heads* (`arc3`) di kiri (`x = 123..135`) dan kanan (`x = 435..447`).
- **2 Saddle Supports** di bawah bejana (`x = 165` dan `x = 405`, `y = 235..250`) lengkap dengan garis pondasi.
- **Nozzle Ber-Flange (`N1`..`N6`)**: setiap nozzle digambar dengan pipa leher + sepasang garis *flange* + label `N1 DN150`, `N2 DN100`, `N3 DN80`, `N4 DN50`, `N5 DN100`, `N6 DN50`.
- **Internal Bejana (API RP 12J)**:
  - **Inlet Deflector Baffle** di depan `N1` (`x = 142`).
  - **Plate Coalescer Pack** (`x = 175..245, y = 268..322`) dengan arsiran 45° (`REF-HATCH`).
  - **Weir Plate** (`x = 325, y = 250..308`) yang memisahkan kompartemen air/emulsi (kiri) dan kompartemen minyak (kanan), lengkap dengan garis permukaan cairan bergelombang/putus-putus (`OIL LEVEL` & `WATER/OIL INTERFACE`).
  - **Demister Pad** (`x = 355..415, y = 312..334`) dengan arsiran 45° di bawah nozzle gas `N2`.
  - **Vortex Breaker** (simbol palang `+` dengan topi) di atas lubang keluar cairan `N4` (`x = 265`) dan `N3` (`x = 435`).

### 4.2 Level Bridle (External Cage) & Tabel Level Setting
- **Water/Interface Bridle (`x = 215` & `x = 240`, di bawah kompartemen kiri)**:
  - Pipa *bridle* vertikal yang terhubung ke sisi bejana melalui katup isolasi atas & bawah + katup *drain* bawah, tempat dipasangnya `LG-133`, `LT-131` (BPCS → `LIC-131`), dan `LT-132` (SIS → `LAHH/LALL-132`).
- **Oil Level Bridle (`x = 370` & `x = 395`, di bawah kompartemen kanan)**:
  - Pipa *bridle* vertikal dengan katup isolasi + *drain*, tempat dipasangnya `LG-123`, `LT-121` (BPCS → `LIC-121`), dan `LT-122` (SIS → `LAHH/LALL-122`).
- **Tabel Level Diagram (`x = 115..205, y = 125..185`)** (persis `SSY-PRO-PID-003`):
  - Tabel ringkas `V-101 LEVEL SETTING`: `HHLL (LSHH): 1850 MM`, `HLL (LAH): 1650 MM`, `NLL: 1350 MM`, `LLL (LAL): 900 MM`, `LLLL (LSLL): 650 MM`, `WEIR HEIGHT: 1500 MM`.

---

## 5. Arsitektur Instrumentasi & SIS Tanpa Kabel *Spaghetti* (ANSI/ISA-5.1-2024)

Agar gambar sangat bersih dan profesional seperti `SSY-PRO-PID-003`:
1. **Simbol Instrumen Lapangan (`bubble`, Ø12 mm)**: `PT-101`, `PT-102`, `PI-103`, `TT-111`, `TI-112`, `LT-121`, `LT-122`, `LT-131`, `LT-132`, `FT-141`, `FT-142`, `FT-143`.
2. **Simbol DCS Shared Display/Control (`dcs`, kotak `14×14 mm` + lingkaran Ø12 mm + garis tengah)**:
   - Dipasang tepat di dekat loop masing-masing (tidak perlu menarik kabel ribuan milimeter melintasi seluruh gambar!):
     - `PIC-101` di atas `PT-101` / `PV-101` (`y = 478`) → terhubung pendek dan rapi ke `PT-101` dan `FY-101` (`PV-101`).
     - `TI-111` tepat di atas `TT-111` (`y = 445`) dengan label alarm `TAH`.
     - `FI-141` tepat di atas `FT-141` (`y = 490`).
     - `LIC-131` di dekat `LT-131` & `LV-131` → langsung menggerakkan `FY-131` (`LV-131`).
     - `FI-143` tepat di atas `FT-143`.
     - `LIC-121` di dekat `LT-121` & `LV-121` → langsung menggerakkan `FY-121` (`LV-121`).
     - `FI-142` tepat di atas `FT-142`.
3. **Simbol SIS / ESD Logic (`esd_block` / `sis_box`, kotak dengan Berlian di dalamnya sesuai ISA-5.1)**:
   - Daripada menarik kabel putus-putus raksasa yang memotong semua pipa, gunakan **SIS Function Block (`sis_box` = Diamond-in-Square)** langsung pada tiap transmitter SIS (`PAHH/PALL-102` di atas `PT-102`, `LAHH/LALL-132` di dekat `LT-132`, `LAHH/LALL-122` di dekat `LT-122`) yang masuk ke **Simbol `ESD-1` (Logic Solver)** dan **Interlock Diamond (`ESD-1`)** pada setiap aktuator terkait (`SY-101` pada `SDV-101`, `FY-131` pada `LV-131`, `FY-121` pada `LV-121`, dan motor `M` pada `P-101`), persis seperti cara penggambaran `ESD / PSD` pada referensi `SSY-PRO-PID-003`!
   - Seluruh persilangan sinyal yang tersisa tetap wajib menggunakan `dashed_brk` (gap 3 mm pada garis minor).

---

## 6. Checklist Verifikasi Wajib Subagent Eksekutor

1. Jalankan build + `apply_text.py` + `validate_dxf_file` (`0 errors`) + `cadgen dxf snapshot`.
2. Pastikan **0 garis pipa menembus simbol katup/pompa/orifice/reducer**.
3. Pastikan semua teks menggunakan MTEXT Arial (`0.5–3.0 mm`), **0 tabrakan teks** (terutama di Title Block, Equipment Data Block, dan sekitar pompa `P-101`).
4. Pastikan semua simbol sesuai ISO 10628-2 / ANSI/ISA-5.1-2024 dan tercantum di kotak `LEGEND`.
