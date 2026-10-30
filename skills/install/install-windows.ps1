# ============================================================================
# install-windows.ps1 - Installer skill CAD perusahaan untuk engineer Windows
# Proyek : gas-prod-facility (opencode / agent lain yang membaca AGENTS.md)
# Sifat  : idempoten (aman dijalankan ulang untuk sinkronisasi versi baru).
# Pakai  : powershell -ExecutionPolicy Bypass -File skills\install\install-windows.ps1
#          -RunSelfTest  : sekalian uji import pustaka via uvx (unduh cadgen saat pertama)
#          -Uninstall    : hapus salinan skill dari profil pengguna
# ============================================================================

param(
    [switch]$Uninstall,
    [switch]$RunSelfTest
)

$ErrorActionPreference = "Stop"

# --- Lokasi sumber (repo) ---
$repo       = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)   # root repo
$srcCompany = Join-Path $repo "skills\company-cad-standard"
$srcPatches = Join-Path $repo "skills\skills-patches"
$srcDxfSnap = Join-Path $srcPatches "dxf-company"     # snapshot skill dxf versi perusahaan

# --- Lokasi tujuan (profil pengguna; sama dengan konvensi Linux/macOS) ---
$homeDir     = $env:USERPROFILE
$agentsDir   = Join-Path $homeDir ".agents\skills"
$patchesDir  = Join-Path $homeDir "skills-patches"
$dstCompany  = Join-Path $agentsDir "company-cad-standard"
$dstDxf      = Join-Path $agentsDir "dxf"

function Copy-Tree {
    param([string]$Src, [string]$Dst)
    if (-not (Test-Path $Src)) { throw "Sumber tidak ditemukan: $Src" }
    if (Test-Path $Dst) {
        if (-not (Test-Path (Join-Path $Dst ".gpf-installed"))) { throw "Direktori sudah ada dan bukan milik paket: $Dst. Cadangkan atau pindahkan dahulu." }
        Remove-Item -Recurse -Force $Dst
    }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Dst) | Out-Null
    Copy-Item -Recurse -Force $Src $Dst
    Set-Content (Join-Path $Dst ".gpf-installed") "GPF package"
}

if ($Uninstall) {
    Write-Host "==> Menghapus salinan skill dari profil pengguna..."
    foreach ($d in @($dstCompany, $dstDxf, (Join-Path $patchesDir "company-cad-standard"), (Join-Path $patchesDir "dxf-company"))) {
        if ((Test-Path $d) -and (Test-Path (Join-Path $d ".gpf-installed"))) { Remove-Item -Recurse -Force $d; Write-Host "    dihapus: $d" }
    }
    Write-Host "OK - uninstall selesai (repo tidak disentuh)."
    exit 0
}

foreach ($d in @($dstCompany, $dstDxf, (Join-Path $patchesDir "company-cad-standard"), (Join-Path $patchesDir "dxf-company"))) {
    if ((Test-Path $d) -and -not (Test-Path (Join-Path $d ".gpf-installed"))) { throw "Direktori sudah ada dan bukan milik paket: $d. Cadangkan atau pindahkan dahulu." }
}

Write-Host "==> Memasang skill company-cad-standard -> $dstCompany"
Copy-Tree $srcCompany $dstCompany

Write-Host "==> Memasang skill dxf (snapshot versi perusahaan) -> $dstDxf"
# Menimpa hasil 'npx skills add earthtojake/text-to-cad' bila ada - itulah gunanya patch.
Copy-Tree $srcDxfSnap $dstDxf

Write-Host "==> Menyimpan salinan patch ke $patchesDir (cadangan + basis sinkronisasi ulang)"
Copy-Tree $srcCompany (Join-Path $patchesDir "company-cad-standard")
Copy-Tree $srcDxfSnap (Join-Path $patchesDir "dxf-company")

# --- Verifikasi struktur ---
foreach ($f in @(
    (Join-Path $dstCompany "SKILL.md"),
    (Join-Path $dstCompany "scripts\validate_cad_rules.py"),
    (Join-Path $dstDxf "SKILL.md"),
    (Join-Path $dstDxf "scripts\apply_text.py")
)) {
    if (-not (Test-Path $f)) { throw "Verifikasi gagal - tidak ada: $f" }
}
Write-Host "OK - struktur skill terverifikasi."

# --- Verifikasi import pustaka (opsional; butuh uv, unduh cadgen saat pertama) ---
if ($RunSelfTest) {
    if (Get-Command uvx -ErrorAction SilentlyContinue) {
        $libs = Join-Path $dstCompany "scripts"
        Write-Host "==> Uji import pustaka via uvx (cadgen==0.7.21; unduhan pertama agak lama)..."
        uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.21 python -c "import sys; sys.path.insert(0, r'$libs'); import validate_cad_rules, apply_text, pid_common, plan_common, iso_common; print('IMPORT OK')"
        if ($LASTEXITCODE -ne 0) { throw "Uji import gagal - periksa instalasi uv / koneksi." }
    } else {
        throw "uvx tidak ditemukan - install uv dulu (lihat INSTALL-ENGINEER.md)."
    }
}

Write-Host ""
Write-Host "SELESAI. Ringkasan:"
Write-Host "  - Skill terpasang di : $dstCompany"
Write-Host "                        $dstDxf"
Write-Host "  - Cadangan patch di  : $patchesDir"
Write-Host "  - Jalankan opencode dari root repo agar AGENTS.md proyek termuat otomatis."
Write-Host "  - Setelah git pull / skill diperbarui, jalankan ulang installer ini (idempoten)."
Write-Host "  - Panduan lengkap    : skills\install\INSTALL-ENGINEER.md"
