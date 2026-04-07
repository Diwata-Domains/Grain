# Context: TASK-0004

## Required Documents

### Canonical
- `docs/canonical/cli_spec.md` — Section 4.2 (path resolution rules: auto-detect root, support `--repo`, support relative paths)
- `docs/canonical/architecture.md` — Section 4.1 (CLI layer must not hold business logic), Section 6.4 (`adapters/` is home for filesystem adapter)

### Working
- `docs/working/implementation_plan.md` — Phase 1: repository root resolution
- `docs/working/current_focus.md` — confirms Phase 1 scope

### Runtime
- `docs/runtime/PROJECT_RULES.md` — always

## Prior Work
- TASK-0001 (`done`): `src/ai_build_toolkit/adapters/` exists and is importable
- TASK-0002 (`done`): `main()` Click group registered; `--repo` option can be wired at top level

## Files Expected to Exist Before Execution
- `src/ai_build_toolkit/adapters/__init__.py`
- `src/ai_build_toolkit/cli/__init__.py` with `main()` Click group

## Notes
No manifest, packet, service, or domain logic needed. This task is purely a filesystem resolution utility in `adapters/`.
