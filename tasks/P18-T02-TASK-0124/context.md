# Context: TASK-0124

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/adapter_profiles.md`

### Canonical (load for this task)
- `docs/canonical/data_contracts.md` — adapter/runtime contract boundaries
- `docs/canonical/architecture.md` — local-first, inspectable artifact handling expectations

### Working (load if needed)
- `docs/working/backlog.md` — Phase 18 extractor scope and dependencies
- `docs/working/open_questions.md` — Q18 metadata-only extraction decision

### Packet Files
- `tasks/P18-T02-TASK-0124/task.md`
- `tasks/P18-T02-TASK-0124/plan.md`
- `tasks/P18-T02-TASK-0124/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** data_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** This task implements the first executable surface behind the newly defined `data_adapter` contract.

## Excluded Context
- `src/grain/services/context_service.py` — integration deferred to P18-T04
- `src/grain/services/codebase_scanner.py` — scanner/onboarding changes deferred to P18-T05
- notebook ownership migration logic — deferred to P18-T03

## Context Sufficiency Note
The Phase 18 adapter contract, metadata-only boundary decision, and existing extractor patterns are sufficient to build a standalone metadata extractor without pulling in later integration work.
