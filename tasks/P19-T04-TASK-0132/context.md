# Context: TASK-0132

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — community adapter trust boundaries and declarative adapter expectations
- `docs/canonical/data_contracts.md` — adapter contract fields and community/local/official distinctions

### Working (load if needed)
- `docs/working/backlog.md` — Phase 19 scope for the scaffold task
- `docs/working/open_questions.md` — Q19 reviewed-registry contract
- `tasks/P19-T02-TASK-0130/results.md` — package shape established by the validator
- `tasks/P19-T03-TASK-0131/results.md` — install behavior the scaffold should align with

### Packet Files
- `tasks/P19-T04-TASK-0132/task.md`
- `tasks/P19-T04-TASK-0132/plan.md`
- `tasks/P19-T04-TASK-0132/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** docs_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** This task is a documentation and scaffold-contract slice for a reviewed community registry repo.

## Excluded Context
- CI automation and GitHub workflow files — deferred to `P19-T05`
- end-to-end install validation — deferred to `P19-T06`

## Context Sufficiency Note
These docs are sufficient because the scaffold only needs to reflect the already-decided Phase 19 package and install contracts.
