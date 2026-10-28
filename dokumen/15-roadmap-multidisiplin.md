# Roadmap Pengembangan Gas Production Facility — AI Engineering Multidisiplin

**Dokumen:** GPF-00-PM-PLN-0015  
**Revisi:** A0  
**Tanggal:** 28 Oktober 2026  
**Status:** usulan roadmap untuk diskusi dan prioritisasi; bukan persetujuan desain atau jadwal proyek.

## 1. Tujuan dan arah

Mengembangkan repositori GPF dari tooling yang saat ini berfokus pada process dan piping menjadi lingkungan kerja engineering multidisiplin yang dapat menghasilkan **draft terstruktur**, melakukan review dan memeriksa konsistensi antardokumen. Hasil dipakai untuk mendukung engineer; persetujuan dan keputusan keselamatan tetap berada pada personel yang berwenang.

Roadmap ini melengkapi, tidak menggantikan, `07-plan-process-piping-cad-suite.md`, `08-plan-pipeline-metering-lbcv-underground.md`, `09-plan-optimasi-tooling.md` dan rencana dua P&ID `14-rencana-eksekusi-pid-meter-kompresor.md`. Cakupan fasilitas, urutan prioritas, personel, biaya, waktu dan dokumen kontraktual perlu disepakati pada awal eksekusi.

**Prinsip:** engineering basis → hubungan antar-disiplin → draft dokumen/model → validasi sesuai cakupan → review independen → persetujuan manusia. Hasil CAD lulus tidak membuktikan kecukupan desain, kepatuhan standar, atau kelayakan konstruksi.

## 2. Kondisi awal yang teramati

- Sudah tersedia design basis proyek, contoh P&ID V-101, piping plan, isometric, model 3D, library simbol dan validator CAD; beberapa modul process/piping telah memiliki demo dan pengujian.
- Dua demo custody metering dan kompresor, beserta review `13` dan rencana `14`, menunjukkan perlunya trace fungsi, acuan domain, pengelolaan data TBD dan review engineering terpisah dari QA drafting.
- `REF-PROC-MINOR` belum tercakup seluruh pemeriksaan validator; kualitas geometri, akurasi process, dan konsistensi lintas disiplin perlu dilaporkan sebagai pemeriksaan yang berbeda.
- Design basis `01-design-basis.md` adalah sumber kebenaran proyek untuk tag/line/koordinat/elevasi sesuai `AGENTS.md`. Paket demo di luar basis tidak boleh otomatis menjadi bagian plant. Konflik dalam basis harus diangkat untuk keputusan engineer; jangan mengubah data otoritatif berdasarkan tebakan.
- Klaim lama seperti “zero-defect” dan target waktu dalam rencana historis adalah target/hasil pada cakupan uji masing-masing, bukan jaminan engineering untuk proyek atau disiplin baru.

## 3. Cakupan disiplin dan hubungan awal

| Disiplin | Keluaran awal yang dituju | Input utama dan interface |
|---|---|---|
| Process | Design basis, PFD/H&MB, P&ID, equipment/line list, relief dan operasi sebagai draft terstruktur | Komposisi, laju dan P/T dari basis; menyediakan kondisi proses untuk seluruh disiplin. |
| Piping & layout | Line list/spec, plot/piping plan, isometric, model/coordinate register dan support interface | P&ID, equipment nozzle, design P/T, layout; berkoordinasi dengan mechanical, civil dan structural. |
| Mechanical/static | Equipment datasheet, nozzle schedule, vessel/tank/exchanger interface, daftar vendor data | Process conditions, material/pressure design, nozzle dan beban untuk piping/structural. |
| Mechanical/rotating | Datasheet dan interface pompa/kompresor, package boundary, utilities, vendor document register | Process envelope, performance map, loads, electrical driver, instrument dan protection interface. |
| Instrument & control | Instrument index, datasheet, I/O list, loop interface, control narrative dan hook-up register | P&ID, equipment/vendor, utilities, electrical power dan control system. |
| SIS & process safety | C&E/SRS draft, safety-function register, relief/flare and hazard-study interface, open action register | Process scenarios, P&ID, instrument, electrical dan operating philosophy. HAZOP/LOPA/SIL formal tetap kerja tim berwenang. |
| Electrical | Load list, power balance, SLD draft, equipment/MCC interface, cable dan earthing register | Mechanical drivers, utility loads, hazardous-area classification dan control power. |
| Civil & structural | Plot/grade interfaces, foundation load register, structure/support and access interfaces | Equipment and piping loads, coordinates, geotechnical data, layout dan operating access. |
| Pipeline, corrosion & materials | Interface route, line/service/spec, coating/CP and materials-selection registers | Composition, H2S/water, pressure, route, soil/environment, corrosion study dan piping boundary. |
| Telecom, fire & gas | Detection and communication interface, device/location and system interface registers | Safety studies, hazardous-area data, layout, electrical power dan control system. |
| Project engineering & document control | Master document register, interfaces, review comments, revision/change and vendor data register | Status dan persetujuan semua disiplin; menjaga keterlacakan baseline. |
| Construction, commissioning & operations | Draft system/subsystem boundary, interface and outstanding-action register | Dokumen desain yang telah dikendalikan, operating philosophy dan input lapangan; bukan instruksi eksekusi lapangan otomatis. |

