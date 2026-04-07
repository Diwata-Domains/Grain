# Context: P2-T09-TASK-0017

## Required Documents

### Canonical
- `docs/canonical/data_contracts.md` — Section 5 (manifest required sections), Section 6 (full manifest schema)

### Working
- `docs/working/implementation_plan.md` — Phase 2: validator test fixtures

### Runtime
- `docs/runtime/PROJECT_RULES.md` — always

## Prior Work
- TASK-0011 (`done`): `manifest_validator.py` — schema rules to match in valid_manifest.yaml
- TASK-0013 (`done`): `doc_existence_validator.py` — needs declared paths to exist in valid_repo fixture
- TASK-0014 (`done`): `authority_validator.py` — bad authority / editable canonical fixtures
- TASK-0015 (`done`): `test_docs_validate_cmd.py` — _minimal_valid_manifest() to be replaced
- TASK-0016 (`done`): `test_docs_show_cmd.py` — _setup_repo() to be replaced

## Files Expected to Exist Before Execution
- `tests/test_docs_validate_cmd.py`
- `tests/test_docs_show_cmd.py`
- `tests/test_manifest_validator.py`
