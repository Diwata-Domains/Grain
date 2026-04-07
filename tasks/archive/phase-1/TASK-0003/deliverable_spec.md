# Deliverable Spec: TASK-0003

## Definition of Done

This task is complete when all of the following are true:

1. All six command groups are registered and reachable: `init`, `docs`, `task`, `context`, `model`, `review`
2. `abt <group> --help` succeeds for all six groups
3. All subcommands from `cli_spec.md` Section 6 appear in each group's help output
4. Subcommand names exactly match `cli_spec.md` Section 6 — no extras, no omissions
5. Each group lives in its own module under `src/ai_build_toolkit/cli/`
6. No business logic in any group or subcommand stub
7. Smoke tests pass for all six groups

## Subcommand Reference (`cli_spec.md` Section 6)

| Group | Subcommands |
|---|---|
| `init` | *(top-level command, no subcommands)* |
| `docs` | `validate`, `index`, `show` |
| `task` | `create`, `list`, `show`, `status`, `validate`, `close` |
| `context` | `build`, `show`, `export` |
| `model` | `show`, `select`, `escalate` |
| `review` | `check`, `handoff`, `summary` |

## Out of Scope
- Any command implementation beyond stub responses
- Output formatting and `--format` flag wiring (P1-T07)
- Shared error types and exit code mapping (P1-T08)
- Global option wiring beyond `--help`
- Any service, domain, adapter, or validator logic
