# Context: TASK-0011

## Required Documents

### Canonical
- `docs/canonical/data_contracts.md` — Section 5 (required top-level sections), Section 6 (full manifest schema including doc entry fields, tasks section, rules section)

### Working
- `docs/working/implementation_plan.md` — Phase 2: manifest schema validator
- `docs/working/current_focus.md` — Phase 2 active

### Runtime
- `docs/runtime/PROJECT_RULES.md` — always

## Prior Work
- TASK-0010 (`done`): `adapters/manifest.py` with `load_manifest()` established; validator receives its output
- TASK-0001 (`done`): `src/ai_build_toolkit/validators/__init__.py` exists

## Files Expected to Exist Before Execution
- `src/ai_build_toolkit/validators/__init__.py`
- `src/ai_build_toolkit/adapters/manifest.py`
