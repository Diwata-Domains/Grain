# Deliverable Spec: TASK-0135

## Required Output

### New Files
- `tests/test_workflow_state_service.py` additions — coverage for review routing once execution artifacts exist
- `tests/test_workflow_run_cmd.py` additions — coverage for review gating in the runner
- `tests/test_prompt_show_cmd.py` additions — coverage for review-prompt selection
- `tests/test_runner_integration.py` additions — cross-command regression coverage

### Modified Files
- `src/grain/services/workflow_service.py` — return `task_review` once an active task has `results.md`
- `src/grain/services/workflow_run_service.py` — gate `task_review` with reviewer/human intervention

## Acceptance Checklist
- [x] Active in-progress tasks with `results.md` route to `task_review`
- [x] `task_review` recommends `prompts/task.review.md`
- [x] `workflow run` surfaces a review gate instead of execution-in-flight once execution artifacts exist
- [x] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Changing close-stage semantics for packets already in `review`
- Assay ingestion or other post-v0.2.0 feature work
