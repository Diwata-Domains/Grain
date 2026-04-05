# Plan: TASK-0012

## Recommended Model
- **Primary:** `frontier_model`
- **Secondary:** `reviewer_model`
- **Reason:** Domain model design — must reconcile field names from two canonical sources (`architecture.md` Section 7.1 and `data_contracts.md` Section 6.2) and produce a clean, queryable structure with no filesystem dependencies.

## Steps

1. Create `src/ai_build_toolkit/domain/documents.py`:
   - `DocumentRecord` dataclass with fields: `id`, `path`, `layer`, `purpose`, `authority`, `editable_by_agents`, `read_when`
   - `DocumentRegistry` class:
     - holds a list of `DocumentRecord` instances
     - `all() -> list[DocumentRecord]`
     - `by_id(id: str) -> DocumentRecord | None`
     - `by_layer(layer: str) -> list[DocumentRecord]`
   - `build_registry(manifest: dict) -> DocumentRegistry` factory:
     - iterates over `canonical`, `working`, `runtime` entries in manifest
     - creates a `DocumentRecord` per entry with `layer` set to the section name
     - skips non-list or empty sections gracefully

2. Write tests in `tests/test_document_registry.py`:
   - `build_registry` with valid manifest returns populated registry
   - `by_id` returns correct record
   - `by_id` returns None for unknown id
   - `by_layer` returns only records for that layer
   - `all()` returns all records across layers
   - Empty manifest returns empty registry without raising
   - Layer field on each record matches its source section

## Patch Strategy
- New file: `src/ai_build_toolkit/domain/documents.py`
- New file: `tests/test_document_registry.py`
- No other files touched
