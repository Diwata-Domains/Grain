# Plan: TASK-0069

## Approach

Write `tests/test_runner_integration.py` covering five integration scenarios that prove the runner command chain works correctly in combination. Update `docs/working/current_focus.md` to reflect current phase status.

---

## Step 1 — Write integration tests

Create `tests/test_runner_integration.py` with these scenarios:

**Scenario A — Task activation chain:**
- Repo with one ready backlog task + matching packet dir
- `workflow next` → task_execute, candidate_tasks listed
- `workflow run` → activates task (writes current_task.md)
- `workflow next` again → task_execute with active_task_id now set
- `workflow run` again → gated: execution_in_flight
- Proves: state mutation from `workflow run` is immediately visible to `workflow next`

**Scenario B — Cross-command state agreement (ready task):**
- Same repo state: one ready task, no active task
- `workflow next` → next_action=task_execute
- `task next` → next_task=<ref>
- `phase next` → phase_action=no_phase_action
- `prompt show` → recommended_prompt contains "execute"
- Proves: all commands surface the same underlying state

**Scenario C — Cross-command agreement (planning scenario):**
- Only draft tasks
- `workflow next` → next_action=task_planning
- `task next` → planning_required=true
- `phase next` → phase_action=phase_planning
- Proves: planning state is consistent across commands

**Scenario D — Phase boundary agreement:**
- All backlog tasks done
- `workflow next` → stop_reason=phase_boundary_review_close_required
- `phase next` → phase_action=phase_review_close
- `workflow run` → gated: phase_boundary
- Proves: phase gate is visible to all runner commands

**Scenario E — JSON output invariants:**
- All automation runner commands include: `ok`, `command`, `repo` in JSON root
- `workflow next` JSON includes `evaluation` key
- `task next` JSON includes `task_next` key
- `phase next` JSON includes `phase_next` key
- `workflow run` JSON includes `workflow_run` key
- `prompt show` JSON includes `prompt` key
- Proves: each command's payload key is stable

---

## Step 2 — Update `docs/working/current_focus.md`

Update to reflect:
- Phase 8 in progress; P8-T01 through P8-T08 done
- P8-T09 active: harden outputs and integration tests
- P8-T10 blocked, P8-T11 draft

---

## Verification

- All new integration tests pass
- Full test suite passes with no regressions
- No source code files modified
