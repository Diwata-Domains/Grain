# Context: P2-T07-TASK-0016

## Required Documents

### Canonical
- `docs/canonical/cli_spec.md` — Section 4.3 (output rules), Section 5 (exit codes)
- `docs/canonical/architecture.md` — Section 4.1/4.2 (thin CLI / service layer)

### Working
- `docs/working/implementation_plan.md` — Phase 2: `abt docs show`

### Runtime
- `docs/runtime/PROJECT_RULES.md` — always

## Prior Work
- TASK-0012 (`done`): `domain/documents.py` — `DocumentRegistry.by_id()`
- TASK-0015 (`done`): `services/docs_service.py` + `cli/docs.py` — service and stub both exist

## Files Expected to Exist Before Execution
- `src/ai_build_toolkit/services/docs_service.py`
- `src/ai_build_toolkit/cli/docs.py` (stub with `docs_show` and `doc_id` arg)
- `src/ai_build_toolkit/cli/output.py`
