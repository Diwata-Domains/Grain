# Handoff: TASK-0040

## Final State
P4-T09 review fixes are complete and the packet is ready for closeout.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0040
- **Phase:** Phase 4 — Context Assembly and Model Routing
- **Status:** review

### Outcome
- **Review Readiness:** ready
- **Recommended Next Status:** review
- **Short Summary:** Em-dash normalization bug is fixed, regression coverage is added, and packet artifacts are now template-conformant.

## What Was Built
- Added em-dash separator handling in `_normalize_text` within `src/forge/domain/routing.py`.
- Added `test_select_model_class_stage_mapping_handles_canonical_em_dash_stage` to verify canonical stage-map behavior.
- Updated task `results.md` and `handoff.md` to match current templates.

## What Review Should Check
- Canonical stage input like `Stage 6 — Closure and Handoff` now routes through `_STAGE_MODEL_MAP`.
- `decision.reason` contains `stage mapping matched` for em-dash stage input, confirming map-path usage.
- Task artifact format now conforms to `templates/tasks/results.md` and `templates/tasks/handoff.md`.

## What Was Not Done
- CLI command wiring for `forge model show`, `forge model select`, and `forge model escalate` (handled in P4-T10/P4-T11/P4-T12).

## Known Issues or Follow-ups
- None blocking for this packet.

## Files Changed
- `src/forge/domain/routing.py` — em-dash normalization fix
- `tests/test_model_service.py` — regression test for canonical em-dash stage mapping
- `tasks/P4-T09-TASK-0040/results.md` — template-conform results artifact
- `tasks/P4-T09-TASK-0040/handoff.md` — template-conform handoff artifact
- `docs/working/current_task.md` — task state set to `in_progress` for rework then back to `review`
- `tasks/P4-T09-TASK-0040/task.md` — packet status set to `in_progress` for rework then back to `review`

## Reviewer Notes
All required fixes from the prior review notes are addressed; full test suite remains green.

## Closeout Intake

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- None
