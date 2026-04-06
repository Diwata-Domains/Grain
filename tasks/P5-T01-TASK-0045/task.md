# Task: Implement review validation service

## Metadata
- **ID:** TASK-0045
- **Status:** done
- **Phase:** Phase 5 — Review, Handoff, and Hardening
- **Backlog:** P5-T01
- **Packet Path:** tasks/P5-T01-TASK-0045/
- **Dependencies:** TASK-0044

## Objective
Implement a review validation service that inspects a task packet for review readiness and completion prerequisites, using existing packet-validation rules as the base for review-state reporting.

## Why This Task Exists
Phase 5 needs a reusable service for `forge review check` and later handoff/summary commands. This task establishes the review-readiness logic without changing CLI behavior yet.

## Scope
- Add `src/forge/services/review_service.py` with review validation logic and a structured report.
- Add tests that verify review readiness, missing-packet failure behavior, and incomplete-packet reporting.
- Reuse existing packet-validation helpers instead of duplicating rules.

## Constraints
- Keep the service filesystem-local and packet-scoped.
- Do not implement `forge review check`, `forge review handoff`, or `forge review summary` CLI wiring in this task.
- Do not modify canonical docs.

## Escalation Conditions
- If review readiness cannot be defined cleanly from the existing packet lifecycle and validator rules, stop and record the ambiguity rather than inventing a hidden contract.
- If the service needs new canonical workflow semantics, escalate through the proposal flow instead of changing canonical docs directly.
