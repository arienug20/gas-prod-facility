"""Contract tests using symbolic, synthetic IDs only."""
import copy
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from cad.roadmap_foundation.readiness import assess_readiness, main, validate_basis


def payload():
    return {
        "schema_version": "1.0",
        "sources": [{"id": "SRC-A", "revision": "REV-X", "locator": "synthetic fixture"}],
        "basis_items": [
            {"id": "BASIS-A", "value": None, "unit": None, "certainty_kind": "tbd",
             "confirmation_state": "unconfirmed", "source_refs": [], "scope": ["DEL-A"]},
            {"id": "BASIS-B", "value": "symbolic observation", "unit": None, "certainty_kind": "source_fact",
             "confirmation_state": "confirmed", "source_refs": ["SRC-A"], "confirmation_ref": "EVIDENCE-A", "scope": ["DEL-A"]},
        ],
        "authorizations": [{"id": "AUTH-A", "kind": "basis_confirmation", "actor": "synthetic reviewer",
                            "scope": ["BASIS-B"], "basis_refs": ["BASIS-B"],
                            "confirmation_ref": "EVIDENCE-A", "active": True}],
        "deliverables": [{"id": "DEL-A", "kind": "pfd", "phase": "FEED", "purpose": "review",
                           "requirements": [
                               {"basis_ref": "BASIS-A", "applicability": "required", "question": "Confirm symbolic basis A.", "task_ids": ["TASK-HOLD"]},
                               {"basis_ref": "BASIS-B", "applicability": "required", "task_ids": ["TASK-INDEPENDENT"]},
                           ]}],
    }


