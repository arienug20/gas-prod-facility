import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    from .roadmap_foundation.registry import NamespaceTagRegistry, adapt_legacy_model, audit_graph
except ImportError:
    from roadmap_foundation.registry import NamespaceTagRegistry, adapt_legacy_model, audit_graph


def allocation():
    return {"id": "allocation-record-test", "approved_by": "test-authority", "namespace": "TEST", "pattern": "{prefix}-{number:03d}", "start": 1, "scope": {"prefixes": ["P"]}}


class RegistryTests(unittest.TestCase):
    def test_no_authorization_and_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError): NamespaceTagRegistry(Path(td) / "r.json", "TEST", None)
            r = NamespaceTagRegistry(Path(td) / "r.json", "TEST", allocation())
            r.reserve("P-001", "one")
            with self.assertRaisesRegex(ValueError, "tag duplikat"):
                r.reserve("P-001", "two")

    def test_persist_and_reopen_stable(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "r.json"
            r = NamespaceTagRegistry(path, "TEST", allocation())
            self.assertEqual(r.allocate("P", "one"), "P-001")
            r.save()
            r = NamespaceTagRegistry.reopen(path, "TEST", allocation())
            self.assertEqual(r.allocate("P", "one"), "P-001")
            self.assertEqual(r.allocate("P", "two"), "P-002")

    def test_stale_write_refused(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "r.json"
            a = NamespaceTagRegistry(path, "TEST", allocation()); a.save()
            b = NamespaceTagRegistry(path, "TEST", allocation())
            a.allocate("P", "one"); a.save()
            b.allocate("P", "two")
            with self.assertRaises(RuntimeError): b.save()

    def test_atomic_failure_keeps_original(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "r.json"
            r = NamespaceTagRegistry(path, "TEST", allocation()); r.save()
            original = path.read_bytes()
            r.allocate("P", "one")
            module = NamespaceTagRegistry.__module__
            with patch(module.rsplit(".", 1)[0] + ".registry.os.replace", side_effect=OSError("simulated")):
                with self.assertRaises(OSError): r.save()
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(list(Path(td).glob("*.tmp")), [])

    def test_bad_schema_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "r.json"; path.write_text(json.dumps({"schema_version": "9"}), encoding="utf-8")
            with self.assertRaises(ValueError): NamespaceTagRegistry(path, "TEST", allocation())

    def test_scope_rejects_unauthorized_reserve_and_prefix(self):
        with tempfile.TemporaryDirectory() as td:
            r = NamespaceTagRegistry(Path(td) / "r.json", "TEST", allocation())
            with self.assertRaises(ValueError): r.reserve("X-001", "object")
            with self.assertRaises(ValueError): r.allocate("X", "object")
            with self.assertRaises(ValueError): r.reserve("P-000", "object")
            with self.assertRaises(ValueError): r.reserve("P-1", "object")

    def test_persisted_forged_or_noncanonical_tag_fails_load(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "r.json"
            r = NamespaceTagRegistry(path, "TEST", allocation()); r.save()
            data = r.to_dict(); data["tags"] = [{"tag": "P-1", "object_id": "one"}]
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError): NamespaceTagRegistry(path, "TEST", allocation())

    def test_object_only_scope_still_requires_pattern(self):
        auth = {"id": "record", "approved_by": "authority", "namespace": "TEST", "pattern": "{prefix}-{number:03d}", "start": 1, "scope": {"object_ids": ["one"]}}
        with tempfile.TemporaryDirectory() as td:
            r = NamespaceTagRegistry(Path(td) / "r.json", "TEST", auth)
            with self.assertRaises(ValueError): r.reserve("anything", "one")
            self.assertEqual(r.reserve("P-001", "one"), "P-001")

    def test_lock_timeout_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "r.json"
            r = NamespaceTagRegistry(path, "TEST", allocation())
            r.save(); r.allocate("P", "one")
            lock = path.with_name(path.name + ".lock"); lock.write_text("held", encoding="utf-8")
            with self.assertRaises(RuntimeError): r.save()
            self.assertTrue(lock.exists())


class GraphTests(unittest.TestCase):
    def test_legacy_adapter_does_not_mutate_and_exposes_missing_internal_topology(self):
        legacy = {"objects": [{"id": "v", "kind": "valve", "tag": "XV-1"}], "lines": [{"a": [0, 0], "b": [1, 1]}]}
        before = json.dumps(legacy, sort_keys=True)
        result = adapt_legacy_model(legacy)
        self.assertEqual(json.dumps(legacy, sort_keys=True), before)
        self.assertEqual(result["model"]["objects"][0]["tag"], "XV-1")
        self.assertTrue(any(f["rule"] == "graph.incomplete" for f in result["findings"]))
        self.assertTrue(any(f["rule"] == "graph.crossing_not_connection" for f in result["findings"]))
        self.assertEqual(result["model"]["connections"], [])

    def test_smart_qa_top_level_ports_connections_roundtrip_without_loss(self):
        legacy = {"objects": [{"id": "source", "kind": "equipment"}, {"id": "dest", "kind": "equipment"}],
                  "ports": [{"id": "p1", "owner": "source", "point": [1, 2], "dn": 50, "spec": "S1"},
                            {"id": "p2", "owner": "dest", "point": [3, 4], "dn": 50, "spec": "S1"}],
                  "connections": [{"id": "c1", "from": "p1", "to": "p2", "dn": 50, "spec": "S1"}]}
        original = json.dumps(legacy, sort_keys=True)
        model = adapt_legacy_model(legacy)["model"]
        self.assertEqual(model["ports"][0]["owner_id"], "source")
        self.assertEqual(model["ports"][0]["point"], [1, 2])
        self.assertEqual(model["ports"][0]["dn"], 50)
        self.assertEqual(model["ports"][0]["spec"], "S1")
        self.assertEqual(model["connections"][0]["from_port"], "p1")
        self.assertEqual(model["connections"][0]["to_port"], "p2")
        self.assertEqual(json.dumps(legacy, sort_keys=True), original)

    def test_top_level_and_nested_duplicate_ports_are_reported(self):
        legacy = {"objects": [{"id": "v", "kind": "assembly", "ports": [{"id": "p"}]}],
                  "ports": [{"id": "p", "owner": "v"}]}
        result = adapt_legacy_model(legacy)
        self.assertEqual(len([p for p in result["model"]["ports"] if p["id"] == "p"]), 2)
        self.assertTrue(any(f["rule"] == "graph.duplicate_id" for f in result["findings"]))

    def test_empty_graph_sections_are_incomplete_not_silent(self):
        findings = audit_graph({"schema_version": "1.0", "objects": [], "ports": [], "connections": []})
        self.assertGreaterEqual(sum(f["rule"] == "graph.incomplete" for f in findings), 3)

    def test_assembly_without_explicit_internal_links_is_not_assessed(self):
        model = {"schema_version": "1.0", "objects": [{"id": "station", "kind": "assembly", "is_assembly": True}], "ports": [], "connections": []}
        findings = audit_graph(model)
        self.assertTrue(any(f.get("assessment") == "NOT ASSESSED" and "internal" in f["message"] for f in findings))

    def test_malformed_nonempty_assembly_links_remain_incomplete(self):
        model = {"schema_version": "1.0", "objects": [{"id": "station", "kind": "assembly", "is_assembly": True, "internal_links": [{}]}], "ports": [], "connections": []}
        self.assertTrue(any(f["rule"] == "graph.assembly_incomplete" for f in audit_graph(model)))

    def test_unhashable_graph_values_return_findings(self):
        model = {"schema_version": "1.0", "objects": [{"id": "o", "kind": "x"}],
                 "ports": [{"id": "p", "owner_id": [], "port_kind": []}],
                 "connections": [{"id": "c", "from_port": [], "to_port": "p", "kind": []}]}
        self.assertTrue(audit_graph(model))

    def test_invalid_port_messages_are_indonesian(self):
        model = {"schema_version": "1.0", "objects": [{"id": "o", "kind": "x"}],
                 "ports": [{"id": "p", "owner_id": "ghost", "port_kind": "process"}],
                 "connections": [{"id": "c", "from_port": "missing", "to_port": "p", "kind": "process"}]}
        messages = [f["message"] for f in audit_graph(model)]
        self.assertTrue(any("Pemilik port" in m for m in messages))
        self.assertTrue(any("Referensi port" in m for m in messages))

    def test_duplicate_tag_message_is_indonesian(self):
        model = {"schema_version": "1.0", "objects": [{"id": "a", "kind": "x", "tag": "P-001"},
                                                           {"id": "b", "kind": "x", "tag": "P-001"}],
                 "ports": [{"id": "pa", "owner_id": "a"}], "connections": [{"id": "c", "from_port": "pa", "to_port": "missing"}]}
        duplicate = next(f for f in audit_graph(model) if f["rule"] == "graph.duplicate_tag")
        self.assertEqual(duplicate["message"], "Tag duplikat: P-001")

    def test_audit_references_unknowns_and_signal_process(self):
        model = {"schema_version": "1.0", "objects": [{"id": "a", "kind": "x"}, {"id": "b", "kind": "x"}],
                 "ports": [{"id": "p1", "owner_id": "a", "port_kind": "signal"}, {"id": "p2", "owner_id": "b", "port_kind": "process"}],
                 "connections": [{"id": "c", "from_port": "p1", "to_port": "p2", "kind": "signal"}]}
        findings = audit_graph(model)
        self.assertTrue(any(f["rule"] == "graph.incompatible_kind" for f in findings))
        unknown = [f for f in findings if f["rule"] == "graph.unknown_service"]
        self.assertTrue(unknown and unknown[0]["assessment"] == "NOT ASSESSED")


if __name__ == "__main__": unittest.main()
