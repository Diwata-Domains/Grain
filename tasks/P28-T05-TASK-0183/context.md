# Context: TASK-0183

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/cli_spec.md` — source of truth for the `grain verify` contract

### Working (load if needed)
- `docs/working/backlog.md` — confirms the final docs closeout scope for Phase 28

### Packet Files
- `tasks/P28-T05-TASK-0183/task.md`
- `tasks/P28-T05-TASK-0183/plan.md`
- `tasks/P28-T05-TASK-0183/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** docs_adapter
- **Secondary Adapters:** code_adapter
- **Adapter Rationale:** this slice is documentation-first, but it must stay consistent with the live verify CLI and workflow gate behavior.

## Excluded Context
- Assay implementation details outside the Grain packet-local bridge are excluded.

## Context Sufficiency Note
The README, canonical CLI spec, runtime rules, close prompt, and release-surface tests are sufficient to document the live Assay verification loop accurately.
