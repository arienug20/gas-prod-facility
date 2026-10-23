# DESIGN BASIS — GAS PRODUCTION FACILITY (SHARED, SINGLE SOURCE OF TRUTH)

Proyek : Fasilitas Produksi Gas Lapangan (onshore) — uji coba tooling CAD
Dok    : GPF-00-DB-0001, Rev A0
Tanggal: 09 Oct 2026
Status : ISSUED FOR EXECUTION (drawing test — bukan untuk konstruksi)

> **ATURAN**: Semua drawing (P&ID, piping plan, isometric) HARUS mengambil
> tag equipment, nomor line, tag instrumen, koordinat, dan elevasi dari
> dokumen ini. KONSISTENSI LINTAS-DRAWING WAJIB. Deviasi dilarang; bila
> terpaksa, catat di laporan eksekusi dengan alasan.

---

## 1. STANDAR ACUAN (terverifikasi 09 Oct 2026)

| Kode | Judul | Edisi/Tahun | Aplikasi |
|---|---|---|---|
| ANSI/ISA-5.1-2024 | Instrumentation and Control — Symbols and Identification | 2024 | Simbol & tagging instrumen P&ID |
| ISA-TR5.1.03-2024 | Graphic Symbol Guidelines | 2024 | Panduan grafis (advisory) |
| ISO 15519-2:2015 | Diagrams for process industry — Measurement and control | 1st ed., 2015 | Konten diagram P&ID |
| ISO 10628-1:2014 | Diagrams for chem/petrochem industry — Part 1 | 2014 | Jenis & struktur diagram |
| ISO 10628-2:2012 | Graphical symbols | 2012 | Simbol equipment PFD/P&ID |
| ISO 5457:1999 | Sizes and layout of drawing sheets | 1999 | Format lembar & border |
| ISO 7200:2004 | Data fields in title blocks | 2004 | Title block |
| ISO 3098-1:2015 | Lettering — Part 1 | 2015 | Huruf (2,5/3,5 mm) |
| ISO 128-24:1999 | Lines on mechanical engineering drawings | 1999 | Jenis garis |
| API RP 12J | Process Design of Oil and Gas Separators and Scrubbers | 9th ed., Sep 2024 | Separator V-101 |
| ASME B31.3 | Process Piping | 2022 | Piping fasilitas |
| API STD 521 | Pressure-relieving and Depressurizing Systems | 7th ed., Jun 2020 (Errata 1: 2022) | Sistem flare/relief |
| API STD 537 | Flare Details for Petroleum, Petrochemical, and Natural Gas Industries | 4th ed., 2024 (Add. 1: 2025, Add. 2: 2026) | Detail flare stack |
| API STD 650 | Welded Tanks for Oil Storage | 13th ed., 2020 | Tangki T-101 |

Catatan: verifikasi ulang edisi saat tahap IFC (standar API/ISO dapat
berubah; API 650 edisi 14 telah terbit — konfirmasi sebelum pakai kontraktual).

## 2. BASIS DESAIN PROSES (ASUMSI UNTUK UJI DRAWING)

| Parameter | Nilai | Keterangan |
|---|---|---|
| Fluida umpan | Wellstream 3-fasa (gas/minyak/air) | — |
| Tekanan operasi V-101 | 10 barg (design 17,2 barg) | assumption |
| Temperatur operasi | 40 °C | assumption |
| Orientasi separator | Horizontal, 3-fasa, weir internal | API RP 12J |
| Ukuran V-101 | ID 2.300 mm × 7.600 mm S/S | assumption |
| Elevasi CL vessel | +3.000 m (dari grade) | — |
| Material pipa | CS ASTM A106 Gr.B / fitting A234 WPB / flange A105 RF #150 | spec class A1A |
| Satuan drawing | mm pada lembar (sheet), koordinat plant dalam meter | — |
| Penamaan ukuran pipa | DN (metric) | 1 m = 1000 mm |

## 3. DAFTAR EQUIPMENT

| Tag | Deskripsi | Posisi plant (E, N) m | Elevasi kunci |
|---|---|---|---|
| V-101 | Horizontal 3-phase separator, E-W | center (14, 34); extent x 10.2–17.8, y 32.85–35.15 | CL +3.0 |
| P-101 | Crude oil transfer pump (horizontal centrifugal) | (22, 30.5) | CL suction +0.6, discharge +0.8 |
| V-102 | Flare KO drum (horizontal kecil, 2.5 m × 1.6 m) | x 70.0–72.5, y 45.2–46.8 | CL +1.0 |
| F-101 | Flare stack self-supported, tinggi 12 m, tip Ø0.6 m | center (84, 46) | tip +12.0 |
| T-101 | Vertical fixed cone roof tank, D 6.0 m × H 6.0 m (±170 m³) | center (69, 14) | — |
| — | Tank bund 14 × 12 m, dinding tinggi 1.0 m | x 62–76, y 8–20 | — |
| — | Pipe rack baja 1 level, x 19–58, y 34–36, support tiap 6 m | supports x = 22, 28, 34, 40, 46, 52, 58 | TOP steel +4.5, CL pipa +5.0 |
| — | Access road lebar 6 m, aspal | y 40–43, x 8–92 | grade |
| — | Fence plot | (0,0)–(100,60) m | — |

