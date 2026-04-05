# Context: TASK-0012

## Required Documents

### Canonical
- `docs/canonical/architecture.md` — Section 6.3 (`domain/` responsibility), Section 7.1 (Document Record minimum fields)
- `docs/canonical/data_contracts.md` — Section 6.2 (doc entry schema field names)

### Working
- `docs/working/implementation_plan.md` — Phase 2: document registry model
- `docs/working/current_focus.md` — Phase 2 active

### Runtime
- `docs/runtime/PROJECT_RULES.md` — always

## Prior Work
- TASK-0010 (`done`): `adapters/manifest.py` — `load_manifest()` returns parsed dict
- TASK-0011 (`done`): `validators/manifest_validator.py` — `validate_manifest_schema()` validates the dict
- TASK-0001 (`done`): `src/ai_build_toolkit/domain/__init__.py` exists

## Files Expected to Exist Before Execution
- `src/ai_build_toolkit/domain/__init__.py`
- `src/ai_build_toolkit/adapters/manifest.py`
- `src/ai_build_toolkit/validators/manifest_validator.py`
