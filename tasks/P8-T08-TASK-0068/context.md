# Context: TASK-0068

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/cli_spec.md` — command shape, output rules, exit codes
- `docs/canonical/workflow_spec.md` — lifecycle states, allowed transitions

### Working (load if needed)
- `docs/working/open_questions.md` — Q16 stop-condition resolution
- `docs/working/current_focus.md` — phase 8 active constraints

### Packet Files
- `tasks/P8-T08-TASK-0068/task.md`
- `tasks/P8-T08-TASK-0068/plan.md`
- `tasks/P8-T08-TASK-0068/deliverable_spec.md`

## Excluded Context
- Phase 1–7 task archives — not needed for this implementation
- `docs/working/v2_adapters.md`, `docs/working/v2_onboarding.md` — future phase planning, not relevant

## Context Sufficiency Note
The selected docs, existing workflow CLI patterns (workflow.py, phase.py, task.py), and the workflow_service.py implementation are sufficient to implement and review this task.
