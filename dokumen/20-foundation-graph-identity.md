# Foundation: graph identity and tag registry

**Status:** implementation foundation only; not engineering semantic approval, design authorization, or evidence that the graph is complete.

`cad/roadmap_foundation/registry.py` provides a stdlib-only persistent tag registry and a conservative adapter to graph schema `1.0`.

## Registry API

Construct with `NamespaceTagRegistry(path, namespace, allocation)`. The allocation record must explicitly provide `id`, `approved_by`, `namespace`, `pattern`, `start`, and `scope`; it must match the registry namespace. `scope` must contain non-empty `prefixes` and/or `object_ids` lists. Allocation is limited to those prefixes/object IDs; reservation checks the supplied tag against the approved pattern/prefix and any object-ID scope. No allocation record means construction fails. A namespace is an administrative boundary, not proof that the same tag is globally unique across namespaces. `reserve(tag, object_id)` preserves supplied identities and rejects collisions and out-of-scope tags. `allocate(prefix, object_id)` is deterministic within the persisted registry. `save()` acquires an exclusive sibling lock before checking the on-disk hash and replacing atomically; contention beyond the bounded wait fails closed. A stale instance cannot overwrite a newer registry. A crashed writer may leave a lock file; resolve that operationally only after confirming no writer remains. `NamespaceTagRegistry.reopen(path, namespace, allocation)` reloads and validates the schema; malformed and unsupported data fails closed. `to_dict()` exposes the auditable record.

Example (use only an actual approved allocation record):

```python
from roadmap_foundation.registry import NamespaceTagRegistry
registry = NamespaceTagRegistry("registry.json", "approved-namespace", approved_allocation_record)
registry.reserve(existing_tag, object_id)
new_tag = registry.allocate(prefix, another_object_id)
registry.save()
```

Do not use the illustrative identifiers in tests as project allocation evidence. If allocation authority is absent, keep the tag unresolved; do not allocate or renumber.

## Graph adapter and audit

`adapt_legacy_model(model)` returns `{"model": ..., "findings": ...}` without mutating its input. It supports the phase1 `smart_qa` shape with top-level ports (`owner`, `point`, `dn`, `spec`) and connections (`from`, `to`, `dn`, `spec`), mapping only those known fields and retaining DN/spec/point as metadata. Canonical model sections are `objects` (`id`, `kind`, optional `tag`), `ports` (`id`, `owner_id`, `port_kind`, `direction`, nullable `service_ref`), and `connections` (`id`, `from_port`, `to_port`, `kind`). Nested and top-level duplicate ports are preserved and explicitly reported. Missing legacy ports/internal links remain findings; explicit assemblies without modeled internal links are `NOT ASSESSED`. Empty graph sections are explicitly incomplete. The adapter does not infer nozzles, valve internals, connections from line geometry, or junctions from crossings. `audit_graph(model)` checks IDs, tags, owner and endpoint references, and explicit kind compatibility. Unknown service/media is reported as `NOT ASSESSED`, not a mismatch or pass. Null DN/spec fields are not blanket errors. Process and signal kinds are distinct when explicitly supplied. No SIL, safety-function, or overall engineering-completeness claim is made.

Run focused checks from the repository root:

```powershell
python -m unittest cad.test_roadmap_registry -v
```

The tests cover authorization, duplicate tags, persistence/reopen, stale write detection, atomic replacement failure, unsupported schema, legacy input immutability, unknown internal topology, and crossings not becoming connections.
