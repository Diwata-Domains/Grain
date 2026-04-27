# Context: TASK-0003

## Required Documents

### Canonical
- `docs/canonical/cli_spec.md` — Section 6 (all command groups and subcommand names), Section 4.1 (command shape), Section 4.3–4.5 (output/dry-run/verbosity options for future reference)
- `docs/canonical/architecture.md` — Section 4.1 (CLI layer must not hold business rules), Section 6.1 (`cli/` module boundary)

### Working
- `docs/working/implementation_plan.md` — Phase 1: command group scaffolding deliverable
- `docs/working/current_focus.md` — confirms this is immediate goal #3

### Runtime
- `docs/runtime/PROJECT_RULES.md` — always

## Prior Work
- TASK-0001 (`done`): `src/ai_build_toolkit/cli/` exists and is importable
- TASK-0002 (`draft`): entrypoint `main()` and top-level dispatch registered in `pyproject.toml`

## Files Expected to Exist Before Execution
- `src/ai_build_toolkit/cli/__init__.py`
- Top-level dispatcher wired in `src/ai_build_toolkit/cli/`
- `pyproject.toml` with `abt` entrypoint registered

## Notes
`cli_spec.md` Section 6 is the sole authority for command and subcommand names. No manifest, packet, service, or adapter context is needed.
