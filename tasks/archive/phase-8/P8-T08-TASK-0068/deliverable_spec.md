# Deliverable Spec: TASK-0068

## Required Output

### New Files
- `src/forge/services/workflow_run_service.py` — runner logic with gate/activate logic
- `tests/test_workflow_run_cmd.py` — tests for `forge workflow run`
- `tasks/P8-T08-TASK-0068/` — task packet (task.md, context.md, plan.md, deliverable_spec.md, results.md, handoff.md)

### Modified Files
- `src/forge/cli/workflow.py` — add `workflow run` command
- `docs/working/current_task.md` — updated to point to this task
- `docs/working/backlog.md` — P8-T08 status updated to `review`

## Acceptance Checklist
- [ ] `forge workflow run` exists and is reachable via CLI
- [ ] Command activates a ready task when: no active task + exactly one ready candidate
- [ ] Command writes `docs/working/current_task.md` correctly on activation (task_id, task_path, status: in_progress)
- [ ] Command gates and exits 0 for: execution_in_flight, task_blocked, human_review_required, planning_required, phase_boundary, conflicting_next_actions
- [ ] Command exits non-zero on evaluation failure (missing required docs)
- [ ] JSON output includes `workflow_run` payload with `action_taken`, `gate_reason`, `gate_condition`, `task_activated`, `recommended_prompt`, `blocking_reasons`, `affected_artifacts`, `active_phase`, `active_task_id`
- [ ] No state mutation occurs on gate paths
- [ ] All new tests passing (at least 7)
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Auto-execution of task content (agent work is out of scope)
- Modification of packet files beyond `current_task.md`
- `--dry-run` flag (may be added in P8-T09 or later)
- Sentinel verification bridge (P8-T10, blocked)
