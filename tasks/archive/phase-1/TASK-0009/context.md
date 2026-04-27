# Context: TASK-0009

## Required Documents

### Canonical
- `docs/canonical/cli_spec.md` — Section 4.1 (command shape), Section 5 (exit codes), Section 6 (command groups and subcommands), Section 12 (v1 command coverage summary)
- `docs/canonical/architecture.md` — Section 4.1 (CLI layer responsibilities)

### Working
- `docs/working/implementation_plan.md` — Phase 1: initial test harness for CLI smoke checks
- `docs/working/current_focus.md` — last remaining Phase 1 task

### Runtime
- `docs/runtime/PROJECT_RULES.md` — always

## Prior Work
- TASK-0002 (`done`): `abt` entrypoint registered, `cli()` wrapper in place
- TASK-0003 (`done`): all 6 groups and 18 subcommands scaffolded
- TASK-0007 (`done`): `--format` global option
- TASK-0008 (`done`): `cli()` wrapper, error handling, exit codes

## Existing Test Coverage (do not duplicate)
- `tests/test_cli_entrypoint.py` — `--help` exits 0, unknown group exits 2 (via CliRunner)
- `tests/test_command_groups.py` — all groups and subcommands via CliRunner
- `tests/test_error_handler.py` — exit code mapping

## Notes
This task adds subprocess-level integration tests and `--version` support. Unit coverage is already in place.
