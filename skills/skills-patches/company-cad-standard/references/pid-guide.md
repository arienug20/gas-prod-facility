# Panduan Engineering P&ID & PFD Oil & Gas (ANSI/ISA-5.1-2024, ISO 10628-2, API RP 12J, API STD 650, TEMA)

Dokumen ini menjadi pedoman teknis wajib bagi seluruh *engineer* dan subagent AI saat membuat atau merevisi **Piping & Instrumentation Diagram (P&ID)** dan **Process Flow Diagram (PFD)** pada pipeline `cadgen/dxf`.

---

## 0. Larangan: Sumber Kebenaran Tunggal — script P&ID wajib `from pid_common import PIDContext, pipe_run_h, pipe_run_v`

1. **LARANGAN KERAS: Duplikasi Primitif & Simbol Lokal**:
   - Dilarang keras mendefinisikan ulang (copy-paste / reimplementasi) fungsi geometri primitif (`line`, `rect`, `circle`, `arc`, `dashed`, `pipe_run_h`, dll.) maupun makro simbol peralatan di dalam script gambar P&ID masing-masing.
   - Menulis ulang fungsi secara lokal menciptakan divergensi standar, memicu tabrakan teks, celah persilangan hilang, dan merusak otomatisasi QA lintas-disiplin.
2. **Kewajiban Penggunaan Pustaka Terpusat**:
   - Seluruh script P&ID dan PFD **WAJIB** mengimpor pustaka bersama terpusat:
     ```python
     from pid_common import PIDContext, pipe_run_h, pipe_run_v, line, rect, circle, arc, dashed, pneu
     ```
   - Seluruh perbaikan geometri, penyesuaian aturan lineweight/layer, proteksi layer kosong cadgen, dan registrasi MTO dikontrol secara tunggal di `scripts/pid_common.py`.

---

## 1. Standar Acuan & Ukuran Lembar
1. **Ukuran Lembar Standar P&ID**: **ISO A1 (841 × 594 mm)** dengan border luar `(10, 7)–(831, 587)` dan border dalam `(20, 15)–(823, 579)` serta grid referensi `1–12` (horizontal) dan `A–H` (vertikal) sesuai **ISO 5457**.
2. **Standar Simbol & Identifikasi**:
   - **ANSI/ISA-5.1-2024**: Simbol instrumen (*field bubble*, *DCS shared display*, *SIS logic block*, *interlock diamond*, sinyal elektrik vs pneumatik).
   - **ISO 10628-2:2012**: Simbol peralatan proses (*vessels*, *tanks*, *heat exchangers*, *compressors*, *pumps*, *pig traps*), katup (*gate*, *globe*, *check*, *angle PSV*, *control valve*), *reducer*, *strainer*, dan *PFD stream flags*.
   - **API RP 12J & API STD 521**: Internals bejana separator & *knock-out drum* (*inlet deflector baffle*, *plate coalescer*, *weir*, *vortex breaker*, *demister pad*) dan *pressure relief system*.
   - **API STD 650**: Tangki timbun atmosferik *cone roof*, *curb angles*, *conservation vent / breather valve*, *level gauges*, dan *containment bundwall*.
   - **TEMA Standards / ASME Section VIII**: Penukar panas cangkang & buluh (*Shell & Tube Heat Exchanger*) tipe horizontal, partisi alir, dan *tubesheet flange joints*.
   - **ASME B31.3 / B31.4 / B31.8**: Batas spesifikasi perpipaan (*spec breaks*), *piping manifolds*, dan fasilitas peluncur/penerima pig (*pig traps*).

---

## 2. Tata Letak Lembar A1 (Sheet Zoning)
- **Area Gambar Proses (`x = 20..655, y = 15..579`)**:
  - **Zona Atas (`y = 515..573`)**: Kotak Tabel Data Equipment (*Equipment Data Block* bergaris tabel lengkap untuk setiap bejana/pompa/tangki: Tag, Service, Size/Type, Design P/T, Operating P/T, Material/Code).
  - **Zona Tengah Atas (`y = 350..500`)**: Jalur pipa gas/relief menuju Flare Header (`PSV`, `PCV/PV`, `FE/FT/FI`) dan blok utama `SIS LOGIC SOLVER (ESD-1)`.
  - **Zona Tengah (`y = 235..350`)**: Bejana utama (`V-101`, `V-102` dll.) beserta *internals*, *nozzles*, *saddles*, dan *level bridles*.
  - **Zona Bawah (`y = 60..235`)**: Jalur pipa cairan keluar (*Produced Water*, *Closed Drain*, *Crude Oil Transfer Pump* & *Discharge*).
