# Context: TASK-0125

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`
- `docs/runtime/adapter_profiles.md`

### Canonical (load for this task)
- `docs/canonical/data_contracts.md` — runtime adapter-profile contract
- `docs/canonical/architecture.md` — inspectable, local-only behavior constraints

### Working (load if needed)
- `docs/working/backlog.md` — Phase 18 migration scope
- `docs/working/open_questions.md` — Q18 metadata-only extraction boundary

### Packet Files
- `tasks/P18-T03-TASK-0125/task.md`
- `tasks/P18-T03-TASK-0125/plan.md`
- `tasks/P18-T03-TASK-0125/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** data_adapter
- **Secondary Adapters:** none
- **Adapter Rationale:** This task changes the runtime ownership and selection behavior for notebook files under the new Phase 18 adapter.

## Excluded Context
- `src/grain/services/data_artifact_extractor.py` — extractor behavior landed in P18-T02 and is not changed here
- `src/grain/services/codebase_scanner.py` — scanner/onboarding updates deferred to P18-T05
- broader context/orchestration ranking behavior — deferred to P18-T04

## Context Sufficiency Note
The runtime adapter profiles, current notebook extractor tests, and the narrow graph-trace compatibility path are sufficient to migrate notebook ownership without touching later Phase 18 integration work.
