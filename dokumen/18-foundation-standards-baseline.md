# Baseline awal standar dan drafting CAD

**Status:** inventaris statis terbatas; bukan persetujuan adopsi, review klausul, atau bukti compliance.  
**Interface:** `cad/roadmap_foundation/standards.py`, schema `1.0`.

## Cakupan

Modul ini menginventarisasi file sumber terpilih dengan path relatif dan SHA-256, mencatat aturan drafting perusahaan yang tertulis, serta menyimpan kandidat standar sebagai `NOT ASSESSED`. Kandidat mencakup ISO 10628-1/-2, ISA 5.1 dan TR5.1.02/03, ISO 15519, ISO 14617, PIP PIC001 (jika diadopsi), dan IEC 61511. Edisi, applicability, scope adopsi, klausul dan compliance tetap tidak diketahui sampai ada sumber terkendali dan review berwenang. Tidak ada teks standar eksternal yang diambil atau klausul yang disimpulkan.

Aturan perusahaan yang dicatat dari `AGENTS.md` dan didukung sebagai implementasi lokal oleh `cad/apply_text.py`: native MTEXT/ARIAL melalui manifest; rentang tinggi teks; gap 3 mm untuk crossing garis minor sementara major utuh; lineweight; panah flow; serta urutan QA build, post-process, validasi, snapshot, dan visual review. Inventaris ini tidak menyatakan aturan rumah sebagai kepatuhan ISO/ISA.

## Observasi kode

Pemeriksaan dilakukan secara statis, tanpa import atau eksekusi generator. `pid_config_builder.py` menunjukkan authoring melalui `cadshim/ezdxf`, snapshot melalui cadshim/ezdxf-matplotlib bila diminta, dan jalur validasi cadgen opsional dalam proses terisolasi. Ini adalah observasi sumber, bukan bukti bahwa cadgen terpasang atau pernah berjalan pada sesi ini. `apply_text.py` mengimpor `cadgen.drawing_checks`; keberadaan import tersebut saja tidak membuktikan backend tersedia. `smart_qa.py` memvalidasi ports/connections yang diberikan pemanggil. Port internal valve assembly belum dimodelkan lengkap menurut catatan implementasi fase 1; kelengkapan semantik assembly karena itu tidak diasumsikan.

Laporan 71 tes pada laporan fase 1 merupakan hasil historis dan tidak direpresentasikan sebagai hasil saat ini. Tidak ada drawing yang diubah atau nilai/tag proyek yang disalin ke laporan ini.

## API dan pemakaian

`build_baseline(repo_root) -> dict` menghasilkan `schema_version="1.0"`, daftar artifact dengan hash/status/batasan, kandidat standar, inventaris rule perusahaan, serta observasi backend berkualifikasi. `validate_catalog(catalog) -> list[dict]` memerlukan versi schema dan empat section (`standards`, `rules`, `symbols`, `mappings`); section kosong dinyatakan coverage `NOT ASSESSED`. Validator melaporkan ID duplikat, source/edition/review evidence standar yang tidak memadai, port simbol yang belum didefinisikan, serta mapping yang tidak memiliki evidence terstruktur atau referensi standar/simbol valid. Evidence harus berupa objek metadata dengan locator; review evidence juga mencatat reviewer dan status. Mapping hanya mendapat status dukungan metadata bila review berstatus `REVIEWED` atau `ACCEPTED`; `REJECTED` dan status lain tidak memenuhi syarat. Bahkan metadata lengkap tetap menghasilkan finding `NOT ASSESSED` atas verifikasi sumber/isi standar dan applicability: validator tidak membuka, mengautentikasi, atau menilai dokumen standar. Keberadaan metadata bukan penerimaan isi standar atau conformity. Standards review tetap manual dan memerlukan salinan terkendali serta reviewer kompeten. Finding membawa `rule`, `category`, `severity`, `message`, `object_ids`, dan `location` (null jika tidak ada lokasi). Gaps yang belum direview tetap unknown; tidak disimpulkan pass.

Contoh dari root repository:

```powershell
python cad/roadmap_foundation/standards.py --repo-root . --out tmp/standards-baseline.json
python -m unittest cad.test_roadmap_standards -v
```

CLI mengurutkan key JSON secara deterministik dan hanya membuat output pada path baru; semua path output yang sudah ada ditolak. Report dapat ditempatkan di luar source set.

## Batas tindak lanjut

Ini adalah tranche inventaris BPD-101/BPD-102, bukan standards applicability approval atau manual standards review. Langkah berikutnya memerlukan salinan/reference standar yang sah dan terkendali, scope deliverable, legend/client profile yang berlaku, pemetaan simbol dengan port dan dukungan, serta review evidence dari discipline standards focal/role berwenang. `NOT ASSESSED` membatasi klaim/check yang bergantung pada entry tersebut; status ini tidak otomatis menahan pekerjaan independen.
