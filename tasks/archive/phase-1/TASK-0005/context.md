# Context: TASK-0005

## Required Documents

### Canonical
- `docs/canonical/cli_spec.md` — Section 6.1 (init command: responsibilities, must-nots, options, expected behavior), Section 4.2 (path resolution), Section 4.4 (dry-run), Section 7.2 (file modification transparency), Section 7.3 (canonical protection rule)
- `docs/canonical/architecture.md` — Section 4.1 (CLI must not hold business logic), Section 4.2 (Application Services Layer), Section 4.9 (Template and Scaffolding System), Section 5 (repository structure layout), Section 6.2 (`services/` boundary)
- `docs/canonical/data_contracts.md` — Section 4 (required canonical docs list), Section 14 (template contract)

### Working
- `docs/working/implementation_plan.md` — Phase 1: repository init command deliverable
- `docs/working/current_focus.md` — confirms `abt init` is immediate goal #5

### Runtime
- `docs/runtime/PROJECT_RULES.md` — always

## Prior Work
- TASK-0001 (`done`): `src/ai_build_toolkit/services/` exists and is importable
- TASK-0003 (`done`): `abt init` stub registered in CLI
- TASK-0004 (`done`): `resolve_repo_root()` available in `adapters/filesystem.py`

## Files Expected to Exist Before Execution
- `src/ai_build_toolkit/cli/init.py`
- `src/ai_build_toolkit/services/__init__.py`
- `src/ai_build_toolkit/adapters/filesystem.py`

## Notes
P1-T06 (template directory structure) is a related but separate task. If seed file templates are not yet defined, `init` should create minimal placeholder content rather than block.
