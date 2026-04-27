# Context: TASK-0049

## Working Context
- Current phase: Phase 5 — Review, Handoff, and Hardening
- Active backlog item: P5-T05
- Related commands: `forge review check`, `forge review handoff`, `forge review summary`
- Packet scope: packet-local inspection only

## Relevant Files
- `src/forge/cli/review.py`
- `src/forge/services/review_service.py`
- `tests/test_review_check_cmd.py`
- `tests/test_review_handoff_cmd.py`
- `tests/test_review_service.py`
- `tests/test_review_summary_cmd.py`

## Notes
- Reuse existing review validation logic.
- Prefer a structured summary that can be serialized to JSON without special casing.
