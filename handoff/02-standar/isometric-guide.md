# Reference — Piping Isometric Drawing Guide (`iso_common.py` API & ISO 6412-2 / ISO 10628-2 / FNKT-10 Standard)

Panduan ini adalah referensi teknis lengkap untuk membuat atau merevisi gambar **Piping Isometric** menggunakan library standar perusahaan `iso_common.py` dan post-processor `apply_text.py`.

---

## 1. Prinsip Utama & Larangan

1. **True Piping Isometric Projection (30° / 150° / 90°)**:
   - `+E` (East): `EX = (+cos 30°, +sin 30°) = (+0.8660254, +0.5)` → miring **+30° kanan-atas**
   - `-E` (West): `WX = (-cos 30°, -sin 30°) = (-0.8660254, -0.5)` → miring **-150° kiri-bawah**
   - `+N` (North): `NX = (-cos 30°, +sin 30°) = (-0.8660254, +0.5)` → miring **+150° kiri-atas**
   - `-N` (South): `SX = (+cos 30°, -sin 30°) = (+0.8660254, -0.5)` → miring **-30° kanan-bawah**
   - `+UP` / `-DN`: `UX = (0.0, +1.0)` / `DNX = (0.0, -1.0)` → vertikal murni **±90°**
   - **DILARANG** menggambar pipa sejajar sumbu plant secara mendatar `0°`.
2. **Bebas `POLYFACE` (Ukuran File Kecil)**:
   - **DILARANG** menyuntikkan mesh 3D (`POLYFACE`) ke dalam file DXF isometrik.
   - Ukuran target: **90–150 KB** per sheet tunggal, **< 500 KB** untuk multi-sheet DXF.
3. **Kewajiban Rantai Build**:
   ```bash
   PY="uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.21 python"
   CG="uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.21 cadgen"

   $PY cad/<iso_script>.py --force
   $PY cad/apply_text.py cad/<iso_script>.dxf cad/<iso_script>.texts.json
   $CG dxf snapshot cad/<iso_script>.dxf cad/<iso_script>.png --width 2400 --height 1700
   ```

---

## 2. Katalog Simbol ISO (`IsoContext` di `iso_common.py`)

Semua simbol pada `IsoContext` otomatis berotasi sejajar vektor arah pipa `u`:

| Komponen | Standar Acuan | Method di `IsoContext` | Geometri Simbol |
|---|---|---|---|
| **Pipe Run** | ISO 6412-2 | `ctx.add_pipe_run(p1, p2)` | Garis tebal (`REF-PROC`, 0.50 mm), belokan miter tajam (0 `ARC`). |
| **Weld Neck Flange** | ISO 6412-2 §5.3 | `ctx.flange(P, u, half=2.0)` | 2 garis paralel tegak lurus `u` (`±0.45 mm`). |
| **Gate Valve** | ISO 10628-2 / FNKT-10 | `ctx.gate(P, u, L=3.4, W=1.8)` | **Bowtie `▷◁` murni** (tanpa garis atas/bawah agar berbeda dari *Pipe Support*) + 2 tick flange `SOLID`. |
| **Globe / Control Valve** | ISO 10628-2 (4.1.2) / ISA-5.1 | `ctx.globe(P, u, has_actuator=True, act_tag="PV-101")` | **Bowtie `▷◁`** + **bola tengah terisi penuh (`●`, `r=0.65`)** + *stem* + kubah aktuator diafragma setengah lingkaran + 2 tick flange `SOLID`. |
| **Check Valve** | ISO 10628-2 (4.1.6) | `ctx.check_valve(P, u, L=3.4, W=1.8)` | 2 garis tegak ujung + **garis diagonal *flapper*** + **titik engsel `●` (`r=0.45`)** di puncak hulu + **kepala panah `SOLID`** di ujung hilir + 2 tick flange `SOLID`. |
| **Concentric Reducer** | ISO 6412-2 §6.4 | `ctx.reducer(P, u, L=2.6, W1=1.2, W2=2.2)` | **Trapesium konsentris tertutup** (`W1` = lebar ujung hulu, `W2` = lebar ujung hilir) sejajar arah `u`. |
| **Y-Strainer** | ISO 10628-2 | `ctx.strainer(P, u, L=3.6, W=2.0)` | Bodi kotak sejajar pipa + kantong cabang Y miring ke bawah-hilir dengan garis saringan (*mesh*) + 2 tick flange `SOLID`. |
| **Orifice + Transmitter** | ANSI/ISA-5.1 | `ctx.orifice(P, u, half=3.8, tag="FT-141", lead_dir=UX)` | 2 pelat orifice tegak lurus pipa + *lead line* yang berhenti di tepi balon instrumen (`r=3.6 mm`). |
| **Shop / Field Weld** | ISO 6412-2 §5.2 / FNKT-10 | `ctx.sw(P, u, txtoff=(0.0, 3.2))` | **Titik las bulat terisi penuh (`●`, `r=0.8 mm`)** tepat di garis pipa + teks `"SW"`. |
| **Pipe Support** | FNKT-10 `Support 1` | `ctx.pipe_support(P, u, "PS-001", "RESTING", leader_vec=(0,-9), shelf_len=16)` | Kotak tertutup miring sejajar pipa dengan silang diagonal (`☒`) + leader ke rak horizontal + teks 2 baris (`PS-xxx` / `RESTING` atau `GUIDE`). |
| **Flow Arrow** | FNKT-10 | `ctx.flow_arrow(P, u)` | Segitiga `SOLID` terisi penuh menempel pada garis pipa searah aliran `u`. |
| **BOM Part Balloon** | ISO 6412-2 / FNKT-10 | `ctx.part_bubble(P_center, target_pt, item_no)` | Lingkaran `r=1.85 mm` berisi nomor item BOM (`1`..`15`) + leader yang dipotong tepat di tepi lingkaran. |
| **Stacked Flange Bubbles** | FNKT-10 | `ctx.stacked_bubbles(target_pt, dir_vec, [flange, gasket, bolt])` | 3 lingkaran balon berderet rapat untuk rakitan sambungan flange (`Flange + Gasket + Stud Bolt`). |
| **Line Callout** | FNKT-10 | `ctx.line_callout(P_pipe, P_elbow, line_str, bop_str, shelf_len=28)` | Kepala panah `SOLID` pada pipa + leader miring + rak horizontal + teks 2 baris (`LINE NO` & `BOP.EL. +xxxx`). |
| **Continuation Pipe** | FNKT-10 | `ctx.continuation(P_start, u, lines_txt, length=14.0)` | Pipa putus-putus (*dashed*) selepas flange batas + teks 3 baris (`CONT. TO/FROM ...`, `DRW NO. ...`, `SHEET x OF y`). |

