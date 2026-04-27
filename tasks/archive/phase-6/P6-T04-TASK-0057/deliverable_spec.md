# Deliverable Spec: TASK-0057

## Required Output

### New Files
- `tasks/P6-T04-TASK-0057/task.md` — packet definition
- `tasks/P6-T04-TASK-0057/context.md` — packet context
- `tasks/P6-T04-TASK-0057/plan.md` — packet plan
- `tasks/P6-T04-TASK-0057/deliverable_spec.md` — packet acceptance criteria
- `tasks/P6-T04-TASK-0057/results.md` — execution results
- `tasks/P6-T04-TASK-0057/handoff.md` — reviewer handoff

### Modified Files
- `templates/tasks/task.md` — adds optional adapter metadata fields
- `templates/tasks/task_packet.md` — adds adapter metadata fields to packet template scaffold
- `src/forge/domain/packets.py` — parser alias support for adapter metadata keys
- `tests/test_packet_status.py` — parser coverage for adapter metadata
- `tests/test_task_create_cmd.py` — packet creation coverage for adapter metadata defaults
- `tests/test_task_validate_cmd.py` — integration coverage for legacy packets without adapter metadata
- `docs/working/backlog.md` — status update for P6-T04
- `docs/working/current_focus.md` — phase focus update
- `docs/working/current_task.md` — active task pointer/status

## Acceptance Checklist
- [x] Task packet templates include optional `primary_adapter` and `secondary_adapters` metadata fields
- [x] Packet metadata parser exposes adapter fields from `task.md`
- [x] Existing packets without adapter metadata continue to parse and validate
- [x] Focused metadata/validation tests passing
- [x] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Context assembly integration for adapter hints
- Adapter-aware review/export hint surfaces
- Canonical doc edits
