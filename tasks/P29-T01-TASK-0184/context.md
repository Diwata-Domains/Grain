# Context: TASK-0184

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/cli_spec.md` — current verify/close loop contract

### Working (load if needed)
- `docs/working/backlog.md` — confirms Phase 29 scope and why this hardening slice comes first

### Packet Files
- `tasks/P29-T01-TASK-0184/task.md`
- `tasks/P29-T01-TASK-0184/plan.md`
- `tasks/P29-T01-TASK-0184/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** docs_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** this slice hardens runtime and prompt guidance rather than changing execution logic.

## Excluded Context
- New workflow blockers, reconcile changes, or diagnostics are excluded; those belong to later Phase 29 tasks.

## Context Sufficiency Note
The runtime guidance, shipped prompt assets, and release-surface tests are sufficient to harden the Grain/Assay loop discipline in the places agents actually read.
