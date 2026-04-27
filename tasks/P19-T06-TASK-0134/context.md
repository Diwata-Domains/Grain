# Context: TASK-0134

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — community adapter trust boundaries
- `docs/canonical/data_contracts.md` — community adapter packaging/install expectations

### Working (load if needed)
- `docs/working/backlog.md` — Phase 19 final integration scope
- `tasks/P19-T02-TASK-0130/results.md` — package validator contract
- `tasks/P19-T03-TASK-0131/results.md` — install contract
- `tasks/P19-T04-TASK-0132/results.md` — scaffold contract
- `tasks/P19-T05-TASK-0133/results.md` — CI/doc contract

### Packet Files
- `tasks/P19-T06-TASK-0134/task.md`
- `tasks/P19-T06-TASK-0134/plan.md`
- `tasks/P19-T06-TASK-0134/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** docs_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** This task integrates the reviewed community registry contract as repo-visible docs, workflow config, and declarative adapter data.

## Excluded Context
- phase-close metrics and seal behavior — phase close comes after this test slice lands
- remote registry fetch behavior — not part of the implemented Phase 19 contract

## Context Sufficiency Note
These docs are sufficient because the phase’s implemented contract is already present and only needs integrated verification now.
