# Deliverable Spec: TASK-0097

## Required Output

### New Files
- `tasks/P13-T04-TASK-0097/task.md` — packet metadata and scope
- `tasks/P13-T04-TASK-0097/context.md` — context contract
- `tasks/P13-T04-TASK-0097/plan.md` — implementation plan
- `tasks/P13-T04-TASK-0097/deliverable_spec.md` — deliverable checklist
- `tasks/P13-T04-TASK-0097/results.md` — execute-stage outcomes
- `tasks/P13-T04-TASK-0097/handoff.md` — review handoff
- `prompts/workflow.onboard.existing.md` — existing-project onboarding prompt
- `tests/test_workflow_onboard_existing_prompt.py` — prompt surface tests

### Modified Files
- `docs/working/backlog.md` — move `P13-T04` to review and `P13-T05` to ready
- `docs/working/current_focus.md` — immediate goals update
- `docs/working/current_task.md` — active packet pointer/status

## Acceptance Checklist
- [ ] `prompts/workflow.onboard.existing.md` exists and is scoped to existing-project adoption
- [ ] prompt includes mandatory CLI steps with explicit command examples
- [ ] prompt includes required output contract and unresolved-gap handling
- [ ] prompt preserves draft-first, human-review-gated behavior
- [ ] prompt-surface tests pass
- [ ] full test suite passes with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Phase 13 integration test suite implementation (`P13-T05`)
- Canonical documentation changes
