# Context: TASK-0186

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/cli_spec.md` — existing workflow-run and packet-lifecycle contract

### Working (load if needed)
- `docs/working/backlog.md` — confirms the Phase 29 runner hardening scope

### Packet Files
- `tasks/P29-T03-TASK-0186/task.md`
- `tasks/P29-T03-TASK-0186/plan.md`
- `tasks/P29-T03-TASK-0186/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** this slice changes the workflow-run bootstrap/service path and its regression tests.

## Excluded Context
- Broader operator diagnostics and later smoke coverage are excluded; they belong to `P29-T04` and `P29-T05`.

## Context Sufficiency Note
The workflow-run service, packet creation service, templates, and focused runner tests are sufficient to fix the activation drift path without broad workflow changes.