Nozzle V-101 (nomor = dipakai di SEMUA drawing):
N1 inlet DN150 (head kiri, CL), N2 gas outlet DN100 (top, x=15 m plant),
N3 oil outlet DN80 (head kanan bawah), N4 water outlet DN50 (bottom, x=26 m),
N5 PSV inlet DN100 (top, x=13 m), N6 drain DN50 (bottom, x=44.5 m).

Nozzle T-101: N1 inlet DN80 di roof (67, 15.8) plant, +6.15 m;
N2 vent; N3 outlet DN80 shell selatan (69, 11) → truck loading (by others).

## 4. LINE LIST (FINAL — TIDAK BOLEH DIUBAH)

| No. Line | DN | Dari → Ke | Valve/Spesial di line | Keterangan |
|---|---|---|---|---|
| 100-PF-1001 | 150 | Production header (BL barat) → V-101 N1 | SDV-101 | ESD valve, fail-closed |
| 100-GO-1002 | 100 | V-101 N2 → reducer → tie-in header di tee rack (50, 35, +5.0) | PV-101, GV-141, FE/FT-141 | slope 1:500 ke KO drum, no pockets |
| 100-FL-1005 | 150 | Tee (50,35,+5.0) [gabung GO-1002 + tailpipe PSV-101] → V-102 → F-101 | — | slope 1:500 ke KO drum |
| 080-CO-1003 | 80 | V-101 N3 → P-101 suction | GV-101, ST-101 | — |
| 080-CO-1004 | 80 | P-101 discharge → T-101 N1 | CV-101, GV-102, LV-121, FE/FT-142, GV-103 | rack CL +5.0; grade CL +1.2 sleeper |
| 050-PW-1006 | 50 | V-101 N4 → BL timur (water treatment) | LV-131, FE/FT-143 | grade CL +1.2 |
| 050-CD-1007 | 50 | V-101 N6 → BL timur (closed drain) | GV-104 (NC) | grade CL +1.2 |

Rute ringkas (koordinat plant meter, E = timur, N = utara):
- **GO-1002/FL-1005**: (15,35) riser +5.0 → E ke (58,35) → N ke (58,46) [crossing road +6.5] → E ke (70.5,46) → turun ke V-102 inlet +1.15.
- **CO-1003**: N3 (17.8,33.2,+2.2) → E 4.2 m → turun → P-101 suction (22,30.9,+0.6).
- **CO-1004**: discharge (22.8,30.5,+0.8) → E 1.2 m [CV-101, GV-102] → riser +5.0 → N ke rack y34 (24,34) → E ke (44,34) [FE-142 di (34,34)] → turun (44,16,+1.2) → E ke (67,16) [LV-121 di (48,16); GV-103 di (65,16)] → N 1.5 m → riser +6.7 → N 1.7 m → turun 0.5 m → T-101 N1.
- **PW-1006**: (26,32.85) → S ke (26,22) → E ke BL (100,22). [N4 di x=26; FE/FT-143 di (30,22)]
- **CD-1007**: (44.5,32.85) → S ke (44.5,6) → E ke BL (100,6).
- **Loading (by others)**: T-101 N3 (69,11) → (69,9.7) → E ke (100,9.7).
- **PF-1001**: BL barat (0,34) → V-101 N1.
- Crossing: CO-1004 (x=44, N-leg) memotong PW-1006 (y=22) di (44,22) — gambar hop.

## 5. INSTRUMENT INDEX (FINAL — TIDAK BOLEH DIUBAH)

