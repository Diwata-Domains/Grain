# Deliverable Spec: TASK-0055

## Required Output

### New Files
- `src/forge/domain/adapters.py` — adapter domain dataclass definitions
- `tests/test_adapter_domain.py` — focused tests for adapter domain model behavior

### Modified Files
- `docs/working/current_task.md` — active task pointer/status
- `docs/working/backlog.md` — P6-T02 status update
- `tasks/P6-T02-TASK-0055/task.md` — packet metadata and scope
- `tasks/P6-T02-TASK-0055/context.md` — task context selection
- `tasks/P6-T02-TASK-0055/plan.md` — implementation plan
- `tasks/P6-T02-TASK-0055/results.md` — implementation/results record
- `tasks/P6-T02-TASK-0055/handoff.md` — reviewer handoff bundle

## Acceptance Checklist
- [x] `AdapterProfile` exists in `src/forge/domain/adapters.py`
- [x] Required fields match the runtime contract (`adapter_id`, `domain_type`, `applies_to`)
- [x] Optional hint sections exist as list fields with safe defaults
- [x] Focused domain tests pass
- [x] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Adapter profile markdown parser/loader (`P6-T03`)
- Packet metadata parser changes (`P6-T04`)
- Context assembly behavior changes (`P6-T05` and `P6-T06`)