- **Kolom Furniture Kanan (`x = 655..823, y = 15..579`)**:
  - `y = 435..579`: **NOTES** (rata kiri `left=True` / `att=4`, `x = 659`).
  - `y = 185..435`: **LEGEND & SYMBOLS** (simbol digambar di `x = 660..685`, teks keterangan rata kiri `left=True` di `x = 690`).
  - `y = 148..185`: **REFERENCE DRAWINGS** (rata kiri `left=True` di `x = 659`).
  - `y = 116..148`: **REVISION TABLE** (*bottom-up*: `A0` di bawah → revisi terbaru di atas).
  - `y = 15..116`: **COMPANY TITLE BLOCK** (ISO 7200).

---

## 3. Enam Aturan Mutlak Anti-Cacat Geometri (Zero-Defect Rules)

### Aturan 3.1 — Auto-Trimming Pipa (`pipe_run_h` & `pipe_run_v`)
- **DILARANG KERAS** menggambar garis pipa menerus (`line(x0, y, x1, y)`) yang menembus simbol katup, pelat *orifice*, *reducer*, atau pompa.
- Selalu gunakan `pipe_run_h(y, x0, x1, gaps=[(cx, hw), ...])` dan `pipe_run_v(x, y0, y1, gaps=[(cy, hh), ...])`:
  - Katup horizontal (`w=10`): `hw = 5.0`
  - Control Valve Station (`span=56.0`): gunakan kembalian tuple langsung `[ctx.control_valve_station_h(...)]` (menghasilkan gap sepanjang `cx ± 28.0 mm`)
  - Pelat Orifice (`FE`): `hw = 1.2`
  - Concentric Reducer (`w=8`): `hw = 4.0`
  - Stream Flag Diamond (`r=4`): `hw = 4.0`
  - Persilangan pipa minor memotong pipa major: tambahkan gap `(x_cross, 1.5)` (celah 3 mm) pada pipa **minor**, sedangkan pipa **major** tetap utuh.

### Aturan 3.2 — Larangan Nozzle Menggantung (*Zero Floating Nozzles*)
- Perhatikan batas koordinat dinding silinder bejana (`x_left` s/d `x_right`, misal `x = 135..435` dan `y_bot = 250, y_top = 340`).
- Semua *bottom nozzles* (`N4`, `N6`, `N3`) dan *top nozzles* (`N5`, `N2`) **WAJIB** memiliki koordinat `x` di dalam rentang dinding silinder lurus (`x_left + 5 <= x_nozzle <= x_right - 5`) sehingga leher nozzle benar-benar menyentuh garis shell (`y = 250` atau `y = 340`).
- **DILARANG** menempatkan nozzle vertikal di area lengkung *ellipsoidal head* (`x > x_right` atau `x < x_left`) karena akan membuat garis nozzle melayang di udara.
- Urutan nozzle bawah harus mengikuti arah aliran hilir agar pipa keluar tidak saling menyilang: misalnya `N6` (*Drain*, `x = 408`) ditempatkan di sebelah kiri `N3` (*Oil Outlet*, `x = 430`), sehingga pipa `N3` yang menuju pompa di sebelah kanan (`x = 490`) tidak pernah memotong pipa `N6`.

### Aturan 3.3 — Level Bridle Tertutup (*Closed-Loop Level Bridle*)
- **DILARANG** menggambar *level bridle* dengan cabang *stub* yang berhenti menggantung di udara atau menarik garis sinyal `LT` menembus batang *sight glass* `LG`.
- Gunakan helper `ctx.level_bridle(...)` atau struktur *closed-loop* berikut:
  1. Standpipe vertikal terhubung ke dinding bawah bejana (`y = 250`) hingga ruang uap atas (`y = 306..308`).
  2. Cabang tap atas dan tap bawah keluar secara horizontal melewati *isolation gate valve* (`w=5.0, h=3.2`) dan **langsung bersambung ke ujung atas & bawah kolom `LG`** (`x_lg_l..x_lg_r`).
  3. Katup *drain* vertikal dipasang di **bawah** dinding shell (`y = 250` turun ke `y = 236` dengan garis penutup *cap*), dan posisinya memiliki jarak bebas minimal `15 mm` dari kaki `SADDLE`.
  4. Garis sinyal putus-putus menuju `LT` ditarik dari **sisi kanan kolom `LG` (`x_lg_r`)** menuju tepi kiri lingkaran *bubble* (`x_lt - 6.0`).

