# HANDOFF — PAKET SERAH TERIMA KEPADA MODEL AI (ANTIGRAVITY / ARGON)

Dibuat : 22 Oct 2026 oleh GLM-5.3-Flash (OpenCode), sesi PM Oil & Gas Surface Facility
Proyek : **GAS PRODUCTION FACILITY — ONSHORE FIELD** (uji coba tooling text-to-cad)
Tujuan : Briefing lengkap agar model lain dapat melanjutkan pekerjaan TANPA kehilangan konteks.

> **CARA PAKAI**: baca dokumen ini berurutan. Semua file pendukung ada di folder
> ini (mandiri). Jika bekerja di mesin yang sama, folder induk proyek adalah
> `/home/arienugraha-rei/gas-prod-facility/` — di sana pula berlaku
> `AGENTS.md` proyek yang otomatis memuat aturan.

---

## 1. RINGKASAN 1 PARAGRAF

Dibangun paket drawing fasilitas produksi gas onshore memakai tooling
**text-to-cad** (cadgen 0.7.21): P&ID separator 3-fasa V-101, piping plan
routing separator→flare+tangki, 3 isometrik, **model 3D STEP**, render
isometrik 3D, dan **DXF multi-sheet format FNKT-10** (viewport isometrik 3D).
Semua drawing mengikuti standar drafting perusahaan (teks MTEXT Arial 0,5–3,
break persilangan, lineweight, flow arrow, valve terorientasi) yang tertanam
PERMANEN di skill. Standar acuan: ANSI/ISA-5.1-2024, ISO 15519-2:2015,
ISO 10628, API RP 12J 9th ed. 2024, ASME B31.3-2022, API 521 7th ed. 2020,
API 537 4th ed. 2024, API 650 13th ed. 2020, ISO 5457/7200/3098/128.

## 2. KRONOLOGI KEPUTUSAN (kenapa keadaannya seperti sekarang)

| # | Keputusan | Alasan |
|---|---|---|
| 1 | Tooling: text-to-cad (`cadgen`) + skill dxf/cad, runtime `uvx --from cadgen==0.7.21` | Permintaan user; uv dkk. sudah terpasang |
| 2 | P&ID/piping plan/iso = **DXF via skill dxf** (bukan DrawIO) | User meminta output CAD sebagai pengujian tooling |
| 3 | Standar perusahaan → **skill overlay `company-cad-standard` + PATCH langsung ke skill dxf terpasang** | User meminta skill dxf diubah langsung; proteksi overwrite via `~/skills-patches/reapply.sh` |
| 4 | **Teks = entity MTEXT** (bukan outline) | Keluhan user: "teks masih garis, bukan MTEXT". Kontrak outline skill dxf (untuk CAM) di-OVERRIDE untuk drawing engineering |
| 5 | Break persilangan (minor gap 3 mm, major utuh), lineweight per layer, flow arrow semua line | Aturan perusahaan (AutoCAD: BREAK/BR) |
| 6 | Gaya isometrik meniru **FNKT-10** (referensi user): **True Piping Isometric** (`+E` = +30° kanan-atas, `+N` = +150° kiri-atas, `+UP` = +90° vertikal; 0 garis pipa datar 0°), dimensi `DIMENSION` asli dengan garis ekstensi miring (*oblique extension lines*), elevasi "BOP.EL. ±xxxx", elbow **miter**, flow arrow segitiga solid, valve + flange tick terotasi sejajar run, balon nomor part BOM (`part_bubble` + `stacked_bubbles`), dan Pipe Support (`PS-xxx RESTING/GUIDE`) | Evaluasi & koreksi PM (Round A5) atas proyeksi viewport `(1, -1, 1)` referensi FNKT-10 |
| 7 | User: "masih XY belum murni 3D" → dibuat **model 3D STEP + render isometrik dari kamera 3D** | DXF tak dapat ditulisi 3DSOLID/ACIS (kontrak ezdxf); jalur benar: STEP 3D + render |
| 8 | User: "hapus polyface, ukuran file kecil, betul-betul sesuai isometrik" → **dihapus seluruh `POLYFACE` mesh DXF**; `GPF-00-PI-ISO-0007 SHT 1 - 3.dxf` dibangun ulang dengan vektor 2D True Isometric + furniture 3 kolom penuh FNKT-10 (**477,9 KB**, turun 98,4% dari 30,4 MB) | Isometrik perpipaan adalah gambar kerja berdimensi vektor 2D murni, bukan mesh 3D |

