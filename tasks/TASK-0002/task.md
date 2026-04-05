# Task: Implement CLI entrypoint

## Metadata
- **ID:** TASK-0002
- **Status:** done
- **Phase:** Phase 1 — Repository Foundation and Core CLI
- **Dependencies:** TASK-0001 (source structure must exist and be importable)

## Objective
Add the main executable entrypoint and top-level command dispatch for the CLI. The result should be a runnable `abt` command that accepts a group and subcommand, routes to the appropriate handler, and returns a valid exit code.

## Why This Task Exists
`implementation_plan.md` Phase 1 lists "CLI entrypoint" as the second major deliverable. `current_focus.md` lists implementing the CLI entrypoint as immediate goal #2. Without this, no command group or service logic can be reached from the terminal.

## Scope
- Add entrypoint registration in `pyproject.toml` pointing to the CLI module
- Add top-level dispatch logic in `src/ai_build_toolkit/cli/`
- Handle unknown commands and missing subcommands with clear output and correct exit code
- No business logic, no service calls, no packet or manifest logic

## Constraints
- Must follow command shape defined in `cli_spec.md` Section 4.1: `abt <group> <command> [arguments] [options]`
- Must support `--help` at top level
- Must return exit codes aligned with `cli_spec.md` Section 5: `0` success, `2` invalid arguments
- Must not embed provider-specific logic
- Must not hold business rules in the CLI layer (`architecture.md` Section 4.1)
- CLI layer must remain thin — dispatch only

## Escalation Conditions
- CLI framework choice introduces architecture constraints not covered by canonical docs
- Entrypoint conventions conflict with package structure from TASK-0001