Daftar tersebut menunjukkan tujuan, bukan pernyataan bahwa skill, library atau template untuk semua disiplin sudah tersedia. PFD/P&ID, data listrik, mekanikal, sipil dan safety harus berbagi referensi namun tetap memiliki penanggung jawab disiplin masing-masing.

## 4. Tahapan dan dependency

### Fase 0 — Baseline dan tata kelola

**Tujuan:** memastikan bahan yang dipakai, scope dan statusnya dapat dipercaya sebelum ekspansi.

- Inventaris dokumen, skill terpasang/salinan repo, tool dan demo: nomor, rev, status, lokasi, pemilik, dependensi dan keterbatasan. Identifikasi source canonical dan salinan distribusi; ukur perbedaan sebelum mengubah installer.
- Audit konflik internal basis dan drawing yang sudah diketahui; daftar sebagai isu, tetapkan pemilik dan keputusan tanpa mengubah design basis sepihak.
- Buat master document register, action/decision register dan matriks RACI awal. Tetapkan definisi demo, concept, IFR, IFC dan as-built sesuai prosedur proyek; kode revisi mengikuti `AGENTS.md`.
- Tentukan standar/edisi kontraktual per domain, sumber resmi dan tanggal verifikasi; jangan menyimpulkan kepatuhan dari nama standar pada template.

**Gate:** baseline dan daftar konflik disetujui pemilik proyek; item belum selesai tetap mempunyai owner dan status. Hasil: laporan baseline dan daftar prioritas yang dapat diaudit.

### Fase 1 — Fondasi data dan QA lintas disiplin

**Tujuan:** setiap fakta memiliki identitas, asal dan status yang jelas sebelum dipakai berulang.

- Rancang register bersama minimal: equipment, nozzle, line, instrument, stream, load, document dan interface. Setiap record memiliki tag/ID, nilai, unit/basis, sumber/revisi, status (`given`, `assumption`, `TBD`, `approved`), penanggung jawab dan referensi perubahan. Tidak menyimpan nilai default simbol sebagai nilai desain.
- Tetapkan aturan nomor unik, satuan, referensi lintas dokumen, perubahan dan konflik. Struktur baru harus kompatibel dengan manifest/schedule yang ada melalui adapter dan pengujian; jangan menyalin data proyek sebagai fakta otomatis.
- Perluas validator ke proses minor, konsistensi tag/schedule, revisi dan interface. Laporkan cakupan, false positive/negative dan `NOT ASSESSED`; bangun fixture positif/negatif berdasarkan kasus P&ID sebelumnya. Status QA CAD, konsistensi data dan review engineering harus terpisah.
- Definisikan workflow membuat, meninjau, merilis draft dan merekonsiliasi salinan skill pada Linux/Windows; perubahan skill/tool dicatat dan diuji sebelum distribusi.

**Gate:** contoh perubahan tag/line dapat ditelusuri ke dokumen terkait; konflik/TBD terdeteksi tanpa diam-diam mengubah basis; suite regresi dan pemeriksaan visual yang relevan lulus. Penilaian engineering tetap terpisah.

### Fase 2 — Process/PFD/P&ID dan metering/kompresi

**Tujuan:** membangun referensi engineering yang dalam sebelum memperluas ke disiplin pengguna data.

- Pisahkan workflow PFD/H&MB dan P&ID; tambahkan trace table proses, kontrol, shutdown, relief dan interface sebelum membuat drawing. Gunakan V-101 sebagai acuan detail dan `dokumen/14` untuk dua pilot.
- Perkuat review P&ID: pisahkan dampak dari keyakinan bukti, nyatakan referensi yang hilang, dan tambahkan panduan metering, separator serta compressor. Sebut AGA 9/8 dan API MPMS sesuai teknologi dan kontrak; jangan menganggap ada kesesuaian tanpa data/calibration.
- Uji pilot custody 10 MMSCFD dan compressor 2 × 50% sebagai contoh mandiri. Basis psi, kapasitas, gas kompresor, H2S service, PSV sizing dan performa vendor tetap TBD sampai dikonfirmasi. Cap/sambungan dan ESD references harus jelas.
- Kembangkan register asumsi, C&E dan interface yang terhubung ke temuan review, tanpa menggantikan HAZOP, relief study, SRS atau persetujuan spesialis.

