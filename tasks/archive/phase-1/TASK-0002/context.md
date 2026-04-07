# Context: TASK-0002

## Required Documents

### Canonical
- `docs/canonical/cli_spec.md` — Section 4.1 (command shape), Section 4.6 (error rule), Section 5 (exit code conventions)
- `docs/canonical/architecture.md` — Section 4.1 (CLI layer must not hold business rules), Section 6.1 (`cli/` module boundary)

### Working
- `docs/working/implementation_plan.md` — Phase 1: CLI entrypoint deliverable
- `docs/working/current_focus.md` — confirms this is immediate goal #2

### Runtime
- `docs/runtime/PROJECT_RULES.md` — always

## Prior Work
- TASK-0001 (`done`): `src/ai_build_toolkit/cli/` exists and is importable; `pyproject.toml` exists with `src` layout

## Files Expected to Exist Before Execution
- `src/ai_build_toolkit/cli/__init__.py`
- `pyproject.toml`

## Notes
No manifest, packet, service, or adapter context needed. Scope is limited to entrypoint registration and top-level dispatch wiring only.
