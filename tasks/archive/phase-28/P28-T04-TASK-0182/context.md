# Context: TASK-0182

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/cli_spec.md` — defines the verification gate intent in the review/close loop

### Working (load if needed)
- `docs/working/backlog.md` — confirms Phase 28 sequencing from status/ingest into workflow gating

### Packet Files
- `tasks/P28-T04-TASK-0182/task.md`
- `tasks/P28-T04-TASK-0182/plan.md`
- `tasks/P28-T04-TASK-0182/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** this slice changes workflow/readiness validation and CLI output behavior around packet-local verification state.

## Excluded Context
- Assay transport, remote polling, and any multi-provider scheduling logic remain out of scope.

## Context Sufficiency Note
The closure validator, workflow evaluator, task close CLI, and existing verification tests are sufficient to wire verification gates into the close path cleanly.
