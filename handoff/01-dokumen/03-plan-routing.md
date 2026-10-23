# PLAN EKSEKUSI B — PIPING PLAN & ISOMETRICS, ROUTING SEPARATOR → FLARE & TANGKI

Dokumen : GPF-00-PI-PLN-0002 (plan) + GPF-00-PI-ISO-0003/0004/0005 (iso), Rev A0
Input   : `dokumen/01-design-basis.md` (WAJIB dibaca dulu)
Output  : `cad/routing_plan.py/.dxf/.png`, `cad/iso_go1002.py/.dxf/.png`,
          `cad/iso_co1003.py/.dxf/.png`, `cad/iso_co1004.py/.dxf/.png`

## 0. URUTAN KERJA

1. Baca `~/.agents/skills/dxf/SKILL.md` + `references/generator-templates.md`.
2. Baca `dokumen/01-design-basis.md` penuh.
3. Kerjakan BERURUT: routing_plan → iso_go1002 → iso_co1003 → iso_co1004.
4. Build + validasi + snapshot per file (perintah sama dengan Plan A §1,
   ganti nama file). Semua perintah dari `~/gas-prod-facility`.
5. **VERIFIKASI VISUAL (WAJIB)**: baca tiap PNG dengan tool `read`
   (kamu subagent dengan kemampuan baca gambar), cek checklist §4a;
   perbaiki + rebuild + snapshot ulang bila ada temuan (maks 3 iterasi
   per file). Temuan tersisa dicatat di laporan.
6. Laporkan sesuai §5.

## 1. ATURAN TEKNIS (SAMA DENGAN PLAN A §2 — BERLAKU PENUH)

Layer resmi proyek ini: `REF-FRAME, REF-TITLE, REF-EQUIP, REF-PROC, REF-SYM,
REF-SIG, REF-TEXT, REF-DIM, REF-GRID, REF-ROAD, REF-FENCE, REF-HATCH`.
(Nota: token pertama `REF` membuat semua layer open-geometry-safe.)
Idiom kode helper: salin dari `dokumen/02-plan-pid.md` §3 (line, circle,
arc, dashed, text, comp) — TIDAK perlu bubble/valve P&ID.

## 2. SHEET A1 PIPING PLAN (GPF-00-PI-PLN-0002)

### 2.1 Mapping koordinat
- Sheet A1 841×594, border (20,10)-(831,584), grid ref kolom/baris seperti Plan A.
- Plot plant (0..100, 0..60) m → sheet: **X = 40 + 5·E ; Y = 40 + 5·N**
  (skala 1:200; 1 m = 5 mm). Semua manifest di bawah diberikan dalam
  koordinat plant (E,N) meter — KONVERSI dengan rumus ini di kode
  (`def P(e, n): return 40 + 5*e, 40 + 5*n`).
- Zona: plot sheet (40,40)-(540,340); north arrow (90,355); plant title
  text (300,365) "PLOT PLAN / PIPING PLAN — SCALE 1:200"; legend box
  (555,150)-(821,470); line-index box (555,480)-(821,580); title block
  (651,15)-(827,105) + rev table (651,105)-(827,120) (field sama Plan A §5,
  TITLE = "PIPING PLAN — SEPARATOR TO FLARE & STORAGE TANK", DOC NO
  GPF-00-PI-PLN-0002, SCALE 1:200@A1).

