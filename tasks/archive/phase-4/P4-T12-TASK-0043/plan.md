# Plan: TASK-0043

## Approach

Add `get_escalation_target` to the routing domain, add `escalate_model_for_class` to the service layer, implement the CLI command body, fix the inline import in `model_select`, and add tests.

---

## Step 1 — Add `get_escalation_target` to `routing.py`

Add a function that:
1. Searches `config.escalation_rules` for a rule where `source_class == current_class`.
2. Falls back to rules where `source_class == "*"`.
3. Returns the first matching `target_class`, or `None` if no rule applies.

Keeps the function pure (no side effects, no hardcoded class names).

---

## Step 2 — Add `escalate_model_for_class` to `model_service.py`

Add a service function that:
1. Loads `ModelRoutingConfig` via `load_model_profiles`.
2. Calls `get_escalation_target(config, current_class, reason)`.
3. Returns `(CommandResult, target_class | None)`.
4. Returns a `CommandResult(ok=False)` with an error message if no path is defined.

---

## Step 3 — Implement `model escalate` in `cli/model.py`

Replace the empty stub with:
- `--from-class TEXT` (required): model class to escalate from
- `--reason TEXT` (optional): reason for escalation (advisory, forwarded to service)
- `@click.pass_context`
- Call `escalate_model_for_class(root, current_class, reason)`
- Text output: `model escalate: ok`, `from_class`, `target_class`, optional `reason`
- JSON output: `{ok, command, repo, from_class, target_class, reason}`
- Error: stderr + non-zero exit when no escalation path found

Also move the inline `select_model_for_stage_or_role` import to module level.

---

## Step 4 — Add tests

In `tests/test_model_escalate_cmd.py`:
- `test_model_escalate_open_to_frontier` — `--from-class open_model` returns `frontier_model`
- `test_model_escalate_wildcard_to_reviewer` — `--from-class frontier_model` returns `reviewer_model`
- `test_model_escalate_json_output` — JSON shape is correct
- `test_model_escalate_unknown_class_exits_nonzero` — unknown class → error + non-zero
- `test_model_escalate_missing_profile_exits_nonzero` — missing `agent_profiles.md` → non-zero

---

## Verification

Run `pytest tests/test_model_escalate_cmd.py` — all pass.
Run `pytest` — full suite green, no regressions.
