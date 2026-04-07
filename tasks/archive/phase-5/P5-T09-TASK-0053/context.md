# Context: TASK-0053

## Working Context
- Current phase: Phase 5 — Review, Handoff, and Hardening
- Active backlog item: P5-T09
- Primary target: model command failure messaging

## Relevant Files
- `src/forge/cli/model.py`
- `src/forge/services/model_service.py`
- `tests/test_model_select_cmd.py`
- `tests/test_model_escalate_cmd.py`
- `tests/test_model_show_cmd.py`
- `tests/test_help_ergonomics.py`

## Notes
- Keep exit codes and control flow stable.
- Tighten assertions where Phase 5 tracking identified gaps.
