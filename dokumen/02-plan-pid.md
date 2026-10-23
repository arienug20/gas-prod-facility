# PLAN EKSEKUSI A — P&ID 3-PHASE SEPARATOR V-101 (untuk subagent glm-5.3-flash)

Dokumen : GPF-00-PI-PID-0001, Rev A0
Input   : `dokumen/01-design-basis.md` (WAJIB dibaca dulu — semua tag/line dari sana)
Output  : `cad/pid_v101.py` → `cad/pid_v101.dxf` → `cad/pid_v101.png`

## 0. URUTAN KERJA (IKUTI PERSIS)

1. Baca `~/.agents/skills/dxf/SKILL.md` dan `~/.agents/skills/dxf/references/generator-templates.md`.
2. Baca `dokumen/01-design-basis.md` penuh.
3. Tulis `cad/pid_v101.py` sesuai manifest di bawah.
4. Build: `python cad/pid_v101.py` dari `~/gas-prod-facility` (lihat §1).
5. Validasi post-hoc + hitungan manifest (§7).
6. Snapshot PNG (§1).
7. **VERIFIKASI VISUAL (WAJIB)**: baca `cad/pid_v101.png` dengan tool `read`
   (kamu subagent dengan kemampuan baca gambar). Cek visual per checklist
   §8a. Bila ada temuan: perbaiki koordinat/kode, rebuild, snapshot ulang.
   Maksimum 3 iterasi; temuan yang tersisa dicatat di laporan.
8. Laporkan sesuai §9.

## 1. LINGKUNGAN & PERINTAH

Semua perintah dari direktori `~/gas-prod-facility`:

```bash
PY="uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.19 python"
CG="uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.19 cadgen"
$PY cad/pid_v101.py                                  # build (harus: built ... .dxf)
$CG dxf snapshot cad/pid_v101.dxf cad/pid_v101.png --appearance light
```

## 2. ATURAN TEKNIS WAJIB (PELANGGARAN = BUILD GAGAL / REWORK)

1. **Layer**: semua nama layer HARUS mengandung token `REF` atau `TEXT`
   (klasifikasi token utuh cadgen: ref/reference/text/notes/label = open OK).
   Daftar layer resmi (hanya ini): `REF-FRAME, REF-TITLE, REF-EQUIP,
   REF-PROC, REF-SYM, REF-SIG, REF-SIGP, REF-HATCH, REF-TEXT`.
2. Semua geometri terbuka (garis, arc) dilarang duplikat persis pada layer
   yang sama (cadgen menolak duplikat). Jangan pernah menggambar segmen
   sama dua kali di layer sama.
3. Teks = outline `bd.Text(...)`. DILARANG entity TEXT DXF.
4. Jangan sentuh atribut `bd.*` di level modul (konstanta angka biasa boleh);
   semua konstruksi geometri di dalam fungsi (hindari kernel import warning).
5. Fungsi `@dxf` TANPA parameter, return `dict {layer: Compound}`.
6. Semua koordinat mm pada lembar A1 (841×594), origin kiri-bawah lembar.
   Tidak ada entity di luar border (20,10)-(831,584).
7. Ukuran teks: tag 2,2; label line 2,5; judul note 3,5; title block 2,5–5,0.
8. Jangan ubah design basis; jika ada konflik manifest vs design basis,
   design basis menang dan catat di laporan.

## 3. IDIOM KODE (TERVERIFIKASI — PAKAI PERSIS)

```python
from cadgen import build123d as bd
from cadgen import dxf

def line(x1, y1, x2, y2):
    return bd.Edge.make_line(bd.Vector(x1, y1, 0), bd.Vector(x2, y2, 0))

def circle(x, y, r):
    return bd.Location((x, y, 0)) * bd.Edge.make_circle(r)

def arc(x, y, r, a1, a2):
    return bd.Location((x, y, 0)) * bd.Edge.make_circle(
        r, start_angle=a1, end_angle=a2)

def dashed(x1, y1, x2, y2, dash=4.0, gap=1.6):
    import math
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy); ux, uy = dx / L, dy / L
    out, t = [], 0.0
    while t < L:
        t2 = min(t + dash, L)
        out.append(line(x1 + ux * t, y1 + uy * t, x1 + ux * t2, y1 + uy * t2))
        t = t2 + gap
    return out

def text(t, x, y, size=2.5, rot=0.0):
    with bd.BuildSketch(bd.Location((x, y, 0))) as sk:
        bd.Text(t, font_size=size, rotation=rot,
                align=(bd.Align.CENTER, bd.Align.CENTER))
    return sk.sketch

def comp(items):  # items: list of shapes/sketches
    return bd.Compound.make_composite(items)
```

