# Context: TASK-0131

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — adapter categories and the inspectable declarative adapter layer
- `docs/canonical/data_contracts.md` — official/community/local adapter contract plus no-shadowing rule
- `docs/canonical/cli_spec.md` — existing adapter command surface and CLI output conventions

### Working (load if needed)
- `docs/working/backlog.md` — Phase 19 task boundaries and dependencies
- `docs/working/open_questions.md` — resolved Q19 trust contract for explicit install sources

### Packet Files
- `tasks/P19-T03-TASK-0131/task.md`
- `tasks/P19-T03-TASK-0131/plan.md`
- `tasks/P19-T03-TASK-0131/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** docs_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** This task changes the declarative adapter install surface and the repo-visible adapter profile file rather than domain runtime behavior.

## Excluded Context
- remote registry networking/auth flows — out of scope for this local-only install slice
- registry submission scaffold details from `P19-T04` — not required to resolve a package directory or a local reviewed-registry checkout

## Context Sufficiency Note
These docs are sufficient because Phase 19 install semantics are constrained to explicit local sources and the install target is the existing adapter profile file.
