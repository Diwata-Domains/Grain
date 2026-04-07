# Task: Add validator test fixtures for docs

## Metadata
- **ID:** TASK-0017
- **Status:** done
- **Phase:** Phase 2 — Documentation Registry and Validation
- **Backlog:** P2-T09
- **Dependencies:** TASK-0011, TASK-0013, TASK-0014, TASK-0015 (all Phase 2 validators and CLI done)

## Objective
Create reusable on-disk test fixtures — valid and invalid manifest/doc structures — and refactor the Phase 2 test suite to use shared fixtures where the same setup is repeated across multiple test files. This improves test maintainability and makes failure cases explicit and inspectable.

## Why This Task Exists
`backlog.md` P2-T09 lists "valid and invalid manifest/doc structure test fixtures" as a Phase 2 deliverable. Currently each test file builds its own inline manifest dict or tmp_path structure. Shared fixtures in `tests/fixtures/` and a `conftest.py` make the intent explicit and reduce duplication without changing test coverage.

## Scope
- Create `tests/fixtures/` directory with on-disk YAML fixture files:
  - `valid_manifest.yaml` — fully valid manifest matching the real repo shape
  - `manifest_missing_section.yaml` — missing one required top-level section
  - `manifest_bad_authority.yaml` — doc entry with invalid authority value
  - `manifest_editable_canonical.yaml` — canonical doc with `editable_by_agents: true`
- Create `tests/conftest.py` with pytest fixtures:
  - `valid_manifest_dict` — loads `valid_manifest.yaml` as a dict
  - `valid_repo(tmp_path)` — builds a tmp_path repo with valid manifest and declared files
- Refactor `test_docs_validate_cmd.py` and `test_docs_show_cmd.py` to use `valid_repo` fixture

## Constraints
- Fixtures must be real files in `tests/fixtures/`, not inline dicts
- `conftest.py` must use `pytest.fixture` — no test logic in conftest
- Do not change the assertions in existing tests — only the setup code
- Do not add new test cases in this task — fixtures only
- `valid_manifest.yaml` must match `data_contracts.md` Section 6 schema exactly

## Escalation Conditions
- Refactoring existing tests reveals a broken test assumption that was masked by inline setup
