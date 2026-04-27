# Deliverable Spec: TASK-0064

## Acceptance Criteria

1. `forge init --primary-adapter code_adapter` succeeds and surfaces `primary_adapter=code_adapter` in text output.
2. `forge init --secondary-adapter frontend_adapter` succeeds and surfaces `secondary_adapter=frontend_adapter` in text output.
3. `forge init --primary-adapter nonexistent` succeeds with a warning about the unknown adapter; no primary_adapter recorded.
4. `forge init` with no adapter options produces no adapter fields and no adapter warnings (adapter-neutral).
5. `forge init --dry-run --primary-adapter code_adapter` validates and reports without writing files.
6. JSON output includes `primary_adapter` and `secondary_adapters` fields.
7. All existing init tests (8) still pass unchanged.
8. 7 new adapter tests pass.
9. Full test suite passes (409 tests).
