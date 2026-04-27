# Deliverable Spec: TASK-0012

## Definition of Done

This task is complete when all of the following are true:

1. `src/ai_build_toolkit/domain/documents.py` exists
2. `DocumentRecord` dataclass has fields: `id`, `path`, `layer`, `purpose`, `authority`, `editable_by_agents`, `read_when`
3. `DocumentRegistry` has methods: `all()`, `by_id(id)`, `by_layer(layer)`
4. `build_registry(manifest: dict) -> DocumentRegistry` factory exists
5. `build_registry` correctly populates records from `canonical`, `working`, and `runtime` sections
6. Each record's `layer` field reflects its source section
7. `by_id` returns `None` for unknown IDs (does not raise)
8. Empty or missing sections handled without raising
9. No filesystem access in `domain/documents.py`
10. Tests cover all public methods and edge cases — all passing

## Out of Scope
- Document existence validation (TASK-0013 / P2-T04)
- Authority-order validation (P2-T05)
- CLI wiring (P2-T06, P2-T07)
