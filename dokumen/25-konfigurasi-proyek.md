# Konfigurasi proyek dan sumber data engineering

Tool bersama memilih design basis, HMB, registri dokumen, direktori drawing, pola penomoran dan identitas lembar dari konfigurasi proyek JSON versi `1.0`. File `project.gpf.json` adalah konfigurasi GPF yang menunjuk basis historis `dokumen/01-design-basis.md`; drawing, nilai dan tag GPF tetap milik proyek tersebut. Path di konfigurasi relatif terhadap direktori file konfigurasi; path absolut juga diperbolehkan.

Pada repo GPF, pemanggilan lama tetap menggunakan `project.gpf.json`. Untuk proyek lain gunakan `--project /path/proyek/project.json` secara eksplisit, termasuk bila perintah dijalankan di dalam repo ini. Pemanggilan tanpa `--project` dari luar repo GPF ditolak. File baru tidak boleh dibuat dengan data GPF secara tersirat; AI memeriksa sumber dan bertanya bila data wajib belum tersedia. Asumsi dan output parsial harus diotorisasi untuk scope yang jelas; tag proyek memerlukan aturan dan alokasi yang disetujui, sedangkan tag demo harus dinyatakan sementara.

```sh
python tools/consistency_check.py --project /path/proyek/project.json --json
python tools/export_xlsx.py --project /path/proyek/project.json -o /path/proyek/register.xlsx
python -m cad.roadmap_foundation.standards --repo-root . --project /path/proyek/project.json
```

## Format konfigurasi

Gunakan `project.gpf.json` sebagai referensi struktur. Field wajib: `schema_version`, `project_id`, `cad_dir`, `documents_registry`, `design_basis` dengan `file` dan `format`, `numbering`, `consistency.core_files`, dan `sheet_profile` dengan `project`, `company`, `consultant`. `hmb` berupa `null` atau `{"file":"hmb.csv"}`; status `NOT PROVIDED`, `MISSING`, atau `AVAILABLE` melaporkan ketersediaan file saja dan bukan validasi data HMB.

`numbering.document_regex` tidak boleh memiliki capture group; `tag_regex` memiliki dua capture group (prefix dan identifier); `line_regex` memiliki satu capture group yang menangkap nomor line penuh. Regex mencari teks manifest; pemetaan komponen bubble terpisah yang ada saat ini hanya didukung untuk pola legacy GPF. `consistency.core_files` menentukan drawing yang dicek terhadap basis; `equipment_scope` menentukan tag yang berlaku per drawing P&ID, dan `unknown_tags_pid` memilih P&ID untuk laporan tag yang tidak dikenal. Cakupan ini harus ditetapkan per proyek agar pemeriksaan tidak menganggap semua equipment harus muncul di setiap sheet.

Untuk membuat gambar dari konfigurasi aktif, berikan `sheet_profile=project.sheet_profile` ke `cad.pid_sheet_profile.draw_sheet`. Identitas GPF yang ada tetap menjadi default bagi pemanggil lama; generator proyek baru wajib memberikan profil eksplisit. Tampilan profil tidak menyetujui data atau drawing.

## Adapter basis

`gpf-markdown-v1` hanya untuk struktur tabel GPF lama. Format Markdown atau HMB lain tidak diparse dengan tebakan. Untuk proyek baru, petakan sumber yang ditinjau ke `register-json-v1`; contoh bentuk minimal:

```json
{
  "schema_version": "1.0",
  "meta": {"doc_no": "PRJ-DB-0001", "rev": "A0"},
  "equipment": [{"tag": "V-777", "description": "scrubber"}],
  "lines": [{"line_no": "999-GO-7777", "dn": 80}],
  "instruments": [{"tag": "PT-777"}]
}
```

Field tambahan opsional untuk ekspor meliputi equipment `position`, `elevation`; line `from_to`, `valves`, `note`; instrumen `loop`, `function`, `location`, `action`. Pertahankan dokumen sumber dan keputusan pemetaan di proyek; register JSON bukan bukti approval atau pengganti basis/HMB asli. Jenis format tidak dikenal, file basis hilang, struktur tidak valid dan DN tidak valid menghasilkan error, bukan register kosong yang dianggap berhasil. Ekspor menolak path output yang menimpa konfigurasi/basis/registri/HMB atau berada dalam direktori drawing.

Checker membandingkan tag, nomor line/DN dan nomor dokumen dalam cakupan yang dikonfigurasi. Ia tidak memastikan basis lengkap, validitas engineering, safety, atau HMB. Hasil `AVAILABLE` tidak menyatakan HMB telah di-review. Pemeriksaan drafting dan review engineering tetap terpisah.
