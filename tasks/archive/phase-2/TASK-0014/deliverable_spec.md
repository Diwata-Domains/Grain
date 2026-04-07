# Deliverable Spec: TASK-0014

## Definition of Done

1. `src/ai_build_toolkit/validators/authority_validator.py` exists
2. `validate_authority(registry: DocumentRegistry, manifest: dict) -> list[str]` implemented
3. Returns empty list for a fully valid registry and manifest
4. Returns error for any record with an `authority` value outside the allowed set
5. Returns error for any canonical-layer record with `editable_by_agents: True`
6. Non-canonical records with `editable_by_agents: True` do not trigger error
7. Returns error if `rules.authority_order` is absent or empty
8. Never raises — always returns a list
9. Does not validate path existence
10. All tests passing

## Out of Scope
- Path existence checks (TASK-0013, done)
- CLI wiring (P2-T06)
