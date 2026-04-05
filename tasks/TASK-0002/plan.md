# Plan: TASK-0002

## Recommended Model
- **Primary:** `frontier_model`
- **Secondary:** `reviewer_model`
- **Reason:** Entrypoint and dispatch design involves framework selection and structural decisions that affect all downstream command groups. Requires reasoning aligned with `cli_spec.md` and `architecture.md` constraints. `reviewer_model` should verify command shape and exit codes match `cli_spec.md` Section 4.1 and Section 5 before marking complete.

## Steps

1. Select CLI framework — confirm it supports `abt <group> <subcommand>` shape and does not violate architecture constraints (Click or Typer are reasonable choices)
2. Add `main()` entrypoint function in `src/ai_build_toolkit/cli/`
3. Register the entrypoint in `pyproject.toml` under `[project.scripts]`: `abt = "ai_build_toolkit.cli:main"`
4. Implement top-level group dispatch accepting `abt <group> <subcommand>`
5. Add `--help` support at the top level
6. Handle unknown group or missing subcommand: clear error message, exit code `2`
7. Verify `abt --help` runs and exits `0`
8. Add smoke test: entrypoint is callable, `--help` returns exit code `0`, unknown group returns exit code `2`

## Patch Strategy
- New or updated files in `src/ai_build_toolkit/cli/`
- Update `pyproject.toml` to add `[project.scripts]`
- No changes to other modules
