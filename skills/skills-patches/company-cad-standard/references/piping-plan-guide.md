# Panduan Engineering 2D Piping Plan & Plot Plan (`plan_common.py`)

**Standar Acuan**: ASME B31.3-2022 (*Process Piping*), API STD 650 13th Ed. 2020 (*Welded Tanks for Oil Storage*), API Spec 12J, 8th Ed. (2008), R2023 (*Oil and Gas Separators*), API STD 521 7th Ed. 2020 (*Pressure-relieving and Depressurizing Systems*), ISO 5457:1999 (*Sizes and layout of drawing sheets*), ISO 7200:2004 (*Data fields in title blocks*) & Company CAD Standard  
**Ukuran Lembar Standar**: ISO A1 (841 × 594 mm)  
**Skala Default**: 1:200 ($1\text{ m} = 5.0\text{ mm}$ di atas kertas)  

Dokumen ini adalah pedoman teknis lengkap bagi *Piping Engineer*, *Layout Designer*, dan subagent AI dalam menyusun gambar **Piping Plan**, **Plot Plan**, dan **Piping Arrangement** tampak atas 2D menggunakan library standar perusahaan `plan_common.py` dan post-processor `apply_text.py`.

---

## 1. Filosofi & Transformasi Koordinat Plant $\leftrightarrow$ Sheet

Gambar Piping Plan dan Plot Plan menghubungkan koordinat survei lapangan (Plant Coordinates) dalam satuan **METER** ke tata letak lembar gambar teknik A1 dalam satuan **MILIMETER**:

$$\begin{aligned}
X_{\text{sheet}} &= px_0 + \text{scale} \times E \\
Y_{\text{sheet}} &= py_0 + \text{scale} \times N
\end{aligned}$$

- **Sumbu Timur ($+E$, Easting)**: Membentang horizontal ke kanan ($+X_{\text{sheet}}$).
- **Sumbu Utara ($+N$, Northing)**: Membentang vertikal ke atas ($+Y_{\text{sheet}}$).
- **Elevasi ($EL.$ / $CL$ / $BOP$ / $TOS$)**: Dinyatakan dalam meter terhadap Plant Grade Datum $+0.000\text{ m}$.
- **Konfigurasi Default Lembar A1 (`PlanContext`)**:
  - `px0 = 40.0 mm`: Margin kiri area gambar.
  - `py0 = 40.0 mm`: Margin bawah area gambar.
  - `scale = 5.0 mm/m`: Skala `1:200` (Area plot $100\text{ m} \times 60\text{ m}$ menempati area $500\text{ mm} \times 300\text{ mm}$ di lembar A1).

```python
from plan_common import PlanContext

ctx = PlanContext(px0=40.0, py0=40.0, scale=5.0)
x_mm, y_mm = ctx.P(e=24.5, n=36.0)  # Mengembalikan koordinat mm kertas
e_m, n_m = ctx.inv_P(x_mm, y_mm)    # Mengembalikan koordinat meter plant
```

---

## 2. Aturan Auto-Trimming & Line Break (Zero-Defect Crossing)

Sesuai **Company CAD Standard §2**, garis pipa proses yang saling bersilangan diatur dengan aturan prioritas mutlak:
1. **Major Process Line** (Header produksi, Flare header, garis proses berdiameter lebih besar): **TIDAK PERNAH DI-BREAK** (garis tetap utuh dan menerus).
2. **Minor Process Line** (Cabang drain, utility water, chemical injection, garis berdiameter lebih kecil): **WAJIB DI-BREAK** dengan celah pemotongan **$3.0\text{ mm}$ di atas kertas**.
3. Pada skala `1:200` (`scale = 5.0 mm/m`), celah kertas $3.0\text{ mm}$ setara dengan celah koordinat plant:
   $$\Delta_{\text{plant}} = \frac{3.0\text{ mm}}{5.0\text{ mm/m}} = 0.60\text{ m} \quad (\pm 0.30\text{ m dari titik pusat silang})$$

