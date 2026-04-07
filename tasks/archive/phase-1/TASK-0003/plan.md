# Plan: TASK-0003

## Recommended Model
- **Primary:** `frontier_model`
- **Secondary:** `reviewer_model`
- **Reason:** Scaffolding command groups requires structural decisions about module layout and framework wiring that affect all downstream command implementations. `reviewer_model` must verify all group and subcommand names against `cli_spec.md` Section 6 before marking complete — no extra commands, no missing commands.

## Steps

1. Create one module per group in `src/ai_build_toolkit/cli/`:
   - `init.py`
   - `docs.py`
   - `task.py`
   - `context.py`
   - `model.py`
   - `review.py`
2. In each module define the group and register all subcommands from `cli_spec.md` Section 6 as stubs:
   - `init`: `abt init`
   - `docs`: `abt docs validate`, `abt docs index`, `abt docs show`
   - `task`: `abt task create`, `abt task list`, `abt task show`, `abt task status`, `abt task validate`, `abt task close`
   - `context`: `abt context build`, `abt context show`, `abt context export`
   - `model`: `abt model show`, `abt model select`, `abt model escalate`
   - `review`: `abt review check`, `abt review handoff`, `abt review summary`
3. Register all six groups with the top-level dispatcher from TASK-0002
4. Verify `abt <group> --help` works for all six groups
5. Add or extend smoke tests: all six groups load, `--help` works per group

## Patch Strategy
- New files: one per group in `src/ai_build_toolkit/cli/`
- Update top-level dispatcher to import and register all six groups
- No changes to `services/`, `domain/`, `adapters/`, or `validators/`
