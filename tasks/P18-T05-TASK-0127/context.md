# Context: TASK-0127

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/adapter_profiles.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — official adapter and onboarding behavior must remain file-backed and inspectable

### Working (load if needed)
- `docs/working/backlog.md` — Phase 18 onboarding/scanner scope

### Packet Files
- `tasks/P18-T05-TASK-0127/task.md`
- `tasks/P18-T05-TASK-0127/plan.md`
- `tasks/P18-T05-TASK-0127/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** data_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** This task updates onboarding and scanner behavior for the now-official Phase 18 adapter.

## Excluded Context
- adapter registry/install flows — deferred to Phase 19
- full Phase 18 integration suite — deferred to P18-T06

## Context Sufficiency Note
The scanner logic, onboarding doc generator, and existing data-adapter contract are sufficient to promote `data_adapter` into the official onboarding path without widening scope.
