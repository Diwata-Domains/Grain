# Context: TASK-0139

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md` — workflow and repo-operation constraints

### Canonical (load for this task)
- `docs/canonical/cli_spec.md` — expected `grain upgrade` operator-facing behavior
- `docs/canonical/workflow_spec.md` — workflow boundaries for non-destructive tooling behavior

### Working (load if needed)
- `docs/working/backlog.md` — Phase 20 contract for P20-T05
- `docs/working/tooling_notes.md` — local source of the customization-safety hardening slice

### Packet Files
- `tasks/P20-T05-TASK-0139/task.md`
- `tasks/P20-T05-TASK-0139/plan.md`
- `tasks/P20-T05-TASK-0139/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Adapter Rationale:** n/a

## Excluded Context
- Assay-specific ingestion work from other tooling notes
- Phase 20 packet-first prompt hardening for P20-T06
- Any TUI or release-status changes outside upgrade safety

## Context Sufficiency Note
The upgrade service, upgrade CLI, Phase 20 backlog contract, and focused tests are sufficient to harden customization handling without touching unrelated workflow-state logic.
