"""Explicit adapter joining readiness, catalog, and graph audits without promotion."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .readiness import assess_readiness
from .registry import audit_graph
from .standards import validate_catalog
from .connectivity import check_connectivity

SCHEMA_VERSION = "1.0"


def _status(findings: list[dict[str, Any]]) -> str:
    """A clean bounded audit is still NOT ASSESSED for engineering acceptance."""
    return "INVALID" if any(item.get("severity") == "error" for item in findings) else "NOT ASSESSED"


def assess_package(payload: Any, catalog: Any, graph: Any, deliverable_id: str, connectivity_requirements: Any = None) -> dict[str, Any]:
    """Assess the three supplied sections independently; never infer missing inputs."""
    package_findings = []
    if not isinstance(payload, dict):
        package_findings.append({"rule": "package.basis_missing", "category": "schema", "severity": "error",
                                 "message": "Payload basis harus berupa objek JSON.", "object_ids": []})
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
                                         "severity": "error", "message": f"Bagian basis {key!r} belum tersedia.",
                                         "object_ids": []})
    if catalog_input == "MISSING":
        catalog_report = [{"rule": "catalog.section_missing", "category": "schema", "severity": "error",
                           "message": "Bagian catalog tidak tersedia; status catalog tetap NOT ASSESSED.", "object_ids": [], "location": None}]
    if graph_input == "MISSING":
        graph_report = [{"rule": "graph.section_missing", "severity": "error", "assessment": "NOT ASSESSED",
                         "message": "Bagian graph tidak tersedia; status graph tetap NOT ASSESSED.", "object_ids": []}]
    if catalog_input == "MISSING":
        package_findings.append({"rule": "package.catalog_missing", "category": "schema", "severity": "error",
                                 "message": "Bagian catalog tidak tersedia atau bernilai null; status catalog tetap NOT ASSESSED.",
                                 "object_ids": []})
    if graph_input == "MISSING":
        package_findings.append({"rule": "package.graph_missing", "category": "schema", "severity": "error",
                                 "message": "Bagian graph tidak tersedia atau bernilai null; status graph tetap NOT ASSESSED.",
                                 "object_ids": []})
    if not isinstance(deliverable_id, str) or not deliverable_id.strip():
        package_findings.append({"rule": "package.deliverable_id", "category": "schema", "severity": "error",
                                 "message": "deliverable_id harus berupa string yang tidak kosong.", "object_ids": []})
    return {
        "schema_version": SCHEMA_VERSION,
        "deliverable_id": deliverable_id,
        "package_findings": package_findings,
        "data_readiness": basis_report,
        "catalog_assessment": {"input_status": catalog_input, "status": "NOT ASSESSED" if catalog_input == "MISSING" else _status(catalog_report), "findings": catalog_report},
        "graph_assessment": {"input_status": graph_input, "status": "NOT ASSESSED" if graph_input == "MISSING" else _status(graph_report), "findings": graph_report},
        "connectivity_assessment": check_connectivity(graph, connectivity_requirements),
        "engineering_review": {"status": "NOT ASSESSED", "findings": []},
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Evaluasi kesiapan data, catalog, dan graph secara terpisah.")
    parser.add_argument("input", type=Path, help="file package JSON berisi basis, catalog, graph, dan deliverable_id")
    parser.add_argument("--out", type=Path, help="simpan report ke file baru; file yang sudah ada tidak ditimpa")
    args = parser.parse_args(argv)
    source = args.input.resolve()
    output = args.out.resolve() if args.out else None
    if output and (output == source or output.exists() or not output.parent.is_dir()):
        parser.error("--out harus berbeda dari input, direktori induknya harus tersedia, dan file tujuan belum boleh ada")
    try:
        raw = json.loads(source.read_text(encoding="utf-8"))
    except OSError as exc:
        parser.error(f"gagal membaca file input: {exc}")
    except json.JSONDecodeError as exc:
        parser.error(f"JSON tidak valid pada baris {exc.lineno}, kolom {exc.colno}.")
    if not isinstance(raw, dict):
        report = assess_package(raw, None, None, "")
    else:
        report = assess_package(raw.get("basis"), raw.get("catalog"), raw.get("graph"), raw.get("deliverable_id"), raw.get("connectivity_requirements"))
        for field in ("basis", "catalog", "graph", "deliverable_id"):
            if field not in raw:
                report["package_findings"].append({"rule": "package.field_missing", "category": "schema", "severity": "error",
                                                   "message": f"Field package {field!r} belum tersedia.", "object_ids": []})
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
            parser.error("file --out sudah ada; file yang ada tidak ditimpa")
        except OSError as exc:
            parser.error(f"gagal menulis report: {exc}")
    print(rendered, end="")
    if report["package_findings"] or report["data_readiness"]["status"] != "ready":
        return 1
    if report["catalog_assessment"]["status"] == "INVALID" or report["graph_assessment"]["status"] == "INVALID":
        return 1
    if report['connectivity_assessment']['status'] in ('INVALID', 'INCOMPLETE'):
        return 1
    # Even a data-ready, structurally clean package does not constitute engineering review.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
