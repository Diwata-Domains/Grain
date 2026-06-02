# Context: TASK-0181

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/cli_spec.md` — stable `grain verify` surface and packet-local verification boundary

### Working (load if needed)
- `docs/working/backlog.md` — confirms Phase 28 sequencing and follow-on verification gate work

### Packet Files
- `tasks/P28-T03-TASK-0181/task.md`
- `tasks/P28-T03-TASK-0181/plan.md`
- `tasks/P28-T03-TASK-0181/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** the ingest bridge is a CLI/service slice over packet-local JSON and markdown workflow artifacts.

## Excluded Context
- Assay internals and remote verification execution are excluded; Grain only owns the local bridge contract.

## Context Sufficiency Note
The verify CLI/service code, packet review bundle format, and Phase 28 backlog contract are sufficient to implement and review this ingest slice.
