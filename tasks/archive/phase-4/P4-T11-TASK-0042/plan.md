# Plan: TASK-0042

## Approach

Implement `forge model select` by wiring the existing `select_model_for_stage_or_role` service into the CLI stub in `src/forge/cli/model.py`. Add `--stage` and `--role` options, enforce at least one is provided, and format output in text and JSON modes. Add tests covering the key paths.

---

## Step 1 — Implement `model select` in CLI

In `src/forge/cli/model.py`, replace the empty `model_select` stub with:
- `@click.option("--stage", ...)` and `@click.option("--role", ...)`
- `@click.pass_context`
- `UsageError` if neither is provided
- Call `select_model_for_stage_or_role(root, stage=stage, role=role)`
- Text output: `model select: ok`, `selected_class`, `reason`, and optional `stage`/`role` lines
- JSON output: `{ok, command, repo, selected_class, reason, stage, role}`
- On error: echo errors to stderr, exit non-zero

---

## Step 2 — Add tests

In `tests/test_model_select_cmd.py`:
- `test_model_select_text_stage` — `--stage "task execution"` returns `open_model`
- `test_model_select_text_role` — `--role "review"` returns `reviewer_model`
- `test_model_select_json_output` — JSON shape is correct
- `test_model_select_no_args_exits_nonzero` — UsageError when neither option given
- `test_model_select_missing_profile_exits_nonzero` — error when `agent_profiles.md` absent

---

## Verification

Run `pytest tests/test_model_select_cmd.py` — all tests pass.
Run `pytest` — full suite green, no regressions.
