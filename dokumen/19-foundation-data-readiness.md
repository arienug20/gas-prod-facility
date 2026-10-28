# Foundation data readiness contract

**Status:** additive prototype contract for roadmap BPD-201/BPD-202/BPD-203; not an approved project schema or engineering acceptance procedure.

## Scope

`cad/roadmap_foundation/readiness.py` is a standalone Python standard-library module. It does not import or modify drawing builders, profiles, design basis, skills, or existing agenda logic. `validate_basis(payload)` reports structural/provenance issues. `assess_readiness(payload, deliverable_id)` returns a JSON-compatible report with `schema_version: "1.0"`, `status`, `questions`, `findings`, `blocked_tasks`, and `independent_work`. The input is never mutated.

## Minimal input contract

The root object has exactly the required collections below; extra keys are tolerated so an adapter can carry metadata, but this prototype assigns no semantics to them.

```json
{
  "schema_version": "1.0",
  "sources": [{"id": "SRC-X", "revision": "REV-X", "locator": "controlled location or citation"}],
  "basis_items": [{
    "id": "BASIS-X", "value": null, "unit": null,
    "certainty_kind": "tbd",
    "confirmation_state": "unconfirmed",
    "source_refs": [], "scope": ["DEL-X"]
  }],
  "authorizations": [],
  "deliverables": [{
    "id": "DEL-X", "kind": "pfd", "phase": "FEED",
    "requirements": [{
      "basis_ref": "BASIS-X", "applicability": "required",
      "task_ids": ["TASK-X"]
    }]
  }]
}
```

Allowed `certainty_kind`: `source_fact`, `assumption`, `tbd`. Allowed `confirmation_state`: `extracted`, `unconfirmed`, `confirmed`, `conflict`, `superseded`. These are independent fields: an extracted fact is not confirmed. A `tbd` value must be JSON null and cannot be confirmed. A confirmed item requires a non-empty `confirmation_ref` and an active `basis_confirmation` authorization with the exact same `confirmation_ref` whose scope covers its basis ID. A source fact requires at least one valid source reference. An assumption requires `authorization_ref` to an active `assumption` authorization whose scope covers that basis ID. Authorizations record declared actor/scope; this prototype cannot authenticate a person's identity or verify an external approval record.

Every basis item needs explicit `scope`, a non-empty deliverable ID string or list of deliverable IDs. This is distinct from `authorizations[].scope`: confirmation/assumption authorization scopes identify basis item IDs, while a partial authorization scope identifies deliverable IDs. A basis item outside the requested deliverable scope produces a visible hold and targeted question; scopes are never inferred or widened. Missing/invalid basis scope is structural invalidity and cannot pass readiness. Legacy records without scope remain unconfirmed/not ready until supplied with explicit scope evidence.

Numeric `value` entries require a non-empty `unit`. The explicit dimensionless convention is `quantity_kind: "dimensionless"` with `unit: "1"`; `unit: "1"` without that declaration is rejected. Text narrative values may keep `unit: null`. The checker does no unit conversion or physical dimension validation, and it infers no unit for unknown or null values.

Sources require stable `id`, `revision`, and `locator`; every `source_refs` entry must resolve. This prototype does not infer a fact from source content or compare source revisions. A contradiction explicitly marked `conflict` remains open. Source revisions are opaque labels, not an ordering rule.

Deliverable `kind` is `basis`, `bfd`, `pfd`, or `pid`; `phase` is `FEED` or `DED`. Requirement applicability is `required`, `conditional`, `not_applicable`, or `unresolved`. `not_applicable` requires a rationale. A conditional requirement with missing/unknown `condition_met` produces a targeted open question. A false condition excludes the requirement from this deliverable; a true condition proceeds to the basis check. `task_ids` are optional labels linking work to a requirement; an unknown requirement creates a hold even when no task ID is supplied (the basis ID is used as the hold label). Other tasks remain listed as independent work.

An active `partial` authorization requires an actor, a deliverable ID in `scope`, explicit `basis_refs`, and a non-empty `purpose`. It produces `partial` status only when its basis references cover every held requirement for that deliverable; holds stay visible and are never resolved by consent. Silence and absence of authorization have no positive effect. `ready` means only that the declared requirements passed these narrow data checks; it is not design approval, document approval, safety acceptance, or proof of standards compliance.

## Statuses and findings

- `invalid`: schema shape, enum, duplicate ID, or reference validation failed; assessment stops.
- `not_assessed`: the deliverable has no requirements declared; it is never treated as ready.
- `blocked`: one or more in-scope questions/holds remain without qualifying partial authorization.
- `partial`: explicit partial authorization covers every held basis item for the deliverable, while applicable holds remain open.
- `ready`: no applicable requirement produced a hold under this contract.

Findings use the shared fields `rule`, `category`, `severity`, `message`, and `object_ids` where an object is identifiable. `questions` identify the related basis item, requested information, and linked task IDs. Readiness questions are separate from structural errors so unknown project data does not masquerade as malformed input.

## Family question prompts

Pesan temuan dan pertanyaan otomatis ditulis dalam Bahasa Indonesia. Jika requirement sudah memuat `question`, teks tersebut dipertahankan persis seperti input dan tidak diterjemahkan diam-diam; isi pertanyaan itu sebaiknya disusun dari scope proyek yang disetujui. Pertanyaan keluarga separator, reciprocating pump, dan flare dapat disediakan profile atau adapter di masa depan; core ini tidak memberlakukan checklist fungsi universal dan tidak menetapkan nilai proses, tag equipment, fungsi, atau applicability untuk keluarga tersebut. Rule ID, field JSON, dan enum status tetap menggunakan identifier kontrak yang stabil.

## CLI and limits

Jalankan `python -m cad.roadmap_foundation.readiness INPUT.json DELIVERABLE_ID [--out REPORT.json]` dari root repository (atau jalankan file modul secara langsung). CLI menampilkan JSON terstruktur, memakai pesan bantuan dan kesalahan khusus dalam Bahasa Indonesia, mengembalikan kode nol hanya untuk status `ready`, dan menolak output yang sama dengan input atau sudah ada. Teks usage dan label opsi bawaan dari argparse dapat tetap berbahasa Inggris. Prototype tidak membuat output jika direktori induknya belum ada.

This is a new, isolated schema and has no adapter to existing builders. It checks only declared links and decisions; it does not cover all roadmap deliverables, calculation validity, standards applicability, safety-critical classification, workflow roles, document approval, or authorization identity. A passing result therefore cannot be promoted to a project-wide readiness or engineering-compliance claim.