### Pemakaian `plan_pipe_h` dan `plan_pipe_v`:
Perhatikan: `plan_pipe_h` dan `plan_pipe_v` adalah **method** dari kelas `PlanContext` (bukan fungsi standalone modul). Script drawing WAJIB mengimpor `PlanContext` lalu memanggil `ctx.plan_pipe_h(...)` / `ctx.plan_pipe_v(...)` agar celah terpotong secara matematis dan bebas garis menumpuk (*zero overlapping/floating lines*):

```python
# Pipa horizontal pada Northing 22.0 m, membentang dari E=26.0 ke E=100.0 m.
# Bersilangan dengan pipa major pada Easting 44.0 m -> auto-break 3.0 mm sheet (0.6 m plant):
ctx.plan_pipe_h(n=22.0, e0=26.0, e1=100.0, breaks_e=[44.0])

# Pipa vertikal pada Easting 44.5 m, membentang dari N=32.85 ke N=6.0 m.
# Bersilangan dengan dua pipa major pada Northing 22.0 m dan Northing 16.0 m:
ctx.plan_pipe_v(e=44.5, n0=32.85, n1=6.0, breaks_n=[22.0, 16.0])
```

---

## 3. Katalog Simbol Tampak Atas Perpipaan (`PlanContext`)

| Komponen | Method di `PlanContext` | Karakteristik Geometri & Layer |
|---|---|---|
| **Flow Arrow** | `ctx.flow_arrow_plan(e, n, ang_deg, size_mm=3.2)` | Segitiga `SOLID` terisi penuh menempel di garis pipa (`REF-PROC`). Wajib ada minimal setiap $\pm 15\text{ m}$ atau pada belokan rute. |
| **Elbow 90° Turning UP** | `ctx.elbow_up(e, n, r_mm=1.8)` *(alias: `elbow_90_up`)* | Lingkaran `circle(r=1.8 mm)` + titik tengah `SOLID` ($r=0.5\text{ mm}$) melambangkan pipa yang belok naik tegak lurus ($+Z$). |
| **Elbow 90° Turning DOWN** | `ctx.elbow_dn(e, n, r_mm=1.8, orient_deg=0.0)` *(alias: `elbow_90_dn`)* | Busur `arc(240°)` terbuka ke arah masuknya pipa `orient_deg` + titik tengah `SOLID` melambangkan pipa yang belok turun ($-Z$). |
| **Tee Branch UP / DN** | `ctx.tee_up(e, n)` / `ctx.tee_dn(e, n, orient_deg)` | Simbol sambungan cabang tee vertikal tampak atas. |
| **Gate Valve Plan** | `ctx.plan_valve_gate(e, n, orient="H", w_mm=7.0, h_mm=4.2, tag="GV-101")` | Simbol *bowtie* presisi + 2 garis *tick flange* di kedua ujung + label teks `tag` (`REF-SYM`). |
| **Pipe Support / Anchor** | `ctx.pipe_support_plan(e, n, orient="H", tag="PS-01", stype="ANCHOR")` | Kotak tumpuan sejajar pipa + diagonal cross `X` (untuk `ANCHOR`) atau plat samping (untuk `GUIDE`) + leader miring ke rak teks 2 baris (`tag` / `stype`). |
| **Pipe Rack & Bracing** | `ctx.pipe_rack(e0, e1, n0, n1, bay_m=6.0)` *(alias: `pipe_rack_bay`)* | 2 rel memanjang (`REF-EQUIP`) + balok melintang (*bents*) setiap `bay_m` meter + ikatan angin diagonal selang-seling (*alternating plan bracing*). |
| **North Arrow Plan** | `ctx.north_arrow_plan(x_mm, y_mm, r_mm=10.0)` | Kompas Utara 2D formal: lingkaran + jarum panah berbilah ganda dengan separuh sisi terisi `SOLID` + huruf `"N"` di puncak. |
| **Coordinate Callout** | `ctx.coord_callout(e, n, el_mm=5000, dx_mm=10.0, dy_mm=10.0)` | Titik target `SOLID` pada titik kerja + garis leader + rak horizontal + teks koordinat `N xxxx / E xxxx` dan `EL. +xxxx`. |
| **Matchline** | `ctx.matchline(e0, n0, e1, n1, text_str="MATCHLINE ...")` | Garis putus-putus tebal (`dash=6, gap=2.5`) batas boundary + teks referensi nomor lembar bersambung. |
| **Battery Limit** | `ctx.battery_limit_arrow(e, n, direction=1)` | Simbol panah chevron batas tanggung jawab baterai (*Battery Limit*). |

