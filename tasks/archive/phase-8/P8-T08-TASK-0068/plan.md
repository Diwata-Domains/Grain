# Plan: TASK-0068

## Approach

Add `forge workflow run` as a thin CLI command backed by a new `workflow_run_service.py`. The service calls the existing read-only `evaluate_workflow_state`, then either takes one mechanical step (activating a ready task into `current_task.md`) or stops with an explicit gate reason. The command follows the established output pattern from `workflow.py`, `phase.py`, and `task.py`.

---

## Step 1 — Implement `workflow_run_service.py`

Create `src/forge/services/workflow_run_service.py` with `run_workflow_step(root)` that:

1. Calls `evaluate_workflow_state(root)` from `workflow_service.py`
2. Maps `evaluation.ok + evaluation.next_action + evaluation.stop_reason` to either:
   - **Gate**: returns a payload with `action_taken: "none"`, `gate_reason`, `gate_condition`
   - **Activate**: finds the candidate task's packet dir, reads task ID, writes `current_task.md` to `in_progress`, returns payload with `action_taken: "activate_task"`, `task_activated`
3. Gate conditions:
   - `evaluation is None` → evaluation failure (returns None payload)
   - `stop_reason` is set (any) → gate with appropriate `gate_reason`
   - `next_action == "task_execute"` with `active_task_id != ""` → gate `"execution_in_flight"`
   - `next_action == "task_close"` → gate `"human_review_required"`
   - `next_action == "task_planning"` → gate `"planning_required"`
4. Activate condition:
   - `next_action == "task_execute"`, no active task, exactly one candidate → activate task
5. Helper: `_find_packet_dir_for_ref(root, task_ref)` — searches `tasks/` for dir starting with `task_ref + "-"`
6. Helper: `_read_task_id_from_packet(packet_dir)` — reads TASK-#### from `task.md` metadata block
7. Helper: `_write_current_task(root, task_id, task_path, status)` — writes `docs/working/current_task.md`

---

## Step 2 — Add `workflow run` command to `workflow.py`

Add `@workflow_group.command("run")` to `src/forge/cli/workflow.py`:
- Calls `run_workflow_step(root)`
- Text output: `"workflow run: ok"` (action taken) or `"workflow run: gated"` (stopped)
- JSON output: `CommandResult` + `"workflow_run"` payload dict
- Exit 0 for both ok and gated (gates are expected states, not errors)
- Exit via `click.ClickException` if evaluation itself failed

---

## Step 3 — Write tests in `tests/test_workflow_run_cmd.py`

Tests:
1. `test_workflow_run_activates_ready_task` — one ready task, no active → activates, ok, writes current_task.md
2. `test_workflow_run_gates_on_in_progress_task` — active task in_progress → gated: execution_in_flight
3. `test_workflow_run_gates_on_blocked_task` — active task blocked → gated: task_blocked
4. `test_workflow_run_gates_on_task_in_review` — task in review with artifacts → gated: human_review_required
5. `test_workflow_run_gates_on_planning_required` — only draft tasks → gated: planning_required
6. `test_workflow_run_gates_on_phase_boundary` — no open tasks → gated: phase_boundary
7. `test_workflow_run_json_output_includes_payload` — JSON output shape validation

---

## Verification

- All 7+ new tests pass
- Full suite passes with no regressions
- Text output reads clearly: "workflow run: ok" / "workflow run: gated"
- JSON output includes `workflow_run` payload with `action_taken`, `gate_reason`, `gate_condition`
- `current_task.md` is correctly written when a task is activated
- Gate paths do not mutate any files
