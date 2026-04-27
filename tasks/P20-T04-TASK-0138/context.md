# Context: TASK-0138

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md` — workflow and repo-operation constraints

### Canonical (load for this task)
- `docs/canonical/workflow_spec.md` — state-machine expectations for workflow completion
- `docs/canonical/data_contracts.md` — command-output stability expectations

### Working (load if needed)
- `docs/working/backlog.md` — Phase 20 contract for P20-T04
- `docs/working/current_focus.md` — real repo example showing completion markers
- `docs/working/tooling_notes.md` — source signal for the missing terminal state

### Packet Files
- `tasks/P20-T04-TASK-0138/task.md`
- `tasks/P20-T04-TASK-0138/plan.md`
- `tasks/P20-T04-TASK-0138/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** [adapter_id or none]
- **Secondary Adapters:** [adapter_ids or none]
- **Adapter Rationale:** n/a

## Excluded Context
- Upgrade/customization work for P20-T05
- Tooling-notes schema work for P20-T07

## Context Sufficiency Note
The workflow evaluator, phase-next surface, and focused tests are sufficient to implement and verify terminal-state handling without touching unrelated task lifecycle code.
