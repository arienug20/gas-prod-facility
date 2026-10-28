"""Persistent, explicitly authorized tag identity and conservative legacy graph adapter."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import time
import re
import string
import tempfile
from pathlib import Path

SCHEMA_VERSION = "1.0"


def _normalize_findings(findings):
    for finding in findings:
        finding.setdefault("category", "graph")
        finding.setdefault("location", None)
    return findings


def _validate_tag_record(tag, object_id, allocation):
    """Require exact canonical rendering of an authorized tag and number range."""
    _key(tag, "tag"); _key(object_id, "object_id")
    scope = allocation["scope"]
    if scope.get("object_ids") and object_id not in scope["object_ids"]:
        raise ValueError(f"object is outside approved allocation scope: {object_id}")
    pieces, prefix_group, number_group = [], False, False
    number_spec = ""
    for literal, field, spec, _conversion in string.Formatter().parse(allocation["pattern"]):
        pieces.append(re.escape(literal))
        if field == "prefix": pieces.append("(?P<prefix>.+?)"); prefix_group = True
        elif field == "number":
            number_spec = spec
            number_chars = "[0-9a-fA-F]+" if spec.endswith(("x", "X")) else "[0-7]+" if spec.endswith("o") else "[0-9]+"
            pieces.append(f"(?P<number>{number_chars})"); number_group = True
    match = re.fullmatch("".join(pieces), tag)
    if not match or not prefix_group or not number_group:
        raise ValueError(f"tag does not match approved pattern: {tag}")
    prefix, raw_number = match.group("prefix"), match.group("number")
    if scope.get("prefixes") and prefix not in scope["prefixes"]:
        raise ValueError(f"tag prefix is outside approved allocation scope: {prefix}")
    base = 16 if number_spec.endswith(("x", "X")) else 8 if number_spec.endswith("o") else 10
    try: number = int(raw_number, base)
    except ValueError: raise ValueError(f"tag number is invalid: {tag}") from None
    if number < allocation["start"]:
        raise ValueError(f"tag number is below approved start: {tag}")
    if allocation["pattern"].format(prefix=prefix, number=number) != tag:
        raise ValueError(f"tag is not canonically formatted: {tag}")
    return tag


def _key(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _allocation(record, namespace):
    if not isinstance(record, dict):
        raise ValueError("explicit approved allocation record is required")
    required = ("id", "approved_by", "namespace", "pattern", "start", "scope")
    if any(k not in record for k in required):
        raise ValueError("allocation requires id, approved_by, namespace, pattern, start, and scope")
    for field in ("id", "approved_by", "namespace", "pattern"):
        _key(record[field], f"allocation.{field}")
    scope = record["scope"]
    if not isinstance(scope, dict) or not any(k in scope for k in ("prefixes", "object_ids")):
        raise ValueError("allocation.scope must authorize prefixes and/or object_ids")
    for field in ("prefixes", "object_ids"):
        if field in scope and (not isinstance(scope[field], list) or any(not isinstance(v, str) or not v.strip() for v in scope[field])):
            raise ValueError(f"allocation.scope.{field} must be a list of non-empty strings")
    if not scope.get("prefixes") and not scope.get("object_ids"):
        raise ValueError("allocation.scope must authorize at least one prefix or object_id")
    if record["namespace"] != namespace:
        raise ValueError("allocation namespace does not match registry namespace")
    if isinstance(record["start"], bool) or not isinstance(record["start"], int) or record["start"] < 0:
        raise ValueError("allocation.start must be a non-negative integer")
    pattern = record["pattern"]
    try:
        parts = list(string.Formatter().parse(pattern))
        fields = [f for _, f, _, _ in parts if f is not None]
        if fields.count("prefix") != 1 or fields.count("number") != 1 or set(fields) != {"prefix", "number"}:
            raise ValueError("pattern must include prefix and number exactly once")
        for _, field, spec, conv in parts:
            if field is not None and (conv or "{" in spec or "}" in spec):
                raise ValueError("conversions and nested formats are unsupported")
            if field == "prefix" and spec:
                raise ValueError("prefix formatting is unsupported")
            if field == "number" and not re.fullmatch(r"0?\d*[dxbXo]?", spec):
                raise ValueError("invalid number format")
        examples = [pattern.format(prefix=p, number=n) for p, n in (("A", record["start"]), ("A", record["start"] + 1), ("B", record["start"]))]
        if len(set(examples)) != 3 or any(not x.strip() for x in examples):
            raise ValueError("pattern must distinguish prefix and number")
    except (ValueError, TypeError, KeyError, IndexError) as exc:
        raise ValueError(f"invalid allocation pattern: {exc}") from exc
    return copy.deepcopy(record)


class NamespaceTagRegistry:
    """A single-namespace persistent registry with optimistic concurrency checks."""
    def __init__(self, path, namespace, allocation):
        self.path = Path(path)
        self.namespace = _key(namespace, "namespace")
        self.allocation = _allocation(allocation, namespace)
        self._by_tag, self._by_object, self._next = {}, {}, {}
        self._disk_hash = None
        if self.path.exists():
            self.load()

    def reserve(self, tag, object_id):
        tag, object_id = _key(tag, "tag"), _key(object_id, "object_id")
        _validate_tag_record(tag, object_id, self.allocation)
        if tag in self._by_tag and self._by_tag[tag] != object_id:
            raise ValueError(f"duplicate tag: {tag}")
        if object_id in self._by_object and self._by_object[object_id] != tag:
            raise ValueError(f"object already has a tag: {object_id}")
        self._by_tag[tag] = object_id
        self._by_object[object_id] = tag
        return tag

    def allocate(self, prefix, object_id):
        prefix, object_id = _key(prefix, "prefix"), _key(object_id, "object_id")
        if self.allocation["scope"].get("prefixes") and prefix not in self.allocation["scope"]["prefixes"]:
            raise ValueError(f"prefix is outside approved allocation scope: {prefix}")
        if self.allocation["scope"].get("object_ids") and object_id not in self.allocation["scope"]["object_ids"]:
            raise ValueError(f"object is outside approved allocation scope: {object_id}")
        if object_id in self._by_object:
            return self._by_object[object_id]
        number = self._next.get(prefix, self.allocation["start"])
        while True:
            tag = self.allocation["pattern"].format(prefix=prefix, number=number)
            number += 1
            if tag not in self._by_tag:
                self._next[prefix] = number
                return self.reserve(tag, object_id)

    def to_dict(self):
        return {"schema_version": SCHEMA_VERSION, "namespace": self.namespace,
                "allocation": copy.deepcopy(self.allocation),
                "tags": [{"tag": tag, "object_id": oid} for tag, oid in sorted(self._by_tag.items())],
                "next": dict(sorted(self._next.items()))}

    def load(self):
        raw = self.path.read_bytes()
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"malformed registry: {exc}") from exc
        if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("unsupported or malformed registry schema")
        if data.get("namespace") != self.namespace or data.get("allocation") != self.allocation:
            raise ValueError("registry namespace/allocation mismatch")
        tags, objects = {}, {}
        entries = data.get("tags")
        if not isinstance(entries, list) or not isinstance(data.get("next"), dict):
            raise ValueError("malformed registry contents")
        for entry in entries:
            if not isinstance(entry, dict) or set(entry) != {"tag", "object_id"}:
                raise ValueError("malformed tag entry")
            tag, oid = _key(entry["tag"], "tag"), _key(entry["object_id"], "object_id")
            _validate_tag_record(tag, oid, self.allocation)
            if tag in tags or oid in objects:
                raise ValueError("duplicate tag or object in registry")
            tags[tag], objects[oid] = oid, tag
        next_values = data["next"]
        if any(not isinstance(k, str) or not k.strip() or isinstance(v, bool) or not isinstance(v, int) or v < self.allocation["start"] for k, v in next_values.items()):
            raise ValueError("malformed allocation counters")
        self._by_tag, self._by_object, self._next = tags, objects, dict(next_values)
        self._disk_hash = hashlib.sha256(raw).hexdigest()
        return self

    @classmethod
    def reopen(cls, path, namespace, allocation):
        return cls(path, namespace, allocation)

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = (json.dumps(self.to_dict(), indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
        lock_path = self.path.with_name(self.path.name + ".lock")
        lock_fd = None
        deadline = time.monotonic() + 2.0
        while lock_fd is None:
            try:
                lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            except FileExistsError:
                if time.monotonic() >= deadline:
                    raise RuntimeError("registry lock unavailable; refusing write")
                time.sleep(0.025)
        tmp = None
        try:
            current_hash = hashlib.sha256(self.path.read_bytes()).hexdigest() if self.path.exists() else None
            if current_hash != self._disk_hash:
                raise RuntimeError("registry changed on disk; refusing stale write")
            fd, tmp = tempfile.mkstemp(prefix=self.path.name + ".", suffix=".tmp", dir=str(self.path.parent))
            with os.fdopen(fd, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(tmp, self.path)
        except BaseException:
            raise
        finally:
            if tmp is not None:
                try: os.unlink(tmp)
                except OSError: pass
            os.close(lock_fd)
            try: os.unlink(lock_path)
            except OSError: pass
        self._disk_hash = hashlib.sha256(payload).hexdigest()
        return self.path


def adapt_legacy_model(model):
    """Convert known legacy fields only; omitted semantic data remains a finding."""
    source = copy.deepcopy(model) if isinstance(model, dict) else {}
    findings = []
    objects = []
    ports = []
    connections = []
    for item in source.get("objects", []) if isinstance(source.get("objects"), list) else []:
        if not isinstance(item, dict):
            findings.append({"rule": "graph.legacy_unknown", "severity": "warning", "message": "Invalid legacy object; skipped", "object_ids": []})
            continue
        oid = item.get("id") or item.get("tag")
        if not oid:
            findings.append({"rule": "graph.legacy_unknown", "severity": "warning", "message": "Legacy object has no stable id", "object_ids": []})
            continue
        obj = {"id": str(oid), "kind": item.get("kind", "unknown")}
        if item.get("is_assembly") is True:
            obj["is_assembly"] = True
            if isinstance(item.get("internal_links"), list):
                obj["internal_links"] = copy.deepcopy(item["internal_links"])
        if item.get("tag") is not None:
            obj["tag"] = item["tag"]
        objects.append(obj)
        for p in item.get("ports", []) if isinstance(item.get("ports"), list) else []:
            if isinstance(p, dict) and p.get("id"):
                port = {"id": str(p["id"]), "owner_id": str(oid), "port_kind": p.get("port_kind", p.get("kind", "unknown")),
                        "direction": p.get("direction", "unknown"), "service_ref": p.get("service_ref")}
                for field in ("point", "dn", "spec"):
                    if field in p: port[field] = copy.deepcopy(p[field])
                ports.append(port)
    # smart_qa-era models store ports at top level with `owner`, `point`, `dn`, `spec`.
    for p in source.get("ports", []) if isinstance(source.get("ports"), list) else []:
        if not isinstance(p, dict) or not p.get("id"):
            findings.append({"rule": "graph.legacy_unknown", "severity": "warning", "message": "Invalid legacy port; skipped", "object_ids": []})
            continue
        port = {"id": str(p["id"]), "owner_id": p.get("owner_id", p.get("owner")),
                "port_kind": p.get("port_kind", p.get("kind", "unknown")),
                "direction": p.get("direction", "unknown"), "service_ref": p.get("service_ref")}
        for field in ("point", "dn", "spec"):
            if field in p: port[field] = copy.deepcopy(p[field])
        ports.append(port)
    port_ids = [p["id"] for p in ports]
    for pid in sorted({p for p in port_ids if port_ids.count(p) > 1}):
        findings.append({"rule": "graph.duplicate_id", "severity": "error", "message": f"Legacy ports share duplicate id {pid}", "object_ids": [pid]})
    for item in source.get("connections", []) if isinstance(source.get("connections"), list) else []:
        if isinstance(item, dict):
            connection = {"id": item.get("id"), "from_port": item.get("from_port", item.get("from")),
                          "to_port": item.get("to_port", item.get("to")), "kind": item.get("kind", "unknown")}
            for field in ("dn", "spec"):
                if field in item: connection[field] = copy.deepcopy(item[field])
            connections.append(connection)
    if not ports:
        findings.append({"rule": "graph.incomplete", "severity": "warning", "assessment": "NOT ASSESSED", "message": "Legacy model has no explicit ports; internal ports are unknown", "object_ids": []})
    if source.get("crossings") or source.get("lines"):
        findings.append({"rule": "graph.crossing_not_connection", "severity": "info", "assessment": "NOT ASSESSED", "message": "Graphical crossings/lines were not converted to connections", "object_ids": []})
    return {"model": {"schema_version": SCHEMA_VERSION, "objects": objects, "ports": ports, "connections": connections}, "findings": _normalize_findings(findings)}


def audit_graph(model):
    findings = []
    if not isinstance(model, dict) or model.get("schema_version") != SCHEMA_VERSION:
        return _normalize_findings([{"rule": "graph.schema", "severity": "error", "message": "Expected graph schema_version 1.0", "object_ids": []}])
    sections = {name: model.get(name) for name in ("objects", "ports", "connections")}
    for name, values in sections.items():
        if not isinstance(values, list):
            findings.append({"rule": "graph.incomplete", "severity": "warning", "message": f"Missing or invalid {name}", "object_ids": []})
            sections[name] = []
        elif not values:
            findings.append({"rule": "graph.incomplete", "severity": "warning", "assessment": "NOT ASSESSED", "message": f"Graph section {name} is empty; completeness is not assessed", "object_ids": []})
    ids, tags = {}, {}
    for section, items in sections.items():
        for item in items:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"].strip():
                findings.append({"rule": "graph.invalid_id", "severity": "error", "message": f"Invalid ID in {section}", "object_ids": []}); continue
            ident = item["id"]
            if ident in ids: findings.append({"rule": "graph.duplicate_id", "severity": "error", "message": f"Duplicate ID {ident}", "object_ids": [ident]})
            ids[ident] = section
            if section == "objects" and item.get("tag") is not None:
                tag = str(item["tag"])
                if tag in tags: findings.append({"rule": "graph.duplicate_tag", "severity": "error", "message": f"Duplicate tag {tag}", "object_ids": [tags[tag], ident]})
                tags[tag] = ident
    objects = {x["id"]: x for x in sections["objects"] if isinstance(x, dict) and isinstance(x.get("id"), str)}
    ports = {x["id"]: x for x in sections["ports"] if isinstance(x, dict) and isinstance(x.get("id"), str)}
    for port in ports.values():
        owner = port.get("owner_id")
        if not isinstance(owner, str) or owner not in objects: findings.append({"rule": "graph.missing_owner", "severity": "error", "message": f"Port owner {owner!r} is unknown", "object_ids": [port["id"]]})
        if port.get("service_ref") is None: findings.append({"rule": "graph.unknown_service", "severity": "info", "assessment": "NOT ASSESSED", "message": "Port service is unknown", "object_ids": [port["id"]]})
    for conn in sections["connections"]:
        if not isinstance(conn, dict): continue
        for field in ("from_port", "to_port"):
            if not isinstance(conn.get(field), str) or conn[field] not in ports: findings.append({"rule": "graph.missing_endpoint", "severity": "error", "message": f"Unknown {field} reference", "object_ids": [str(conn.get("id"))]})
        conn_kind = conn.get("kind")
        if not isinstance(conn_kind, str) or conn_kind not in ("process", "signal", "utility", "unknown"):
            findings.append({"rule": "graph.unknown_kind", "severity": "warning", "message": "Connection kind is unknown", "object_ids": [str(conn.get("id"))]})
        a = ports.get(conn.get("from_port")) if isinstance(conn.get("from_port"), str) else None
        b = ports.get(conn.get("to_port")) if isinstance(conn.get("to_port"), str) else None
        if a and b and conn_kind in ("process", "signal"):
            ka, kb = a.get("port_kind"), b.get("port_kind")
            if not isinstance(ka, str) or not isinstance(kb, str):
                findings.append({"rule": "graph.unknown_kind", "severity": "warning", "assessment": "NOT ASSESSED", "message": "Endpoint port kind is missing or malformed", "object_ids": [str(conn.get("id")), a["id"], b["id"]]})
            elif {ka, kb} == {"signal", "process"}:
                findings.append({"rule": "graph.incompatible_kind", "severity": "error", "message": "Signal and process ports are connected", "object_ids": [str(conn.get("id")), a["id"], b["id"]]})
    for obj in objects.values():
        if obj.get("kind") == "unknown": findings.append({"rule": "graph.unknown_kind", "severity": "info", "assessment": "NOT ASSESSED", "message": "Object kind is unknown", "object_ids": [obj["id"]]})
        links = obj.get("internal_links")
        valid_links = isinstance(links, list) and bool(links) and all(
            isinstance(link, dict) and isinstance(link.get("id"), str) and link["id"].strip()
            and isinstance(link.get("from_port"), str) and link["from_port"] in ports
            and isinstance(link.get("to_port"), str) and link["to_port"] in ports
            and ports[link["from_port"]].get("owner_id") == obj["id"]
            and ports[link["to_port"]].get("owner_id") == obj["id"]
            for link in links
        )
        if obj.get("is_assembly") is True and not valid_links:
            findings.append({"rule": "graph.assembly_incomplete", "severity": "warning", "assessment": "NOT ASSESSED", "message": "Assembly internal ports/links are not explicitly modeled", "object_ids": [obj["id"]]})
    if not sections["ports"]: findings.append({"rule": "graph.incomplete", "severity": "warning", "message": "No explicit ports; topology is incomplete", "object_ids": []})
    return _normalize_findings(findings)