class ReadinessTests(unittest.TestCase):
    def test_unknown_is_a_hold_and_unrelated_task_remains_independent(self):
        report = assess_readiness(payload(), "DEL-A")
        assert report["schema_version"] == "1.0"
        assert report["status"] == "blocked"
        assert report["questions"] == [{"basis_ref": "BASIS-A", "question": "Confirm symbolic basis A.", "task_ids": ["TASK-HOLD"]}]
        assert report["blocked_tasks"] == ["TASK-HOLD"]
        assert report["independent_work"] == ["TASK-INDEPENDENT"]


    def test_fact_does_not_imply_confirmation_and_confirmed_needs_active_scoped_auth(self):
        data = payload()
        data["basis_items"][1]["confirmation_state"] = "unconfirmed"
        assert assess_readiness(data, "DEL-A")["status"] == "blocked"
        data["basis_items"][1]["confirmation_state"] = "confirmed"
        data["authorizations"].clear()
        assert "basis.confirmation_authorization" in {f["rule"] for f in validate_basis(data)}


    def test_tbd_null_is_never_confirmable_and_conflict_stays_visible(self):
        data = payload()
        data["basis_items"][0]["confirmation_state"] = "confirmed"
        data["basis_items"][0]["confirmation_ref"] = "EVIDENCE-B"
        assert "basis.confirmation_evidence" in {f["rule"] for f in validate_basis(data)}
        data = payload()
        data["basis_items"][1]["confirmation_state"] = "conflict"
        report = assess_readiness(data, "DEL-A")
        assert any(f["rule"] == "basis.conflict" for f in report["findings"])
        assert report["status"] == "blocked"


    def test_assumption_requires_active_authorization_covering_basis(self):
        data = payload()
        item = data["basis_items"][1]
        item.update(certainty_kind="assumption", authorization_ref="AUTH-A")
        data["authorizations"].append({"id": "AUTH-C", "kind": "basis_confirmation", "actor": "synthetic reviewer",
                                       "scope": ["BASIS-B"], "confirmation_ref": "EVIDENCE-A", "active": True})
        data["authorizations"].append({"id": "AUTH-S", "kind": "assumption", "actor": "synthetic owner",
                                       "scope": ["BASIS-B"], "basis_refs": ["BASIS-B"], "active": True})
        item["authorization_ref"] = "AUTH-S"
        assert not validate_basis(data)
        data["authorizations"][2]["scope"] = ["OTHER"]
        assert "authorization.assumption" in {f["rule"] for f in validate_basis(data)}
        data["authorizations"][2]["active"] = False
        assert "authorization.assumption" in {f["rule"] for f in validate_basis(data)}


    def test_na_rationale_and_conditional_unknown_are_not_silently_skipped(self):
        data = payload()
        reqs = data["deliverables"][0]["requirements"]
        reqs[0]["applicability"] = "conditional"
        reqs[1].update(applicability="not_applicable")
        assert "requirement.na_rationale" in {f["rule"] for f in validate_basis(data)}
        reqs[1]["rationale"] = "out of scoped review"
        report = assess_readiness(data, "DEL-A")
        assert report["status"] == "blocked"
        assert report["questions"][0]["basis_ref"] == "BASIS-A"


    def test_partial_authorization_is_explicit_scoped_and_never_clears_holds(self):
        data = payload()
        data["authorizations"].append({"id": "AUTH-P", "kind": "partial", "actor": "synthetic owner",
                                       "scope": ["DEL-A"], "basis_refs": ["BASIS-A"],
                                       "purpose": "review known subset", "active": True})
        report = assess_readiness(data, "DEL-A")
        assert report["status"] == "partial"
        assert report["blocked_tasks"] == ["TASK-HOLD"]
        assert report["questions"]
        data["authorizations"][-1]["scope"] = ["OTHER-DEL"]
        assert assess_readiness(data, "DEL-A")["status"] == "blocked"

    def test_partial_must_cover_every_hold_and_empty_task_list_still_blocks(self):
        data = payload()
        data["deliverables"][0]["requirements"][0]["task_ids"] = []
        report = assess_readiness(data, "DEL-A")
        assert report["status"] == "blocked"
        assert report["blocked_tasks"] == ["basis:BASIS-A"]
        data["authorizations"].append({"id": "AUTH-P", "kind": "partial", "actor": "synthetic owner",
                                       "scope": ["DEL-A"], "basis_refs": ["BASIS-B"],
                                       "purpose": "review subset", "active": True})
        assert assess_readiness(data, "DEL-A")["status"] == "blocked"

    def test_conditional_true_checks_basis_and_malformed_unhashable_values_are_findings(self):
        data = payload()
        data["deliverables"][0]["requirements"][0]["applicability"] = "conditional"
        data["deliverables"][0]["requirements"][0]["condition_met"] = True
        assert assess_readiness(data, "DEL-A")["questions"][0]["question"] == "Confirm symbolic basis A."
        data["basis_items"][0]["certainty_kind"] = []
        report = assess_readiness(data, "DEL-A")
        assert report["status"] == "invalid"
        assert any(f["rule"] == "basis.certainty" for f in report["findings"])

    def test_adversarial_refs_task_ids_and_empty_scope_never_crash_or_pass(self):
        data = payload()
        data["basis_items"][1].update(certainty_kind="assumption", authorization_ref=[])
        report = assess_readiness(data, "DEL-A")
        assert report["status"] == "invalid"
        assert any(f["rule"] == "authorization.assumption" for f in report["findings"])

        data = payload()
        data["deliverables"][0]["requirements"][0]["task_ids"] = [[]]
        assert any(f["rule"] == "requirement.task_ids" for f in validate_basis(data))
        data["deliverables"][0]["requirements"][0]["task_ids"] = None
        assert any(f["rule"] == "requirement.task_ids" for f in validate_basis(data))

        data = payload()
        data["basis_items"][1]["source_refs"] = []
        assert any(f["rule"] == "basis.source_required" for f in validate_basis(data))

        data = payload()
        data["authorizations"][0]["confirmation_ref"] = "UNRELATED-EVIDENCE"
        assert any(f["rule"] == "basis.confirmation_authorization" for f in validate_basis(data))

        data = payload()
        data["deliverables"][0]["requirements"] = []
        report = assess_readiness(data, "DEL-A")
        assert report["status"] == "not_assessed"
        assert report["status"] != "ready"

    def test_basis_scope_is_explicit_delivery_scoped_and_can_be_shared(self):
        data = payload()
        data["basis_items"][1]["scope"] = ["OTHER-DEL"]
        report = assess_readiness(data, "DEL-A")
        assert report["status"] == "blocked"
        assert any(f["rule"] == "basis.scope_mismatch" for f in report["findings"])
        data["basis_items"][1]["scope"] = None
        assert "basis.scope_missing" in {f["rule"] for f in validate_basis(data)}
        data["basis_items"][1]["scope"] = ["DEL-A", "DEL-B"]
        assert assess_readiness(data, "DEL-A")["status"] == "blocked"  # BASIS-A remains TBD.
        data["deliverables"][0]["requirements"] = [{"basis_ref": "BASIS-B", "applicability": "required"}]
        assert assess_readiness(data, "DEL-A")["status"] == "ready"
        other = copy.deepcopy(data["deliverables"][0])
        other["id"] = "DEL-B"
        data["deliverables"].append(other)
        assert assess_readiness(data, "DEL-B")["status"] == "ready"

    def test_numeric_units_are_explicit_without_coercing_narrative_values(self):
        data = payload()
        item = data["basis_items"][1]
        item.update(value=12.0, unit=None)
        findings = validate_basis(data)
        assert "basis.numeric_unit" in {f["rule"] for f in findings}
        assert "harus mencantumkan satuan secara eksplisit" in next(f["message"] for f in findings if f["rule"] == "basis.numeric_unit")
        item.update(unit="1")
        assert "basis.dimensionless_explicit" in {f["rule"] for f in validate_basis(data)}
        item.update(quantity_kind="dimensionless")
        assert not validate_basis(data)
        item.update(value="symbolic narrative", unit=None)
        assert not validate_basis(data)

    def test_default_questions_and_scope_messages_are_indonesian_but_input_question_is_preserved(self):
        data = payload()
        data["deliverables"][0]["requirements"][0].pop("question")
        report = assess_readiness(data, "DEL-A")
        self.assertTrue(report["questions"][0]["question"].startswith("Konfirmasikan basis item BASIS-A"))

        data = payload()
        data["basis_items"][1]["scope"] = ["OTHER-DEL"]
        report = assess_readiness(data, "DEL-A")
        scope_message = next(f["message"] for f in report["findings"] if f["rule"] == "basis.scope_mismatch")
        self.assertIn("tidak mencakup deliverable", scope_message)
        self.assertTrue(report["questions"][1]["question"].startswith("Konfirmasikan apakah basis item BASIS-B"))

        data = payload()
        self.assertEqual(assess_readiness(data, "DEL-A")["questions"][0]["question"], "Confirm symbolic basis A.")

    def test_cli_help_and_malformed_json_use_indonesian_custom_text(self):
        with contextlib.redirect_stdout(io.StringIO()) as help_output:
            try:
                main(["--help"])
            except SystemExit as exc:
                self.assertEqual(exc.code, 0)
        self.assertIn("Periksa kesiapan basis", help_output.getvalue())
        self.assertIn("simpan report JSON", help_output.getvalue())
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "bad.json"
            source.write_text("{", encoding="utf-8")
            error_output = io.StringIO()
            with contextlib.redirect_stderr(error_output):
                try:
                    main([str(source), "DEL-A"])
                except SystemExit as exc:
                    self.assertEqual(exc.code, 2)
            self.assertIn("JSON tidak valid pada baris", error_output.getvalue())


    def test_conflicting_or_invalid_references_are_structural_and_nonmutating(self):
        data = payload()
        data["deliverables"][0]["requirements"][0]["basis_ref"] = "MISSING"
        original = copy.deepcopy(data)
        report = assess_readiness(data, "DEL-A")
        assert report["status"] == "invalid"
        assert data == original


    def test_cli_outputs_structured_report_and_refuses_overwrite_or_input_alias(self):
        data = payload()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, output = root / "input.json", root / "report.json"
            source.write_text(json.dumps(data), encoding="utf-8")
            assert main([str(source), "DEL-A", "--out", str(output)]) == 1
            report = json.loads(output.read_text(encoding="utf-8"))
            assert report["status"] == "blocked"
            before = output.read_bytes()
            try:
                main([str(source), "DEL-A", "--out", str(output)])
            except SystemExit as exc:
                assert exc.code == 2
            else:
                raise AssertionError("existing output should be refused")
            assert output.read_bytes() == before
            try:
                main([str(source), "DEL-A", "--out", str(source)])
            except SystemExit as exc:
                assert exc.code == 2
            else:
                raise AssertionError("input alias should be refused")
