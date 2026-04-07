# Plan: TASK-0049

1. Add a summary helper to the review service that assembles packet state, validation findings, and next actions.
2. Wire `forge review summary` into `src/forge/cli/review.py` with text and JSON output.
3. Add CLI and service tests for ready, incomplete, missing-packet, and JSON behavior.
4. Update the working task packet artifacts and close the execute step with reviewer-ready outputs.
