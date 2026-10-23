#!/usr/bin/env bash
# Re-apply company patch ke skill dxf dan company-cad-standard SETELAH `npx skills add earthtojake/text-to-cad#latest`
# (installer menimpa ~/.agents/skills/dxf — patch ini mengembalikannya dan menyinkronkan seluruh artefak standar).
set -euo pipefail

SKILL="$HOME/.agents/skills/dxf"
PATCH="$HOME/skills-patches/dxf-company"
COMP_SKILL="$HOME/.agents/skills/company-cad-standard"
COMP_PATCH="$HOME/skills-patches/company-cad-standard"

if [ ! -d "$SKILL" ]; then
  echo "ERROR: $SKILL tidak ada — install dulu: npx skills add earthtojake/text-to-cad#latest" >&2
  exit 1
fi
if [ ! -d "$PATCH" ]; then
  echo "ERROR: $PATCH (hasil patch) tidak ada." >&2
  exit 1
fi
NEW_LIBS="wellhead_common.py compression_common.py powergen_common.py air_system_common.py metering_common.py lbcv_common.py underground_common.py supports_insulation_common.py alignment_sheet_builder.py"
if [ ! -d "$COMP_PATCH" ]; then
  echo "ERROR: $COMP_PATCH (company patch) tidak ada." >&2
  exit 1
fi

echo "==> Menyinkronkan artefak ke $COMP_SKILL..."
mkdir -p "$COMP_SKILL/scripts" "$COMP_SKILL/references"
cp "$COMP_PATCH/SKILL.md" "$COMP_SKILL/SKILL.md"
cp "$COMP_PATCH/references/"*.md "$COMP_SKILL/references/"
cp "$COMP_PATCH/scripts/apply_text.py" "$COMP_SKILL/scripts/apply_text.py"
cp "$COMP_PATCH/scripts/iso_common.py" "$COMP_SKILL/scripts/iso_common.py"
cp "$COMP_PATCH/scripts/pid_common.py" "$COMP_SKILL/scripts/pid_common.py"
cp "$COMP_PATCH/scripts/plan_common.py" "$COMP_SKILL/scripts/plan_common.py"
cp "$COMP_PATCH/scripts/validate_cad_rules.py" "$COMP_SKILL/scripts/validate_cad_rules.py"
chmod +x "$COMP_SKILL/scripts/validate_cad_rules.py"
for s in $NEW_LIBS; do
  cp "$COMP_PATCH/scripts/$s" "$COMP_SKILL/scripts/$s"
done
for t in "$COMP_PATCH/scripts/"test_*.py; do
  if [ -f "$t" ]; then
    cp "$t" "$COMP_SKILL/scripts/"
    chmod +x "$COMP_SKILL/scripts/$(basename "$t")"
  fi
done

echo "==> Menyinkronkan artefak ke $SKILL..."
mkdir -p "$SKILL/scripts" "$SKILL/references"
cp "$PATCH/SKILL.md" "$SKILL/SKILL.md"
cp "$PATCH/references/generator-templates.md" "$SKILL/references/generator-templates.md"
# Salin semua panduan referensi standar ke dxf skill
cp "$COMP_PATCH/references/"*.md "$SKILL/references/"
cp "$COMP_PATCH/scripts/apply_text.py" "$SKILL/scripts/apply_text.py"
cp "$COMP_PATCH/scripts/iso_common.py" "$SKILL/scripts/iso_common.py"
cp "$COMP_PATCH/scripts/pid_common.py" "$SKILL/scripts/pid_common.py"
cp "$COMP_PATCH/scripts/plan_common.py" "$SKILL/scripts/plan_common.py"
cp "$COMP_PATCH/scripts/validate_cad_rules.py" "$SKILL/scripts/validate_cad_rules.py"
chmod +x "$SKILL/scripts/validate_cad_rules.py"
for s in $NEW_LIBS; do
  cp "$COMP_PATCH/scripts/$s" "$SKILL/scripts/$s"
done
for t in "$COMP_PATCH/scripts/"test_*.py; do
  if [ -f "$t" ]; then
    cp "$t" "$SKILL/scripts/"
    chmod +x "$SKILL/scripts/$(basename "$t")"
  fi
done

# Pastikan dxf-company juga menyimpan salinan artefak sinkron
for t in "$COMP_PATCH/scripts/"test_*.py; do
  if [ -f "$t" ]; then
    cp "$t" "$PATCH/scripts/"
    chmod +x "$PATCH/scripts/$(basename "$t")"
  fi
done
cp "$COMP_PATCH/scripts/plan_common.py" "$PATCH/scripts/plan_common.py"
if [ -f "$COMP_PATCH/scripts/validate_cad_rules.py" ]; then
  cp "$COMP_PATCH/scripts/validate_cad_rules.py" "$PATCH/scripts/validate_cad_rules.py"
  chmod +x "$PATCH/scripts/validate_cad_rules.py"
fi
if [ -f "$COMP_PATCH/scripts/pid_common.py" ]; then
  cp "$COMP_PATCH/scripts/pid_common.py" "$PATCH/scripts/pid_common.py"
fi
if [ -f "$COMP_PATCH/scripts/iso_common.py" ]; then
  cp "$COMP_PATCH/scripts/iso_common.py" "$PATCH/scripts/iso_common.py"
fi
for s in $NEW_LIBS; do
  cp "$COMP_PATCH/scripts/$s" "$PATCH/scripts/$s"
done

echo "OK — company patch re-applied ke $SKILL dan $COMP_SKILL"