### 2.2 Manifest geometri (koordinat plant meter)
| Item | Geometri (REF-*) |
|---|---|
| Fence | rect (0,0)-(100,60) dashed (dash 6/gap 2), REF-FENCE |
| Grid | tick + huruf A–K tiap 10 m pada X, angka 1–6 tiap 10 m pada Y (di luar fence 3 mm), REF-GRID; label huruf 2,5 |
| North arrow | segitiga (88,52)-(92,52)-(90,55) + "N" di (90,56.5) — koordinat sheet langsung (460,330) area; REF-SYM |
| V-101 | rect (10.2,32.85)-(17.8,35.15) + 2 arc head; label "V-101 3-PHASE SEP." (14, 30.5); skid dashed rect (9.5,32)-(18.5,36.5); REF-EQUIP |
| P-101 | simbol pump kecil: rect (21.4,30.2)-(22.6,30.8) + segitiga discharge; label "P-101" (22, 29.5); REF-EQUIP |
| Rack | 2 garis solid (19,34)-(58,34) & (19,36)-(58,36); diagonal cross-brace tiap 6 m; label "PIPE RACK TOP +4.5" (38, 37); REF-EQUIP |
| Supports | kotak 0.4 m di x=22,28,34,40,46,52,58 pada y 34..36; label "TYP. PIPE SUPPORT" leader ke satu support; REF-SYM |
| V-102 | rect (70,45.2)-(72.5,46.8) + arc; label "V-102 FLARE KO DRUM" (71.25, 48); REF-EQUIP |
| F-101 | lingkaran r=0.3 di (84,46) + lingkaran kecil kedua r=0.15 + garis utara-selatan melalui pusat 1 m; label "F-101 FLARE STACK H=12 m" (84, 49.5); exclusion: lingkaran **r=13 m** dashed center (84,46), label "EXCLUSION R=13 m (API 521 — ASSUMED, CONFIRM BY CALC)" di (84, 33) teks 2,0; REF-SYM |
| Road | band 2 garis (8,40)-(92,40) & (8,43)-(92,43) + hatch tengah dash; label "ACCESS ROAD 6 m" (50, 41.5); REF-ROAD |
| T-101 | bund: rect dinding (62,8)-(76,20) tebal 0.3 (gambar 2 rect); tank lingkaran r=3 di (69,14); label "T-101 API 650 D6.0×H6.0" (69, 6.5); REF-EQUIP |
| Crossing OH flare | di (58, 41.5): kotak 1×3 m kosong + label "OVHD CROSSING EL +6.5" (63, 42); REF-SYM |
| Line hop | semicircle r=0.5 m di (44,22) pada PW-1006 (lihat rute); REF-SYM |

### 2.3 Rute pipa (REF-PROC; label REF-TEXT 2,5 mm, panah arrow_r tiap ±15 m dan di tiap BL)
| Line | Polyline (E,N) m | Label |
|---|---|---|
| 100-PF-1001 DN150 | (0,34)→(10.2,34) | "100-PF-1001 DN150 FROM PRODUCTION HEADER" di (5,35) |
| 100-GO-1002 DN100 | (15,35.15)→(15,35)→(50,35) | "100-GO-1002 DN100 SLOPE 1:500" (32,35.6) |
| 100-FL-1005 DN150 | (13,35)→(50,35)→(58,35)→(58,46)→(70,46) | "100-FL-1005 DN150 FLARE HEADER (PSV TAIL + GO-1002) SLOPE 1:500 TO KO DRUM" (54,44) rot sesuai |
| 080-CO-1003 DN80 | (17.8,33.2)→(22,33.2)→(22,30.9) | "080-CO-1003 DN80" (20,34.2) |
| 080-CO-1004 DN80 | (22.8,30.5)→(24,30.5)→(24,34)→(44,34)→(44,16)→(67,16)→(67,17.5)→(67,15.8) | "080-CO-1004 DN80 TO TANK" (34,32.8) & (55,16.8) |
| 050-PW-1006 DN50 | (26,32.85)→(26,22)→(100,22) | "050-PW-1006 DN50 TO PW TREATMENT" (60,22.8) |
| 050-CD-1007 DN50 | (44.5,32.85)→(44.5,6)→(100,6) | "050-CD-1007 DN50 TO CLOSED DRAIN" (60,6.8) |
| Loading (by others) | (69,11)→(69,9.7)→(100,9.7) | "T-101 N3 TO TRUCK LOADING (BY OTHERS)" (80,10.4) |
| PSV-101 tail DN150 | (13,35.15)→(13,36)→(50,36)→(50,35) | "PSV-101 TAIL DN150" (30,36.7) |

BL arrows (bl_arrow arah +X): (100,22), (100,6), (100,9.7); arah −X di (0,34).

### 2.4 Label elevasi (REF-DIM/REF-TEXT, teks 2,2 + leader garis pendek)
"CL +5.000" di rack (30,36.4); "CL +1.200" di PW-1006 (32,22); "CL +1.200"
CD (50,6.6); "EL +6.500 CROSSING" (58,42.8); "RISE TO +6.7 → T-101 N1" (67,18.5).

### 2.5 Legend (box 555,150)-(821,470))
1. PIPE LINE (solid) — semua line label per line-index.
2. FENCE (dashed), ROAD (band), RACK (2 garis + brace).
3. PIPE SUPPORT (kotak), OVHD CROSSING, LINE HOP.
4. EXCLUSION RADIUS (dashed circle).
5. BL ARROW.
Line-index table: salin tabel §4 design basis (7 line + loading), font 2,2.

