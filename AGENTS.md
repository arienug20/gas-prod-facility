# AGENTS.md — GAS PRODUCTION FACILITY (PROYEK GPF)

Aturan proyek ini lebih spesifik dan MENANG atas AGENTS.md global untuk
pekerjaan di dalam folder ini.

## Drawing discipline (P&ID, piping plan, isometric)

1. **WAJIB memuat skill `company-cad-standard`** (~/.agents/skills/
   company-cad-standard/SKILL.md) SETIAP kali membuat/merevisi drawing,
   bersama skill `dxf` (yang sudah DIPATCH perusahaan — bila SKILL-nya
   belum berisi seksi "Company standard override", jalankan
   `~/skills-patches/reapply.sh` dulu). Aturan perusahaan (ringkas):
   - **Teks = entity MTEXT** (style ARIAL, tinggi 0,5–3,0 mm; equipment
     2,5–3,0; line number 1,5–2,0; flow from/to 1,8–2,3) via manifest
     `TEXTS` + post-processor `cad/apply_text.py`. DILARANG outline
     bd.Text pada drawing engineering.
   - Persilangan garis: garis MINOR di-break (gap 3 mm), MAJOR process
     line selalu tampil utuh.
   - Lineweight per jenis line (major 0,50 mm; minor 0,13–0,25 mm)
     dipasang `apply_text.py` (MTEXT + pens sekali jalan).
   - Teks dilarang bertabrakan dengan line/teks/equipment/valve.
   - Setiap line proses wajib punya panah aliran.
2. Urutan build per drawing: build → `apply_text.py` (MTEXT + pens) →
   validasi (0 error) → snapshot → visual check (subagent pembaca gambar).
3. Pilih konfigurasi proyek aktif dan baca design basis, HMB bila ada, serta
   sumber/revisi yang berlaku sebelum menentukan tag, line, koordinat, elevasi,
   dan data proses. Repo GPF ini menggunakan `project.gpf.json`, yang menunjuk
   ke `dokumen/01-design-basis.md`; proyek lain wajib memakai basisnya sendiri.
   Bila basis/HMB atau data yang dibutuhkan belum tersedia, tanyakan data primer
   yang relevan; catat asumsi, TBD dan konflik dengan sumber serta owner. Gunakan
   asumsi/keluaran parsial hanya dalam lingkup yang diotorisasi secara eksplisit.
   Konflik dengan basis yang berlaku dicatat sebagai deviation, bukan diubah diam-diam.
   Tag proyek hanya dibuat mengikuti aturan/alokasi yang disetujui; tag demo
   sementara harus jelas bukan tag proyek dan tidak masuk registry proyek.
4. Kontrol revisi: bump REV pada title block + rev table (A0→A1→…; B0 IFC;
   C0 as-built) dengan keterangan perubahan.

## Struktur folder

- `dokumen/` — design basis, plan, review log (Markdown).
- `cad/` — script sumber `.py`, hasil `.dxf`, snapshot `.png`, helper.
- `skills/` — salinan in-repo skill perusahaan (identik dengan yang
  terpasang di `~/.agents/skills/`); boleh dimuat dari sini bila workstation
  belum menjalankan installer.

## Instalasi workstation (Windows / opencode / lainnya)

- **Windows**: `powershell -ExecutionPolicy Bypass -File
  skills\install\install-windows.ps1` (idempoten; `-RunSelfTest` untuk uji
  import pustaka, `-Uninstall` untuk menghapus). Panduan lengkap:
  `skills/install/INSTALL-ENGINEER.md`.
- **Linux/macOS**: `bash skills/skills-patches/reapply.sh`.
- Bila skill `dxf` terpasang belum berisi seksi "Company standard override"
  (tertimpa `npx skills add`), jalankan ulang installer di atas.

## Keamanan informasi

Sesuai AGENTS.md global: jangan sertakan kredensial/data komersial lain ke
dokumen proyek ini.