### Aturan 3.4 — Akurasi Simbol Katup & Instrumen (ISO 10628-2 & ISA-5.1)
1. **Control Valve (`control_valve_h`) & Shutdown Valve (`sdv_h`)**:
   - Batang vertikal (*stem*) langsung menyatu dengan kubah diafragma setengah lingkaran (`arc(..., 0, 180)` + garis alas). **DILARANG** menambahkan palang *handwheel T-bar* di tengah *stem* aktuator otomatis.
2. **Check Valve (`valve_check_h`)**:
   - Hanya terdiri dari 2 garis tegak ujung + 1 garis diagonal *flapper* + titik engsel `SOLID` di kiri-atas + kepala panah `SOLID` di kanan-bawah + *flange ticks*. **DILARANG** menutup sisi atas dan bawah dengan garis horizontal (agar tidak menjadi kotak).
3. **Orifice Plate (`orifice_h`)**:
   - Label `FE-xxx` ditempatkan di ruang kosong di sebelah kiri-atas atau tepat di bawah pelat *orifice* (`y - 8.5`), tidak boleh menimpa garis pipa atau garis sinyal `FT`.

### Aturan 3.5 — Pemotongan Garis Permukaan Cairan (*Internal Liquid Level Lines*)
- Garis putus-putus permukaan cairan di dalam bejana (`OIL LEVEL`, `OIL / WATER INTERFACE`) **WAJIB** dihentikan dengan jarak bebas minimal `4–5 mm` sebelum menyentuh *Plate Coalescer*, *Weir*, *Standpipe Bridle*, *Bubble Instrumen*, maupun kotak `LAHH/LALL` (`sis_box`).

### Aturan 3.6 — Penjajaran Teks (`att=4` vs `att=5`)
- Teks panjang di dalam tabel (`NOTES`, `LEGEND`, `REFERENCE DRAWINGS`, `EQUIPMENT DATA`, `LEVEL SETTING`) **WAJIB** menggunakan `left=True` (`att=4` *Middle-Left*).
- Teks di dalam *bubble* instrumen, label katup, dan judul kolom menggunakan rata tengah (`left=False` / `att=5` *Middle-Center*).

---

## 4. Katalog Peralatan Proses Tambahan (ISO 10628-2, API & TEMA)

`PIDContext` versi 2 menyediakan pustaka peralatan proses parametrik siap-pakai:

### 4.1 Knock-Out Drum / Vertical Scrubber (`vessel_vertical_ko`)
```python
ctx.equip += ctx.vessel_vertical_ko(
    cx=100.0,
    y_bot=200.0,
    y_top=280.0,
    r=18.0,
    tag="V-102",
    demister=True,
)
```
- **Fitur Geometri**:
  - Dinding silinder vertikal pada $x = cx \pm r$.
  - Tutup atas dan bawah elipsoidal 2:1 (`arc3`) dengan garis batas las (*tangent seam lines*) putus-putus.
  - Penopang rok silinder (*skirt support*) di bawah `y_bot` lengkap dengan *base ring* (bebas lingkaran access hole agar tidak menabrak nozzle dasar).
  - *Demister pad* berarsir 45° otomatis dimasukkan ke layer `REF-HATCH`.
  - Salib penahan pusaran (*vortex breaker*) standar ISO 10628-2 berupa plat silang (*cruciform*) di dalam head dasar dan nozzle drain flanged ke bawah.
  - Tagging otomatis ke `schedule_equipment`.

### 4.2 Tangki Timbun Atmosferik API 650 (`storage_tank_atm`)
```python
# Mode P&ID (bund=False default, fondasi rapi tanpa tanggul plot plan)
ctx.equip += ctx.storage_tank_atm(
    cx=200.0,
    y_bot=100.0,
    w=48.0,
    h_shell=36.0,
    h_roof=8.0,
    tag="T-101",
    bund=False,
)

# Mode Plot Plan / Containment Dike (bund=True)
ctx.equip += ctx.storage_tank_atm(
    cx=200.0,
    y_bot=100.0,
    w=48.0,
    h_shell=36.0,
    h_roof=8.0,
    tag="T-102",
    bund=True,
)
```
- **Fitur Geometri**:
  - Dinding cangkang silinder (*shell*) persegi panjang dan pelat dasar (*bottom plate*) dengan fondasi ring.
  - Atap kerucut segitiga (*cone roof*) dengan puncak atap di `y_bot + h_shell + h_roof`.
  - Katup pernapasan / pengaman vakum (*conservation vent / breather valve*) di puncak kerucut.
  - Garis batas permukaan cairan normal (putus-putus 75% ketinggian) dengan simbol segitiga level.
  - Opsi tanggul pengaman (`bund=True`): digambar berupa dua garis horizontal sejajar di kaki tangki kiri dan kanan dengan *tick* arsir kecil. Default `bund=False` untuk P&ID standar.
  - Tagging otomatis ke `schedule_equipment`.

