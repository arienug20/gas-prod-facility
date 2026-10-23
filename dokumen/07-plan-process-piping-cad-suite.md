# Blueprint & Arsitektur Ekosistem AI-CAD Disiplin Process & Piping

**Dokumen No.**: `GPF-00-PM-PLN-0007`  
**Revisi**: `A0`  
**Tanggal**: `23 Oktober 2026`  
**Disiplin**: Process Engineering & Piping Engineering  
**Standar Acuan**: ANSI/ISA-5.1-2024, ISO 10628-2:2012, ISO 6412-2:2017, API RP 12J, API STD 521, API STD 650, ASME B31.3

---

## 1. Tujuan & Filosofi Arsitektur
Untuk memastikan seluruh *Process Engineer* dan *Piping Engineer* di perusahaan dapat menggunakan AI untuk menghasilkan gambar teknik CAD (**PFD, P&ID, Piping Plan, dan Isometric**) yang **100% seragam, bebas garis tidak terhubung (*zero floating lines*), bebas tabrakan teks (*zero text collisions*), dan konsisten lintas dokumen**, aturan tidak boleh hanya berupa teks pasif, melainkan harus dikodekan menjadi **Tiga Pilar Eksekusi**:
1. **Paket 1 — *Automated CAD Linter & Cross-Discipline QA* (`validate_cad_rules.py`)**: Polisi geometri & konsistensi otomatis.
2. **Paket 2 — *Process & P&ID Advanced Library + Auto-Schedule Exporter* (`pid_common.py` v2)**: Pustaka simbol proses lengkap, *macro assemblies* (`control_valve_station`, `psv_station`, `spec_break`), dan ekstraktor otomatis ke tabel jadwal (*Line List, Valve List, Instrument Index*).
3. **Paket 3 — *Piping Plan / Plot Plan Standard Library & Guide* (`plan_common.py` + `piping-plan-guide.md`)**: Pustaka standar tampak atas perpipaan dengan konversi koordinat *Plant* $(E, N, EL) \rightarrow$ *Sheet* $(x, y)$, *auto-trimming*, simbol *elbow up/down*, *pipe support*, dan *North Arrow* standar.

---

## 2. Spesifikasi Teknis Paket 1: `validate_cad_rules.py`
**Lokasi Target**:
- `~/.agents/skills/company-cad-standard/scripts/validate_cad_rules.py`
- Salinan proyek: `/home/arienugraha-rei/gas-prod-facility/cad/validate_cad_rules.py`

### 2.1 Fitur Pemeriksaan Geometri & Standar (`check_dxf(dxf_path, json_path, mode)`)
Script CLI Python (menggunakan `ezdxf` dan `math`) yang mendukung mode `--mode pid|iso|plan|auto` dan memeriksa:
1. **Audit Entitas Terlarang & Layer**:
   - Gagal (`ERROR`) jika ada entitas `POLYFACE`, `MESH`, `3DSOLID`, atau `TEXT` (single-line; wajib `MTEXT` font `ARIAL`).
   - Memastikan semua layer memiliki `lineweight > 0` sesuai standar perusahaan (`REF-PROC = 50`, `REF-EQUIP = 35`, `REF-SYM = 25`, `REF-TEXT = 18`, `REF-SIG = 13`, `REF-DIM = 9`).
2. **Audit Tinggi Font (`MTEXT`)**:
   - Memastikan seluruh `MTEXT` memiliki `char_height` dalam rentang **`0.5 <= h <= 3.0 mm`**.
3. **Deteksi *Unbroken Line Crossings* (Persilangan Tanpa Break)**:
   - Mengekstrak segmen `LINE` horizontal dan vertikal pada layer `REF-PROC`, `REF-EQUIP`, dan `REF-SIG`.
   - Mendeteksi bila ada dua segmen ortogonal yang saling memotong di bagian dalam (*interior intersection*, jarak dari ujung $> 1.0\text{ mm}$) tanpa *gap* 3 mm:
     - `REF-PROC` memotong `REF-PROC` (bukan T-junction).
     - `REF-SIG` memotong `REF-PROC` atau `REF-EQUIP` (kecuali di titik koneksi tap instrumen).
4. **Deteksi *Text-to-Line Collision* (Tabrakan Teks dengan Garis)**:
   - Menghitung *bounding box* 2D setiap entitas `MTEXT` dari manifest `.texts.json` (berdasarkan `x, y, h, len(t), rot, att=4|5`, dengan lebar karakter rata-rata `0.62 * h` dan margin aman `-0.3 mm`).
   - Memeriksa apakah ada segmen `LINE` dari layer `REF-PROC` atau `REF-EQUIP` yang menembus kotak teks tersebut.
