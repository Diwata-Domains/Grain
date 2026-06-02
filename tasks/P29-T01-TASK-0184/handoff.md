# Handoff: TASK-0184

## What Changed
- Strengthened runtime anti-drift guidance in `AGENTS.md`, `CLAUDE.md`, and `PROJECT_RULES.md`
- Strengthened shipped execution/close prompts to stop and return to the Grain workflow when packet or verification state is unclear
- Added release-surface coverage so the hardened guidance does not regress quietly

## Verification
- `10 passed in 0.15s` via `tests/test_release_surface.py`

## Review Focus
- Check that the new guidance is firm without introducing workflow semantics that the code does not actually enforce yet
- Verify the wording stays aligned with the current Grain/Assay packet-local loop

## Follow-Ups
- `P29-T02` should add real workflow misuse blockers for the most common off-rails states surfaced by this guidance slice
