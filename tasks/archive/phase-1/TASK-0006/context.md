# Context: TASK-0006

## Required Documents

### Canonical
- `docs/canonical/architecture.md` — Section 4.9 (Template and Scaffolding System), Section 6.6 (`templates/` module boundary)
- `docs/canonical/data_contracts.md` — Section 14 (Template Contract: templates are source artifacts, not live state; validators distinguish template presence from generated artifacts)

### Working
- `docs/working/implementation_plan.md` — Phase 1: template directory structure deliverable

### Runtime
- `docs/runtime/PROJECT_RULES.md` — always

## Prior Work
- TASK-0001 (`done`): `src/ai_build_toolkit/templates/__init__.py` exists
- TASK-0005 (`done`): `abt init` creates `templates/docs/`, `templates/tasks/`, `templates/prompts/` directories in a repo

## Files Expected to Exist Before Execution
- `src/ai_build_toolkit/templates/__init__.py`
- `templates/` directory (at repo root — created by `abt init` or already present)

## Notes
Plain markdown is the correct v1 template format — no Jinja2 or rendering engine needed at this stage. The loader only needs to resolve and return template file content by name.
