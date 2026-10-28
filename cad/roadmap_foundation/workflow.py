"""Explicit adapter joining readiness, catalog, and graph audits without promotion."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .readiness import assess_readiness
from .registry import audit_graph
from .standards import validate_catalog

SCHEMA_VERSION = "1.0"


def _status(findings: list[dict[str, Any]]) -> str:
    """A clean bounded audit is still NOT ASSESSED for engineering acceptance."""
    return "INVALID" if any(item.get("severity") == "error" for item in findings) else "NOT ASSESSED"


def assess_package(payload: Any, catalog: Any, graph: Any, deliverable_id: str) -> dict[str, Any]:
    """Assess the three supplied sections independently; never infer missing inputs."""
    package_findings = []
    if not isinstance(payload, dict):
        package_findings.append({"rule": "package.basis_missing", "category": "schema", "severity": "error",
                                 "message": "Basis payload must be an object.", "object_ids": []})
        basis_payload = None
    else:
        basis_payload = payload
    basis_report = assess_readiness(basis_payload, deliverable_id)

    catalog_report = validate_catalog(catalog)
    graph_report = audit_graph(graph)
    if catalog is None:
        catalog_input = "MISSING"
    else:
        catalog_input = "PRESENT"
    if graph is None:
        graph_input = "MISSING"
    else:
        graph_input = "PRESENT"
    if isinstance(payload, dict):
        for key in ("schema_version", "sources", "basis_items", "authorizations", "deliverables"):
            if key not in payload:
                package_findings.append({"rule": "package.basis_section_missing", "category": "schema",
                                         "severity": "error", "message": f"Basis section {key!r} is missing.",
                                         "object_ids": []})
    if catalog_input == "MISSING":
        catalog_report = [{"rule": "catalog.section_missing", "category": "schema", "severity": "error",
                           "message": "Catalog section is missing; catalog is NOT ASSESSED.", "object_ids": [], "location": None}]
    if graph_input == "MISSING":
        graph_report = [{"rule": "graph.section_missing", "severity": "error", "assessment": "NOT ASSESSED",
                         "message": "Graph section is missing; graph is NOT ASSESSED.", "object_ids": []}]
    if catalog_input == "MISSING":
        package_findings.append({"rule": "package.catalog_missing", "category": "schema", "severity": "error",
                                 "message": "Catalog section is missing or null; catalog status remains NOT ASSESSED.",
                                 "object_ids": []})
    if graph_input == "MISSING":
        package_findings.append({"rule": "package.graph_missing", "category": "schema", "severity": "error",
                                 "message": "Graph section is missing or null; graph status remains NOT ASSESSED.",
                                 "object_ids": []})
    if not isinstance(deliverable_id, str) or not deliverable_id.strip():
        package_findings.append({"rule": "package.deliverable_id", "category": "schema", "severity": "error",
                                 "message": "deliverable_id must be a non-empty string.", "object_ids": []})
    return {
        "schema_version": SCHEMA_VERSION,
        "deliverable_id": deliverable_id,
        "package_findings": package_findings,
        "data_readiness": basis_report,
        "catalog_assessment": {"input_status": catalog_input, "status": "NOT ASSESSED" if catalog_input == "MISSING" else _status(catalog_report), "findings": catalog_report},
        "graph_assessment": {"input_status": graph_input, "status": "NOT ASSESSED" if graph_input == "MISSING" else _status(graph_report), "findings": graph_report},
        "engineering_review": {"status": "NOT ASSESSED", "findings": []},
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="package JSON with basis, catalog, graph, deliverable_id")
    parser.add_argument("--out", type=Path, help="write report to a new path; existing paths are refused")
    args = parser.parse_args(argv)
    source = args.input.resolve()
    output = args.out.resolve() if args.out else None
    if output and (output == source or output.exists() or not output.parent.is_dir()):
        parser.error("--out must be distinct from input, have an existing parent, and not already exist")
    try:
        raw = json.loads(source.read_text(encoding="utf-8"))
    except OSError as exc:
        parser.error(f"cannot read input file: {exc}")
    except json.JSONDecodeError as exc:
        parser.error(f"malformed JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}")
    if not isinstance(raw, dict):
        report = assess_package(raw, None, None, "")
    else:
        report = assess_package(raw.get("basis"), raw.get("catalog"), raw.get("graph"), raw.get("deliverable_id"))
        for field in ("basis", "catalog", "graph", "deliverable_id"):
            if field not in raw:
                report["package_findings"].append({"rule": "package.field_missing", "category": "schema", "severity": "error",
                                                   "message": f"Package field {field!r} is missing.", "object_ids": []})
        if "catalog" not in raw:
            report["catalog_assessment"].update(input_status="MISSING", status="NOT ASSESSED")
        if "graph" not in raw:
            report["graph_assessment"].update(input_status="MISSING", status="NOT ASSESSED")
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if output:
        try:
            with output.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(rendered)
        except FileExistsError:
            parser.error("--out already exists; refusing to overwrite")
        except OSError as exc:
            parser.error(f"cannot write report: {exc}")
    print(rendered, end="")
    if report["package_findings"] or report["data_readiness"]["status"] != "ready":
        return 1
    if report["catalog_assessment"]["status"] == "INVALID" or report["graph_assessment"]["status"] == "INVALID":
        return 1
    # Even a data-ready, structurally clean package does not constitute engineering review.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