### 4.3 Shell & Tube Heat Exchanger (`heat_exchanger_st`)
```python
ctx.equip += ctx.heat_exchanger_st(
    cx=320.0,
    cy=200.0,
    length=44.0,
    r=10.0,
    tag="E-101",
)
```
- **Fitur Geometri**:
  - Cangkang horizontal dengan *bonnet channel head* kiri dan *return head* kanan berbentuk setengah lingkaran mulus tanpa sudut tajam.
  - Garis flensa ganda untuk *tubesheet* di kedua ujung shell.
  - *Channel spool* silinder di sisi kiri dilengkapi 2 nozzle vertikal (Tube Inlet di bawah dan Tube Outlet di atas).
  - Garis putus-putus internal berkas pipa (*tube bundle*) dan sekat partisi aliran (*pass partition*).
  - 2 Nozzle shell vertikal (Shell Inlet di atas, Shell Outlet di bawah) berjarak aman dari kaki penopang pelana (*saddle supports*).
  - Tagging otomatis ke `schedule_equipment`.

### 4.4 Kompresor Sentrifugal Gas (`compressor_centrifugal`)
```python
ctx.equip += ctx.compressor_centrifugal(
    cx=420.0,
    cy=200.0,
    r_in=6.0,
    r_out=9.0,
    tag="K-101",
)
```
- **Fitur Geometri**:
  - Rumah kompresor trapesium tirus ISO 10628-2 (suction besar $r_{out}$, discharge menyempit $r_{in}$).
  - Nozzle hisap (*suction*) flanged vertikal ke atas di sisi suction (kiri).
  - Nozzle tekan (*discharge*) flanged vertikal ke atas di sisi discharge (kanan).
  - Motor listrik penggerak berlabel `"M"`, kopling poros fleksibel, kaki penopang, dan pelat dasar (*skid baseplate*).
  - Tagging otomatis ke `schedule_equipment`.

### 4.5 Pig Launcher / Receiver (`pig_trap`)
```python
# Pig Launcher (aliran mengarah ke kanan, pintu di kiri)
ctx.equip += ctx.pig_trap(
    cx=520.0,
    cy=200.0,
    length=36.0,
    h_minor=6.0,
    h_major=10.0,
    direction=1,
    tag="PL-101",
)

# Pig Receiver (aliran dari kiri, pintu di kanan)
ctx.equip += ctx.pig_trap(
    cx=600.0,
    cy=200.0,
    length=36.0,
    h_minor=6.0,
    h_major=10.0,
    direction=-1,
    tag="PR-101",
)
```
- **Fitur Geometri**:
  - Pintu buka-cepat berengsel (*Quick-Opening Closure door*).
  - Laras besar (*major barrel*) dan laras kecil (*minor barrel*).
  - *Eccentric bottom-flat reducer*: garis dasar lurus horizontal agar scraper/mandrel pig meluncur tanpa benturan pada leher pipa.
  - Nozzle jalur pendorong (*kicker line*) dan penunjuk lintasan pig (*pig passage signaller* `XI`).
  - Tagging otomatis ke `schedule_equipment` dan `schedule_instruments`.

---

## 5. Macro Assemblies Perpipaan & Simbol PFD

### 5.1 Control Valve Bypass Station (`control_valve_station_h`)
Rakitan terpadu untuk stasiun katup kendali dengan bypass manual:
```python
# Gambar stasiun dan peroleh gap untuk pipe_run_h (span=56.0 default)
gap_station = ctx.control_valve_station_h(
    cx=350.0,
    cy=300.0,
    cv_tag="PV-101",
    gv_up_tag="GV-101A",
    gv_dn_tag="GV-101B",
    bp_tag="BV-101",
    fail="FC",
    span=56.0,
    bypass_dy=18.0,
)

# Pipa utama otomatis terpotong rapi sepanjang stasiun (cx ± 28.0 mm)
ctx.proc += pipe_run_h(300.0, 200.0, 500.0, gaps=[gap_station])
```
- **Komponen Otomatis**:
  - Di jalur utama: Gate Valve Upstream di `cx - 20`, Control Valve di `cx`, Gate Valve Downstream di `cx + 20` (jarak antar-katup $\ge 20\text{ mm}$ dengan segmen pipa nyata).
  - Pipa penghubung antara katup-katup utama dan riser bypass.
  - Riser vertikal di `cx - 28` dan `cx + 28` menuju `cy + 18`.
  - Bypass Valve dengan arsiran *Normally Closed* (NC Solid) **TANPA** kubah aktuator diafragma.
  - Anotasi status `"NC"` ditempatkan di posisi bebas di sisi kanan katup bypass (bebas dari kubah aktuator control valve di bawahnya).
  - Seluruh katup terdaftar otomatis di `schedule_valves`.