### 2.6 Notes (di bawah line-index, 2,2, nomori)
1. PLAN SCALE 1:200 @ A1. PLANT GRID 10 m. COORDINATES IN METERS.
2. ELEVATIONS IN METERS FROM PLANT GRADE DATUM ±0.00.
3. PIPING PER ASME B31.3-2022. FLARE SYSTEM PER API STD 521 (7th ed. 2020) & API STD 537 (4th ed. 2024). TANK PER API 650 (13th ed. 2020). SEPARATOR PER API RP 12J (9th ed. 2024).
4. FLARE HEADER SLOPE 1:500 TO KO DRUM — NO POCKETS.
5. EXCLUSION RADIUS 13 m ASSUMED — CONFIRM BY FLARE RADIATION CALC (API 521).
6. TANK BUND CAPACITY ≥110% TANK VOLUME.
7. ROUTE SURVEY & PIPE SUPPORT DESIGN BY OTHERS.
8. SEE P&ID GPF-00-PI-PID-0001 FOR INSTRUMENTATION.

## 3. ISOMETRICS (A3 420×297, NTS — DIMENSION GOVERN)

### 3.1 Transform isometrik (SATU untuk semua iso)
```
UP axis  = ( 0.000, +1.000)   # vertikal ke atas di sheet
E  axis  = (+0.866, -0.500)   # 30° bawah-kanan
N  axis  = (-0.866, -0.500)   # 30° bawah-kiri
sheet_pt = start + k·( E·ΔE + N·ΔN + UP·ΔUP )   # k = skala mm/m per iso
```
Panjang digambar = k × panjang sesungguhnya (m); bila < 12 mm → pakai 12 mm
(NTS) tetapi teks dimensi = nilai sesungguhnya (mm). Teks dim = "43000",
format tanpa satuan + note "ALL DIMENSIONS IN MM".

Triad axes block di kiri-atas tiap iso: 3 panah dari satu titik sepanjang
15 mm + label "N", "E", "UP" (2,5) + kotak "PLAN NORTH →" kecil.

### 3.2 Furniture iso (semua iso sama)
- Border A3 (20,10)-(410,287); title block (215,15)-(410,75): TITLE
  "PIPE ISOMETRIC — <LINE>", DOC NO sesuai, SCALE NTS, DATE 09 OCT 2026,
  dst. sama Plan A §5.
- BOM box (215,80)-(410,180): tabel POS/QTY/DESC/SIZE.
- Notes kiri-bawah (30,20)-(210,75): "1. ALL DIMENSIONS IN MM.
  2. NTS — DIMENSIONS GOVERN. 3. SPEC A1A PER PROJECT SPEC.
  4. FIELD WELDS ▽ (FW). 5. SLOPE PER LINE LIST."
- Flow arrows di tiap segmen (panah kecil searah aliran).

### 3.3 ISO-1 — GPF-00-PI-ISO-0003 — line 100-GO-1002 + 100-FL-1005
Start A di sheet (70, 210), k = 3.5 mm/m.
Vertex (E,N,UP m) berurutan (fitting pada segmen):
```
A (15.0,35.0,4.15)  N2 flange DN100 (gbr flange = 2 tick)
  → UP 0.85       : elbow LR90 (di B)
B (15.0,35.0,5.00)
  → E 35.0        : PV-101 globe+actuator @17 m; GV-141 gate @25 m;
                    FE-141 orifice+FT leader @32 m; TEE+REDUCER DN100/DN150 @50 m
C (50.0,35.0,5.00)
  → E 8.0         : (lanjut DN150)
D (58.0,35.0,5.00)
  → N 11.0        : ROAD CROSSING @40..43 m → label "+6.5"; elbow di E
E (58.0,46.0,6.50→5.00 dgn slope)
  → E 12.5        : elbow di F
F (70.5,46.0,5.00)
  → DN 3.85       : elbow-flange V-102 N1
G (70.5,46.0,1.15) V-102 INLET FLANGE
```
Tee branch di C: stub 0.4 m ke arah N + cap + label "BRANCH: PSV-101 TAIL
100-FL-1005 — SEE P&ID". FW marks di: N2, C (field joint reducer), E, F, G.
Dimensi teks (mm): 850, 35000, 8000, 11000, 12500, 3850.
Label line: "100-GO-1002 DN100 → 100-FL-1005 DN150".
BOM: 1× elbow LR90 DN100; 4× elbow LR90 DN150; 1× globe DN100 w/ actuator
(PV-101); 1× gate DN150 (GV-141); 1× orifice assy DN100 (FE-141);
1× tee DN150×150×150 + reducer DN100×150; 2× flange DN100 + 2× flange DN150 (weld-neck).

