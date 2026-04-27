# Task: Scaffold command groups

## Metadata
- **ID:** TASK-0003
- **Status:** done
- **Phase:** Phase 1 — Repository Foundation and Core CLI
- **Dependencies:** TASK-0002 (CLI entrypoint and top-level dispatch must exist)

## Objective
Register all six command groups (`init`, `docs`, `task`, `context`, `model`, `review`) with the top-level dispatcher. Each group must be reachable via `abt <group> --help`. Subcommands within each group must be named and listed in help output but may be stubs — no implementation logic at this stage.

## Why This Task Exists
`implementation_plan.md` Phase 1 lists "command group scaffolding" as a major deliverable. `current_focus.md` lists scaffolding the primary command groups as immediate goal #3. Without the group and subcommand structure in place, no subsequent command implementation has a stable home.

## Scope
- Register all six command groups with the entrypoint dispatcher
- Define all subcommands per group as named stubs
- Each group must respond to `--help`
- One module per group under `src/ai_build_toolkit/cli/`

## Constraints
- Group names and subcommand names must exactly match `cli_spec.md` Section 6
- Must not hold business logic in any group or stub (`architecture.md` Section 4.1)
- Must not implement any command behavior beyond stub responses
- Each group must live in its own module under `src/ai_build_toolkit/cli/`
- Global options (`--repo`, `--format`, `--dry-run`, `--quiet`, `--verbose`) may be noted but need not be wired

## Escalation Conditions
- CLI framework from TASK-0002 makes the group/subcommand structure incompatible with `cli_spec.md` naming
- A command group name conflicts with a reserved keyword in the chosen framework
