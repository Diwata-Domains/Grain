# Context: TASK-0123

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/adapter_profiles.md`

### Canonical (load for this task)
- `docs/canonical/data_contracts.md` — adapter profile runtime contract and official/custom adapter boundaries
- `docs/canonical/architecture.md` — advisory outputs must stay proposal-only; adapter behavior must remain file-backed and inspectable

### Working (load if needed)
- `docs/working/backlog.md` — Phase 18 task scope and sequencing
- `docs/working/current_focus.md` — active-phase status and immediate goals
- `docs/working/open_questions.md` — Q18 resolution for metadata-only extraction boundaries

### Packet Files
- `tasks/P18-T01-TASK-0123/task.md`
- `tasks/P18-T01-TASK-0123/plan.md`
- `tasks/P18-T01-TASK-0123/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** docs_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** This slice is primarily a runtime-doc and contract-definition task. `docs_adapter` is the right execution lens because the task changes adapter documentation and packet planning, not code-path behavior yet.

## Excluded Context
- `src/grain/services/context_service.py` — integration changes are deferred to P18-T04
- `src/grain/services/notebook_extractor.py` — notebook behavior remains unchanged in this task
- `src/grain/services/codebase_scanner.py` — onboarding/scanner recommendations are deferred to P18-T05

## Context Sufficiency Note
The runtime adapter profile contract, Phase 18 backlog scope, and Q18 resolution are sufficient to document the new adapter without widening into later implementation slices.