**Gate:** reviewer process, metering, machinery dan instrument dapat menelusuri fungsi dari sumber ke tujuan dan mengidentifikasi setiap data yang belum diketahui. Demo tidak diklaim sebagai desain konstruksi.

### Fase 3 — Piping dan mechanical terintegrasi

**Tujuan:** konsistensi antara proses, peralatan, ruang dan piping.

- Sinkronkan equipment/nozzle/line dan design P/T dari baseline; cocokkan P&ID ↔ line list ↔ plan/model ↔ isometric ↔ datasheet dengan identitas dan revisi sumber.
- Tambahkan interface untuk vessel, pumps, compressor packages, nozzle orientation, maintenance/access dan vendor loads. Identifikasi perbedaan konseptual, geometris dan data vendor tanpa menyimpulkan kebenaran desain dari model semata.
- Sediakan review untuk akses, clash, support interface dan constructability; pastikan keterbatasan model, toleransi dan cakupan tertera.

**Gate:** satu pilot equipment-to-line dapat ditelusuri pada dokumen terkait, termasuk satu perubahan nozzle dan konsekuensinya; isu yang membutuhkan perhitungan piping/mechanical tetap open sampai diverifikasi engineer.

### Fase 4 — Instrument, control dan process safety

**Tujuan:** membuat interface fungsi kontrol dan keselamatan dapat ditelusuri.

- Bangun instrument index, I/O dan loop reference dari data yang disetujui; tampilkan `sensor → logic/controller → final element → action` beserta referensi P&ID/C&E/SRS dan interface vendor.
- Buat C&E drafting, alarm/trip dan safety-function registers dengan status bukti, independensi dan keputusan manusia; bedakan BPCS, SIS dan protection lain. Jangan menyimpulkan SIL atau independensi hanya dari tag/simbol.
- Siapkan interface relief, flare/blowdown, fire and gas dan hazardous-area study; catat pressure scenarios, tujuan disposal dan kebutuhan calculation/vendor sebagai open item bila belum tersedia.

**Gate:** satu loop kontrol dan satu fungsi shutdown ditelusuri antar P&ID, index, C&E dan vendor interface; seluruh keputusan keselamatan memiliki pemilik, sumber dan verifikasi manusia.

### Fase 5 — Electrical, civil/structural dan pendukung

**Tujuan:** memvalidasi beban dan interface lintas disiplin untuk pilot yang sama.

- Electrical: hubungkan equipment/driver ke load list, power supply dan SLD draft; klasifikasi area, starting, critical loads, UPS dan ratings berdasar data yang disetujui.
- Civil/structural: hubungkan koordinat, elevasi, equipment/support loads, foundation, access dan geotechnical basis; perhitungan desain tetap di alat dan proses disiplin masing-masing.
- Kembangkan interface corrosion/materials, pipeline, telecom dan fire & gas berdasarkan prioritas proyek; jangan mengasumsikan scope atau geoteknik dari simbol.

**Gate:** pilot mencocokkan satu driver P&ID ↔ equipment list ↔ load list ↔ SLD serta satu equipment ↔ loads ↔ foundation interface; mismatch dan sumber revisi tercatat.

### Fase 6 — Pilot end-to-end, distribusi dan operasi berkelanjutan

- Jalankan satu kasus end-to-end dari basis → PFD → P&ID → datasheet → piping/model → instrument/C&E → electrical/civil interface, sesuai data yang tersedia. Lakukan review independen dan uji perubahan satu parameter terhadap artefak terkait.
- Paketkan dokumentasi, versi tool/skill, contoh, hasil uji dan cara instalasi; verifikasi distribusi dari repo ke workstation terisolasi, termasuk rollback dan hak akses. Data kredensial/komersial tidak masuk repo.
- Dokumentasikan known limitations, support owner dan mekanisme menerima temuan. Validasi dampak perubahan setiap kali referensi standar, helper, skill atau baseline proyek diperbarui.

