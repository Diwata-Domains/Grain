# Deliverable Spec: TASK-0011

## Definition of Done

This task is complete when all of the following are true:

1. `src/ai_build_toolkit/validators/manifest_validator.py` exists
2. `validate_manifest_schema(manifest: dict) -> list[str]` is implemented
3. Returns empty list for a fully valid manifest
4. Returns error strings for each missing required top-level section
5. Returns error strings for missing required fields on doc entries in `canonical`, `working`, `runtime`
6. Returns error strings for missing required sub-keys in `tasks` and `rules`
7. Returns error string if `editable_by_agents` is not a boolean
8. Returns error string if `read_when` is absent or empty
9. Does not raise exceptions — always returns a list
10. Does not load files — operates on a dict
11. Tests cover valid and invalid cases — all passing

## Out of Scope
- File existence checks (TASK-0012 / P2-T04)
- Document registry model (P2-T03)
- CLI wiring (P2-T06)
