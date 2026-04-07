# Deliverable Spec: TASK-0015

## Definition of Done

1. `src/ai_build_toolkit/services/docs_service.py` exists with `validate_docs(root: Path) -> CommandResult`
2. `validate_docs` calls all five Phase 2 components in sequence
3. All validation errors collected into `CommandResult.errors`
4. `CommandResult.ok = False` when any errors are present
5. `abt docs validate` exits 0 on a valid repo, exits 3 on validation failure
6. `abt docs validate --format json` produces valid JSON output
7. Missing manifest is reported as an error (not a crash)
8. CLI layer stays thin — no validation logic in `docs.py`
9. Tests cover pass, manifest-missing, schema-error, existence-error cases
10. All tests passing, no regressions

## Out of Scope
- `abt docs show` (TASK-0016 / P2-T07)
- `abt docs index` (P2-T08, blocked on Q5)
- Validator test fixtures (P2-T09)