## 3. STATUS DELIVERABLE (semua valid, QA lolos)

| Deliverable | Dok. No | REV | File (folder `03-drawing/`; asli di `~/gas-prod-facility/cad/`) |
|---|---|---|---|
| P&ID V-101 (A1) | GPF-00-PI-PID-0001 | A2 | `pid_v101.dxf` + png |
| Piping plan 1:200 (A1) | GPF-00-PI-PLN-0002 | A2 | `routing_plan.dxf` + png |
| Iso gas→flare (A3) | GPF-00-PI-ISO-0003 | **A5** | `iso_go1002.dxf` (**108,5 KB**) + png |
| Iso suction pump (A3) | GPF-00-PI-ISO-0004 | **A5** | `iso_co1003.dxf` (**92,4 KB**) + png |
| Iso discharge→tank (A3) | GPF-00-PI-ISO-0005 | **A5** | `iso_co1004.dxf` (**123,9 KB**) + png |
| Multi-sheet format FNKT | GPF-00-PI-ISO-0007 | **A5** | `GPF-00-PI-ISO-0007 SHT 1 - 3.dxf` (**477,9 KB**, 0 `POLYFACE`) + png |
| Model 3D (folder `04-model-3d/`) | — | — | `piping_3d.step` (17 leaves, 283 KB) + 5 render PNG |

Riwayat revisi lengkap & temuan QA per round: `01-dokumen/04-review-log.md`
(round A1, A2, A3, A4, 3D, FNKT-FORMAT, **A5 TRUE PIPING ISO**).

## 4. SUMBER KEBENARAN & ATURAN

- **`01-dokumen/01-design-basis.md`** = single source of truth: koordinat
  plant (meter), elevasi, line list (7 line + loading), instrument index,
  nozzle, konvensi drawing + §6a standar perusahaan. KONFLIK APA PUN →
  design basis menang; catat deviasi.
- **`02-standar/company-cad-standard-SKILL.md`** = rulebook drafting
  perusahaan §1–§8 (MTEXT per kategori, break, lineweight, flow, QA
  checklist, §7 gaya isometrik FNKT-10 + orientasi).
- **`02-standar/dxf-SKILL-patched-0.7.21.md`** = SKILL.md skill dxf yang
  sudah dipatch (seksi "Company standard override").
- Di mesin asal, skill terpasang di `~/.agents/skills/` dan project
  `AGENTS.md` otomatis mengikat aturan untuk agent yang bekerja di folder
  proyek.

## 5. PERINTAH PENTING (runtime cadgen 0.7.21)

```bash
PY="uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.21 python"
CG="uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.21 cadgen"

# 2D drawing (dxf skill):
$PY cad/<drawing>.py                      # build (atau "current" bila no-op)
$PY cad/apply_text.py cad/<d>.dxf cad/<d>.texts.json   # MTEXT + DIM + SOLID + pens (WAJIB tiap build)
$CG dxf snapshot cad/<d>.dxf cad/<d>.png --appearance light
$CG viewer --host 127.0.0.1 --json --detach   # viewer; mati tiap server restart — hidupkan ulang

# 3D model:
$PY src/piping_3d.py                      # build STEP
$CG snapshot step/piping_3d.step render/render_iso.png   # render (kamera auto-fit)

# mesh DXF & sheet FNKT-format:
$PY src/export_mesh_dxf.py
$PY src/export_iso_sheet_dxf.py

# validasi:
$PY -c "from cadgen.drawing_checks import validate_dxf_file; print([f.render() for f in validate_dxf_file('<file>.dxf')])"
```

Urutan wajib drawing engineering: **build → apply_text → validate (0 error)
→ snapshot → visual check** (rebuild menimpa .dxf → post-process WAJIB
diulang).

