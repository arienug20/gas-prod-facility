# Kompresi sentrifugal 50 MMSCFD — basis dan deviasi contoh

`GPF-DEMO-PID-COMP-50`, Rev A0, adalah drawing konsep untuk evaluasi CAD;
belum diverifikasi oleh engineer atau vendor, bukan untuk konstruksi/operasi.
Ini adalah paket terpisah, di luar design basis GPF-00-DB-0001; seluruh
identitas, label, dan sambungan digunakan untuk demonstrasi, bukan tie-in
ke fasilitas yang ada.

## Basis yang diminta dan interpretasi yang belum dikonfirmasi

- Dua train paralel 2 × 50%, 50 MMSCFD total, diinterpretasikan sebagai
  25 MMSCFD per train; kondisi referensi standard volume belum ditetapkan.
- Tekanan inlet 300 psi dan outlet 450 psi: basis psig atau psia harus
  ditetapkan. Rasio tekanan tidak dihitung hingga basis tekanan absolut jelas.
- Rentang 60–110% diasumsikan terhadap nominal per train, sebagai **target**,
  belum dibuktikan sebagai rentang stabil, deliverability atau performa aman.
- Komposisi gas kompresor, temperatur, Z, molecular weight, pengotor dan
  parameter proses tidak ditetapkan; gas custody meter tidak diasumsikan sama.

## Cakupan dan hal yang masih perlu engineering

- Tiap train menunjukkan scrubber suction, keluaran liquid menuju interface
  TBD dengan LT/LIC/LV, LSHH dan referensi ESD, kompresor, check valve, dan
  recycle anti-surge. Gas outlet scrubber berasal dari ruang atas demister.
- PSV scrubber, ukuran dan set pressure ditampilkan TBD; jalur relief,
  pressure drop, backpressure, semua skenario serta kebutuhan proteksi sisi
  discharge masih harus dianalisis. Tidak ada analisis API 520/521 di sini.
- Recycle diambil dari discharge sebelum check dan kembali setelah SDV ke
  inlet scrubber. ASV digambarkan fail-open sebagai asumsi konsep; studi
  kapasitas valve, dinamika, sumber energi dan filosofi keselamatan masih TBD.
- PT/TT/FT dihubungkan ke UIC melalui referensi tag. ESD ditunjukkan sebagai
  referensi fungsi; cause-and-effect, integritas dan independensi sensor,
  logika serta trip motor harus dirancang dan diverifikasi. PSHH ditampilkan
  di sisi kompresor sebelum check valve. PSHH/trip bukan pengganti PSV:
  proteksi relief untuk segmen discharge terisolasi harus ditetapkan melalui
  studi overpressure tersendiri dan belum disediakan pada gambar ini.
- Detail vendor seal gas, lube oil, cooling, drain, blowdown, driver, instrument
  air, shutdown isolation dan interlock hanya berupa interface/ruang lingkup.
  Liquid bukan disalurkan secara otomatis ke flare. Tidak ada ukuran line,
  kelas material, desain P/T, equipment rating atau bukti sour-service.
- Komponen menunjukkan konsep P&ID, bukan pernyataan sertifikasi atau
  kesesuaian standar. Pemeriksaan CAD tidak memvalidasi desain proses.
