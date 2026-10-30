# Paket skill Windows untuk OpenCode

Ekstrak ZIP seluruhnya dan simpan folder `gpf-windows` di lokasi yang dapat ditulis. Paket memuat skill perusahaan, referensi template generator, pustaka CAD dan tools. `manifest.json` memuat revisi sumber dan SHA-256 tiap berkas. Contoh template berada di `skills/skills-patches/dxf-company/references/generator-templates.md`.

## Prasyarat dan instalasi

Windows 10/11, PowerShell, OpenCode dan uv diperlukan. Install uv dengan `winget install --id astral-sh.uv`, lalu buka terminal baru. Instal OpenCode sesuai dokumentasi resminya. Internet diperlukan saat unduhan dependensi pertama.

```powershell
cd gpf-windows
powershell -ExecutionPolicy Bypass -File skills\install\install-windows.ps1 -RunSelfTest
```

Skill dipasang di `%USERPROFILE%\.agents\skills`. Installer menolak menimpa direktori yang tidak memiliki penanda paket; cadangkan dan pindahkan instalasi sebelumnya secara manual sebelum pemasangan. Jalankan ulang installer untuk memperbarui skill yang dipasang paket ini. Gunakan `-Uninstall` untuk menghapus hanya direktori bertanda paket.

Jalankan OpenCode dari root proyek yang memiliki `AGENTS.md` dan basis desainnya sendiri. Minta agent membaca kedua skill; referensi template menjelaskan generator. Tools tersedia di folder `tools`; sebagian memerlukan konfigurasi dan dokumen proyek. Untuk dependensi tools gunakan Python virtual environment dan `pip install -r requirements.txt`. CAD opsional dijelaskan di `DEPENDENCIES.md`.

Jika `uvx` tidak ditemukan, instal uv dan buka terminal baru. Jika unduhan gagal, periksa koneksi atau proxy. Self-test menggunakan cadgen 0.7.21 dan dapat memerlukan unduhan besar. Paket tidak mencakup basis desain atau gambar proyek; jangan gunakan tag atau data demo sebagai data proyek.

## Membuat ulang ZIP dari repository

Pada mesin pembuat paket, jalankan `python skills/install/build-package.py`. Hasilnya `dist/gpf-windows-skills.zip`. Generator memilih aset tercatat Git dan membaca isi working tree; hash di manifest menunjukkan isi sebenarnya. Periksa perubahan lokal sebelum distribusi.
