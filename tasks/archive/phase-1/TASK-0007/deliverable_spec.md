# Deliverable Spec: TASK-0007

## Definition of Done

This task is complete when all of the following are true:

1. `src/ai_build_toolkit/cli/output.py` exists with `CommandResult` and `print_result()`
2. `CommandResult` fields match `cli_spec.md` Section 10: `ok`, `command`, `files_created`, `files_updated`, `files_skipped`, `files_blocked`, `errors`, `warnings`
3. `print_result()` supports `fmt="text"` (default) and `fmt="json"`
4. `abt init` uses `CommandResult` and `print_result()` instead of direct `click.echo` calls
5. `abt init --format json` produces valid JSON output
6. Formatter lives in `cli/output.py`, not in services or domain
7. Tests cover text output, JSON output, and empty result — all passing

## Out of Scope
- Applying the formatter to commands other than `init` (that follows in later tasks)
- Full `--format` wiring on all command groups (P1-T08 covers global error conventions)
- Any service or domain changes