5. **Deteksi *Floating / Dangling Endpoints* pada P&ID**:
   - Memeriksa apakah ada ujung garis `REF-PROC` yang menggantung di ruang kosong (jarak ke garis/lingkaran/arc terdekat di `REF-PROC`, `REF-EQUIP`, atau `REF-SYM` $> 1.8\text{ mm}$).
6. **Cross-Check Lintas Disiplin (`--cross-check pid.texts.json iso1.texts.json ...`)**:
   - Mengekstrak semua nomor pipa berpola `\b\d{3}-[A-Z]{2}-\d{4}\b` (mis. `100-GO-1002`, `080-CO-1003`, `080-CO-1004`, `100-FL-1005`, `050-PW-1006`, `050-CD-1007`) dan memverifikasi bahwa setiap *line number* pada file Isometric terdaftar di P&ID dan memiliki ukuran `DN` yang konsisten.

---

## 3. Spesifikasi Teknis Paket 2: Upgrade `pid_common.py` v2 (Process & P&ID)
**Lokasi Target**:
- `~/.agents/skills/company-cad-standard/scripts/pid_common.py`
- Salinan proyek: `/home/arienugraha-rei/gas-prod-facility/cad/pid_common.py`

### 3.1 Katalog Peralatan Proses Tambahan (ISO 10628-2 & API)
Tambahkan metode baru pada kelas `PIDContext` (dengan tetap mempertahankan seluruh metode yang sudah ada agar `pid_v101.py` 100% *backward-compatible*):
1. `vessel_vertical_ko(cx, y_bot, y_top, r, tag, demister=True)`:
   - Menggambar bejana vertikal (Knock-Out Drum / Scrubber) dengan *ellipsoidal head* atas & bawah (`arc3`), *skirt support* di bawah `y_bot`, *demister pad* berarsir 45° di bagian atas, dan *vortex breaker* di nozzle bawah.
2. `storage_tank_atm(cx, y_bot, w, h_shell, h_roof, tag)`:
   - Menggambar tangki timbun atmosferik *cone roof* sesuai **API STD 650** (`rect` shell + atap kerucut segitiga + simbol *breather valve / conservation vent* di puncak atap + garis *bundwall*).
3. `heat_exchanger_st(cx, cy, length, r, tag)`:
   - Menggambar *Shell & Tube Heat Exchanger* sesuai ISO 10628-2 / TEMA (silinder + *channel head* + garis *tube bundle* internal + 4 nozzle *shell/tube*).
4. `compressor_centrifugal(cx, cy, r_in, r_out, tag)`:
   - Menggambar kompresor gas sentrifugal / ekspander berupa trapesium/lingkaran tirus ISO 10628-2 + motor penggerak `M`.
5. `pig_trap(cx, cy, length, d_minor, d_major, direction, tag)`:
   - Menggambar *Pig Launcher / Pig Receiver* dengan *quick-opening closure door*, *barrel* besar-kecil, dan indikator `XI`/`PI`/`TI`.

### 3.2 *Macro Assemblies* Perpipaan & PFD pada `PIDContext`
1. `spec_break_h(x, y, left_spec="150# A1A", right_spec="300# B1A")` & `spec_break_v(x, y, bot_spec, top_spec)`:
   - Menggambar simbol batas kelas perpipaan (*Piping Class / Spec Break*): garis tegak lurus pipa dengan bendera segitiga di kedua sisi + teks spesifikasi kiri/kanan.
2. `control_valve_station_h(cx, cy, cv_tag, gv_up_tag, gv_dn_tag, bp_tag, fail="FC")`:
   - Menggambar rakitan *Control Valve Bypass Station* lengkap: *Upstream Block Gate Valve* + *Control Valve* + *Downstream Block Gate Valve* pada jalur utama `cy`, dilengkapi loop pipa *bypass* di atas/bawah dengan *Bypass Globe Valve (NC)* dan *bleed/drain valve*, serta mengembalikan `(cx, half_width_total)` untuk dipotong otomatis oleh `pipe_run_h`.
3. `stream_flag_h(x, y, stream_no, p_barg, t_degc, flow_kgh)`:
   - Simbol *Stream Diamond Flag* untuk **PFD (Process Flow Diagram)** sesuai ISO 10628-2 lengkap dengan kotak mini parameter tekanan, temperatur, dan laju alir.

