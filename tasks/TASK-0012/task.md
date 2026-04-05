# Task: Implement document registry model

## Metadata
- **ID:** TASK-0012
- **Status:** done
- **Phase:** Phase 2 — Documentation Registry and Validation
- **Dependencies:** TASK-0010 (manifest loader), TASK-0011 (manifest schema validator)

## Objective
Implement the in-memory document registry model in `src/ai_build_toolkit/domain/documents.py`. This consists of a `DocumentRecord` dataclass representing one known project document and a `DocumentRegistry` class that holds and queries document records by ID, layer, and other attributes.

## Why This Task Exists
`implementation_plan.md` Phase 2 lists "authority-aware document registry model" as a major deliverable. `architecture.md` Section 7.1 defines the minimum fields for a document record. The registry is the queryable in-memory representation that all downstream Phase 2 work (`abt docs validate`, `abt docs show`) depends on.

## Scope
- `DocumentRecord` dataclass with fields from `architecture.md` Section 7.1
- `DocumentRegistry` class with methods: `all()`, `by_id(id)`, `by_layer(layer)`
- `build_registry(manifest: dict) -> DocumentRegistry` factory that parses a validated manifest dict into registry entries
- All three doc layers supported: `canonical`, `working`, `runtime`

## Constraints
- Must live in `domain/` — this is a pure domain model, no filesystem access (`architecture.md` Section 6.3)
- `DocumentRecord` fields must match `architecture.md` Section 7.1 minimum: `id`, `path`, `layer`, `purpose`, `authority`, `editable_by_agents`, `read_when`
- `build_registry` must accept an already-validated manifest dict — do not call `load_manifest` or `validate_manifest_schema` internally
- Must not raise on an empty or partial manifest — return a registry with zero entries

## Escalation Conditions
- `architecture.md` Section 7.1 field list conflicts with manifest schema fields in `data_contracts.md` Section 6.2