### 3.4 ISO-2 — GPF-00-PI-ISO-0004 — line 080-CO-1003
Start A di sheet (80, 200), k = 20 mm/m.
```
A (17.8,33.2,2.20) N3 flange DN80
  → E 4.2   : GV-101 gate @1.7 m; ST-101 Y-strainer @3.3 m
B (22.0,33.2,2.20)
  → DN 1.6  : reducer DN80×DN65 @ +1.0 m; pump suction flange DN65
C (22.0,30.9,0.60) P-101 SUCTION FLANGE
```
Dims (mm): 4200, 1600. FW di A & C. Elbow LR90 DN80 ×1 (di B).
BOM: 1× elbow DN80; 1× gate DN80; 1× Y-strainer DN80; 1× red DN80×65;
2× flange DN80.

### 3.5 ISO-3 — GPF-00-PI-ISO-0005 — line 080-CO-1004
Start A di sheet (60, 220), k = 2.5 mm/m.
```
A (22.8,30.5,0.80) P-101 DISCHARGE FLANGE DN65
  → E 1.2   : CV-101 check @0.4; GV-102 gate @0.9; red DN65×80 @1.1
B (24.0,30.5,0.80)
  → UP 4.2
C (24.0,30.5,5.00)
  → N 3.5   : elbow di C dan D
D (24.0,34.0,5.00)
  → E 20.0  : FE-142 orifice @10 m (34,34)
E (44.0,34.0,5.00)
  → DN 3.8
F (44.0,16.0,1.20)
  → E 23.0  : LV-121 globe+actuator @4 m (48,16); GV-103 gate @21 m (65,16)
G (67.0,16.0,1.20)
  → N 1.5   : elbow di G dan H
H (67.0,17.5,1.20)
  → UP 5.5
I (67.0,17.5,6.70)
  → N 1.7   : elbow di I dan J
J (67.0,15.8,6.70)
  → DN 0.5  : elbow-flange T-101 N1
K (67.0,15.8,6.20) T-101 ROOF NOZZLE N1
```
Dims (mm): 1200, 4200, 3500, 20000, 3800, 23000, 1500, 5500, 1700, 500.
FW di: A, E, F, H, K. Elbows LR90 DN80 ×8. Note tambahan: "SUPPORT RISER
H–I FROM TANK SHELL BRACKET (BY OTHERS)".
BOM: 8× elbow LR90 DN80; 1× check DN80; 2× gate DN80; 1× globe DN80
w/ actuator (LV-121); 1× orifice assy DN80 (FE-142); 1× red DN65×80;
flange WN DN65 ×1, DN80 ×3.

### 3.6 Simbol iso (REF-SYM)
- Pipe run: garis solid tunggal sepanjang sumbu transform.
- Elbow LR90: arc r=6 mm di vertex (arah belok bebas asal mulus).
- Flange: 2 garis tegak lurus pipe, panjang 6 mm, jarak 1,5 mm.
- Gate: bowtie 10×7 + batang; Globe: bowtie + titik; Check: bowtie + arc;
  semua diorientasikan sepanjang arah segmen (rotasi manual via trigonometri
  sederhana — boleh simbol axis-aligned di titik nearest-vertex bila sulit;
  catat sebagai deviasi minor).
- FW: lingkaran r=1.2 + garis leader 6 mm + text "FW" 2,0.
- Dimensi (REF-DIM): extension line 5 mm dari titik, dim line dengan
  panah runcing 3×1 mm di kedua ujung, teks dim di tengah offset 4 mm
  (rotasi mengikuti arah segmen).
- FT leader: garis tipis 8 mm dari orifice + bubble kecil Ø10 "FT-14x".

## 4. VALIDASI PER FILE (WAJIB)

1. `built ... .dxf` exit 0.
2. `validate_dxf_file` → 0 error.
3. Layer ⊆ daftar resmi; entity count per layer > 0 (kecuali REF-HATCH/
   REF-SIG/REF-GRID boleh 0 pada iso bila tak dipakai).
4. BBox semua entity dalam border masing-masing sheet.
5. Manifest: jumlah vertex iso sesuai tabel (laporkan jumlah LINE per layer
   sebagai bukti); plan: jumlah polyline bend = jumlah rute.
6. Snapshot PNG per file.
7. Viewer URL per file.

## 4a. CHECKLIST VERIFIKASI VISUAL (per PNG)

1. Rute pipa menyambung mulus antar segmen (tidak ada gap/putus aneh).
2. Label line tidak menimpa garis/objek hingga tak terbaca.
3. Tank, bund, flare + exclusion circle, road, rack, support terlihat & proporsional.
4. Iso: sumbu N/E/UP triad ada; dimensi terbaca di tiap segmen; simbol valve
   berada di jalur pipa; FW marks terlihat.
5. Title block & BOM berada dalam kotak, tidak keluar border.
6. Tidak ada geometri di luar border.

## 5. FORMAT LAPORAN BALIK
Sama dengan Plan A §9, per file (4 file drawing).