### 3.3 Auto-Registry & Schedule Exporter (`export_schedules(out_json_path)`)
- Setiap kali metode `valve_*`, `control_valve_h`, `sdv_h`, `psv_angle`, `bubble`, `dcs`, `sis_box`, atau `continuity_box_*` dipanggil, `PIDContext` otomatis mencatat item tersebut ke dalam `self.schedule_valves`, `self.schedule_instruments`, dan `self.schedule_lines`.
- Metode `export_schedules(out_path)` mengekspor ringkasan JSON terstruktur (`lines`, `valves`, `instruments`) sehingga *Process/Piping Engineer* langsung mendapatkan draf *Valve MTO* dan *Instrument Index* yang 100% sinkron dengan gambar P&ID.

---

## 4. Spesifikasi Teknis Paket 3: `plan_common.py` & `piping-plan-guide.md`
**Lokasi Target**:
- `~/.agents/skills/company-cad-standard/scripts/plan_common.py`
- `~/.agents/skills/company-cad-standard/references/piping-plan-guide.md`
- Salinan proyek: `/home/arienugraha-rei/gas-prod-facility/cad/plan_common.py`

### 4.1 Kelas `PlanContext` pada `plan_common.py`
Menyediakan kerangka kerja standar untuk gambar **Piping Plan / Plot Plan (A1 841×594 mm)**:
1. **Transformasi Koordinat Plant $\leftrightarrow$ Sheet**:
   - `PlanContext(px0=40.0, py0=40.0, scale=5.0)` (default skala `1:200` di mana $1\text{ m} = 5\text{ mm}$ di kertas A1).
   - `P(e, n) -> (x, y)` mengonversi koordinat *Plant Easting & Northing* (meter) ke milimeter lembar A1.
2. **Auto-Trimming Rute Pipa Plan (`plan_pipe_h`, `plan_pipe_v`)**:
   - Menggambar segmen pipa horizontal (E-W) dan vertikal (N-S) dalam koordinat *Plant* `(E, N)` dengan pemotongan otomatis (*break gap* 3 mm pada ukuran kertas = `3.0 / scale` meter di koordinat *plant*) saat pipa minor melintasi pipa major.
3. **Simbol Tampak Atas Perpipaan (Piping Plan Symbols)**:
   - `elbow_90_up(e, n, r_mm=1.8)`: lingkaran kecil + titik tengah (`⊙`) untuk *elbow* yang belok naik (+UP).
   - `elbow_90_dn(e, n, r_mm=1.8)`: busur 3/4 lingkaran + titik tengah untuk *elbow* yang belok turun (-DN).
   - `tee_up(e, n)` & `tee_dn(e, n)`: simbol *tee* tampak atas.
   - `plan_valve_gate(e, n, orient="H"|"V", tag="")`: simbol katup tampak atas dengan *handwheel* melingkar/T-bar + auto-gap.
   - `pipe_rack_bay(e0, e1, n0, n1, bay_m=6.0)`: menggambar rel *pipe rack* beserta ikatan angin diagonal (*plan bracing*) otomatis setiap `bay_m` meter.
   - `north_arrow_plan(x, y, r=10.0)`: kompas Utara 2D standar *Plot Plan* (panah menunjuk ke atas `+N` dengan separuh bilah terisi `SOLID` + huruf `N`).
   - `coord_callout(e, n, el_mm, dx=8.0, dy=8.0)`: garis penunjuk (*leader*) dengan teks koordinat titik kerja `N xxxx / E xxxx` dan `EL. +xxxx`.
   - `matchline(e0, n0, e1, n1, label="MATCHLINE N 60000 - SEE DWG ...")`: garis batas area putus-titik tebal (*phantom line*) beserta teks referensi lembar sebelahnya.

---

## 5. Pembagian Tugas Subagent Eksekutor (Model `flash`)
Ketiga paket akan dieksekusi secara paralel oleh **3 Subagent `flash`**:
1. **Subagent 1 (`CAD Linter & QA Engineer`)**: Mengimplementasikan `validate_cad_rules.py` dan mengujinya langsung terhadap `pid_v101.dxf`, `iso_go1002.dxf`, `iso_co1003.dxf`, `iso_co1004.dxf`, dan `routing_plan.dxf`.
2. **Subagent 2 (`Process & P&ID Library Developer`)**: Mengimplementasikan `pid_common.py` v2 (katalog peralatan proses, *macro assemblies*, dan *schedule exporter*) serta memperbarui `references/pid-guide.md`.
3. **Subagent 3 (`Piping Plan Library Developer`)**: Mengimplementasikan `plan_common.py` dan menulis panduan `references/piping-plan-guide.md` serta memperbarui `SKILL.md` dan `reapply.sh`.
