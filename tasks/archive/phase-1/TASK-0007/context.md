# Context: TASK-0007

## Required Documents

### Canonical
- `docs/canonical/cli_spec.md` — Section 4.3 (output rules: `--format text|json`), Section 9 (human-readable output expectations), Section 10 (structured output fields: ok, command, errors, warnings, etc.)
- `docs/canonical/architecture.md` — Section 4.1 (CLI layer responsibility: format output), Section 6.1 (`cli/` module boundary)

### Working
- `docs/working/implementation_plan.md` — Phase 1: CLI output formatting base
- `docs/working/open_questions.md` — Q6 (JSON output surface) is still open; default to text-first

### Runtime
- `docs/runtime/PROJECT_RULES.md` — always

## Prior Work
- TASK-0002 (`done`): `main()` Click group with `--repo` option exists
- TASK-0005 (`done`): `abt init` uses `click.echo` directly — this task updates it to use the formatter

## Files Expected to Exist Before Execution
- `src/ai_build_toolkit/cli/__init__.py`
- `src/ai_build_toolkit/cli/init.py`

## Notes
Q6 is open. Keep JSON as a prepared interface (a method that serialises to JSON) but do not require all commands to implement JSON output at this stage.
