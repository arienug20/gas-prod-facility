# Roadmap Pengembangan Gas Production Facility — AI Engineering Multidisiplin

**Dokumen:** GPF-00-PM-PLN-0015  
**Revisi:** A1
**Tanggal:** 28 Oktober 2026  
**Status:** usulan roadmap untuk diskusi dan prioritisasi; bukan persetujuan desain, bukti compliance, atau jadwal proyek.

## 1. Tujuan dan hubungan dokumen

Roadmap mengembangkan tooling GPF dari fokus process/piping menjadi lingkungan engineering multidisiplin untuk menghasilkan draft yang terstruktur, menjaga keterlacakan, dan membantu review konsistensi. Keputusan dan persetujuan engineering tetap pada personel berwenang.

Roadmap ini melengkapi `07-plan-process-piping-cad-suite.md`, `08-plan-pipeline-metering-lbcv-underground.md`, `09-plan-optimasi-tooling.md`, `14-rencana-eksekusi-pid-meter-kompresor.md`, dan konsep P&ID general FEED/DED pada `15-konsep-pid-general-feed-ded.md`. Rincian eksekusi prioritas BFD/PFD/P&ID terdapat di `16-backlog-roadmap-bfd-pfd-pid.md`.

**Arah prioritas:** kembangkan kualitas P&ID yang sistematis menurut ISO/ISA dan standar proyek yang telah diverifikasi, sambil menjalankan pengumpulan dan rekonsiliasi data proses secara paralel. Ketiadaan kalkulasi universal tidak otomatis memblokir seluruh P&ID; data yang wajib untuk fungsi atau keputusan tertentu tetap menjadi hold yang terlihat. General engine, profile company/client, dan data proyek GPF adalah lapisan terpisah.

## 2. Prinsip kerja dan data-first

1. Baca dan inventarisasi sumber yang berlaku, termasuk design basis, dokumen proyek, vendor, standar kontraktual, serta revisinya. Ajukan pertanyaan data primer secara adaptif sampai input wajib untuk deliverable, sistem, dan fase terkait lengkap serta konsisten.
2. Konfirmasi basis dan batas sistem sebelum menetapkan desain. Diam bukan persetujuan. Jangan membuat angka, tag, design pressure, set point, nozzle, ukuran, fungsi proteksi, atau koneksi seolah-olah fakta.
3. Asumsi atau keluaran parsial berstatus TBD hanya boleh dipakai setelah persetujuan eksplisit untuk tujuan dan batas penggunaan tertentu. Inventaris independen, daftar pertanyaan, pemetaan sumber, dan pekerjaan yang tidak bergantung pada jawaban dapat berjalan terus.
4. Otomatisasi tag hanya mengikuti aturan penomoran dan alokasi yang telah disetujui; identifier sementara harus jelas bukan tag proyek.
5. Pisahkan status kepastian data (sumber/fakta/asumsi/TBD), keputusan engineering (opsi, alasan, owner, bukti), dan approval dokumen (author/checker/approver, issue purpose, revisi). Satu status tidak menyiratkan status lainnya.
6. Readiness ditentukan per deliverable dan fase melalui applicability serta bukti. FEED tidak memerlukan semua detail konstruksi DED, tetapi tidak boleh menghilangkan fungsi relevan atau menyembunyikan ketidakpastian. `Unknown`/`not assessed` bukan `pass`.
7. Hasil lint, tes, model atau drawing tidak membuktikan keselamatan, kecukupan desain, konstruktabilitas, atau compliance standar.

Untuk tag, line, koordinat, dan elevasi GPF, `dokumen/01-design-basis.md` tetap sumber kebenaran. Konflik diangkat sebagai deviation/decision; jangan mengubah basis secara sepihak. Pilot sintetik tidak ditambahkan ke basis GPF.

## 3. Batas awal dan bukti yang tersedia

