# Panduan Instalasi — Engineer Windows (opencode / agent lain)

Panduan memasang tooling CAD perusahaan (skill `company-cad-standard` +
skill `dxf` versi perusahaan) di workstation **Windows 10/11** untuk
engineer yang bekerja dengan **opencode** atau agent CLI lain yang membaca
`AGENTS.md`. Untuk Linux/macOS gunakan `skills/skills-patches/reapply.sh`.

---

## 1. Prasyarat

| Perangkat lunak | Cara instalasi | Cek |
|---|---|---|
| **uv** (runtime Python + cadgen) | `winget install --id=astral-sh.uv` atau `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"` lalu buka terminal baru | `uvx --version` |
| **git** | `winget install --id Git.Git` | `git --version` |
| **opencode** | `npm install -g opencode-ai` (butuh Node 18+) atau `scoop install opencode` | `opencode --version` |

Catatan: snapshot gambar pertama akan mengunduh headless browser bawaan
cadgen (sekali saja, butuh internet).

## 2. Instalasi skill

```powershell
git clone https://github.com/arienug20/gas-prod-facility.git
cd gas-prod-facility

# Pasang + verifikasi struktur:
powershell -ExecutionPolicy Bypass -File skills\install\install-windows.ps1

# Sekalian uji import pustaka via uvx (unduh cadgen saat pertama, agak lama):
powershell -ExecutionPolicy Bypass -File skills\install\install-windows.ps1 -RunSelfTest
```

Installer bersifat **idempoten**: setelah `git pull` / skill diperbarui,
jalankan ulang perintah yang sama untuk sinkronisasi. Opsi `-Uninstall`
menghapus salinan dari profil (`%USERPROFILE%\.agents\skills\` dan
`%USERPROFILE%\skills-patches\`) tanpa menyentuh repo.

Yang dipasang:
1. `%USERPROFILE%\.agents\skills\company-cad-standard\` — aturan drafting +
   seluruh pustaka (pid/plan/iso common + 9 modul lanjutan) + linter + test.
2. `%USERPROFILE%\.agents\skills\dxf\` — skill dxf **versi ter-patch
   perusahaan** (snapshot lengkap; menimpa hasil `npx skills add` bila ada —
   jangan lupa jalankan ulang installer setelah update upstream).

## 3. Cara kerja dengan opencode

1. Selalu jalankan `opencode` **dari root repo** — `AGENTS.md` proyek
   (aturan SOP drawing: rantai build, MTEXT, QA) termuat otomatis sebagai
   instruksi.
2. `AGENTS.md` memerintahkan pemuatan 2 skill; keduanya kini terpasang di
   `~\.agents\skills\` (konvensi lintas agent). Bila versi opencode Anda
   tidak memuat skill dari direktori itu secara otomatis, tidak masalah —
   AGENTS.md memberi path eksplisit dan agent tinggal membaca file
   `SKILL.md` tersebut; sebagai cadangan ada juga salinan dalam repo di
   `skills\company-cad-standard\SKILL.md` dan
   `skills\skills-patches\dxf-company\SKILL.md` (isi identik).
3. Instruksi global pribadi boleh diletakkan di `~\AGENTS.md` — aturan
   proyek tetap menang untuk pekerjaan dalam repo ini.

## 4. Perintah harian (PowerShell)

```powershell
$PY = "uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.21 python"
$CG = "uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.21 cadgen"

# Build + QA satu drawing (contoh P&ID separator):
Invoke-Expression "$PY cad\pid_v101.py --force"
Invoke-Expression "$PY cad\apply_text.py cad\pid_v101.dxf cad\pid_v101.texts.json"
Invoke-Expression "$PY cad\validate_cad_rules.py cad\pid_v101.dxf cad\pid_v101.texts.json"   # harus exit 0
Invoke-Expression "$CG dxf snapshot cad\pid_v101.dxf cad\pid_v101.png --width 2400 --height 1700"
```

Rantai lengkap dan aturannya: lihat `SKILL.md` skill `company-cad-standard`
(§1–§8) dan `AGENTS.md` di root repo.

## 5. Troubleshooting

| Gejala | Solusi |
|---|---|
| `uvx` tidak dikenali | Install uv (lihat §1) lalu **buka terminal baru**. |
| Script diblokir PowerShell | Gunakan `powershell -ExecutionPolicy Bypass -File ...` seperti contoh. |
| Uji import lambat/gagal saat pertama | cadgen diunduh saat pertama; cek koneksi/proxy. Perusahaan dengan proxy: set `HTTP_PROXY`/`HTTPS_PROXY` sebelum menjalankan uvx. |
| Skill `dxf` kembali seperti upstream | Itu efek `npx skills add` menimpa — jalankan ulang installer ini. |
| Hasil validasi berbeda dengan Linux | Pastikan versi cadgen terpin `0.7.21` (perintah sudah memuatnya); jangan pakai python sistem. |