### 5.2 Piping Specification Break (`spec_break_h` & `spec_break_v`)
Simbol resmi batas kelas perpipaan (ASME B31.3):
```python
# Horizontal pipe spec break
ctx.proc += ctx.spec_break_h(x=150.0, y=350.0, left_spec="150# A1A", right_spec="300# B1A")

# Vertical pipe spec break
ctx.proc += ctx.spec_break_v(x=250.0, y=350.0, bot_spec="150# A1A", top_spec="300# B1A")
```
- Garis transversal $\pm 6\text{ mm}$ tegak lurus sumbu pipa.
- Sepasang bendera segitiga *solid* di sisi berlawanan.
- Teks kelas pipa di masing-masing sisi tanpa menabrak pipa.

### 5.3 Simbol Bendera Aliran PFD (`stream_flag_h`)
Simbol belah ketupat data proses pada Process Flow Diagram (ISO 10628-2):
```python
ctx.proc += ctx.stream_flag_h(
    x=450.0,
    y=350.0,
    stream_no="1",
    p_barg="10.0",
    t_degc="40",
    flow_kgh="12500",
)
```
- Belah ketupat bernomor aliran (*Stream Number*).
- Garis penunjuk (*leader*) ke tabel data parameter mini 3 baris:
  - Baris 1: Tekanan Operasi ($P$ dalam $\text{barg}$)
  - Baris 2: Temperatur Operasi ($T$ dalam $^\circ\text{C}$)
  - Baris 3: Laju Alir Massa ($W$ dalam $\text{kg/h}$)

---

## 6. Auto-Registry Schedules & MTO Exporter

`PIDContext` versi 2 secara otomatis melacak seluruh entitas ber-tag selama proses pembuatan gambar CAD berlangsung:

### 6.1 Pendaftaran Garis Pipa Manual
```python
ctx.register_line(
    line_no="100-GO-1002",
    spec="300# B1A",
    service="Gas Outlet to Compression",
    dn=100,
)
```

### 6.3 Ekspor Manifest & Pencegahan Error Cadgen (`export_manifest` & `get_layers`)
Pada fungsi utama bergaya decorator `@dxf`, kembalikan manifest dengan memanggil `ctx.export_manifest`:
```python
@dxf
def my_pid_drawing():
    ctx = PIDContext()
    # ... gambar peralatan dan perpipaan ...
    return ctx.export_manifest("my_drawing.texts.json")
```
- **Proteksi Layer Kosong**:
  - `ctx.export_manifest()` dan `ctx.get_layers()` secara otomatis memfilter dan hanya mengembalikan layer yang memiliki entitas geometri (`self.equip`, `self.proc`, dll.).
  - Layer yang tidak digunakan tidak akan disertakan dalam dictionary compound, mencegah fatal error cadgen: `cadgen error 'layer contains no geometry'`. Engineer tidak perlu lagi mengisi entitas dummy pada layer yang tidak terpakai.
File JSON yang dihasilkan memiliki struktur terstandarisasi untuk deliverable proyek:
```json
{
  "equipment": [
    {
      "tag": "V-102",
      "type": "VERTICAL KO DRUM / SCRUBBER",
      "x": 100.0,
      "y": 240.0,
      "y_bot": 200.0,
      "y_top": 280.0,
      "radius": 18.0,
      "demister": true
    }
  ],
  "valves": [
    {
      "tag": "PV-101",
      "type": "CONTROL VALVE",
      "orientation": "H",
      "x": 350.0,
      "y": 300.0,
      "fail": "FC"
    }
  ],
  "instruments": [
    {
      "tag": "PT-101",
      "type": "FIELD INSTRUMENT",
      "x": 290.0,
      "y": 400.0
    }
  ],
  "lines": [
    {
      "line_no": "100-GO-1002",
      "spec": "300# B1A",
      "service": "Gas Outlet to Compression",
      "dn": 100
    }
  ]
}
```
Hasil JSON ini siap digunakan oleh disiplin Piping dan Instrumentation untuk:
1. Validasi lintas-disiplin (*Cross-Discipline QA* terhadap file Isometric dan Line List).
2. Pembuatan otomatis *Equipment List*, *Valve MTO*, dan *Instrument Index*.
