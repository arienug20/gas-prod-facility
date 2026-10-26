# skills-patches — company patch untuk skill `dxf` (text-to-cad)

## Latar

Skill `dxf` hasil instalasi text-to-cad (~/.agents/skills/dxf) dipatch agar
sesuai **standar drafting perusahaan** untuk drawing engineering
(P&ID, piping plan, isometric). Patch disimpan di sini karena
`npx skills add earthtojake/text-to-cad#latest` MENIMPA folder skill —
setelah update, jalankan `./reapply.sh`.

## Isi folder

| Path | Fungsi |
|---|---|
| `dxf-pristine/` | Salinan skill dxf SEBELUM dipatch (10 Okt 2026, cadgen 0.7.19) — untuk diff/migrasi |
| `dxf-company/SKILL.md` | SKILL.md versi perusahaan |
| `dxf-company/references/generator-templates.md` | template + pola manifest MTEXT |
| `dxf-company/scripts/apply_text.py` | post-processor MTEXT (style ARIAL) + DIMENSION (dengan `oblique_angle`) + SOLID + layer pens, idempoten |
| `dxf-company/scripts/iso_common.py` | library bersama True Piping Isometric (30°/150°/90°), simbol ISO 6412-2 / ISO 10628-2, dan furniture 3-kolom FNKT-10 |
| `company-cad-standard/` | backup lengkap skill `company-cad-standard` (`SKILL.md`, `scripts/iso_common.py`, `references/isometric-guide.md`) |
| `reapply.sh` | mengembalikan patch `dxf` dan `company-cad-standard` setelah `npx skills add` |

## Perubahan vs pristine (ringkas)

1. Kontrak teks dipecah: CAM cut/marking = outline bd.Text (asli upstream);
   **engineering drawing = entity MTEXT** via `scripts/apply_text.py`
   (style ARIAL, tinggi 0,5–3,0 mm per kategori).
2. Seksi baru "Company standard override": break persilangan (minor
   di-break gap 3 mm, major selalu tampil), lineweight per layer,
   larangan tabrakan teks, flow arrow semua line proses, rantai build
   wajib build → apply_text → validate → snapshot → visual, kontrol revisi.
3. Blok Tool + seksi Validation ditambah (apply_text step + QA MTEXT:
   jumlah == manifest, style ARIAL, tinggi dalam range, tanpa entity TEXT).
4. generator-templates.md: pola `TEXTS` manifest + penanganan build no-op
   (jangan menimpa manifest baik dengan list kosong).

## Prosedur update text-to-cad

```bash
npx skills add earthtojake/text-to-cad#latest -g -a opencode -y
~/skills-patches/reapply.sh
# lalu uji: uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.19 \
#   python ~/.agents/skills/dxf/scripts/apply_text.py <uji>.dxf <uji>.texts.json
```

Bila upstream mengubah SKILL.md/generator-templates.md secara substansial,
diff dulu terhadap `dxf-pristine/` (`diff -ru dxf-pristine dxf-company`)
dan merge manual ke `dxf-company/` sebelum re-apply.


## Windows (opencode / engineer lain)

Untuk workstation Windows gunakan installer PowerShell (setara `reapply.sh`,
ikut memasang snapshot `dxf-company` lengkap sehingga tidak perlu `npx`):

```powershell
powershell -ExecutionPolicy Bypass -File skills\install\install-windows.ps1 [-RunSelfTest]
```

Panduan lengkap (prasyarat uv/opencode, perintah harian, troubleshooting):
`skills/install/INSTALL-ENGINEER.md`.
