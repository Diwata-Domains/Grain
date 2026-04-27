# Task: Implement `grain workflow loop` command

## Metadata
- **ID:** TASK-0091
- **Status:** done
- **Phase:** Phase 12 — Automated Workflow Loop
- **Backlog:** P12-T02
- **Packet Path:** tasks/P12-T02-TASK-0091/
- **Dependencies:** TASK-0090
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Implement `grain workflow loop` to repeatedly evaluate workflow state, resolve stage prompts and agent config, and run until a stop condition is reached.

## Why This Task Exists
Phase 12 requires a loop command that executes workflow stages with supervision-aware stopping behavior using the Phase 8 state machine and Phase 12 config contract.

## Scope
- Add workflow loop service for repeated execution.
- Add `workflow loop` CLI command and output contract (text + JSON).
- Add command tests for gated, supervised, and JSON behaviors.

## Constraints
- Keep scope limited to loop command behavior and state transitions.
- Do not implement P12-T03 guardrails (`--dry-run`, expanded logging policy) in this task.

## Escalation Conditions
- If stage command invocation semantics conflict with runtime contract wording, log follow-up in review notes and proceed with minimal deterministic behavior.
