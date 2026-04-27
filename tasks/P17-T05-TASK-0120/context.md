# Context: TASK-0120

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — advisory outputs must remain deterministic and non-authoritative
- `docs/canonical/product_scope.md` — intelligence-layer outputs remain proposal-only

### Working (load if needed)
- `docs/working/backlog.md` — P17-T05 scope and remaining Phase 17 dependencies
- `docs/working/implementation_plan.md` — ranking-layer goals for impacted-file advice

### Packet Files
- `tasks/P17-T05-TASK-0120/task.md`
- `tasks/P17-T05-TASK-0120/plan.md`
- `tasks/P17-T05-TASK-0120/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Adapter Rationale:** n/a — orchestration impact ranking sits in shared service code

## Excluded Context
- authoritative workflow task selection — deferred behind Q17 / P17-T04
- Phase 17 integration suite — deferred to P17-T06

## Context Sufficiency Note
This context is sufficient because the task is limited to proposal-only ranking metadata for impacted files in the existing orchestration path.
