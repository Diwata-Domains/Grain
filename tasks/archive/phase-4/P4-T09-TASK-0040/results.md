# Results: TASK-0040

## Status
in_progress

## Packet State
- **Current Task Status:** review
- **Review Readiness:** ready
- **Recommended Next Status:** review

## Files Changed
- `src/forge/domain/routing.py` — added em-dash normalization in `_normalize_text` so canonical stage names map correctly
- `tests/test_model_service.py` — added canonical em-dash stage-map regression test and stronger stage-map assertion
- `tasks/P4-T09-TASK-0040/results.md` — updated to current template structure
- `tasks/P4-T09-TASK-0040/handoff.md` — updated to current template structure
- `docs/working/current_task.md` — moved task status to `in_progress` for rework and back to `review`
- `tasks/P4-T09-TASK-0040/task.md` — status moved to `in_progress` for rework and back to `review`

## Summary
Applied the required post-review fix for P4-T09: canonical workflow stage strings with em dash (`—`) now normalize into the stage-map key format. Added a regression test that explicitly verifies the stage-map path is used for a canonical em-dash stage name. Reworked packet artifacts to match current results/handoff templates.

## Test Results
12/12 targeted tests passing; 324/324 total tests passing.

## Efficiency
- **Prompt Runs:** 1
- **Conversation Restarts:** 0
- **Files Read (estimated):** 14
- **Exact Tokens:** not available
- **Efficiency Notes:** Rework was narrowly scoped to one normalization path, one regression test, and artifact-template alignment.

## Review Notes
- Verify `_normalize_text` now handles em dash (`—`) in addition to underscore and hyphen separators.
- Verify `test_select_model_class_stage_mapping_handles_canonical_em_dash_stage` exercises the stage-map branch, not only keyword fallback.

## Review Intake
- **Review Decision:** ready
- **Definition of Done Met:** yes
- **Recommended Next Status:** done

### Required Fixes
- None

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- None

### Residual Risks
- `_match_profile_use_for` substring matching remains broad; monitor in P4-T10+ if routing noise appears.

## Deliverable Checklist
- [x] Workflow stage and task-role inputs resolve to model classes deterministically
- [x] Selection logic remains provider-agnostic and role/capability based
- [x] Service loads runtime profile config and reports missing-config errors cleanly
- [x] All tests passing

## Blockers
None.