- Tersedia design basis dan contoh P&ID V-101, piping plan, isometric, model 3D, library simbol serta validator CAD; cakupan engineering dan versi tool harus dinilai per artefak.
- Laporan tooling fase 1 (`11-report-tooling-phase1.md`) mencatat prototipe builder, router, anotasi, dan QA; 71 tes lulus secara historis pada sesi laporan. Angka tersebut bukan hasil uji kondisi saat ini atau jaminan cakupan engineering.
- Builder tahap 1 menunjukkan control-valve station dan transfer-line typical, tetapi port internal setiap valve belum dimodelkan lengkap. Tag registry belum persisten lintas proses. Label menggunakan bounding box perkiraan.
- Validasi fase 1 tercatat memakai cadshim/ezdxf; `validate_dxf_file` shim adalah stub dan bukan bukti bahwa cadgen asli telah divalidasi. Demo drawing lain yang memakai cadgen nyata tidak boleh digeneralisasi sebagai stub.
- Prioritas P&ID adalah melengkapi representasi instrumentasi dan kontrol (PI/PT beserta tag/fungsi sesuai basis, signal/loop, BPCS/SIS yang jelas), valve, drain, vent, seal, tie-in, serta kebutuhan operasi/maintenance yang applicable. Tidak ada simbol generik yang menggantikan keputusan proses atau safety.
- Typical dua P&ID pada rencana 14, demo metering/kompresor, dan basis flare memiliki status/tujuan masing-masing. Jangan menggabungkan data contoh dengan data GPF tanpa keputusan eksplisit.

## 4. Standar, otoritas dan pemeriksaan

Sebelum rule otomatis atau klaim kesesuaian dibuat, susun matriks standar per deliverable dengan edisi/addendum, kontrak, applicability, salinan resmi yang berhak digunakan, owner reviewer, tanggal pemeriksaan, dan status. Pemeriksaan klausul harus menggunakan salinan sah/terkendali; jangan mengklaim nomor klausul atau compliance berdasarkan ingatan.

| Rujukan awal untuk verifikasi | Penggunaan yang direncanakan | Status sampai verifikasi sumber berlaku |
|---|---|---|
| ISO 10628-1 dan ISO 10628-2 | Diagram process industry: klasifikasi/isi dan simbol | Matriks perlu menetapkan bagian/edisi serta batas penerapan. |
| ISA 5.1; ISA-TR5.1.02 dan ISA-TR5.1.03 | Instrumentation symbols/identification dan panduan penerapannya | Verifikasi edisi, kontrak, dan interpretasi project legend. |
| ISO 15519; ISO 14617 bagian relevan | Presentasi diagram process engineering dan simbol grafis | Identifikasi bagian yang benar-benar applicable; jangan menganggap semua bagian berlaku. |
| PIP PIC001 | Kandidat praktik P&ID hanya jika diadopsi proyek/klien | `NOT ASSESSED` sampai adopsi dan salinan terkendali dikonfirmasi. |
| ISA 5.4; IEC 62424 | Interface diagram loop/control engineering pada tahap lanjut | Bukan pengganti P&ID; cakupan interface dan fase ditetapkan kemudian. |
| IEC 61511 / ISA 61511 | Siklus hidup SIS dan interface safety | Wajib review disiplin berwenang; tool tidak menetapkan SIL atau membuktikan independensi. |
| API/ASME spesifik lingkup | Process equipment, relief, piping, metering, machinery sesuai scope | Standar dipilih per keputusan/perhitungan dan basis kontraktual; tidak ada penerapan blanket. |

Legenda, template, dan konvensi perusahaan adalah persyaratan drafting/proyek jika disetujui; hal tersebut tidak otomatis sama dengan persyaratan ISO/ISA. Standar yang belum tersedia/ditinjau dilaporkan `NOT ASSESSED`, bukan dianggap dipenuhi atau tidak dipenuhi.

## 5. Work packages dan dependency

Backlog task-level, acceptance test positif/negatif, dependency, evidence, status dan owner role ada di dokumen 16. Urutan berikut adalah dependency, bukan estimasi kalender.

