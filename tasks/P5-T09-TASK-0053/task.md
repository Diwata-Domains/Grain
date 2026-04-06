# Task: Clean up error messages and failure reporting

## Metadata
- **ID:** TASK-0053
- **Status:** done
- **Phase:** Phase 5 — Review, Handoff, and Hardening
- **Backlog:** P5-T09
- **Packet Path:** tasks/P5-T09-TASK-0053/
- **Dependencies:** TASK-0052

## Objective
Improve user-facing failure messaging for model routing commands while preserving existing command behavior and failure semantics.

## Why This Task Exists
Phase 5 hardening called out error-message assertion gaps in model select/escalate tests. This task closes those gaps and standardizes failure output formatting.

## Scope
- Improve text-mode failure rendering for `model select` and `model escalate`.
- Enrich JSON-mode failure payloads with command context fields.
- Add tests that assert failure text and JSON shape for these error paths.

## Constraints
- Do not change success-path behavior.
- Do not change command exit behavior.
- Keep scope limited to message quality and failure reporting clarity.

## Escalation Conditions
- If any message change requires altering command semantics, stop and record the conflict.
- If broader CLI groups need harmonization, defer them instead of broadening this packet.
