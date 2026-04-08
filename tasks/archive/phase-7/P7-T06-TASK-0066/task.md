# Task: Add onboarding integration tests and phase-level docs updates

## Metadata
- **ID:** TASK-0066
- **Status:** done
- **Phase:** Phase 7 — New-Project Onboarding Flow
- **Backlog:** P7-T06
- **Packet Path:** tasks/P7-T06-TASK-0066/
- **Dependencies:** TASK-0062, TASK-0065
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add focused integration coverage for the new-project onboarding flow (init scaffolding, adapter selection, and optional bootstrap), and update phase-level docs so user-facing guidance reflects the currently supported onboarding path.

## Why This Task Exists
Phase 7 exit criteria require evidence that the onboarding path works end-to-end and clear docs that match implemented behavior. Without integration tests and doc alignment, onboarding remains fragile and harder to validate during review.

## Scope
- Add `tests/test_phase7_integration.py` with onboarding-path integration coverage.
- Update `README.md` onboarding guidance to reflect supported `forge init` onboarding options.
- Update `docs/working/current_focus.md` to reflect current Phase 7 priorities and boundaries.

## Constraints
- Keep onboarding scope limited to new-project flow; existing-project adoption remains deferred.
- Do not modify canonical docs directly.
- Keep tests and docs updates narrowly tied to implemented onboarding behavior.

## Escalation Conditions
- If integration assertions require canonical contract changes, log a proposal instead of editing canonical docs.
- If onboarding behavior diverges from locked Phase 7 decisions, stop and record the conflict before proceeding.

## Model Selection Rationale
`open_model` is appropriate because this task is primarily bounded test/docs integration work over already-implemented onboarding behavior.
