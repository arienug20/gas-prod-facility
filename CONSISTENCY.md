# CONSISTENCY.md — Cek Konsistensi Design Basis ↔ Drawing

Linter geometri (`cad/validate_cad_rules.py`) memeriksa **bentuk** gambar:
teks Arial, lineweight, persilangan line, tabrakan teks, ujung menggantung.
Yang **tidak** bisa ia lihat adalah apakah isi gambar sesuai dokumen sumber.

`tools/consistency_check.py` menutup celah itu.

---

## 1. Mengapa ini perlu

`AGENTS.md` menetapkan `dokumen/01-design-basis.md` sebagai **sumber
kebenaran** untuk tag equipment, nomor line, tag instrumen, dan koordinat.
Sebelum ada pemeriksa otomatis, ketidaksesuaian hanya ditemukan lewat
review manual — dan memang pernah terjadi:

| Temuan historis (04-review-log.md) | Jenis |
|---|---|
| `EL +6.200` di ISO-0005 vs `+6.15` di design basis | Angka lintas dokumen |
| BOM "4× elbow" vs geometri 3 belokan | Hitungan tidak konsisten |
| Design basis masih "Rev A0" saat subagent sudah bump A1 | Revisi tidak sinkron |

---

## 2. Aturan yang diperiksa

| Kode | Aturan | Level |
|---|---|---|
| **D1** | Nomor dokumen di title block cocok dengan registri `tools/documents.json` | ERROR |
| **D2** | Satu nomor dokumen tidak dipakai dua file | ERROR |
| **D3** | Setiap manifest punya entri registri, dan sebaliknya | ERROR / WARN |
| **R1** | Sel revisi tertinggi == deklarasi `REV: Xn` | ERROR |
| **R2** | Revisi monoton tanpa celah (A0, A1, A3 → gagal) | ERROR |
| **T1** | Tag equipment & instrumen design basis muncul di P&ID | ERROR |
| **T2** | Nomor line design basis muncul di drawing **dan DN-nya cocok** | ERROR |
| **T3** | Tag instrumen design basis muncul di P&ID | ERROR |
| **X1** | Tag di P&ID yang tidak dikenal design basis | WARN |

`X1` sengaja WARNING: modul di luar design basis (wellhead, kompresi,
utilitas) memang sah — lihat `ROUND ROADMAP-08` di review log.

---

## 3. Dua jebakan yang ditangani

### 3.1 Bubble ISA ditulis sebagai DUA teks

Di P&ID, instrumen tidak disimpan sebagai `"LIC-121"` utuh, melainkan:

```
teks 1: "LIC"   @ (534, 140)
teks 2: "121"   @ (534, 144)   -> jarak 4,4 mm (di dalam bubble Ø12)
```

Validator menyatukannya kembali berdasarkan **kedekatan** (< 13 mm),
bukan regex saja. Tanpa ini, 10 dari 22 instrumen akan terlaporkan
"hilang" — false positive.

### 3.2 Tag majemuk `FE/FT`

Design basis menulis `FE/FT-141` (ISA 5.1: FE = element, FT = transmitter),
sedangkan drawing memisahkan menjadi `FE-141` + `FI-141`. Tag dianggap
terpenuhi bila **salah satu** komponennya ada.

### 3.3 Cakupan equipment per lembar

P&ID area separator memang **tidak** memuat flare stack `F-101` dan KO drum
`V-102` — keduanya domain routing plan. Pemetaan cakupan:

```python
EQUIP_SCOPE = {
    "pid_v101":     {"V-101", "P-101", "T-101"},
    "routing_plan": <semua equipment design basis>,
}
```

---

## 4. Registri dokumen

`tools/documents.json` memetakan file → nomor dokumen:

```json
{"file": "pid_v101", "doc_no": "GPF-00-PI-PID-0001", "sheet": "A1", "type": "P&ID"}
```

**Tambahkan entri setiap kali membuat drawing baru**, kalau tidak gate
akan gagal dengan `D3`.

---

## 5. Pemakaian

```bash
python tools/consistency_check.py            # laporan
python tools/consistency_check.py --json     # terstruktur (CI)
python tools/consistency_check.py --strict   # warning = gagal
```

Contoh keluaran (kondisi repo saat dokumen ini ditulis):

```
design basis : 01-design-basis.md (5 equipment, 7 line, 22 instrument)
manifest     : 16 drawing
[WARN ] X1   pid_v101   22 tag tidak ada di design basis: CV-101, FE-141, ...
HASIL: 0 error, 1 warning
KONSISTEN
```

---

## 6. Uji negatif (bukti validator bisa GAGAL)

Validator yang selalu hijau tidak berguna. `tools/test_consistency_negative.py`
menyuntikkan kerusakan ke **salinan** repo dan memastikan tiap aturan menangkapnya:

```
[PASS] D2: nomor dokumen ganda
[PASS] D1: doc no title block salah
[PASS] R2: celah revisi (A0,A1,A3)
[PASS] R1: deklarasi REV tidak cocok
[PASS] T1: tag equipment hilang dari P&ID
[PASS] T2: DN salah untuk line di drawing
[PASS] D3: manifest tanpa entri registri
[PASS] baseline repo bersih (harus exit 0)
HASIL NEGATIVE TEST: 8/8
```

Keduanya dijalankan otomatis di quality gate (`consistency` +
`consistency-negtest`) dan di CI.

---

## 7. Temuan terbuka yang tercatat

Warning `X1` pada `pid_v101` menyebut valve `CV-101`, `GV-101..105`,
`GV-131`, `GV-141`, `SDV-101`. Tag ini memang ada di kolom
*"Valve/Spesial di line"* pada **line list** design basis, tetapi belum
masuk **instrument index**. Kandidat perbaikan design basis (bukan bug
drawing).