---

## 3. Tabel Sudut Dimensi Miring (*Oblique Isometric Extension Lines*)

Gunakan `ctx.dimrec(p1, p2, text, angle, base, oblique=...)` sesuai orientasi segmen pipa:

| Arah Segmen Pipa | Posisi Garis Dimensi (`base`) | `angle` | `oblique` | Arah Garis Ekstensi yang Dihasilkan |
|---|---|---|---|---|
| **Timur (`+E` / `EX`)** | Ditarik ke **bawah** pipa (`(0, -18)`) | `30.0` | `-120.0` | Jatuh vertikal ke bawah (`-90°`) |
| **Timur (`+E` / `EX`)** | Ditarik ke **atas** pipa (`(0, +12)`) | `30.0` | `60.0` | Naik vertikal ke atas (`+90°`) |
| **Utara (`+N` / `NX`)** | Ditarik ke **bawah-kiri** pipa (`(0, -11)`) | `-30.0` | `-60.0` | Jatuh vertikal ke bawah (`-90°`) |
| **Utara (`+N` / `NX`)** | Ditarik ke **atas-kanan** pipa (`(0, +11)`) | `-30.0` | `120.0` | Naik vertikal ke atas (`+90°`) |
| **Vertikal (`+UP` / `UX`)** | Ditarik ke **kiri-bawah** (`mulp(WX, 8.0)`) | `90.0` | `120.0` | Miring sejajar sumbu `WX/EX` (`+30°/-150°`) |

---

## 4. Struktur Template Script Isometrik Baru

```python
from cadgen import dxf
from iso_common import (
    IsoContext, EX, WX, NX, SX, UX, DNX,
    addp, subp, mulp, dashed_line, line
)

CTX = IsoContext()

def build_iso_example(ctx: IsoContext) -> None:
    # 1. Definisikan koordinat titik belok (True Isometric EX, NX, UX)
    A = (60.0, 95.0)
    B = addp(A, mulp(UX, 20.0))
    C = addp(B, mulp(EX, 60.0))

    # 2. Gambar run pipa
    ctx.add_pipe_run(A, B)
    ctx.add_pipe_run(B, C)

    # 3. Tambahkan simbol ISO, Pipe Support, dan Balon BOM
    ctx.flange(A, UX, half=2.2)
    ctx.stacked_bubbles(A, WX, [5, 7, 9])
    ctx.gate(addp(B, mulp(EX, 25.0)), EX)

    # 4. Tambahkan dimensi dengan Oblique Extension Lines
    ctx.dimrec(A, B, "1000", 90.0, addp(A, mulp(WX, 8.0)), oblique=120.0)
    ctx.dimrec(B, C, "5000", 30.0, addp(B, (0.0, -16.0)), oblique=-120.0)

    # 5. Bangun Furniture 3-Kolom FNKT-10
    ctx.build_furniture(
        sheet_no=1, total_sheets=1,
        drw_no="GPF-00-PI-ISO-0001",
        line_no="100-GO-1001 DN100",
        service="PROCESS GAS",
        code="ASME B31.3", pipe_class="A1A",
        design_temp="60 °C", design_press="17.2 BARG",
        op_temp="40 °C", op_press="10.0 BARG",
        bom_items=[...], notes=[...],
    )

@dxf
def iso_example():
    global CTX
    CTX = IsoContext()
    build_iso_example(CTX)
    return CTX.get_layers()

if __name__ == "__main__":
    iso_example()
    iso_example.__cadgen_model__.func()
    CTX.save_manifest("cad/iso_example.texts.json")
```