(Nama API terverifikasi: `make_composite`.)

Helper simbol (buat semua, pakai berulang):

```python
BUBBLE_R = 6.0

def bubble(top, bot, cx, cy):        # field instrument, ISA-5.1
    return [circle(cx, cy, BUBBLE_R),
            text(top, cx, cy + 1.8, 2.2), text(bot, cx, cy - 1.9, 2.2)]

def dcs(top, bot, cx, cy):           # shared display (kotak+lingkaran+garis)
    return [line(cx-8, cy-8, cx+8, cy-8), line(cx+8, cy-8, cx+8, cy+8),
            line(cx+8, cy+8, cx-8, cy+8), line(cx-8, cy+8, cx-8, cy-8),
            circle(cx, cy, BUBBLE_R),
            line(cx-6, cy, cx+6, cy),
            text(top, cx, cy + 1.8, 2.2), text(bot, cx, cy - 1.9, 2.2)]

def esd_block(cx, cy):               # SIS logic solver (kotak+diamond)
    return [line(cx-10, cy-10, cx+10, cy-10), line(cx+10, cy-10, cx+10, cy+10),
            line(cx+10, cy+10, cx-10, cy+10), line(cx-10, cy+10, cx-10, cy-10),
            line(cx-6, cy, cx, cy+6), line(cx, cy+6, cx+6, cy),
            line(cx+6, cy, cx, cy-6), line(cx, cy-6, cx-6, cy),
            text("ESD", cx, cy + 3.5, 2.0), text("1", cx, cy - 3.5, 2.0)]

def bowtie(cx, cy, w=12.0, h=8.0):   # badan valve umum pada garis horizontal
    return [line(cx - w/2, cy - h/2, cx, cy), line(cx, cy, cx - w/2, cy + h/2),
            line(cx + w/2, cy - h/2, cx, cy), line(cx, cy, cx + w/2, cy + h/2),
            line(cx - w/2, cy - h/2, cx - w/2, cy + h/2),
            line(cx + w/2, cy - h/2, cx + w/2, cy + h/2)]

def valve_gate(cx, cy, tag, extra=""):
    return bowtie(cx, cy) + [line(cx, cy - h_ := 5.5, cx, cy + h_),
            text(tag, cx, cy + 9, 2.2), text(extra, cx, cy - 9, 2.2)]

def valve_globe(cx, cy, tag, extra=""):
    return bowtie(cx, cy) + [circle(cx, cy, 1.6),
            text(tag, cx, cy + 9, 2.2), text(extra, cx, cy - 9, 2.2)]

def valve_check(cx, cy, tag):
    return bowtie(cx, cy, 10.0, 7.0) + [arc(cx, cy, 3.0, 200, 340),
            text(tag, cx, cy + 8, 2.2)]

def actuator(cx, cy):                # dome di atas valve (di cy = titik puncak batang)
    return [arc(cx, cy, 4.0, 0, 180),
            line(cx - 4, cy, cx - 4, cy + 3), line(cx + 4, cy, cx + 4, cy + 3),
            arc(cx, cy + 3, 4.0, 180, 360)]

def psv(cx, cy):                     # angle valve + spring, inlet dari bawah, outlet ke kanan
    return [line(cx, cy - 6, cx, cy),                    # inlet riser
            line(cx - 4, cy, cx, cy - 3), line(cx, cy - 3, cx + 4, cy),
            line(cx + 4, cy, cx, cy + 3), line(cx, cy + 3, cx - 4, cy),
            line(cx, cy, cx + 6, cy),                    # outlet horizontal
            line(cx, cy, cx, cy + 6),                    # stem
            line(cx - 3, cy + 6, cx + 3, cy + 9), line(cx + 3, cy + 9, cx - 3, cy + 12),
            line(cx - 3, cy + 12, cx + 3, cy + 15)]

def orifice(cx, cy):                 # flange orifice pada garis horizontal
    return [line(cx - 1.5, cy - 5, cx - 1.5, cy + 5),
            line(cx + 1.5, cy - 5, cx + 1.5, cy + 5)]

def pump(cx, cy):                    # discharge ke kanan
    return [circle(cx, cy, 6.0),
            line(cx + 6, cy - 5, cx + 6, cy + 5),        # casing edge
            line(cx, cy - 6, cx + 6, cy), line(cx + 6, cy, cx, cy + 6),
            line(cx, cy - 6, cx, cy + 6),
            line(cx - 8, cy - 8, cx + 8, cy - 8)]        # baseplate

def level_cage(x, ytop, h=60.0, w=8.0):   # external cage; ytop = y bottom vessel
    return [line(x, ytop, x, ytop - h), line(x + w, ytop, x + w, ytop - h),
            line(x, ytop - h, x + w, ytop - h)]

def lgauge(x, ytop, h=60.0):              # level gauge sempit
    return [line(x, ytop, x, ytop - h), line(x + 4, ytop, x + 4, ytop - h),
            line(x, ytop - h, x + 4, ytop - h)]

def arrow_r(x, y):                    # panah arah aliran ke kanan pada garis
    return [line(x, y, x - 4, y + 2), line(x, y, x - 4, y - 2)]

def bl_arrow(x, y, label, dx=1):      # battery limit arrow + label, arah +x
    return [line(x, y - 3.5, x, y + 3.5), line(x, y - 3.5, x + 8, y),
            line(x + 8, y, x, y + 3.5),
            text(label, x + 4 + 32 * dx, y + 6, 2.5)]

def pneu_ticks(x1, y1, x2, y2, spacing=8.0):  # "//" pada garis pneumatic
    import math
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    px, py = -uy, ux                    # normal
    out, t = [], spacing / 2
    while t < L:
        mx, my = x1 + ux * t, y1 + uy * t
        out += [line(mx - px * 1.2 - ux * 1.2, my - py * 1.2 - uy * 1.2,
                     mx + px * 1.2 - ux * 0.0, my + py * 1.2 - uy * 0.0),
                line(mx + ux * 1.2 - px * 1.2, my + uy * 1.2 - py * 1.2,
                     mx + ux * 1.2 + px * 1.2, my + uy * 1.2 + py * 1.2)]
        t += spacing
    return out
```

