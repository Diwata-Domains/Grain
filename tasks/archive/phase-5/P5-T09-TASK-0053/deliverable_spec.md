# Deliverable Spec: TASK-0053

## Required Deliverables
- Cleaner text failure output for `model select` and `model escalate`.
- Enriched JSON error payloads for those commands.
- Focused tests covering the refined failure-reporting contract.

## Acceptance Criteria
- Failure output starts with command-scoped status (`<command>: failed`).
- Text output includes concrete error details and hinting for missing profile config.
- JSON error responses include command context fields.
