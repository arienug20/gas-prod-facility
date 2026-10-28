# P&ID scrubber vertikal — catatan demo dan deviasi

Drawing `GPF-DEMO-PID-SCRUBBER`, Rev A1, adalah contoh terpisah untuk
evaluasi tooling; bukan desain fasilitas dan tidak untuk konstruksi.

Design basis GPF-00-DB-0001 tidak mencakup V-901, line 9901–9904,
instrumen atau ESD-901. Identitas dan ukuran pipa pada gambar bersifat
ilustratif, tidak mengubah line list atau instrument index proyek. Tidak
ada data operasi, desain vessel, kapasitas, material, ukuran dan set PSV,
atau filosofi disposal yang disetujui. Semua ini harus ditetapkan sebelum
gambar dipakai sebagai dasar engineering.

Rev A1 memperjelas koneksi PSV di top, level bridle, jalur kontrol level
dan konsep shutdown LSHH → ESD → SDV. ESD-901 di atas SDV adalah referensi
fungsi yang sama dengan logic solver pada loop LSHH, bukan perangkat kedua.
Independensi sensing SIS dan BPCS, tingkat integritas, penyebab lain, serta
cause-and-effect final harus diverifikasi oleh disiplin terkait.

Satu PSV digambar untuk demonstrasi; kebutuhan PSV standby dan changeover
harus diputuskan dalam filosofi operasi dan studi relief. Penempatan PSV,
relief load, inlet pressure drop, backpressure, penyaluran flare, serta
kapasitas line dan nozzle belum dihitung. Valve fail action dan ukuran line
ditampilkan sebagai asumsi ilustratif dan belum disetujui.

Rev A0 adalah draft awal; A1 merupakan koreksi review, bukan IFC. Tidak ada
verifikasi engineering oleh pemeriksa manusia atau persetujuan desain.

Review independen GPT-6.1 Terra mengidentifikasi perbedaan lineweight minor,
tag isolasi bridle yang belum tampil, legend pneumatik, dan cap drain yang
ambigu; keempatnya dikoreksi pada A1. Layer `REF-PROC-MINOR` diberi 0,25 mm;
validator CAD belum memeriksa layer ini untuk seluruh tes crossing,
tabrakan, dan endpoint. Karena itu hasil validator bukan bukti lengkap
untuk konektivitas atau clearance pada cabang minor.
