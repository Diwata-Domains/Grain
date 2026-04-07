# Context: TASK-0051

## Working Context
- Current phase: Phase 5 — Review, Handoff, and Hardening
- Active backlog item: P5-T07
- Fixture targets: manifest files and review-ready packet artifacts

## Relevant Files
- `tests/fixtures/phase5/docs_manifest.yaml`
- `tests/fixtures/phase5/workflow_spec.md`
- `tests/fixtures/phase5/review_results.md`
- `tests/fixtures/phase5/review_handoff.md`
- `tests/test_phase5_integration.py`
- `tests/test_review_check_cmd.py`
- `tests/test_review_handoff_cmd.py`
- `tests/test_review_summary_cmd.py`

## Notes
- Prefer shared fixture files over inline multiline test blobs.
- Keep the fixture data stable and human-readable.
