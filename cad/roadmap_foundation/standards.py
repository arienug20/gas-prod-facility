"""Bounded, evidence-aware inventory for the CAD standards baseline."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"

STANDARD_CANDIDATES = [
    {"id": "ISO-10628-1", "title": "Diagrams for the chemical and petrochemical industry — Part 1", "status": "NOT ASSESSED", "edition": None, "review_evidence": None},
    {"id": "ISO-10628-2", "title": "Graphical symbols", "status": "NOT ASSESSED", "edition": None, "review_evidence": None},
    {"id": "ISA-5.1", "title": "Instrumentation Symbols and Identification", "status": "NOT ASSESSED", "edition": None, "review_evidence": None},
    {"id": "ISA-TR5.1.02", "title": "Calon laporan teknis simbol instrumentasi", "status": "NOT ASSESSED", "edition": None, "review_evidence": None},
    {"id": "ISA-TR5.1.03", "title": "Calon laporan teknis simbol instrumentasi", "status": "NOT ASSESSED", "edition": None, "review_evidence": None},
    {"id": "ISO-15519", "title": "Spesifikasi diagram untuk industri proses", "status": "NOT ASSESSED", "edition": None, "review_evidence": None},
    {"id": "ISO-14617", "title": "Simbol grafis untuk diagram", "status": "NOT ASSESSED", "edition": None, "review_evidence": None},
    {"id": "PIP-PIC001", "title": "Kriteria dokumentasi P&ID PIP (kandidat adopsi)", "status": "NOT ASSESSED", "edition": None, "review_evidence": None},
    {"id": "IEC-61511", "title": "Functional safety — safety instrumented systems", "status": "NOT ASSESSED", "edition": None, "review_evidence": None},
]

COMPANY_RULES = [
    {"id": "company.text.native_mtext", "category": "drafting", "source": "AGENTS.md", "rule": "Teks gambar menggunakan MTEXT native, ARIAL, dan manifest melalui cad/apply_text.py; bd.Text yang di-outline dilarang.", "status": "INVENTORIED"},
    {"id": "company.text.height", "category": "drafting", "source": "AGENTS.md", "rule": "Tinggi teks 0.5–3.0 mm; peralatan 2.5–3.0 mm, nomor line 1.5–2.0 mm, arah aliran from/to 1.8–2.3 mm.", "status": "INVENTORIED"},
    {"id": "company.crossing.minor_gap", "category": "drafting", "source": "AGENTS.md", "rule": "Persilangan line minor diberi gap 3 mm; line proses major tetap utuh.", "status": "INVENTORIED"},
    {"id": "company.lineweight", "category": "drafting", "source": "AGENTS.md", "rule": "Lineweight major 0.50 mm; minor 0.13–0.25 mm, diterapkan oleh post-processor.", "status": "INVENTORIED"},
    {"id": "company.flow.arrow", "category": "drafting", "source": "AGENTS.md", "rule": "Setiap line proses memiliki panah aliran.", "status": "INVENTORIED"},
    {"id": "company.qa.lifecycle", "category": "workflow", "source": "AGENTS.md", "rule": "Build, apply_text, validasi tanpa error, snapshot, dan pemeriksaan visual independen.", "status": "INVENTORIED"},
]

ARTIFACT_PATHS = [
    "AGENTS.md", "dokumen/01-design-basis.md", "dokumen/11-report-tooling-phase1.md",
    "dokumen/15-roadmap-multidisiplin.md", "dokumen/16-backlog-roadmap-bfd-pfd-pid.md",
    "cad/apply_text.py", "cad/smart_qa.py", "cad/pid_config_builder.py",
    "skills/company-cad-standard/SKILL.md", "skills/skills-patches/dxf-company/SKILL.md",
]


def _artifact(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    if not path.is_file():
        return {"path": relative, "sha256": None, "status": "MISSING", "known_limitations": ["Artefak tidak ditemukan saat inventarisasi."]}
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    limits = []
    if relative.endswith("01-design-basis.md"):
        limits.append("Dicatat hanya sebagai provenance; nilai atau tag proyek tidak disalin ke laporan ini.")
    if relative == "cad/pid_config_builder.py":
        limits.append("Sumber statis menunjukkan authoring cadshim/ezdxf dan jalur validasi cadgen terisolasi yang opsional; ketersediaan dan kinerjanya tidak diuji dalam inventarisasi ini.")
    if relative == "cad/smart_qa.py":
        limits.append("Pemeriksaan model memvalidasi port/koneksi yang diberikan; hal ini tidak membuktikan kelengkapan semantik internal valve assembly.")
    return {"path": relative, "sha256": digest, "status": "PRESENT_STATIC_REVIEW", "known_limitations": limits}


def build_baseline(repo_root: str | Path) -> dict[str, Any]:
    """Inventory selected sources without importing or executing CAD generators."""
    root = Path(repo_root).resolve()
    if not root.is_dir():
        raise ValueError(f"repo root bukan direktori: {root}")
    artifacts = [_artifact(root, rel) for rel in ARTIFACT_PATHS]
    # The candidates deliberately carry no edition or adoption assertion.
    catalog = {
        "schema_version": SCHEMA_VERSION,
        "standards": [dict(x) for x in STANDARD_CANDIDATES],
        "rules": [dict(x) for x in COMPANY_RULES],
        "symbols": [],
        "mappings": [],
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "BOUNDED_STATIC_INVENTORY",
        "artifacts": artifacts,
        "catalog": catalog,
        "backend_observations": {
            "authoring": {"value": "cadshim/ezdxf", "evidence": "sumber statis cad/pid_config_builder.py", "status": "SOURCE_OBSERVED_NOT_RUNTIME_VERIFIED"},
            "validation": {"value": "jalur validasi cadgen terisolasi opsional; cad/apply_text.py mengimpor cadgen.drawing_checks", "evidence": "sumber statis cad/pid_config_builder.py dan cad/apply_text.py", "status": "AVAILABILITY_NOT_ASSESSED"},
            "snapshot": {"value": "cadshim/ezdxf-matplotlib bila diminta", "evidence": "sumber statis cad/pid_config_builder.py", "status": "SOURCE_OBSERVED_NOT_RUNTIME_VERIFIED"},
        },
        "limitations": [
            "Tidak ada teks standar yang diambil dari jaringan; tidak ada klaim mengenai edisi, klausul, applicability, adopsi, atau compliance.",
            "Generator CAD, validator, maupun drawing tidak dijalankan atau diubah.",
            "Inventaris simbol dan mapping simbol-ke-standar belum dinilai karena tranche ini tidak mencatat bukti katalog simbol yang disetujui.",
            "Jumlah tes historis pada laporan fase bukan hasil tes terkini.",
        ],
    }


def validate_catalog(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    """Kembalikan finding deterministik untuk gap struktur/bukti dalam katalog."""
    findings: list[dict[str, Any]] = []

    def add(rule: str, category: str, severity: str, message: str, object_ids: list[str] | None = None) -> None:
        findings.append({"rule": rule, "category": category, "severity": severity, "message": message,
                         "object_ids": object_ids or [], "location": None})

    if not isinstance(catalog, dict):
        return [{"rule": "catalog.type", "category": "schema", "severity": "error", "message": "Katalog harus berupa object.", "object_ids": [], "location": None}]
    if catalog.get("schema_version") != SCHEMA_VERSION:
        add("catalog.schema_version", "schema", "error", f"schema_version harus {SCHEMA_VERSION!r}.")
    for section in ("standards", "rules", "symbols", "mappings"):
        if section not in catalog:
            add("catalog.section_missing", "schema", "error", f"Bagian wajib {section!r} tidak tersedia.")
        elif isinstance(catalog[section], list) and not catalog[section]:
            add("catalog.coverage_unassessed", section, "warning", f"Belum ada entri {section}; cakupan berstatus NOT ASSESSED.")
    ids: dict[str, set[str]] = {}
    for section in ("standards", "rules", "symbols", "mappings"):
        rows = catalog.get(section, [])
        if not isinstance(rows, list):
            add("catalog.section_type", "schema", "error", f"{section} harus berupa list.")
            continue
        seen: set[str] = set()
        ids[section] = seen
        for i, row in enumerate(rows):
            if not isinstance(row, dict):
                add("catalog.row_type", section, "error", f"{section}[{i}] harus berupa object.")
                continue
            oid = row.get("id")
            if not isinstance(oid, str) or not oid.strip():
                add("catalog.missing_id", section, "error", f"{section}[{i}] tidak memiliki id yang terisi.")
                oid = f"{section}[{i}]"
            elif oid in seen:
                add("catalog.duplicate_id", section, "error", f"Id duplikat {oid!r}.", [oid])
            seen.add(oid)
            if section == "standards":
                source = row.get("source")
                if not isinstance(source, dict) or not _valid_evidence(source, ("locator",)):
                    add("standard.missing_source", section, "warning", f"Standar {oid} tidak memiliki referensi sumber terkendali.", [oid])
                edition = row.get("edition")
                if not isinstance(edition, dict) or not isinstance(edition.get("designation"), str) or not edition.get("designation", "").strip() or not _valid_evidence(edition, ("locator",)):
                    add("standard.missing_edition", section, "warning", f"Edisi standar {oid} belum diketahui.", [oid])
                review = row.get("review_evidence")
                if not isinstance(review, dict) or not _valid_evidence(review, ("locator", "reviewer", "status")):
                    add("standard.missing_review_evidence", section, "warning", f"Standar {oid} tidak memiliki bukti review.", [oid])
                elif str(review.get("status", "")).upper() != "REVIEWED":
                    add("standard.review_not_complete", section, "warning", f"Status review standar {oid} bukan REVIEWED.", [oid])
                if isinstance(source, dict) and _valid_evidence(source, ("locator",)) or isinstance(review, dict) and _valid_evidence(review, ("locator", "reviewer", "status")):
                    add("standard.evidence_verification_not_assessed", section, "warning", f"Verifikasi sumber/isi dan applicability standar {oid} tetap NOT ASSESSED oleh validator metadata ini.", [oid])
            if section == "symbols" and not row.get("ports"):
                add("symbol.undefined_ports", section, "warning", f"Simbol {oid} tidak memiliki port yang didefinisikan; semantiknya belum diketahui.", [oid])
            if section == "mappings" and not isinstance(row.get("support_evidence"), dict):
                add("mapping.unsupported", section, "warning", f"Mapping {oid} tidak memiliki bukti pendukung.", [oid])
            elif section == "mappings" and not _valid_evidence(row["support_evidence"], ("locator", "reviewer", "status")):
                add("mapping.unsupported", section, "warning", f"Bukti pendukung mapping {oid} wajib memuat locator, reviewer, dan status.", [oid])
            elif section == "mappings" and row["support_evidence"].get("status", "").upper() not in {"REVIEWED", "ACCEPTED"}:
                add("mapping.unsupported", section, "warning", f"Status bukti pendukung mapping {oid} wajib REVIEWED atau ACCEPTED.", [oid])
    standards = ids.get("standards", set())
    symbols = ids.get("symbols", set())
    for row in catalog.get("mappings", []) if isinstance(catalog.get("mappings"), list) else []:
        if not isinstance(row, dict):
            continue
        mid = row.get("id")
        for field, known in (("standard_id", standards), ("symbol_id", symbols)):
            ref = row.get(field)
            if not isinstance(ref, str) or ref not in known:
                add("mapping.dangling_reference", "mappings", "warning", f"Mapping {mid} memiliki {field} yang hilang atau belum terselesaikan.", [str(mid), str(ref)])
    findings.sort(key=lambda f: (f["category"], f["rule"], f["object_ids"], f["message"]))
    return findings


def _valid_evidence(value: dict[str, Any], fields: tuple[str, ...]) -> bool:
    """Evidence needs structured locator/reviewer/status fields, not prose strings."""
    return all(isinstance(value.get(field), str) and bool(value[field].strip()) for field in fields)


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventaris terbatas baseline standar dan drafting CAD.")
    parser.add_argument("--repo-root", required=True, type=Path, help="Path root repository")
    parser.add_argument("--out", type=Path, help="Path laporan JSON (harus belum ada)")
    args = parser.parse_args()
    report = build_baseline(args.repo_root)
    report["catalog_findings"] = validate_catalog(report["catalog"])
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.out:
        out = args.out.resolve()
        if out.exists():
            parser.error("--out harus menunjuk path baru; file yang sudah ada tidak akan ditimpa")
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            with out.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(rendered)
        except FileExistsError:
            parser.error("--out sudah ada; file yang sudah ada tidak akan ditimpa")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
