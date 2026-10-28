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
    {"id": "ISA-TR5.1.02", "title": "Instrumentation symbols technical report candidate", "status": "NOT ASSESSED", "edition": None, "review_evidence": None},
    {"id": "ISA-TR5.1.03", "title": "Instrumentation symbols technical report candidate", "status": "NOT ASSESSED", "edition": None, "review_evidence": None},
    {"id": "ISO-15519", "title": "Specification for diagrams for process industry", "status": "NOT ASSESSED", "edition": None, "review_evidence": None},
    {"id": "ISO-14617", "title": "Graphical symbols for diagrams", "status": "NOT ASSESSED", "edition": None, "review_evidence": None},
    {"id": "PIP-PIC001", "title": "PIP P&ID documentation criteria (adoption candidate)", "status": "NOT ASSESSED", "edition": None, "review_evidence": None},
    {"id": "IEC-61511", "title": "Functional safety — safety instrumented systems", "status": "NOT ASSESSED", "edition": None, "review_evidence": None},
]

COMPANY_RULES = [
    {"id": "company.text.native_mtext", "category": "drafting", "source": "AGENTS.md", "rule": "Drawing text uses native MTEXT, ARIAL, manifest plus cad/apply_text.py; outlined bd.Text is prohibited.", "status": "INVENTORIED"},
    {"id": "company.text.height", "category": "drafting", "source": "AGENTS.md", "rule": "Text height 0.5–3.0 mm; equipment 2.5–3.0 mm, line number 1.5–2.0 mm, flow from/to 1.8–2.3 mm.", "status": "INVENTORIED"},
    {"id": "company.crossing.minor_gap", "category": "drafting", "source": "AGENTS.md", "rule": "Minor line crossing gap 3 mm; major process lines remain continuous.", "status": "INVENTORIED"},
    {"id": "company.lineweight", "category": "drafting", "source": "AGENTS.md", "rule": "Major lineweight 0.50 mm; minor 0.13–0.25 mm, applied by post-processor.", "status": "INVENTORIED"},
    {"id": "company.flow.arrow", "category": "drafting", "source": "AGENTS.md", "rule": "Every process line has a flow arrow.", "status": "INVENTORIED"},
    {"id": "company.qa.lifecycle", "category": "workflow", "source": "AGENTS.md", "rule": "Build, apply_text, zero-error validation, snapshot, independent visual check.", "status": "INVENTORIED"},
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
        return {"path": relative, "sha256": None, "status": "MISSING", "known_limitations": ["Artifact absent at inventory time."]}
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    limits = []
    if relative.endswith("01-design-basis.md"):
        limits.append("Recorded as provenance only; no project tag/value payload is copied into this report.")
    if relative == "cad/pid_config_builder.py":
        limits.append("Static source indicates cadshim/ezdxf authoring and an optional isolated cadgen validation path; availability/performance was not probed by this inventory.")
    if relative == "cad/smart_qa.py":
        limits.append("Model checks validate supplied ports/connections; this does not establish complete assembly-internal valve semantics.")
    return {"path": relative, "sha256": digest, "status": "PRESENT_STATIC_REVIEW", "known_limitations": limits}


def build_baseline(repo_root: str | Path) -> dict[str, Any]:
    """Inventory selected sources without importing or executing CAD generators."""
    root = Path(repo_root).resolve()
    if not root.is_dir():
        raise ValueError(f"repo root is not a directory: {root}")
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
            "authoring": {"value": "cadshim/ezdxf", "evidence": "cad/pid_config_builder.py static source", "status": "SOURCE_OBSERVED_NOT_RUNTIME_VERIFIED"},
            "validation": {"value": "optional isolated cadgen validation path; cad/apply_text.py imports cadgen.drawing_checks", "evidence": "cad/pid_config_builder.py and cad/apply_text.py static source", "status": "AVAILABILITY_NOT_ASSESSED"},
            "snapshot": {"value": "cadshim/ezdxf-matplotlib when requested", "evidence": "cad/pid_config_builder.py static source", "status": "SOURCE_OBSERVED_NOT_RUNTIME_VERIFIED"},
        },
        "limitations": [
            "No network standards text was consulted; no edition, clause, applicability, adoption, or compliance claim is made.",
            "No CAD generator, validator, or drawing was executed or modified.",
            "Symbol inventory and symbol-to-standard mappings remain unassessed because this tranche records no approved symbol catalog evidence.",
            "Historical test totals in phase reports are not current test results.",
        ],
    }


