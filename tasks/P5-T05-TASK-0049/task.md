# Task: Implement `forge review summary`

## Metadata
- **ID:** TASK-0049
- **Status:** done
- **Phase:** Phase 5 — Review, Handoff, and Hardening
- **Backlog:** P5-T05
- **Packet Path:** tasks/P5-T05-TASK-0049/
- **Dependencies:** TASK-0045, TASK-0046, TASK-0047, TASK-0048

## Objective
Wire a read-only `forge review summary` command that produces a structured packet summary with packet state, validation findings, and next actions for final inspection.

## Why This Task Exists
Phase 5 needs a user-facing packet summary command after review checking and handoff generation exist. This task gives reviewers and operators a concise final-inspection view without mutating packet state.

## Scope
- Implement `forge review summary` in `src/forge/cli/review.py`.
- Add a small review-service helper if needed to keep the CLI thin.
- Add tests for ready, incomplete, JSON, and missing-packet cases.

## Constraints
- Keep the command read-only and filesystem-local.
- Do not alter canonical docs or packet state.
- Do not make the summary command fail just because the packet still has validation findings.

## Escalation Conditions
- If the expected summary shape conflicts with existing CLI output conventions, stop and record the mismatch rather than inventing a new format.
- If the task requires changing review or closure semantics, escalate through the proposal flow instead of editing canonical docs directly.
