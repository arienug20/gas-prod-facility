import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from cad.roadmap_foundation.standards import build_baseline, validate_catalog


class StandardsBaselineTests(unittest.TestCase):
    def test_repo_baseline_is_bounded_and_unassessed(self):
        root = Path(__file__).resolve().parents[1]
        report = build_baseline(root)
        self.assertEqual(report["schema_version"], "1.0")
        self.assertTrue(all(x["status"] == "NOT ASSESSED" for x in report["catalog"]["standards"]))
        self.assertTrue(all(x["sha256"] for x in report["artifacts"] if x["status"] == "PRESENT_STATIC_REVIEW"))
        self.assertIn("AVAILABILITY_NOT_ASSESSED", [x["status"] for x in report["backend_observations"].values()])
        self.assertTrue(any("Tidak ada teks standar" in x for x in report["limitations"]))

    def test_missing_artifact_is_recorded_without_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = build_baseline(tmp)
        self.assertTrue(all(x["status"] == "MISSING" for x in report["artifacts"]))

    def test_catalog_reports_duplicate_and_missing_evidence_and_semantics(self):
        catalog = {
            "standards": [
                {"id": "S1"}, {"id": "S1"}
            ],
            "rules": [],
            "symbols": [{"id": "valve"}],
            "mappings": [{"id": "map-1"}],
        }
        rules = {x["rule"] for x in validate_catalog(catalog)}
        self.assertTrue({"catalog.duplicate_id", "standard.missing_source", "standard.missing_edition",
                         "standard.missing_review_evidence", "symbol.undefined_ports", "mapping.unsupported"}.issubset(rules))

    def test_complete_evidence_has_no_gap_findings(self):
        evidence = {"locator": "control/ref", "reviewer": "role-1", "status": "REVIEWED"}
        catalog = {"schema_version": "1.0", "standards": [{"id": "S1", "source": {"locator": "control/ref"},
                    "edition": {"designation": "E1", "locator": "control/ref"}, "review_evidence": evidence}],
                   "rules": [{"id": "r1"}], "symbols": [{"id": "v", "ports": ["in", "out"]}],
                   "mappings": [{"id": "m", "standard_id": "S1", "symbol_id": "v", "support_evidence": evidence}]}
        findings = validate_catalog(catalog)
        self.assertIn("standard.evidence_verification_not_assessed", {x["rule"] for x in findings})
        evidence_finding = next(x for x in findings if x["rule"] == "standard.evidence_verification_not_assessed")
        self.assertIn("Verifikasi sumber/isi", evidence_finding["message"])
        self.assertNotIn("mapping.unsupported", {x["rule"] for x in findings})

    def test_empty_catalog_is_not_green_and_requires_schema_sections(self):
        findings = validate_catalog({})
        rules = {x["rule"] for x in findings}
        self.assertIn("catalog.schema_version", rules)
        self.assertIn("catalog.section_missing", rules)

    def test_arbitrary_evidence_strings_are_rejected(self):
        catalog = {"schema_version": "1.0", "standards": [{"id": "S1", "source": "source",
                    "edition": "edition", "review_evidence": "review"}], "rules": [{"id": "r"}],
                   "symbols": [{"id": "v", "ports": ["in"]}],
                   "mappings": [{"id": "m", "standard_id": "S1", "symbol_id": "v", "support_evidence": "approved"}]}
        rules = {x["rule"] for x in validate_catalog(catalog)}
        self.assertTrue({"standard.missing_source", "standard.missing_edition", "standard.missing_review_evidence",
                         "mapping.unsupported"}.issubset(rules))

    def test_mapping_references_must_resolve(self):
        catalog = {"schema_version": "1.0", "standards": [{"id": "S1"}], "rules": [{"id": "r"}],
                   "symbols": [{"id": "v", "ports": ["in"]}], "mappings": [{"id": "m", "standard_id": "ghost", "symbol_id": "ghost"}]}
        self.assertEqual(sum(x["rule"] == "mapping.dangling_reference" for x in validate_catalog(catalog)), 2)

    def test_rejected_mapping_evidence_is_not_support(self):
        catalog = {"schema_version": "1.0", "standards": [{"id": "S1"}], "rules": [{"id": "r"}],
                   "symbols": [{"id": "v", "ports": ["in"]}],
                   "mappings": [{"id": "m", "standard_id": "S1", "symbol_id": "v",
                                 "support_evidence": {"locator": "ref", "reviewer": "role", "status": "REJECTED"}}]}
        self.assertIn("mapping.unsupported", {x["rule"] for x in validate_catalog(catalog)})

    def test_cli_refuses_existing_output(self):
        import contextlib
        import io
        from cad.roadmap_foundation import standards
        with tempfile.TemporaryDirectory() as tmp:
            existing = Path(tmp) / "drawing.dxf"
            existing.write_text("preserve", encoding="utf-8")
            error_output = io.StringIO()
            with patch("sys.argv", ["standards", "--repo-root", tmp, "--out", str(existing)]), contextlib.redirect_stderr(error_output):
                with self.assertRaises(SystemExit) as caught: standards.main()
            self.assertEqual(caught.exception.code, 2)
            self.assertEqual(existing.read_text(encoding="utf-8"), "preserve")
            self.assertIn("file yang sudah ada tidak akan ditimpa", error_output.getvalue())


if __name__ == "__main__":
    unittest.main()
