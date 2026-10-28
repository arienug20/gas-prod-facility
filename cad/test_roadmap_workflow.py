"""Integration contract tests for the additive foundation workflow adapter."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from cad.roadmap_foundation.workflow import assess_package, main


def basis(confirmed=False):
    item = {"id": "BASIS-SYMBOL", "value": "symbolic basis", "unit": None,
            "certainty_kind": "source_fact", "confirmation_state": "unconfirmed",
            "source_refs": ["SOURCE-SYMBOL"], "scope": ["DEL-SYMBOL"]}
    auth = []
    if confirmed:
        item.update(confirmation_state="confirmed", confirmation_ref="EVIDENCE-SYMBOL")
        auth.append({"id": "AUTH-SYMBOL", "kind": "basis_confirmation", "actor": "synthetic reviewer",
                     "scope": ["BASIS-SYMBOL"], "basis_refs": ["BASIS-SYMBOL"],
                     "confirmation_ref": "EVIDENCE-SYMBOL", "active": True})
    return {"schema_version": "1.0",
            "sources": [{"id": "SOURCE-SYMBOL", "revision": "REV-SYMBOL", "locator": "synthetic fixture"}],
            "basis_items": [item], "authorizations": auth,
            "deliverables": [{"id": "DEL-SYMBOL", "kind": "pfd", "phase": "FEED",
                              "requirements": [{"basis_ref": "BASIS-SYMBOL", "applicability": "required",
                                                "task_ids": ["TASK-SYMBOL"]}]}]}


def catalog():
    # Empty sections are explicit evidence gaps and must remain NOT ASSESSED.
    return {"schema_version": "1.0", "standards": [], "rules": [], "symbols": [], "mappings": []}


def graph():
    return {"schema_version": "1.0",
            "objects": [{"id": "OBJECT-SYMBOL", "kind": "equipment"}],
            "ports": [{"id": "PORT-SYMBOL", "owner_id": "OBJECT-SYMBOL", "service_ref": "SERVICE-SYMBOL"}],
            "connections": []}


class WorkflowTests(unittest.TestCase):
    def test_unknown_basis_holds_despite_structurally_valid_catalog_and_graph(self):
        report = assess_package(basis(), catalog(), graph(), "DEL-SYMBOL")
        self.assertEqual(report["schema_version"], "1.0")
        self.assertEqual(report["data_readiness"]["status"], "blocked")
        self.assertEqual(report["data_readiness"]["blocked_tasks"], ["TASK-SYMBOL"])
        self.assertEqual(report["catalog_assessment"]["status"], "NOT ASSESSED")
        self.assertEqual(report["graph_assessment"]["status"], "NOT ASSESSED")
        self.assertEqual(report["engineering_review"]["status"], "NOT ASSESSED")
        self.assertNotIn("overall_status", report)

    def test_confirmed_scoped_basis_is_data_ready_without_promotion(self):
        report = assess_package(basis(confirmed=True), catalog(), graph(), "DEL-SYMBOL")
        self.assertEqual(report["data_readiness"]["status"], "ready")
        self.assertEqual(report["catalog_assessment"]["status"], "NOT ASSESSED")
        self.assertEqual(report["graph_assessment"]["status"], "NOT ASSESSED")
        self.assertEqual(report["engineering_review"], {"status": "NOT ASSESSED", "findings": []})

    def test_missing_catalog_and_graph_are_explicit_not_assessed(self):
        report = assess_package(basis(confirmed=True), None, None, "DEL-SYMBOL")
        self.assertEqual(report["catalog_assessment"]["input_status"], "MISSING")
        self.assertEqual(report["catalog_assessment"]["status"], "NOT ASSESSED")
        self.assertEqual(report["graph_assessment"]["input_status"], "MISSING")
        self.assertEqual(report["graph_assessment"]["status"], "NOT ASSESSED")

    def test_missing_basis_field_and_empty_audits_never_create_ready_claim(self):
        report = assess_package({}, catalog(), graph(), "DEL-SYMBOL")
        self.assertEqual(report["data_readiness"]["status"], "invalid")
        self.assertTrue(report["package_findings"])
        cleanish = assess_package(basis(confirmed=True), catalog(), {"schema_version": "1.0", "objects": [], "ports": [], "connections": []}, "DEL-SYMBOL")
        self.assertEqual(cleanish["graph_assessment"]["status"], "NOT ASSESSED")

    def test_cli_json_input_report_and_exclusive_output(self):
        package = {"basis": basis(), "catalog": catalog(), "graph": graph(), "deliverable_id": "DEL-SYMBOL"}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, output = root / "package.json", root / "report.json"
            source.write_text(json.dumps(package), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main([str(source), "--out", str(output)]), 1)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["data_readiness"]["status"], "blocked")
            before = output.read_bytes()
            with self.assertRaises(SystemExit) as error, contextlib.redirect_stderr(io.StringIO()):
                main([str(source), "--out", str(output)])
            self.assertEqual(error.exception.code, 2)
            self.assertEqual(output.read_bytes(), before)

    def test_cli_malformed_json_reports_parse_location(self):
        help_output = io.StringIO()
        with contextlib.redirect_stdout(help_output), self.assertRaises(SystemExit) as help_exit:
            main(["--help"])
        self.assertEqual(help_exit.exception.code, 0)
        self.assertIn("Evaluasi kesiapan data", help_output.getvalue())
        self.assertIn("file package JSON", help_output.getvalue())
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "broken.json"
            source.write_text('{"basis":', encoding="utf-8")
            error_output = io.StringIO()
            with self.assertRaises(SystemExit) as error, contextlib.redirect_stderr(error_output):
                main([str(source)])
            self.assertEqual(error.exception.code, 2)
            self.assertIn("JSON tidak valid pada baris", error_output.getvalue())

    def test_cli_ready_basis_with_null_catalog_and_graph_exits_nonzero(self):
        package = {"basis": basis(confirmed=True), "catalog": None, "graph": None,
                   "deliverable_id": "DEL-SYMBOL"}
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "package.json"
            source.write_text(json.dumps(package), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                code = main([str(source)])
        self.assertEqual(code, 1)
        report = assess_package(package["basis"], None, None, "DEL-SYMBOL")
        self.assertEqual(report["data_readiness"]["status"], "ready")
        self.assertEqual(report["catalog_assessment"]["status"], "NOT ASSESSED")
        self.assertEqual(report["graph_assessment"]["status"], "NOT ASSESSED")
        self.assertTrue(any(f["rule"] == "package.catalog_missing" for f in report["package_findings"]))
        self.assertTrue(any(f["rule"] == "package.graph_missing" for f in report["package_findings"]))
        self.assertIn("tidak tersedia atau bernilai null", next(f["message"] for f in report["package_findings"] if f["rule"] == "package.catalog_missing"))


if __name__ == "__main__":
    unittest.main()
