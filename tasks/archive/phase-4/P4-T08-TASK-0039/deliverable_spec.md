# Deliverable Spec: TASK-0039

## Required Output

### New Files
- `src/forge/domain/routing.py` — routing config domain dataclasses (`ModelProfile`, `EscalationRule`, `ModelRoutingConfig`)
- `src/forge/adapters/model_config.py` — markdown loader/parser for `docs/runtime/agent_profiles.md`
- `tests/test_model_config_loader.py` — unit tests for model config loading/parsing behavior

### Modified Files
- `tasks/P4-T08-TASK-0039/task.md` — finalized task metadata and scope
- `tasks/P4-T08-TASK-0039/context.md` — recorded minimal required context
- `tasks/P4-T08-TASK-0039/plan.md` — recorded implementation plan
- `tasks/P4-T08-TASK-0039/deliverable_spec.md` — recorded deliverable contract
- `tasks/P4-T08-TASK-0039/results.md` — recorded implementation results
- `tasks/P4-T08-TASK-0039/handoff.md` — recorded reviewer handoff
- `docs/working/current_task.md` — set active task and moved to review

## Acceptance Checklist
- [x] Loader parses `open_model`, `frontier_model`, and `reviewer_model` into structured routing objects
- [x] Escalation rules and preferred model mappings are parsed from runtime markdown
- [x] Missing config file and incomplete profile content raise typed errors
- [x] All new tests passing
- [x] Full test suite passing with no regressions
- [x] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Implementing `forge model show`, `forge model select`, or `forge model escalate` command behavior
- Introducing a new YAML/JSON config source for model profiles