| WP | Tujuan dan keluaran utama | Gate |
|---|---|---|
| WP0 — Baseline dan tata kelola | Inventaris sumber, tool, skill, standar, status data, konflik, owner/decision register dan baseline evidence | Sumber/revisi/status serta batas tiap demo dapat ditelusuri; konflik punya owner. |
| WP1 — Standar, legend dan drafting | Matriks applicability/adopsi dan manual review; mapping legend/project profile/company-client; P&ID A3 V-101 sebagai acuan drafting; alur MTEXT/QA | Scope adopsi dan legend tersedia disetujui; standar yang belum dinilai ditandai `NOT ASSESSED`, dengan hold hanya pada bagian scope yang terdampak; tidak ada klaim compliance. |
| WP2 — Data contract dan readiness | Schema data-first berversi; pertanyaan adaptif; readiness per design basis/BFD/PFD/P&ID FEED/DED berdasarkan applicability | Sistem tidak mengisi nilai kosong; hold/readiness dapat dijelaskan dengan bukti dan owner. |
| WP3 — Graph, ports, connections dan tag | Model graph equipment/valve/instrument/ports; koneksi internal; persistent identity/tag registry; adapter ke manifest/schedule | Positif/negatif membuktikan kontinuitas dan stabilitas; tag hanya dari alokasi disetujui. |
| WP4 — P&ID FEED/DED | Library/assembly dan fungsi lintas sistem, loop/signal, valve/drain/vent/seal, operasi, SIS interface, change impact | Pilot separator/scrubber sintetik lolos engineering review serta minimum semantic/drafting QA; agregasi QA dan release gate dilakukan WP6; batas FEED/DED berlaku. |
| WP5 — BFD/PFD/H&MB/kalkulasi | Alur BFD/PFD serta import H&MB CSV/JSON dan hasil kalkulasi yang diverifikasi; API simulator kelak | Nilai/satuan/sumber/revisi dan perubahan direkonsiliasi; hasil simulator bukan source tanpa review. |
| WP6 — QA, change dan issue bundle | Checks, delta impact, evidence, revision/issue package berversi dan reproducible | Paket satu versi input/model/rule/output; status engineering/model/drafting/approval terpisah. |
| WP7 — Multidisiplin dan integrasi | Integrasi interface process ke piping, mechanical/static & rotating, instrument/control, SIS/safety, electrical, civil/structural, corrosion/materials, pipeline, F&G/telecom, document control, construction/commissioning/operations | Pilot end-to-end menunjukkan owner, interface, gap, provenance dan approval untuk semua interface applicable. |

WP4 dimulai dengan kualitas P&ID dan fixture separator/scrubber sintetik berorientasi V-101. Fixture ditandai test-only dan memiliki scope yang disetujui; angka/tag di dalamnya tidak menjadi data GPF. Minimum validator dan drafting lifecycle menjadi prasyarat pilot; agregasi QA lintas package dan issue/release gate dilakukan kemudian di WP6. Pump dan flare dipertahankan sebagai regresi, dengan cakupan aktual dinyatakan. Data process dan P&ID dikerjakan paralel melalui WP2/WP5. Kalkulasi atau simulator hanya menjadi input/gate bila applicable pada keputusan dan deliverable terkait; tidak ada kalkulasi universal sebagai blocker.

## 6. Interface lintas disiplin (ekspansi WP7)

Core menyimpan interface dan provenance, bukan menggantikan metode/perangkat engineering disiplin. Tiap disiplin menyuplai deliverable terkendali, status, owner, assumptions/TBD, interface ID dan perubahan yang terdampak.

