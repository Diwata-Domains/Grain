# Deliverable Spec: P2-T09-TASK-0017

## Definition of Done

1. `tests/fixtures/valid_manifest.yaml` exists and passes `validate_manifest_schema()`
2. `tests/fixtures/manifest_missing_section.yaml` exists and fails schema validation
3. `tests/fixtures/manifest_bad_authority.yaml` exists and fails authority validation
4. `tests/fixtures/manifest_editable_canonical.yaml` exists and fails authority validation
5. `tests/conftest.py` exists with `valid_manifest_dict` and `valid_repo` fixtures
6. `test_docs_validate_cmd.py` uses `valid_repo` fixture — no inline manifest builder
7. `test_docs_show_cmd.py` uses `valid_repo` fixture — no inline setup helper
8. All 147 existing tests still pass after refactor
9. No new test cases added — fixtures and refactor only