## 6. GOTCHA TEKNIS (pelajari — hemat jam debugging)

1. `bd.Compound.make_composite` (BUKAN make_compound); `Vector` build123d
   berattribute `.X/.Y/.Z` (bukan .x).
2. `MeshBuilder.render_polyface` (bukan .render); hasilnya entity **POLYLINE**
   polyface (query 'POLYFACE' = 0 — bukan hilang).
3. ezdxf VIEWPORT: atribut bernama **`view_direction_vector`** (bukan
   view_direction); `layout.add_viewport(center, size, view_center_point,
   view_height)`; `layouts.delete("Layout1")` gagal bila masih satu-satunya
   paperspace — hapus SETELAH layout sheet dibuat.
4. **Tessellate mengabaikan toleransi** — triangulasi tersimpan di dalam STEP
   (AP242), selalu 133.017 tri. Ingin mesh lebih kasar → BRepTools.Clean +
   BRepMesh ulang (belum diimplementasi).
5. `cadgen snapshot` selalu auto-fit seluruh model (tak bisa partial framing)
   → close-up = render hi-res + crop.
6. `render_polyface` sudah dedup vertex internal; ukuran DXF didominasi
   **face entity** (133k face ≈ 23 MB ASCII) — normal; ZIP hemat 90%.
7. Viewer cadgen mati setiap server/host restart → jalankan ulang perintah
   viewer di atas.
8. Update `npx skills add earthtojake/text-to-cad#latest` MENIMPA skill dxf
   → jalankan `~/skills-patches/reapply.sh` + merge pin versi baru
   (pola patch & backup: `~/skills-patches/`, baca README-nya).
9. cadgen **telemetry ON** (keputusan user, 9 Oct) — matikan dengan
   `uvx ... cadgen telemetry off` bila berubah pikiran.

## 7. TEMUAN TERBUKA (UNTUK B0 / IFC)

1. P&ID: label FC/N2 berdempet di cluster pump (minor, terbaca).
2. iso_co1004: segmen D–E tergambar campuran E+UP (14,04°) — pecah jadi 2 leg
   murni; dim sudah benar per leg.
3. Iso: tambah spec break, test package limit, support span mark.
4. Exclusion radius flare 13 m = asumsi — wajib kalkulasi radiasi API 521.
5. Sizing PSV/flare header (DN100×150 / DN150) belum diverifikasi hydraulik.
6. Approval grid (SIGNATURE/NAME/DATE) masih kosong — isi sebelum IFC.
7. Tick garis kecil tak berlabel di margin kanan sheet FNKT (kosmetik).
8. BOM reference file FNKT punya typo template "DESCRIPTIOS" — kita tulis
   "DESCRIPTION" (koreksi disengaja).

## 8. MAP PAKET INI

```
handoff/
├── HANDOFF.md                  ← dokumen ini
├── 01-dokumen/                 design basis, 2 plan eksekusi, review log
├── 02-standar/                 company-cad-standard, dxf SKILL patched,
│                               apply_text.py, README skills-patches
├── 03-drawing/                 5 DXF + PNG + multi-sheet FNKT-format (+zip)
├── 04-model-3d/                STEP, 5 render PNG
└── 05-skrip/                   piping_3d.py, export_iso_sheet_dxf.py,
                                export_mesh_dxf.py, apply_text.py
```

File referensi asli user (JANGAN diubah): `~/Downloads/Piping 3.zip`,
`~/Downloads/PIPING 1.zip`, hasil ekstrak `~/ref-iso/`.

## 9. GAYA KOMUNIKASI USER (agar kelanjutan terasa nyambung)

Bahasa Indonesia; respons ringkas-padat; tabel untuk rekap; setiap klaim
teknis diverifikasi (standar dicantumkan + edisi); QA berlapis (validasi
otomatis + visual oleh subagent pembaca gambar + review independen dengan
pola kutip→masalah→koreksi→status); subagent eksekusi = model
**glm-5.3-flash** (resume session bila perlu); user suka ditanya hanya bila
ambigu — selebihnya eksekusi dengan asumsi terdokumentasi.