---

## 4. Tata Letak Lembar A1 & Furniture Standar

Lembar Piping Plan A1 ($841 \times 594\text{ mm}$) distandarkan ke dalam zona-zona berikut:

```
+-------------------------------------------------------------------------------+
|  1   |   2   |   3   |   4   |   5   |   6   |   7   |   8                    |
|A                                                                            A |
|  +-------------------------------------------------------+ +---------------+  |
|  | [REF-ROAD] ACCESS ROAD (North Plot)                   | | [LINE INDEX]  |  |
|B |                                                       | | Tabel nomor   |B |
|  | [REF-EQUIP] V-102 Flare KO Drum   [F-101] Flare Stack | | pipa, ukuran  |  |
|  |                                                       | | DN, asal/tuju |  |
|C | [REF-EQUIP] PIPE RACK (E-W) + PIPE SUPPORTS           | +---------------+C |
|  |                                                       | | [LEGEND]      |  |
|  | [REF-EQUIP] V-101 Separator      [P-101] Pump Skid    | | Simbol pipa,  |  |
|D |                                                       | | valve, tanda  |D |
|  | [REF-EQUIP] T-101 Storage Tank + Bund Wall Hatch      | | batas, acuan  |  |
|  |                                                       | | standar       |  |
|E | [REF-FENCE] Plot Boundary Fence                       | +---------------+E |
|  +-------------------------------------------------------+ | [TITLE BLOCK] |  |
|  | [REF-TEXT] NOTES (1..8) & GRID TICKS A..K, 1..6       | | ISO 7200 + Rev|  |
|F +-------------------------------------------------------+-+---------------+F |
+-------------------------------------------------------------------------------+
```

1. **Area Gambar Proses & Plot (`x = 40..540, y = 40..460`)**:
   - Skala $1:200$ mencakup plot area hingga $100\text{ m} \times 80\text{ m}$.
   - Grid plant diberi penanda *tick* setiap $10\text{ m}$ dengan huruf `A..K` pada sumbu $E$ dan angka `1..6` pada sumbu $N$.
2. **Line Index Box (`x = 555..821, y = 480..580`)**:
   - Kolom: `LINE NO` | `DN` | `FROM — TO` | `VALVES / REMARKS`.
3. **Legend & Notes Box (`x = 555..821, y = 150..470`)**:
   - Berisi contoh simbol garis proses, batas pagar, jalan, rak pipa, tumpuan, dan acuan standar material.
4. **Title Block ISO 7200 & Revision Table (`x = 651..827, y = 15..125`)**:
   - Dilengkapi nomor dokumen proyek, judul, revisi segitiga, tanggal, dan tanda tangan *Drawn / Checked / Approved*.

---

## 5. Standar Lineweight & Layer (`apply_text.py`)

Setiap gambar yang dihasilkan oleh `plan_common.py` wajib diproses melalui `apply_text.py` agar layer memiliki bobot garis (*lineweight*) yang benar saat dicetak maupun dilihat pada CAD viewer:

| Nama Layer | Lineweight | Keterangan Penggunaan |
|---|---|---|
| `REF-PROC` | **0.50 mm** | Jalur pipa proses utama (*Major pipe, headers, riser*) |
| `REF-EQUIP` | 0.35 mm | Shell bejana, nozzle, rel pipe rack, bodi pompa, tangki |
| `REF-FRAME` | 0.35 mm | Garis batas luar kertas dan border gambar ISO 5457 |
| `REF-SYM` | 0.25 mm | Katup gate/globe, pipe support, north arrow, matchline |
| `REF-TITLE` | 0.25 mm | Kotak dan sekat title block ISO 7200 |
| `REF-TEXT` | 0.18 mm | Seluruh teks anotasi MTEXT (font Arial, $0.5 \le h \le 3.0\text{ mm}$) |
| `REF-ROAD` | 0.18 mm | Batas tepi perkerasan jalan akses plot |
| `REF-FENCE` | 0.13 mm | Garis pagar keliling plot (*dashed*) |
| `REF-HATCH` | 0.13 mm | Arsiran dinding tanggul bundwall (sudut 45°) |
| `REF-GRID` | 0.09 mm | Garis tick referensi koordinat plant |
| `REF-DIM` | 0.09 mm | Garis ekstensi dimensi dan leader elevasi |

