# Review independen foundation wave 1

**Tanggal:** 28 Oktober 2026  
**Status:** review terbatas atas implementasi dan pengujian fondasi; bukan persetujuan desain atau PASS roadmap.

## Lingkup dan hasil

Review mencakup `cad/roadmap_foundation/standards.py`, `readiness.py`, `registry.py`, dan pengujian unit pendampingnya, dengan acuan backlog `dokumen/16-backlog-roadmap-bfd-pfd-pid.md`. Reviewer meninjau kode dan kasus negatif yang relevan, kemudian menjalankan `python -m unittest cad.test_roadmap_standards cad.test_roadmap_readiness cad.test_roadmap_registry -q`: **34 tes lulus** pada Python 3.14.2 (9 standards, 11 readiness, 14 registry). Pesan penggunaan CLI yang muncul merupakan bagian dari tes penolakan overwrite yang diharapkan.

Temuan awal mengenai katalog kosong dan evidence yang belum terverifikasi, overwrite, hold tanpa task ID, input malformed, scope dan referensi konfirmasi, serta aturan tag, stale write dan kelengkapan assembly telah ditangani dalam kode dan kasus uji yang ditinjau. Hasil ini hanya mendukung perilaku yang diuji, bukan validasi menyeluruh semua input atau sistem.

## Batas dan tindak lanjut

- Kandidat standar tetap `NOT ASSESSED`; metadata evidence adalah pernyataan caller, belum merupakan pemeriksaan independen salinan standar, klausul, adopsi, atau compliance.
- Readiness adalah evaluasi data dan scope yang dipasok. Identitas dan otoritas actor dalam metadata tidak diautentikasi oleh modul; status bukan persetujuan engineering atau dokumen.
- Registry memeriksa allocation yang diberikan serta menggunakan lock dan stale-hash sebelum replace. Pengujian mencakup lock yang sudah dipegang dan stale write, tetapi belum merupakan uji race multiprocess; lock tertinggal setelah proses berhenti abnormal memerlukan penanganan operasional yang hati-hati.
- Audit graph terbatas pada representasi eksplisit yang disuplai; ini tidak membuktikan kelengkapan semantik valve assembly, koneksi lapangan, nozzle, atau kesesuaian engineering. Crossing geometris tidak membuktikan junction.
- Pilot separator/scrubber, drawing lifecycle, validator aktual, snapshot dan visual check belum dilakukan dalam tranche ini. Tidak ada klaim compliance atau kesiapan penerbitan drawing.
- Regression pytest router/annotations/QA existing dicoba oleh integrator tetapi tidak berjalan karena `pytest` tidak tersedia pada runtime Python 3.14.2; ini bukan hasil gagal tes dan cakupan regresi existing masih belum terverifikasi.

## Addendum integrasi

Review tambahan mencakup adapter legacy top-level ports dan `cad/roadmap_foundation/workflow.py` serta tes integrasinya. Workflow memisahkan readiness data, penilaian katalog, graph, dan engineering review; hasil engineering tetap `NOT ASSESSED`. Input basis yang hilang tidak menghasilkan data ready. Katalog atau graph null dicatat sebagai input hilang dengan finding dan menyebabkan CLI keluar nonzero; output existing ditolak. Adapter mempertahankan informasi port legacy yang tersedia dan graph kosong tetap ditandai belum lengkap.

Pada pemeriksaan ulang setelah integrasi, `python -m unittest cad.test_roadmap_standards cad.test_roadmap_readiness cad.test_roadmap_registry cad.test_roadmap_workflow -q` menghasilkan **44 tes lulus** pada Python 3.14.2. Ini melengkapi, bukan menggantikan, batas review di atas; hasil tersebut tidak membuktikan kesiapan engineering atau roadmap secara keseluruhan.

## Addendum regresi runtime pengguna

Reviewer memeriksa catatan eksekusi Luna di `dokumen/22-execution-foundation-wave1.md`. Di lingkungan dengan akses site-packages profil pengguna, pytest 9.1.1 sudah tersedia; keterbatasan impor sebelumnya berlaku pada runtime sandbox. Perintah pytest yang tercatat mencakup tujuh modul: smart annotations, router, QA, standards, readiness, registry, dan workflow. Hasil yang dilaporkan Luna adalah **75 passed, 131 warnings dalam 3,28 detik**, exit code 0. Tidak ada paket yang dipasang pada langkah verifikasi tersebut. Reviewer tidak mengulang eksekusi ini; hasil berasal dari catatan pelaksana. Cakupan tersebut tidak membuktikan seluruh repository, roadmap, atau drawing telah lulus.

## Addendum koreksi readiness

Setelah review sebelumnya, integrator menemukan bahwa basis yang terkonfirmasi dapat menghasilkan `ready` walaupun scope-nya tidak mencakup deliverable dan nilai numeriknya tidak memiliki satuan. Ini adalah celah dalam cakupan review sebelumnya; hasil 44 dan 75 tes di atas tidak mendeteksinya. Reviewer meninjau perbaikan dan tes negatif baru: scope basis harus eksplisit dan mencakup deliverable yang memakai item; nilai numerik memerlukan unit eksplisit, dengan unit `1` dan deklarasi `dimensionless` untuk besaran tak berdimensi. Nilai naratif dapat tanpa unit. Pengujian tidak membuktikan kebenaran dimensi atau satuan secara engineering.

Reviewer menjalankan ulang empat suite fondasi dengan `python -m unittest cad.test_roadmap_standards cad.test_roadmap_readiness cad.test_roadmap_registry cad.test_roadmap_workflow -q`: **46 tes lulus**. Luna melaporkan regresi tujuh modul **77 passed, 131 warnings dalam 3,37 detik**, serta kompilasi delapan file sumber/tes; reviewer tidak mengulang pytest tersebut. Menurut rincian pelaksana, warning berasal dari deprecation ezdxf/pyparsing (7 call sites, 62 `parseString`, 62 `parseAll`). Tes tujuh modul mencakup toolkit legacy lokal sebagai regresi tambahan; suite empat modul fondasi dapat dijalankan terpisah. Kesimpulan tetap terbatas pada perilaku yang diuji, bukan penerimaan desain atau seluruh roadmap.

## Addendum bahasa Indonesia

Review terbatas atas perubahan bahasa mencakup pesan dan pertanyaan bawaan, bantuan dan error CLI khusus pada empat modul fondasi. ID rule, kunci schema, enum status, serta teks pertanyaan yang disediakan pengguna dipertahankan. Teks bawaan `argparse` dari pustaka standar dan modul legacy di luar fondasi tidak termasuk lokalisasi ini. Reviewer menjalankan empat suite fondasi: **50 tes lulus**; angka 46 di atas adalah hasil historis sebelum perubahan bahasa. Pengujian tidak merupakan review engineering atau validasi drawing.
