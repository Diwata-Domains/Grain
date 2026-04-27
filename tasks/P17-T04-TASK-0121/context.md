# Context: TASK-0121

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — advisory outputs must stay deterministic and proposal-only
- `docs/canonical/product_scope.md` — intelligence-layer outputs cannot silently mutate workflow authority

### Working (load if needed)
- `docs/working/backlog.md` — Q17-resolved task scope for P17-T04
- `docs/working/open_questions.md` — advisory-only resolution for ranked next-task signals
- `docs/working/implementation_plan.md` — Phase 17 ranking-layer objective

### Packet Files
- `tasks/P17-T04-TASK-0121/task.md`
- `tasks/P17-T04-TASK-0121/plan.md`
- `tasks/P17-T04-TASK-0121/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Adapter Rationale:** n/a — task advice lives in shared orchestration/service code

## Excluded Context
- authoritative workflow state evaluation — unchanged by this task
- Phase 17 integration suite — deferred to P17-T06

## Context Sufficiency Note
This context is sufficient because the task is limited to adding advisory ranked task suggestions on a proposal-only surface.
