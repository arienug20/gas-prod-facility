# Baseline awal standar dan drafting CAD

**Status:** inventaris statis terbatas; bukan persetujuan adopsi, tinjauan klausul, atau bukti kepatuhan.  
**Antarmuka:** `cad/roadmap_foundation/standards.py`, schema `1.0`.

## Cakupan

Modul ini menginventarisasi berkas sumber terpilih dengan path relatif dan SHA-256, mencatat aturan drafting perusahaan yang tertulis, serta menyimpan kandidat standar berstatus `NOT ASSESSED`. Kandidat mencakup ISO 10628-1/-2, ISA 5.1 dan TR5.1.02/03, ISO 15519, ISO 14617, PIP PIC001 (jika diadopsi), dan IEC 61511. Edisi, keberlakuan, cakupan adopsi, klausul, dan kepatuhan tetap belum diketahui sampai tersedia sumber terkendali dan tinjauan oleh pihak berwenang. Tidak ada teks standar eksternal yang diambil atau klausul yang disimpulkan.

Aturan perusahaan yang dicatat dari `AGENTS.md` dan didukung sebagai implementasi lokal oleh `cad/apply_text.py`: MTEXT/ARIAL native melalui manifest; rentang tinggi teks; gap 3 mm untuk persilangan garis minor sementara garis major tetap utuh; ketebalan garis; panah aliran; serta urutan QA berupa build, post-process, validasi, snapshot, dan tinjauan visual. Inventaris ini tidak menyatakan aturan internal sebagai kepatuhan ISO/ISA.

## Observasi kode

Pemeriksaan dilakukan secara statis, tanpa import atau eksekusi generator. `pid_config_builder.py` menunjukkan pembuatan melalui `cadshim/ezdxf`, snapshot melalui cadshim/ezdxf-matplotlib bila diminta, dan jalur validasi cadgen opsional dalam proses terisolasi. Ini merupakan observasi sumber, bukan bukti bahwa cadgen terpasang atau pernah dijalankan pada sesi ini. `apply_text.py` mengimpor `cadgen.drawing_checks`; keberadaan import itu saja tidak membuktikan backend tersedia. `smart_qa.py` memvalidasi port/koneksi yang diberikan pemanggil. Port internal valve assembly belum dimodelkan lengkap menurut catatan implementasi fase 1; kelengkapan semantik assembly karena itu tidak diasumsikan.

Laporan 71 tes pada laporan fase 1 merupakan hasil historis dan tidak direpresentasikan sebagai hasil saat ini. Tidak ada drawing yang diubah atau nilai/tag proyek yang disalin ke laporan ini.

## API dan pemakaian

`build_baseline(repo_root) -> dict` menghasilkan `schema_version="1.0"`, daftar artefak beserta hash/status/batasan, kandidat standar, inventaris aturan perusahaan, serta observasi backend dengan kualifikasi. `validate_catalog(catalog) -> list[dict]` memerlukan versi schema dan empat bagian (`standards`, `rules`, `symbols`, `mappings`); bagian kosong dinyatakan dengan cakupan `NOT ASSESSED`. Validator melaporkan ID duplikat, sumber/edisi/bukti tinjauan standar yang tidak memadai, port simbol yang belum didefinisikan, serta mapping tanpa bukti terstruktur atau referensi standar/simbol yang valid. Bukti harus berupa objek metadata dengan locator; bukti tinjauan juga mencatat reviewer dan status. Mapping hanya mendapat dukungan metadata bila status tinjauan `REVIEWED` atau `ACCEPTED`; `REJECTED` dan status lain tidak memenuhi syarat. Metadata lengkap sekalipun tetap menghasilkan finding `NOT ASSESSED` untuk verifikasi sumber/isi standar dan keberlakuan: validator tidak membuka, mengautentikasi, atau menilai dokumen standar. Keberadaan metadata bukan penerimaan isi standar atau bukti kesesuaian. Tinjauan standar tetap manual dan memerlukan salinan terkendali serta reviewer kompeten. Finding membawa `rule`, `category`, `severity`, `message`, `object_ids`, dan `location` (null jika tidak ada lokasi). Gap yang belum ditinjau tetap belum diketahui; tidak disimpulkan sebagai pass.

Contoh dari root repository:

```powershell
python cad/roadmap_foundation/standards.py --repo-root . --out tmp/standards-baseline.json
python -m unittest cad.test_roadmap_standards -v
```

CLI mengurutkan key JSON secara deterministik dan hanya membuat output pada path baru; path output yang sudah ada ditolak. Laporan dapat ditempatkan di luar kumpulan sumber.

## Batas tindak lanjut

Ini adalah tahap inventaris BPD-101/BPD-102, bukan persetujuan keberlakuan standar atau tinjauan standar manual. Langkah berikutnya memerlukan salinan/referensi standar yang sah dan terkendali, cakupan deliverable, legend/profil klien yang berlaku, pemetaan simbol dengan port dan bukti pendukung, serta bukti tinjauan dari focal standar disiplin atau peran berwenang. `NOT ASSESSED` membatasi klaim/pemeriksaan yang bergantung pada entri tersebut; status ini tidak otomatis menahan pekerjaan independen.