| Loop | Tag | Fungsi | Lokasi | Output/Aksi |
|---|---|---|---|---|
| 101 | PT-101 | Pressure transmitter (BPCS) | field, top vessel | → PIC-101 (DCS) |
| 101 | PIC-101 | Pressure indicating controller | DCS shared display | → FY-101 → PV-101 |
| 101 | PV-101 | Backpressure control valve DN100, globe, FC | line GO-1002 | — |
| 101 | FY-101 | I/P converter | field, dekat PV-101 | pneumatic ke actuator |
| 101 | PT-102 | Pressure transmitter (SIS) | field, top vessel | → ESD-1 (PSHH/PSLL) |
| 101 | PI-103 | Pressure indicator (gauge) | field, local | — |
| 101 | PSV-101 | Pressure safety valve DN100×150 | N5, tail ke FL-1005 | set per MAWP |
| 111 | TT-111 | Temperature transmitter (TW) | field, top vessel | → TI-111 (DCS, TAH) |
| 111 | TI-112 | Local temperature indicator | field | — |
| 121 | LT-121 | Oil level transmitter (external cage) | field, bawah vessel sisi oil | → LIC-121 (DCS) |
| 121 | LIC-121 | Level indicating controller | DCS | → FY-121 → LV-121 |
| 121 | LV-121 | Level control valve DN80, globe, FC | CO-1004 di (48,16) | — |
| 121 | LT-122 | Oil level transmitter (SIS) | field | → ESD-1 (LSHH/LSLL) |
| 121 | LG-123 | Level gauge (oil) | field | — |
| 131 | LT-131 | Interface LT (BPCS) | field, bawah vessel sisi water | → LIC-131 (DCS) |
| 131 | LIC-131 | Interface level controller | DCS | → FY-131 → LV-131 |
| 131 | LV-131 | Level control valve DN50, globe, FC | PW-1006 | — |
| 131 | LT-132 | Interface LT (SIS) | field | → ESD-1 |
| 131 | LG-133 | Level gauge (interface) | field | — |
| 141 | FE/FT-141 | Orifice + FT gas | GO-1002 (32,35) | → FI-141 (DCS) |
| 142 | FE/FT-142 | Orifice + FT oil | CO-1004 (34,34) | → FI-142 (DCS) |
| 143 | FE/FT-143 | Orifice + FT water | PW-1006 (30,22) | → FI-143 (DCS) |
| — | SDV-101 | ESD valve DN150 gate, FC + solenoid SY-101 | PF-1001 | ditutup oleh ESD-1 |
| — | ESD-1 | SIS logic solver | — | lihat note C&E |

**Cause & Effect ESD-1** (wajib tertulis di notes P&ID):
- PT-102 PSHH/PSLL → close SDV-101, close LV-121, trip P-101
- LT-122 LSHH/LSLL → close SDV-101, close LV-121, trip P-101
- LT-132 LSHH/LSLL → close LV-131
Alarm BPCS (PAH/PAL/LAH/LAL) diimplementasikan di DCS dari PT-101/LT-121/LT-131.

## 6. KONVENSI DRAWING

- Simbol instrumen: ANSI/ISA-5.1-2024; konten diagram: ISO 15519-2:2015.
- Signal listrik = garis putus (dash 4 mm, gap 1,6 mm); pneumatic = garis
  dengan tanda slash ganda "//" tiap 8 mm; line proses = garis solid.
- Bubble field = lingkaran Ø12; DCS shared display = kotak 16×16 berisi
  lingkaran Ø12; ESD logic = kotak 20×20 berisi diamond 12.
- Semua teks = **entity MTEXT** (style ARIAL) via manifest `TEXTS` +
  post-processor `apply_text.py` — BUKAN outline bd.Text, BUKAN entity TEXT.
- Sheet A1 = 841×594 mm, A3 = 420×297 mm, border ISO 5457 (kiri 20 mm,
  lainnya 10 mm), title block ISO 7200.

### 6a. STANDAR DRAFTING PERUSAHAAN (WAJIB — lihat skill company-cad-standard)

1. **Teks**: font Arial, tinggi 0,5–3,0 mm pada ukuran kertas:
   - Penamaan equipment 2,5–3,0 mm (tag instrumen dalam bubble ≥2,0).
   - Nomor line 1,5–2,0 mm.
   - Flow from/to 1,8–2,3 mm (label BL tujuan + nomor line dipisah teks
     dengan tinggi masing-masing).
   - Semua teks lain 0,5–3,0 mm (cap 3,0 mm termasuk judul/title block).
2. **Persilangan garis**: garis minor di-BREAK gap 3 mm pada titik silang;
   MAJOR process line selalu tampil utuh. Prioritas: proses utama > proses
   minor (DN kecil yang break) > sinyal > dimensi.
3. **Lineweight** per jenis line: REF-PROC 0,50; REF-EQUIP/FRAME 0,35;
   REF-SYM/TITLE 0,25; REF-TEXT 0,18; REF-SIG/SIGP/HATCH/DIM/FENCE 0,13;
   REF-GRID 0,09 — dipasang `cad/apply_text.py` (MTEXT + pens) SETELAH
   setiap build.
4. **Tabrakan teks** dengan line/teks/equipment/valve dilarang.
5. **Setiap line proses wajib punya panah aliran** (tiap belokan,
   tiap ±100 mm P&ID / ±15 m plan, semua BL arrow).
- Nomor dokumen: GPF-00-PI-PID-0001 (P&ID), GPF-00-PI-PLN-0002 (plan),
  GPF-00-PI-ISO-0003/0004/0005 (iso), semua **Rev A1**,
  "REVISED PER COMPANY DRAFTING STANDARD — ISSUED FOR REVIEW".
- Project name di title block: "GAS PRODUCTION FACILITY — ONSHORE FIELD".
- Drawn: GLM-5.3-FLASH; Checked: PM (AI); Approved: (kosong).
- Tanggal: 09 OCT 2026.
