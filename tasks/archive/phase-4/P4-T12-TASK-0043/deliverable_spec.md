# Deliverable Spec: TASK-0043

## Required Output

### New Files
- `tests/test_model_escalate_cmd.py` — CLI tests for `forge model escalate`

### Modified Files
- `src/forge/domain/routing.py` — add `get_escalation_target` function
- `src/forge/services/model_service.py` — add `escalate_model_for_class` function
- `src/forge/cli/model.py` — implement `model_escalate` command; fix inline import in `model_select`

## Acceptance Checklist
- [ ] `forge model escalate --from-class open_model` returns `frontier_model`
- [ ] `forge model escalate --from-class frontier_model` returns `reviewer_model` (wildcard path)
- [ ] `--format json` emits `{ok, command, repo, from_class, target_class, reason}`
- [ ] Unknown `--from-class` value returns non-zero exit with error message
- [ ] Missing `agent_profiles.md` causes non-zero exit
- [ ] Inline import of `select_model_for_stage_or_role` moved to module level in `model.py`
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- Changes to canonical docs
- `forge context` or `forge task` changes