---

## 6. Template Script Minimal Piping Plan (`drawing_plan.py`)

Berikut struktur standar kode Python untuk membuat drawing Piping Plan baru:

```python
"""PIPING PLAN - SAMPLE DRAWING.
Doc No: GPF-00-PI-PLN-0002 Rev A0.
"""
from __future__ import annotations
from pathlib import Path
from cadgen import dxf
from plan_common import PlanContext, line, circle, rect, dashed, comp

@dxf
def sample_plan():
    ctx = PlanContext(px0=40.0, py0=40.0, scale=5.0)

    # 1. Setup Furnitur Lembar A1
    ctx.setup_a1_frame(
        doc_no="GPF-00-PI-PLN-0002",
        title="PIPING PLAN — SEPARATOR TO FLARE",
        rev="A0",
        scale_str="1:200 @ A1",
        date_str="23 OCT 2026",
    )
    ctx.setup_plant_grid(e_max=100.0, n_max=60.0, step_m=10.0)
    ctx.setup_plot_fence(0.0, 0.0, 100.0, 60.0)
    ctx.setup_road(8.0, 92.0, n_bot=40.0, n_top=43.0)

    # 2. Peralatan Utama (Equipment)
    ctx.horizontal_vessel(e_center=14.0, n_center=34.0, length_m=7.6, diameter_m=2.3, tag="V-101", desc="3-PHASE SEPARATOR")
    ctx.pipe_rack(e0=19.0, e1=58.0, n0=34.0, n1=36.0, bay_m=6.0)
    ctx.storage_tank(e_center=69.0, n_center=14.0, diameter_m=6.0, bund_w_m=14.0, bund_l_m=12.0, tag="T-101", desc="CRUDE STORAGE")

    # 3. Jalur Pipa & Auto-Trimming
    # Line Major (Flare Header)
    ctx.plan_pipe_h(n=35.0, e0=15.0, e1=58.0)
    ctx.elbow_up(e=15.0, n=35.0)
    ctx.flow_arrow_plan(e=33.0, n=35.0, ang_deg=0.0)

    # Line Minor (Water Drain) - terpotong otomatis saat melintasi Easting 44.0
    ctx.plan_pipe_h(n=22.0, e0=26.0, e1=100.0, breaks_e=[44.0])
    ctx.flow_arrow_plan(e=55.0, n=22.0, ang_deg=0.0)

    # 4. Simbol Khusus & Anotasi
    ctx.north_arrow_plan(x_mm=90.0, y_mm=56.0)
    ctx.pipe_support_plan(e=22.0, n=34.0, orient="H", tag="PS-101", stype="ANCHOR")
    ctx.coord_callout(e=14.0, n=34.0, el_mm=3200)

    # 5. Simpan manifest .texts.json dan kembalikan layer dictionary
    return ctx.export_manifest(Path("cad/sample_plan.texts.json"))

if __name__ == "__main__":
    sample_plan()
```

---

## 7. Rantai Eksekusi Build & Quality Assurance (QA)

Setiap script drawing wajib dijalankan dengan urutan perintah berikut:

```bash
PY="uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.21 python"
CG="uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.21 cadgen"

# 1. Jalankan script model cadgen untuk meng-generate geometri DXF murni
$PY cad/sample_plan.py --force

# 2. Jalankan post-processor untuk menginjeksi MTEXT, SOLID, dan memasang lineweight
$PY cad/apply_text.py cad/sample_plan.dxf cad/sample_plan.texts.json

# 3. Verifikasi dengan CAD Linter otomatis (Zero-Defect Audit)
$PY cad/validate_cad_rules.py cad/sample_plan.dxf cad/sample_plan.texts.json --mode plan

# 4. Render snapshot PNG resolusi tinggi untuk visual inspection
$CG dxf snapshot cad/sample_plan.dxf cad/sample_plan.png --width 2400 --height 1700
```