| Disiplin | Interface awal dan gate ringkas |
|---|---|
| Piping/layout | P&ID ↔ line list ↔ plan/iso/model ↔ nozzle; line spec/P-T dan lokasi disinkronkan dari basis yang disetujui; geometry dan hydraulic/stress review terpisah. |
| Mechanical/static | Equipment datasheet, nozzle schedule, vessel/tank/exchanger dan vendor loads; equipment/nozzle basis direkonsiliasi dengan process/piping. |
| Mechanical/rotating | Pump/compressor duty, package boundary, driver, utilities dan vendor data; pump regression menjadi salah satu fixture, bukan desain proyek. |
| Instrument/control | Instrument index, PI/PT/tag, I/O/loop, control narrative, signal dan final element; trace measurement→logic→action sesuai fase dan evidence. |
| SIS/process safety | C&E/SRS, safety function, HAZOP/LOPA/SIL dan relief/flare interface; approval oleh tim berwenang, tidak disimpulkan dari simbol. |
| Electrical | Load list, power balance, SLD, MCC/driver, hazardous area, cable/earthing; equipment ↔ load ↔ supply dapat ditelusuri. |
| Civil/structural | Plot/grade, geotechnical basis, foundation/support loads, access; load/coordinate source serta design check tercatat. |
| Corrosion/materials | Fluida, water/H2S, material, corrosion allowance, coating/CP dan compatibility; basis/material selection review sesuai scope. |
| Pipeline | Route, boundaries, operating envelope, line/service/spec dan tie-in; interface ke facility dan crossing/ROW/study dicatat. |
| Telecom, fire & gas | Detection, communication, device/location, cause/effect interface dan power/control; kebutuhan mengikuti safety study dan layout. |
| Project engineering/document control | Master document register, revision, transmittal, comment/action/decision/vendor register; approval aktual dan issue purpose terkendali. |
| Construction/commissioning/operations | System/subsystem, isolation, startup/shutdown, commissioning, maintenance dan field feedback; dokumen terkendali dan sign-off sesuai prosedur. |

## 7. Aturan mutu drawing dan issue

Setiap P&ID A3 untuk acuan V-101 tetap mematuhi `AGENTS.md`: skill `company-cad-standard` dan `dxf` dipakai saat drawing; company override dipastikan aktif; teks berupa native MTEXT ARIAL melalui manifest dan `cad/apply_text.py`, lineweight dipasang oleh post-processor, collision dicegah, garis minor crossing diberi gap 3 mm sedangkan process major line utuh, dan setiap process line menunjukkan flow arrow. Urutan: build → apply_text → validasi 0 error → snapshot → visual check independen oleh pembaca gambar. Catat backend yang benar-benar berjalan; stub bukan bukti. Setiap revisi drawing menaikkan REV dan mencatat perubahan pada title block/revision table.

Satu issue bundle mengikat versi/hash input, schema/rules/library, graph, manifest, register, findings, assumptions/TBD, drawing, snapshot dan approval aktual. Kriteria readiness untuk design basis, BFD, PFD, P&ID FEED dan P&ID DED dirinci di backlog. Penerbitan IFR/IFC/as-built tunduk pada prosedur proyek; output tooling bukan approval.

## 8. Prioritas, ukuran hasil dan batas klaim

Prioritas eksekusi: WP0 → WP1/WP2 → WP3 → WP4, dengan WP5 data/process berjalan paralel sesuai input; WP6 mengikat issue; WP7 memperluas secara bertahap. Urutan ini tidak mengasumsikan tanggal, biaya, atau jumlah personel.

Ukuran hasil mencakup coverage evidence/applicability, jumlah pertanyaan dan hold yang ditutup/terbuka, kesalahan semantik yang tertangkap pada fixture, dampak perubahan lintas artefak, hasil drafting/visual QA, dan waktu authoring setelah baseline kualitas. Hindari klaim “zero-defect”, “fully compliant”, atau otomatisasi keselamatan tanpa cakupan dan bukti yang sesuai.

HAZOP/HAZID, relief sizing, SIL/LOPA, electrical protection, equipment/mechanical design, structural calculation, material selection dan persetujuan IFC tetap memerlukan sumber, proses, kompetensi, serta persetujuan berwenang. Yang belum dinilai dilabel `NOT ASSESSED`.

## 9. Riwayat revisi

| Revisi | Tanggal | Perubahan |
|---|---|---|
| A0 | 28 Oktober 2026 | Roadmap multidisiplin awal. |
| A1 | 28 Oktober 2026 | Memprioritaskan P&ID ISO/ISA dengan workflow data-first; menambahkan standar review matrix, readiness per deliverable/fase, pemisahan engine/profile/data, status fakta kode fase 1, WP0–WP7, pilot sintetik V-101, integrasi H&MB, dan referensi backlog rinci. |
