# Context: TASK-0010

## Required Documents

### Canonical
- `docs/canonical/data_contracts.md` — Section 5 (manifest required path: `docs/runtime/docs_manifest.yaml`), Section 6.1 (root schema shape)
- `docs/canonical/architecture.md` — Section 6.4 (`adapters/` is home for filesystem adapter)

### Working
- `docs/working/implementation_plan.md` — Phase 2: docs manifest loader
- `docs/working/current_focus.md` — Phase 2 is now active

### Runtime
- `docs/runtime/PROJECT_RULES.md` — always

## Prior Work
- TASK-0001 (`done`): `src/ai_build_toolkit/adapters/__init__.py` exists
- TASK-0004 (`done`): `adapters/filesystem.py` with `resolve_repo_root()` established the adapter pattern
- TASK-0008 (`done`): `MissingPathError` and `ConfigError` available in `domain/errors.py`

## Files Expected to Exist Before Execution
- `src/ai_build_toolkit/adapters/filesystem.py`
- `src/ai_build_toolkit/domain/errors.py`
- `docs/runtime/docs_manifest.yaml` (present in this repo — used for test fixture reference)
