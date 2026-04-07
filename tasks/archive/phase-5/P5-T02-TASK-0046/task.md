# Task: Implement `forge review check`

## Metadata
- **ID:** TASK-0046
- **Status:** done
- **Phase:** Phase 5 — Review, Handoff, and Hardening
- **Backlog:** P5-T02
- **Packet Path:** tasks/P5-T02-TASK-0046/
- **Dependencies:** TASK-0045

## Objective
Wire the review validation service into a working `forge review check` CLI command that reports packet review readiness, blocker details, and exit status in the same style as the other Forge commands.

## Why This Task Exists
Phase 5 needs an actual review command surface after the review-validation service exists. This task makes the review readiness logic user-visible and scriptable.

## Scope
- Implement `forge review check` in `src/forge/cli/review.py`.
- Add CLI tests for success, blocker reporting, JSON output, and missing packet failures.
- Reuse the existing review service rather than duplicating packet validation logic.

## Constraints
- Keep the CLI thin and filesystem-local.
- Do not implement `forge review handoff` or `forge review summary` in this task.
- Do not modify canonical docs.

## Escalation Conditions
- If the review output contract is inconsistent with the existing CLI conventions, stop and record the inconsistency rather than inventing a new format.
- If implementing the CLI requires changing review readiness semantics, escalate through the proposal flow instead of changing canonical docs directly.