(Sesuaikan detail kecil helper bila perlu, tetap bentuk simbol ISA.)

## 4. SHEET & FURNITURE (A1 841×594)

| Item | Geometri |
|---|---|
| Border | rect (20,10)-(831,584), garis ganda luar (0,0)-(841,594) |
| Grid ref | kolom 1–8 (x tiap 101,25 dari 20 ke 831, teks 2,5 di atas & bawah border), baris A–F (y tiap 95,67 dari 10 ke 584, teks di kiri & kanan) |
| Title block | rect (651,15)-(827,105); field: lihat §5 |
| Legend | rect (651,120)-(827,420), isi lihat §6 |
| Notes | rect (651,435)-(827,580), isi lihat §6 |
| Diagram area | (30,30)-(640,575) — semua manifest §7 di dalam ini |

## 5. TITLE BLOCK (ISO 7200 — field & teks)

Baris (y): 
- (651..827, 88..105): "GAS PRODUCTION FACILITY — ONSHORE FIELD" (4,0)
- (651..827, 71..88): "PIPING & INSTRUMENTATION DIAGRAM" (3,5) / "3-PHASE PRODUCTION SEPARATOR V-101" (3,5)
- (651..827, 15..71): grid field: DOC NO GPF-00-PI-PID-0001 | REV A0 (ISSUED FOR REVIEW) | SCALE NTS | DATE 09 OCT 2026 | DRAWN GLM-5.3-FLASH | CHECKED PM (AI) | APPROVED — | SHEET 1 OF 1 | UNITS mm
- Rev table kecil di (651,105)-(827,120): kolom REV/DESC/DATE, isi "A0 | ISSUED FOR REVIEW | 09 OCT 26"

## 6. LEGEND & NOTES

