# Context: TASK-0015

## Required Documents

### Canonical
- `docs/canonical/cli_spec.md` — Section 4.1 (command shape), Section 4.3 (output rules), Section 5 (exit codes)
- `docs/canonical/architecture.md` — Section 4.1 (CLI layer must not hold business rules), Section 4.2 (services layer)

### Working
- `docs/working/implementation_plan.md` — Phase 2: `abt docs validate`

### Runtime
- `docs/runtime/PROJECT_RULES.md` — always

## Prior Work
- TASK-0010 (`done`): `adapters/manifest.py` — `load_manifest(root)`
- TASK-0011 (`done`): `validators/manifest_validator.py` — `validate_manifest_schema(manifest)`
- TASK-0012 (`done`): `domain/documents.py` — `build_registry(manifest)`
- TASK-0013 (`done`): `validators/doc_existence_validator.py` — `validate_doc_existence(registry, root)`
- TASK-0014 (`done`): `validators/authority_validator.py` — `validate_authority(registry, manifest)`
- TASK-0002/TASK-0007 (`done`): `cli/output.py` — `CommandResult`, `print_result()`; `adapters/filesystem.py` — `resolve_repo_root()`

## Files Expected to Exist Before Execution
- `src/ai_build_toolkit/cli/docs.py` (stub exists)
- `src/ai_build_toolkit/services/__init__.py`
- `src/ai_build_toolkit/services/init_service.py` (pattern reference)
- All adapters and validators listed above
