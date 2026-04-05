# Deliverable Spec: TASK-0042

## Required Output

### New Files
- `tests/test_model_select_cmd.py` — CLI tests for `forge model select`

### Modified Files
- `src/forge/cli/model.py` — implement `model_select` command body

## Acceptance Checklist
- [ ] `forge model select --stage <stage>` returns the correct model class
- [ ] `forge model select --role <role>` returns the correct model class
- [ ] `--format json` emits `{ok, command, repo, selected_class, reason, stage, role}`
- [ ] UsageError when neither `--stage` nor `--role` is provided
- [ ] Error reported and non-zero exit when `agent_profiles.md` is missing
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- `forge model escalate` implementation (P4-T12)
- Changes to `model_service.py` or `routing.py`