def validate_catalog(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    """Return deterministic findings for structural/evidence gaps in a catalog."""
    findings: list[dict[str, Any]] = []

    def add(rule: str, category: str, severity: str, message: str, object_ids: list[str] | None = None) -> None:
        findings.append({"rule": rule, "category": category, "severity": severity, "message": message,
                         "object_ids": object_ids or [], "location": None})

    if not isinstance(catalog, dict):
        return [{"rule": "catalog.type", "category": "schema", "severity": "error", "message": "Catalog must be an object.", "object_ids": [], "location": None}]
    if catalog.get("schema_version") != SCHEMA_VERSION:
        add("catalog.schema_version", "schema", "error", f"schema_version must be {SCHEMA_VERSION!r}.")
    for section in ("standards", "rules", "symbols", "mappings"):
        if section not in catalog:
            add("catalog.section_missing", "schema", "error", f"Required section {section!r} is missing.")
        elif isinstance(catalog[section], list) and not catalog[section]:
            add("catalog.coverage_unassessed", section, "warning", f"No {section} entries are recorded; coverage is NOT ASSESSED.")
    ids: dict[str, set[str]] = {}
    for section in ("standards", "rules", "symbols", "mappings"):
        rows = catalog.get(section, [])
        if not isinstance(rows, list):
            add("catalog.section_type", "schema", "error", f"{section} must be a list.")
            continue
        seen: set[str] = set()
        ids[section] = seen
        for i, row in enumerate(rows):
            if not isinstance(row, dict):
                add("catalog.row_type", section, "error", f"{section}[{i}] must be an object.")
                continue
            oid = row.get("id")
            if not isinstance(oid, str) or not oid.strip():
                add("catalog.missing_id", section, "error", f"{section}[{i}] has no non-empty id.")
                oid = f"{section}[{i}]"
            elif oid in seen:
                add("catalog.duplicate_id", section, "error", f"Duplicate id {oid!r}.", [oid])
            seen.add(oid)
            if section == "standards":
                source = row.get("source")
                if not isinstance(source, dict) or not _valid_evidence(source, ("locator",)):
                    add("standard.missing_source", section, "warning", f"Standard {oid} has no controlled source reference.", [oid])
                edition = row.get("edition")
                if not isinstance(edition, dict) or not isinstance(edition.get("designation"), str) or not edition.get("designation", "").strip() or not _valid_evidence(edition, ("locator",)):
                    add("standard.missing_edition", section, "warning", f"Standard {oid} edition is unknown.", [oid])
                review = row.get("review_evidence")
                if not isinstance(review, dict) or not _valid_evidence(review, ("locator", "reviewer", "status")):
                    add("standard.missing_review_evidence", section, "warning", f"Standard {oid} has no review evidence.", [oid])
                elif str(review.get("status", "")).upper() != "REVIEWED":
                    add("standard.review_not_complete", section, "warning", f"Standard {oid} review status is not REVIEWED.", [oid])
                if isinstance(source, dict) and _valid_evidence(source, ("locator",)) or isinstance(review, dict) and _valid_evidence(review, ("locator", "reviewer", "status")):
                    add("standard.evidence_verification_not_assessed", section, "warning", f"Standard {oid} source/content verification and applicability remain NOT ASSESSED by this metadata validator.", [oid])
            if section == "symbols" and not row.get("ports"):
                add("symbol.undefined_ports", section, "warning", f"Symbol {oid} has no defined ports; semantics remain unknown.", [oid])
            if section == "mappings" and not isinstance(row.get("support_evidence"), dict):
                add("mapping.unsupported", section, "warning", f"Mapping {oid} lacks support evidence.", [oid])
            elif section == "mappings" and not _valid_evidence(row["support_evidence"], ("locator", "reviewer", "status")):
                add("mapping.unsupported", section, "warning", f"Mapping {oid} support evidence must include locator, reviewer, and status.", [oid])
            elif section == "mappings" and row["support_evidence"].get("status", "").upper() not in {"REVIEWED", "ACCEPTED"}:
                add("mapping.unsupported", section, "warning", f"Mapping {oid} support status must be REVIEWED or ACCEPTED.", [oid])
    standards = ids.get("standards", set())
    symbols = ids.get("symbols", set())
    for row in catalog.get("mappings", []) if isinstance(catalog.get("mappings"), list) else []:
        if not isinstance(row, dict):
            continue
        mid = row.get("id")
        for field, known in (("standard_id", standards), ("symbol_id", symbols)):
            ref = row.get(field)
            if not isinstance(ref, str) or ref not in known:
                add("mapping.dangling_reference", "mappings", "warning", f"Mapping {mid} has missing or unresolved {field}.", [str(mid), str(ref)])
    findings.sort(key=lambda f: (f["category"], f["rule"], f["object_ids"], f["message"]))
    return findings


def _valid_evidence(value: dict[str, Any], fields: tuple[str, ...]) -> bool:
    """Evidence needs structured locator/reviewer/status fields, not prose strings."""
    return all(isinstance(value.get(field), str) and bool(value[field].strip()) for field in fields)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--out", type=Path, help="JSON report path (must not already exist)")
    args = parser.parse_args()
    report = build_baseline(args.repo_root)
    report["catalog_findings"] = validate_catalog(report["catalog"])
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.out:
        out = args.out.resolve()
        if out.exists():
            parser.error("--out must be a new path; existing files are never overwritten")
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            with out.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(rendered)
        except FileExistsError:
            parser.error("--out already exists; existing files are never overwritten")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
