# Context: TASK-0126

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/adapter_profiles.md`

### Canonical (load for this task)
- `docs/canonical/architecture.md` — proposal-only orchestration boundary
- `docs/canonical/data_contracts.md` — runtime adapter and file-backed artifact expectations

### Working (load if needed)
- `docs/working/backlog.md` — Phase 18 scope and sequencing

### Packet Files
- `tasks/P18-T04-TASK-0126/task.md`
- `tasks/P18-T04-TASK-0126/plan.md`
- `tasks/P18-T04-TASK-0126/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** data_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** This slice wires the new Phase 18 adapter into existing context-export and orchestration surfaces.

## Excluded Context
- `src/grain/services/codebase_scanner.py` — scanner/onboarding work deferred to P18-T05
- phase-level integration suite — deferred to P18-T06

## Context Sufficiency Note
The new extractor, the migrated notebook ownership rules, and the existing export/orchestration surfaces are sufficient to complete this integration slice without widening into scanner or full phase-integration work.
