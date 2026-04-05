# Context: P2-T08-TASK-0018

## Required Documents

### Canonical
- `docs/canonical/architecture.md` — Section 4.1/4.2 (thin CLI, service layer)
- `docs/canonical/cli_spec.md` — Section 4.3 (output), Section 4.4 (dry-run)

### Working
- `docs/working/implementation_plan.md` — Phase 2: `abt docs index`
- `docs/working/open_questions.md` — Q5 resolved: manifest primary, index generated

### Runtime
- `docs/runtime/PROJECT_RULES.md` — always
- `docs/runtime/docs_index.md` — current content (will be overwritten by this command)

## Prior Work
- TASK-0010 (`done`): `adapters/manifest.py` — `load_manifest()`
- TASK-0012 (`done`): `domain/documents.py` — `build_registry()`
- TASK-0015 (`done`): `services/docs_service.py` — service pattern established
- P2-T07-TASK-0016 (`done`): `cli/docs.py` — `docs_index` stub exists

## Files Expected to Exist Before Execution
- `src/ai_build_toolkit/services/docs_service.py`
- `src/ai_build_toolkit/cli/docs.py` (stub with `docs_index` command)
- `docs/runtime/docs_index.md` (will be overwritten)
