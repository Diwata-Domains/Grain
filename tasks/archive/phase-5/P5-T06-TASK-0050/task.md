# Task: Expand integration tests across core flows

## Metadata
- **ID:** TASK-0050
- **Status:** done
- **Phase:** Phase 5 — Review, Handoff, and Hardening
- **Backlog:** P5-T06
- **Packet Path:** tasks/P5-T06-TASK-0050/
- **Dependencies:** TASK-0045, TASK-0046, TASK-0047, TASK-0048, TASK-0049

## Objective
Add end-to-end tests that exercise the main command chain across repository init, docs validation, task creation, context export, and review flows.

## Why This Task Exists
Phase 5 needs a golden-path integration layer so the core CLI flows are verified together rather than only through isolated unit tests.

## Scope
- Add a focused integration test file that walks through the CLI core flows.
- Reuse existing fixtures and command behavior instead of adding new runtime code.
- Keep the test data small and deterministic.

## Constraints
- Stay within CLI-first v1 scope.
- Use local filesystem state only.
- Do not change canonical docs or workflow semantics.

## Escalation Conditions
- If the integration flow reveals a command contract mismatch, stop and record it rather than broadening the test to hide the issue.
- If the test requires new workflow behavior, escalate through the proposal flow instead of changing canonical docs directly.
