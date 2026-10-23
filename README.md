# Gas Production Facility (GPF) — CAD Suite & AI Engineering Standards

Repositori lengkap fasilitas produksi gas (*Onshore Gas Production Facility*), mencakup seluruh dokumen perancangan, model 3D, gambar teknik 2D (P&ID, Piping Plan, Isometrik), pustaka CAD (`cadgen`), skrip audit mutu (*linter*), serta seluruh paket keahlian AI (*company-cad-standard*).

---

## 📁 Struktur Repositori

```text
gas-prod-facility/
├── AGENTS.md                   # Aturan kerja & SOP AI Project Manager Oil & Gas
├── cad/                        # Script Python cadgen, file DXF, PNG, dan manifest JSON
│   ├── pid_v101.py             # P&ID 3-Phase Separator V-101 Rev A4 (ISO 10628 & ISA-5.1)
│   ├── pid_common.py           # Pustaka modul simbol P&ID, PFD, & macro stasiun
│   ├── plan_common.py          # Pustaka modul perpipaan tampak atas & grid plant
│   ├── iso_common.py           # Pustaka isometrik true 30°/150°/90° (ISO 6412-2)
│   ├── validate_cad_rules.py   # Linter QA geometris 6-pillar & cross-discipline checker
│   ├── apply_text.py           # Post-processor injeksi MTEXT Arial & layer lineweight
│   ├── routing_plan.py         # Piping Plan area separator ke flare & storage tank
│   └── iso_*.py                # 3 Lembar Isometrik Pipa (GO-1002, CO-1003, CO-1004)
├── dokumen/                    # Dokumen teknis perencanaan & catatan engineering
│   ├── 01-design-basis.md      # Basis desain proses & mekanikal fasilitas
│   ├── 02-plan-pid.md          # Konsep awal P&ID
│   ├── 03-plan-routing.md      # Konsep routing pipa
│   ├── 04-review-log.md        # Log review teknis & catatan QA
│   ├── 05-plan-iso-true.md     # Perancangan isometrik presisi ISO 6412-2
│   ├── 06-plan-pid-true.md     # Perancangan P&ID standar ANSI/ISA-5.1
│   ├── 07-plan-process-piping-cad-suite.md # Arsitektur paket linter & pustaka
│   └── 08-plan-pipeline-metering-lbcv-underground.md # Rencana modul lanjutan
├── handoff/                    # Paket deliverable terpadu serah terima proyek
│   ├── HANDOFF.md              # Lembar serah terima teknis
│   ├── 01-dokumen/             # Salinan dokumen perancangan
│   ├── 02-standar/             # Salinan standar drafting perusahaan
│   ├── 03-drawing/             # Seluruh file DXF & PNG resolusi tinggi
│   ├── 04-model-3d/            # Model 3D STEP & render
│   └── 05-skrip/               # Script generator
├── skills/                     # Paket AI Skills & Patches Perusahaan Lengkap
│   ├── company-cad-standard/   # Master skill company-cad-standard
│   │   ├── SKILL.md            # Aturan drafting, font Arial, lineweight, & QA
│   │   ├── references/         # Buku panduan P&ID, Plan, & Isometrik
│   │   └── scripts/            # Pustaka Python, linter, & unit tests
│   └── skills-patches/         # Script instalasi & patch environment workstation
│       └── reapply.sh          # One-click installer sinkronisasi ke ~/.agents/skills/
├── src/                        # Script utilitas ekspor multi-sheet isometrik & 3D
├── step/                       # File model 3D mekanikal (piping_3d.step)
└── render/                     # Gambar render 3D close-up bejana & pompa
```

---

## 🚀 Cara Menjalankan & Validasi

### 1. Build Drawing CAD (Python 3.13 / cadgen)
```bash
PY="uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.21 python"
CG="uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.21 cadgen"

# Build P&ID Rev A4
$PY cad/pid_v101.py --force
$PY cad/apply_text.py cad/pid_v101.dxf cad/pid_v101.texts.json
$CG dxf snapshot cad/pid_v101.dxf cad/pid_v101.png --width 2400 --height 1700
```

### 2. Audit Mutu dengan Linter (Zero-Defect Enforcement)
```bash
# Validasi geometri P&ID
$PY cad/validate_cad_rules.py cad/pid_v101.dxf

# Cross-Check Lintas Disiplin (P&ID vs Isometrik & Piping Plan)
$PY cad/validate_cad_rules.py --cross-check cad/pid_v101.texts.json cad/iso_go1002.texts.json cad/iso_co1003.texts.json cad/iso_co1004.texts.json cad/routing_plan.texts.json
```

### 3. Pasang Skill ke Workstation Engineer Lain
```bash
bash skills/skills-patches/reapply.sh
```
