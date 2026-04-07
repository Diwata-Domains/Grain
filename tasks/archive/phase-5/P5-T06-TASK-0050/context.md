# Context: TASK-0050

## Working Context
- Current phase: Phase 5 — Review, Handoff, and Hardening
- Active backlog item: P5-T06
- Core flows under test: init, docs validate, task create, context export, review check, review handoff, review summary

## Relevant Files
- `tests/test_phase5_integration.py`
- `tests/test_docs_validate_cmd.py`
- `tests/test_task_create_cmd.py`
- `tests/test_context_export_cmd.py`
- `tests/test_review_check_cmd.py`
- `tests/test_review_handoff_cmd.py`
- `tests/test_review_summary_cmd.py`

## Notes
- Prefer one small happy-path integration test that actually chains the commands together.
- Reuse the packet repository fixture for packet templates.