**Gate:** tim lintas disiplin menerima hasil pilot dan catatan gap; tidak ada item keselamatan berstatus selesai tanpa bukti dan persetujuan pemiliknya. Ekspansi disiplin dan penggunaan proyek nyata diputuskan berdasarkan hasil pilot.

## 5. Prinsip review dan penerimaan

1. Tiap deliverable memiliki nomor, revisi, status, batas ruang lingkup, sumber, author, checker dan approver sesuai proses proyek. AI tidak menandatangani sebagai engineer yang telah menyetujui desain.
2. Temuan memiliki ID, lokasi, fakta terlihat, implikasi, tingkat dampak, keyakinan bukti, rekomendasi, owner, status dan referensi; `TBD` yang berpotensi berdampak tinggi tidak diturunkan hanya karena dokumen pendukung belum tersedia.
3. Bukti dan persetujuan dibedakan: linter/tes = cakupan otomatis; visual = keterbacaan dan geometri yang diamati; cross-check = atribut yang benar-benar dibandingkan; engineer/vendor = keputusan disiplin dalam batas otoritas mereka.
4. Setiap gambar P&ID/piping/iso mengikuti `AGENTS.md`: skill perusahaan + dxf, build → apply_text → validasi → snapshot → visual review independen; revisi dan deviasi dicatat. Laporan sisa keterbatasan dan layer yang tidak tercakup harus terlihat.
5. HAZOP/HAZID, relief sizing, SIL/LOPA, electrical protection, vessel design, structural calculations, material selection dan persetujuan IFC memerlukan proses, data dan penanggung jawab yang sesuai; roadmap tidak mengotomatisasi klaimnya.

## 6. Prioritas, pemilik dan ukuran keberhasilan

| Prioritas | Pekerjaan | Pemilik yang diperlukan | Bukti selesai |
|---|---|---|---|
| P0 | Baseline dokumen, konflik design basis, status demo dan kepemilikan | Project engineering + Process + document control | Register versi dan keputusan konflik; asumsi/TBD dapat ditelusuri. |
| P1 | Data bersama dan QA, termasuk layer minor serta risiko/bukti review | Tooling + Process/Piping + QA | Fixture positif/negatif; laporan cakupan dan dampak perubahan pada dokumen. |
| P2 | PFD/P&ID mendalam; pilot metering dan kompresor | Process + Metering + Machinery + Instrument + Safety | Trace functions, catatan standar/kontrak, review independen dan daftar gap terbuka. |
| P3 | Integrasi nozzle/line, mechanical dan model | Piping + Mechanical + Structural | Pilot perubahan lintas P&ID/datasheet/model/plan dapat ditelusuri. |
| P4 | Instrument/SIS serta interface listrik dan sipil | Instrument + Safety + Electrical + Civil/Structural | Pilot loop/C&E, driver/load/SLD, equipment/load/foundation terhubung. |
| P5 | Pilot menyeluruh dan distribusi skill/tool | Engineering leads + QA + IT/document control | Laporan pilot, tes distribusi, keterbatasan dan keputusan ekspansi. |

Urutan adalah dependensi yang direkomendasikan, bukan jadwal kalender. Aktivitas disiplin dapat berjalan paralel setelah input bersama disepakati. Ukuran utama: keterlacakan dan penyelesaian temuan kritis berdasarkan bukti; penghematan waktu/token baru diukur setelah baseline kualitas ditetapkan. Tidak menjanjikan “zero-defect”.

## 7. Keputusan yang perlu disepakati untuk memulai

1. Pilih pilot terpadu: V-101 existing atau salah satu contoh metering/kompresor; tetapkan apakah demo terhubung dengan plant dan sumber data yang berlaku.
2. Tentukan disiplin tahap pertama dan engineering lead/checker untuk masing-masing; tentukan sumber standar berlisensi, sistem penyimpanan dan kewenangan persetujuan.
3. Tentukan apakah model data/referensi dipakai hanya untuk contoh atau untuk project deliverables, serta format dan kebijakan revisi/change control.
4. Setelah scope dan sumber tersedia, uraikan fase prioritas menjadi backlog terukur dengan estimasi yang disepakati; roadmap ini belum mengasumsikan biaya atau tanggal selesai.

## 8. Langkah pertama yang dapat dieksekusi

Mulai dari **Fase 0 dan Fase 1**: inventaris baseline; daftar konflik dan data yang hilang; rancangan kecil register lintas disiplin; proof-of-concept pada satu jalur V-101; cakupan validator minor dan tes regresi. Laporkan opsi dan bukti sebelum memperluas template atau skill ke disiplin lain. Pertahankan gambar dan perubahan pengguna yang ada selama inventaris.