Legend (conten dalam box, teks 2,5, sampel garis panjang 25 mm):
1. PROCESS LINE — solid.
2. ELECTRIC SIGNAL — dashed (contoh helper dashed()).
3. PNEUMATIC SIGNAL — solid + "//" ticks.
4. Bubble kosong — FIELD INSTRUMENT.
5. Kotak+lingkaran — DCS SHARED DISPLAY/CONTROL.
6. Kotak+diamond — SIS LOGIC SOLVER (ESD).
7. Valve simbol: gate/globe/check/PSV + "FC = FAIL CLOSED".
8. Orifice flange simbol.

Notes (nomori 1..9, persis):
1. SCHEMATIC — NOT TO SCALE. NO ORIENTATION IMPLIED.
2. LINE DESIGNATION PER LINE INDEX. PIPE SPEC A1A (CS, RF#150).
3. INSTRUMENT SYMBOLS & TAGGING PER ANSI/ISA-5.1-2024. DIAGRAM CONTENT PER ISO 15519-2:2015.
4. ESD-1 (SIS) CAUSE & EFFECT: PT-102 PSHH/PSLL & LT-122 LSHH/LSLL → CLOSE SDV-101, CLOSE LV-121, TRIP P-101. LT-132 LSHH/LSLL → CLOSE LV-131. SEE C&E CHART.
5. PSV-101 SET PRESSURE = V-101 MAWP PER VESSEL DATASHEET. RELIEF SYSTEM PER API STD 521.
6. ALARMS PAH/PAL/LAH/LAL IMPLEMENTED IN DCS FROM PT-101, LT-121, LT-131.
7. FLARE HEADER 100-FL-1005 SLOPE 1:500 TO KO DRUM — NO POCKETS.
8. SIZES/DIMENSIONS FOR CLARITY ONLY — REFER TO LINE INDEX.
9. EQUIPMENT DESIGN: V-101 PER API RP 12J; T-101 PER API 650.

## 7. MANIFEST DIAGRAM (KOORDINAT FINAL — GAMBAR SEMUA)

### 7.1 Vessel & internals (REF-EQUIP)
| Item | Geometri |
|---|---|
| Shell | rect x 110–460, y 280–370 |
| Head kiri | arc 3-titik (110,280)-(101.5,325)-(110,370) |
| Head kanan | arc 3-titik (460,280)-(468.5,325)-(460,370) |
| Weir | garis x=330, y 280→345 + text "WEIR" vertikal (330, 362) rot 90 |
| Inlet diverter | garis miring (125,300)-(132,340) + (132,300)-(125,340) (pelat V) |
| Plate coalescer | rect (170,300)-(250,350) + hatch 45° spacing 3 (REF-HATCH) + text "PLATE COALESCER" (210,292) 2,2 |
| Demister | rect (370,335)-(430,365) + hatch 45° spacing 3 + text "DEMISTER" (400,328) 2,2 |
| Label | text "V-101" (180, 385) 4,0; "3-PHASE SEPARATOR" (180, 378) 2,5; "HORIZONTAL, ID 2300 X 7600" (180, 372.5) 2,2 |
| Nozzle tags | N1 (100,325) text "N1 DN150" (100,312) 2,2; N2 (400,375) "N2 DN100" (400,383) kanan-atas; N5 (150,375) "N5 DN100" (150,383); N3 (475,310) "N3 DN80" (480,300); N4 (260,275)→text (260,268) "N4 DN50"; N6 (445,275)→text (445,268) "N6 DN50" |

### 7.2 Process lines (REF-PROC) + label (REF-TEXT)
| Line | Rute & elemen |
|---|---|
| PF-1001 inlet | bl_arrow label "FROM PRODUCTION HEADER\n100-PF-1001 DN150" di (35,325); garis (43,325)-(100,325); SDV-101: valve_gate (58,325) "SDV-101" extra "FC" + actuator (58,333) + stem line (58,329)-(58,333); solenoid box 5×5 di (64,329) dgn text "S"; arrow_r (90,325) |
| PSV branch | riser (150,370)-(150,424); psv(150,430); garis (156,430)-(627,430); bl_arrow (627,430) "TO FLARE HEADER 100-FL-1005 DN150"; label line (300,436) 2,5 "100-FL-1005 DN150 (PSV-101 TAIL)" |
| GO-1002 gas | riser (400,370)-(400,455); garis (400,455)-(627,455); valve_globe+actuator (430,455) "PV-101"/"FC"; valve_gate (468,455) "GV-141"; orifice (508,455); bl_arrow (627,455) "TO FLARE HEADER 100-FL-1005 DN150"; arrow_r (420,455), arrow_r (540,455); label (300,449) "100-GO-1002 DN100"; reducer simbol trapesium kecil di (530,455) + text "DN100/DN150" (530,463) 2,0 |
| CO-1003 suction | garis (470,310)-(540,310) + (540,310)-(540,118); valve_gate (540,240) "GV-101"; strainer: rect 8×8 (540,200) + diagonal + text "ST-101" (552,200) 2,2; pump(540,112); label vertikal (552,290) rot 90 "080-CO-1003 DN80"; arrow_r (490,310) |
| CO-1004 discharge | garis (546,112)-(627,112); valve_check (560,112) "CV-101"; valve_gate (578,112) "GV-102"; valve_globe+actuator (598,112) "LV-121"/"FC"; orifice (616,112); bl_arrow (627,112) "TO TANK T-101 080-CO-1004 DN80"; label (590,98) 2,5 |
| PW-1006 water | riser (260,280)-(260,245); garis (260,245)-(627,245); valve_globe+actuator (330,245) "LV-131"/"FC"; orifice (372,245); bl_arrow (627,245) "TO PRODUCED WATER TREAT 050-PW-1006 DN50"; label (300,239) "050-PW-1006 DN50" |
| CD-1007 drain | riser (445,280)-(445,215); garis (445,215)-(627,215); valve_gate (470,215) "GV-104" extra "NC"; bl_arrow (627,215) "TO CLOSED DRAIN 050-CD-1007 DN50"; label (470,229) 2,2 "NORMALLY CLOSED" |

### 7.3 Level instruments (REF-SYM + REF-TEXT)
Semua cage: `level_cage(x, 278)` (ytop 278 = 2 mm di bawah shell) h=60:
| Tag | x cage | Bubble (cx, cy=185) | Keterangan |
|---|---|---|---|
| LT-121 | 380 | (380,185) "LT"/"121" | oil side |
| LT-122 | 400 | (400,185) "LT"/"122" | SIS |
| LG-123 | 420 | lgauge(420,278); text "LG-123" (422,205) | oil |
| LT-131 | 200 | (200,185) "LT"/"131" | water/int |
| LT-132 | 220 | (220,185) "LT"/"132" | SIS |
| LG-133 | 240 | lgauge(240,278); text "LG-133" (242,205) | interface |

### 7.4 Instrumen atas vessel (REF-SYM + REF-TEXT)
| Tag | Posisi | Bentuk |
|---|---|---|
| PT-101 | riser (200,370)-(200,408); bubble (200,420) "PT"/"101" | field |
| TT-111 | riser (220,370)-(220,408); bubble (220,420) "TT"/"111"; text "TW" (226,410) 2,0 | field |
| TI-112 | riser (245,370)-(245,408); bubble (245,420) "TI"/"112" | field |
| PT-102 | riser (300,370)-(300,408); bubble (300,420) "PT"/"102" | field SIS |
| PI-103 | riser (350,370)-(350,408); bubble (350,420) "PI"/"103" | gauge |
| FT-141 | bubble (508,492) "FT"/"141" + dashed drop (508,486)-(508,460) | field |
| FT-142 | bubble (616,148) "FT"/"142" + dashed drop (616,142)-(616,118) | field |
| FT-143 | bubble (372,270) "FT"/"143" + dashed (372,264)-(372,250) | field |

### 7.5 DCS & ESD (REF-SYM + REF-TEXT)
| Tag | Posisi (cx,cy) | Bentuk |
|---|---|---|
| PIC-101 | (430,530) | dcs "PIC"/"101" |
| TI-111 | (468,530) | dcs "TI"/"111" |
| LIC-121 | (506,530) | dcs "LIC"/"121" |
| LIC-131 | (544,530) | dcs "LIC"/"131" |
| FI-141 | (582,530) | dcs "FI"/"141" |
| FI-142 | (430,560) | dcs "FI"/"142" |
| FI-143 | (468,560) | dcs "FI"/"143" |
| ESD-1 | (70,530) | esd_block |

### 7.6 Signal lines
Listrik (REF-SIG, dashed):
- PT-101 (200,426)→(200,500)→(424,500)→(424,522) [ke PIC-101]
- TT-111 (220,426)→(220,490)→(462,490)→(462,522)
- LT-121 (380,191)→(380,60)→(502,60)→(502,522)  [bus bawah]
- LT-131 (200,191)→(200,60)→gabung bus (naik di x=502)
- FT-141 (514,492)→(514,510)→(578,510)→(578,522)
- FT-142 (616,154)→(616,170)→(430,170)→(430,522) [sisi kiri DCS row via x 430]
- FT-143 (372,276)→(372,300)?? — HINDARI vessel: (372,264 naik dilarang) → rute: (372,258)→(360,258)…SIMPULAN: rute dashed FT-143: turun (372,258)-(372,60) gabung bus.
Pneumatic (REF-SIGP, solid + ticks):
- FY-101 box 8×8 di (430,478) text "FY"/"101"; dashed dari PIC-101 (426,522)-(430,482)?? → GANTI: dashed (430,522)-(430,482) LALU pneumatic (430,474)-(430,461) ticks + ke actuator PV-101.
- FY-121 box (598,146); dashed dari bus x502: (502,60)-(598,60)-(598,142); pneumatic (598,150)-(598,121).
- FY-131 box (330,272)→ di bawah vessel: (330,262)-(330,253) ticks ke actuator LV-131; dashed LIC-131 (544,522)-(544,480)-(334,480)-(334,266). SIMPLIFIKASI BOLEH: dashed (544,522)-(544,266) vertikal melalui area kosong x=544? ADA garis gas y=455 & PV-101 di (430..) — x 544 melewati garis GO-1002 (y455) → crossing diperbolehkan.
- SY-101: dashed dari ESD-1 (70,522)-(70,420)-(58,420)-(58,336) [ke solenoid SDV]; label "ESD SIGNAL" (100,414) 2,0.
- dashed ESD-1 → LV-121 solenoid: (80,522)-(80,180)-(594,180)-(594,124) label "CLOSE".
- dashed ESD-1 → P-101 trip: (80,522)-(80,140)-(534,140)-(534,118) label "TRIP".

## 8. CHECKLIST BUILD & VALIDASI (WAJIB SEMUA LOLOS)

1. `built ... pid_v101.dxf` exit 0.
2. Post-hoc: `validate_dxf_file` → 0 error.
3. ezdxf: layer set == daftar §2.1; per-layer entity count > 0 kecuali REF-HATCH boleh 0 tidak (harus >0).
4. Extent: semua entity dalam (20,10)-(831,584) — hitung bbox dari entity (bukan header EXTMIN/MAX).
5. Manifest count: jumlah lingkaran bubble Ø12 pada REF-SYM = 3 (field PT/TT/TI/FT…) — hitung: CIRCLE r=6 → jumlah = 11 field bubble + 7 dcs circle + 1 pump circle + gauges… KONSEKUENSI: cukup laporkan jumlah CIRCLE per radius per layer sebagai bukti.
6. Snapshot PNG terbuat.
7. Buka viewer: `$CG viewer --host 127.0.0.1 --json --detach` → catat URL `?file=`.

## 8a. CHECKLIST VERIFIKASI VISUAL (via PNG)

Baca PNG dengan tool `read`, periksa:
1. Tidak ada teks/simbol bertumpuk hingga tak terbaca (overlap parah).
2. Semua bubble instrumen terlihat utuh (lingkaran tidak terpotong garis proses).
3. Vessel + internals (weir, demister, coalescer hatch) terlihat.
4. Semua label line & tag nozzle ada dan dekat objeknya.
5. Title block, legend, notes berada DI DALAM kotaknya, tidak keluar border.
6. Panah aliran & BL arrow ada di semua line.
7. Garis dashed (signal) terlihat putus-putus, bukan solid.
8. Tidak ada geometri nyasar di luar border / di zona title block.

## 9. FORMAT LAPORAN BALIK

- File dibuat + ukuran, stdout build.
- Hasil tiap check §8 (angka aktual).
- Deviasi dari plan (atau "TIDAK ADA").
- Kendala & solusi.
Jangan menghapus/mengubah file lain.
