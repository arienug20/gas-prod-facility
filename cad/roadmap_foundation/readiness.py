"""Small, data-first readiness evaluator for roadmap foundation inputs.

This module is intentionally standalone and uses only the Python standard library.
It checks provenance and scoped decisions; it does not evaluate engineering design.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
CERTAINTY = {"source_fact", "assumption", "tbd"}
CONFIRMATION = {"extracted", "unconfirmed", "confirmed", "conflict", "superseded"}
APPLICABILITY = {"required", "conditional", "not_applicable", "unresolved"}


def _finding(code: str, message: str, **extra: Any) -> dict:
    row = {"rule": code, "category": code.split(".", 1)[0], "severity": "error",
           "message": message, **extra}
    if "basis_id" in row:
        row.setdefault("object_ids", [row["basis_id"]])
    elif "deliverable_id" in row:
        row.setdefault("object_ids", [row["deliverable_id"]])
    return row


def validate_basis(payload: Any) -> list[dict]:
    """Return structural/provenance findings. Empty means structurally valid."""
    out: list[dict] = []
    if not isinstance(payload, dict):
        return [_finding("schema.payload", "Payload must be an object.")]
    if payload.get("schema_version") != SCHEMA_VERSION:
        out.append(_finding("schema.version", "schema_version must be '1.0'."))
    for key in ("sources", "basis_items", "authorizations", "deliverables"):
        if not isinstance(payload.get(key), list):
            out.append(_finding("schema.collection", f"{key} must be an array.", path=key))
    if out:
        return out

    sources = _unique_map(payload["sources"], "sources", out)
    items = _unique_map(payload["basis_items"], "basis_items", out)
    auths = _unique_map(payload["authorizations"], "authorizations", out)
    delivers = _unique_map(payload["deliverables"], "deliverables", out)
    for sid, source in sources.items():
        for field in ("revision", "locator"):
            if not _nonempty(source.get(field)):
                out.append(_finding("source.field", f"Source {sid} needs {field}.", source_id=sid))

    for bid, item in items.items():
        if not isinstance(item.get("certainty_kind"), str) or item.get("certainty_kind") not in CERTAINTY:
            out.append(_finding("basis.certainty", f"Basis item {bid} has invalid certainty_kind.", basis_id=bid))
        if not isinstance(item.get("confirmation_state"), str) or item.get("confirmation_state") not in CONFIRMATION:
            out.append(_finding("basis.confirmation", f"Basis item {bid} has invalid confirmation_state.", basis_id=bid))
        if not _valid_scope(item.get("scope")):
            out.append(_finding("basis.scope_missing", f"Basis item {bid} needs explicit deliverable scope as a string ID or non-empty array of string IDs.", basis_id=bid))
        refs = item.get("source_refs")
        if not isinstance(refs, list):
            out.append(_finding("basis.source_refs", f"Basis item {bid} source_refs must be an array.", basis_id=bid))
        else:
            if item.get("certainty_kind") == "source_fact" and not refs:
                out.append(_finding("basis.source_required", f"Source fact {bid} needs at least one source reference.", basis_id=bid))
            for ref in refs:
                if not isinstance(ref, str) or ref not in sources:
                    out.append(_finding("provenance.source_ref", f"Basis item {bid} references unknown source {ref!r}.", basis_id=bid))
        if item.get("certainty_kind") == "tbd" and item.get("value") is not None:
            out.append(_finding("basis.tbd_value", f"TBD item {bid} must have null value.", basis_id=bid))
        if item.get("certainty_kind") != "tbd" and "value" not in item:
            out.append(_finding("basis.value", f"Basis item {bid} needs value (use null only for tbd).", basis_id=bid))
        value = item.get("value")
        if isinstance(value, bool):
            out.append(_finding("basis.value_type", f"Boolean value is not accepted as a numeric basis value for {bid}.", basis_id=bid))
        elif isinstance(value, float) and not math.isfinite(value):
            out.append(_finding("basis.value_finite", f"Basis value for {bid} must be finite.", basis_id=bid))
        elif isinstance(value, (int, float)):
            unit = item.get("unit")
            quantity_kind = item.get("quantity_kind")
            if not _nonempty(unit):
                out.append(_finding("basis.numeric_unit", f"Numeric basis item {bid} needs an explicit unit.", basis_id=bid))
            elif unit == "1" and quantity_kind != "dimensionless":
                out.append(_finding("basis.dimensionless_explicit", f"Numeric basis item {bid} using unit '1' must declare quantity_kind='dimensionless'.", basis_id=bid))
            elif quantity_kind == "dimensionless" and unit != "1":
                out.append(_finding("basis.dimensionless_unit", f"Dimensionless basis item {bid} must use unit '1'.", basis_id=bid))
        if item.get("unit") is not None and not _nonempty(item.get("unit")):
            out.append(_finding("basis.unit_type", f"Basis item {bid} unit must be null or a non-empty string.", basis_id=bid))
        if item.get("certainty_kind") == "assumption":
            aid = item.get("authorization_ref")
            auth = auths.get(aid) if isinstance(aid, str) else None
            if not _authorization_matches(auth, bid, "assumption"):
                out.append(_finding("authorization.assumption", f"Assumption {bid} needs active, explicit matching authorization.", basis_id=bid))
        if item.get("confirmation_state") == "confirmed":
            if item.get("certainty_kind") == "tbd" or item.get("value") is None or not _nonempty(item.get("confirmation_ref")):
                out.append(_finding("basis.confirmation_evidence", f"Confirmed item {bid} needs a non-TBD value and explicit confirmation_ref.", basis_id=bid))
            elif not any(_authorization_matches(auth, bid, "basis_confirmation", item.get("confirmation_ref")) for auth in auths.values()):
                out.append(_finding("basis.confirmation_authorization", f"Confirmed item {bid} needs active, scoped confirmation authorization.", basis_id=bid))

    for aid, auth in auths.items():
        if not isinstance(auth.get("kind"), str) or auth.get("kind") not in {"basis_confirmation", "assumption", "partial"}:
            out.append(_finding("authorization.kind", f"Authorization {aid} has invalid kind.", authorization_id=aid))
        if auth.get("active") is True and (not _nonempty(auth.get("actor")) or not _valid_scope(auth.get("scope"))):
            out.append(_finding("authorization.scope", f"Active authorization {aid} needs actor and scope.", authorization_id=aid))
        if auth.get("kind") == "partial" and auth.get("active") is True:
            if not isinstance(auth.get("basis_refs"), list) or not _nonempty(auth.get("purpose")):
                out.append(_finding("authorization.partial_evidence", f"Active partial authorization {aid} needs explicit basis_refs and purpose.", authorization_id=aid))
        if "basis_refs" in auth and (not isinstance(auth["basis_refs"], list) or not all(_nonempty(ref) for ref in auth["basis_refs"])):
            out.append(_finding("authorization.basis_refs", f"Authorization {aid} basis_refs must be an array of strings.", authorization_id=aid))
        if "confirmation_ref" in auth and not _nonempty(auth["confirmation_ref"]):
            out.append(_finding("authorization.confirmation_ref", f"Authorization {aid} confirmation_ref must be a non-empty string.", authorization_id=aid))
    for did, deliverable in delivers.items():
        if not isinstance(deliverable.get("kind"), str) or deliverable.get("kind") not in {"basis", "bfd", "pfd", "pid"}:
            out.append(_finding("deliverable.kind", f"Deliverable {did} has invalid kind.", deliverable_id=did))
        if not isinstance(deliverable.get("phase"), str) or deliverable.get("phase") not in {"FEED", "DED"}:
            out.append(_finding("deliverable.phase", f"Deliverable {did} phase must be FEED or DED.", deliverable_id=did))
        reqs = deliverable.get("requirements")
        if not isinstance(reqs, list):
            out.append(_finding("requirement.collection", f"Deliverable {did} requirements must be an array.", deliverable_id=did))
            continue
        for index, req in enumerate(reqs):
            path = f"deliverables.{did}.requirements.{index}"
            if not isinstance(req, dict):
                out.append(_finding("requirement.shape", f"{path} must be an object.")); continue
            ref = req.get("basis_ref")
            if not isinstance(ref, str) or ref not in items:
                out.append(_finding("provenance.basis_ref", f"{path} references unknown basis item {ref!r}."))
            if not isinstance(req.get("applicability"), str) or req.get("applicability") not in APPLICABILITY:
                out.append(_finding("requirement.applicability", f"{path} has invalid applicability."))
            if req.get("applicability") == "not_applicable" and not _nonempty(req.get("rationale")):
                out.append(_finding("requirement.na_rationale", f"{path} needs a not-applicable rationale."))
            if "task_ids" in req and (not isinstance(req["task_ids"], list) or not all(_nonempty(task) for task in req["task_ids"])):
                out.append(_finding("requirement.task_ids", f"{path} task_ids must be an array of non-empty strings."))
            for field in ("question", "rationale"):
                if field in req and not _nonempty(req[field]):
                    out.append(_finding("requirement.text", f"{path} {field} must be a non-empty string.", field=field))
    return out


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_scope(value: Any) -> bool:
    return _nonempty(value) or (isinstance(value, list) and bool(value) and all(_nonempty(v) for v in value))


def _unique_map(rows: list, name: str, out: list) -> dict:
    result = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or not _nonempty(row.get("id")):
            out.append(_finding("schema.id", f"{name}[{index}] needs a non-empty string id.")); continue
        if row["id"] in result:
            out.append(_finding("schema.duplicate_id", f"Duplicate {name} id {row['id']!r}.")); continue
        result[row["id"]] = row
    return result


def _scope_covers(scope: Any, target: str) -> bool:
    if isinstance(scope, str):
        return scope == target
    return isinstance(scope, list) and target in scope


def _authorization_matches(auth: Any, basis_id: str, kind: str, evidence_ref: str | None = None) -> bool:
    return bool(isinstance(auth, dict) and auth.get("active") is True and auth.get("kind") == kind
                and _nonempty(auth.get("actor")) and _scope_covers(auth.get("scope"), basis_id)
                and (not isinstance(auth.get("basis_refs"), list) or basis_id in auth["basis_refs"])
                and (evidence_ref is None or auth.get("confirmation_ref") == evidence_ref))


def assess_readiness(payload: Any, deliverable_id: str) -> dict:
    """Evaluate requirements for one deliverable without mutating the payload."""
    structural = validate_basis(payload)
    report = {"schema_version": SCHEMA_VERSION, "deliverable_id": deliverable_id,
              "status": "invalid" if structural else "blocked", "questions": [],
              "findings": list(structural), "blocked_tasks": [], "independent_work": []}
    if structural:
        return report
    delivery = next((d for d in payload["deliverables"] if d["id"] == deliverable_id), None)
    if delivery is None:
        report["findings"].append(_finding("deliverable.unknown", f"Unknown deliverable {deliverable_id!r}."))
        return report
    if not delivery["requirements"]:
        report["status"] = "not_assessed"
        report["findings"].append(_finding("readiness.scope_unassessed", "No requirements are declared; readiness is not assessed.", deliverable_id=deliverable_id))
        return report
    items = {i["id"]: i for i in payload["basis_items"]}
    holds, held_basis_refs, partial = [], [], False
    for index, req in enumerate(delivery["requirements"]):
        bid, app = req["basis_ref"], req["applicability"]
        task_ids = req.get("task_ids", [])
        if app == "not_applicable":
            continue
        if app == "conditional" and req.get("condition_met") is False:
            continue
        if app == "conditional" and req.get("condition_met") is not True:
            _add_question(report, req, bid, "Confirm whether the stated condition applies to this deliverable.", task_ids)
            _record_hold(holds, held_basis_refs, task_ids, bid); continue
        if app == "unresolved":
            _add_question(report, req, bid, req.get("question") or "Resolve applicability for this requirement.", task_ids)
            _record_hold(holds, held_basis_refs, task_ids, bid); continue
        item = items[bid]
        if not _scope_covers(item.get("scope"), deliverable_id):
            report["findings"].append(_finding("basis.scope_mismatch", f"Basis item {bid} is not scoped to deliverable {deliverable_id}.", basis_id=bid,
                                                deliverable_id=deliverable_id))
            _add_question(report, req, bid, f"Confirm whether basis item {bid} applies to deliverable {deliverable_id}.", task_ids)
            _record_hold(holds, held_basis_refs, task_ids, bid)
            continue
        known = item.get("confirmation_state") == "confirmed" and item.get("certainty_kind") != "tbd"
        if not known:
            q = req.get("question") or f"Confirm basis item {bid} for {delivery['kind']} {delivery['phase']}."
            _add_question(report, req, bid, q, task_ids)
            _record_hold(holds, held_basis_refs, task_ids, bid)
        if item.get("confirmation_state") == "conflict":
            report["findings"].append(_finding("basis.conflict", f"Basis item {bid} is in conflict.", basis_id=bid))
    active_partials = [a for a in payload["authorizations"] if a.get("active") is True and a.get("kind") == "partial"
                       and _scope_covers(a.get("scope"), deliverable_id)
                       and _nonempty(a.get("purpose"))
                       and set(held_basis_refs).issubset(set(a.get("basis_refs", [])))]
    if active_partials and holds:
        partial = True
        report["findings"].append(_finding("authorization.partial_scope", "Explicit partial authorization permits review only; listed holds remain open.", authorization_ids=[a["id"] for a in active_partials]))
    report["blocked_tasks"] = holds
    report["independent_work"] = _independent_tasks(payload, delivery, set(holds))
    if holds:
        report["status"] = "partial" if partial else "blocked"
    else:
        report["status"] = "ready"
    return report


def _add_question(report: dict, req: dict, bid: str, text: str, task_ids: list) -> None:
    report["questions"].append({"basis_ref": bid, "question": text, "task_ids": list(task_ids)})


def _record_hold(holds: list, held_basis_refs: list, task_ids: list, bid: str) -> None:
    # Preserve a hold even when no downstream task was declared.
    for identifier in task_ids or [f"basis:{bid}"]:
        if identifier not in holds:
            holds.append(identifier)
    if bid not in held_basis_refs:
        held_basis_refs.append(bid)


def _independent_tasks(payload: dict, delivery: dict, held: set) -> list:
    # Tasks associated only with resolved/N/A requirements are independent of current holds.
    result = []
    for req in delivery["requirements"]:
        if req["applicability"] == "not_applicable":
            continue
        for task in req.get("task_ids", []):
            if task not in held and task not in result:
                result.append(task)
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON payload")
    parser.add_argument("deliverable", help="deliverable id")
    parser.add_argument("--out", type=Path, help="write report JSON without overwriting")
    args = parser.parse_args(argv)
    source = args.input.resolve()
    output = args.out.resolve() if args.out else None
    if output and (output == source or output.exists() or not output.parent.is_dir()):
        parser.error("output must be distinct from input, non-existing, and have an existing parent")
    try:
        report = assess_readiness(json.loads(source.read_text(encoding="utf-8")), args.deliverable)
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(f"cannot read valid JSON input: {exc}")
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if output:
        with output.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(rendered)
    print(rendered, end="")
    return 0 if report["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
