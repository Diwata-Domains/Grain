# Task: Add initial CLI smoke tests

## Metadata
- **ID:** TASK-0009
- **Status:** done
- **Phase:** Phase 1 — Repository Foundation and Core CLI
- **Dependencies:** TASK-0002, TASK-0003, TASK-0008 (full CLI stack must be in place)

## Objective
Create a consolidated smoke test suite that verifies the CLI can be invoked as an installed command, all command groups load correctly, help output is present, and the error handling conventions hold. This is the Phase 1 gate check — if these tests pass, the CLI foundation is shippable to Phase 2.

## Why This Task Exists
`implementation_plan.md` Phase 1 lists "initial test harness for CLI smoke checks" as a major deliverable. The individual tasks already produced unit tests scoped to their own modules. This task adds a top-level integration smoke test that exercises the installed `abt` entrypoint as a subprocess and confirms the whole stack hangs together, not just individual units.

## Scope
- Invoke `abt` as a real subprocess (not just via CliRunner) to verify the installed entrypoint works
- Confirm `abt --help` exits 0 and lists all six command groups
- Confirm each group's `--help` exits 0
- Confirm `abt <unknown>` exits 2
- Add `--version` flag to the CLI and verify it outputs the version string

## Constraints
- Subprocess tests must work against the installed `.venv` entrypoint
- `--version` string must be derived from `pyproject.toml` — do not hardcode it separately
- Must not duplicate unit-level tests already in place; focus on integration and entrypoint verification
- Must not require network access or external services

## Escalation Conditions
- Subprocess invocation environment differs from test environment in a way that breaks discovery
