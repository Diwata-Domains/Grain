# Deliverable Spec: TASK-0013

## Definition of Done

1. `src/ai_build_toolkit/validators/doc_existence_validator.py` exists
2. `validate_doc_existence(registry: DocumentRegistry, root: Path) -> list[str]` implemented
3. Returns empty list when all declared paths exist
4. Returns error string (with record id and path) for each missing file or directory
5. Empty `path` string treated as missing
6. Does not raise — always returns a list
7. Does not validate schema or authority
8. Tests passing

## Out of Scope
- Authority-order validation (TASK-0014 / P2-T05)
- CLI wiring (P2-T06)
