# Task: Action launcher wiring for execute/review/close flows

## Metadata
- **ID:** TASK-0149
- **Status:** done
- **Phase:** Phase 22 — TUI Foundation and Workflow Surfaces
- **Backlog:** P22-T04 — Action launcher wiring for execute/review/close flows
- **Packet Path:** tasks/P22-T04-TASK-0149/
- **Dependencies:** TASK-0146, TASK-0147, TASK-0148
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Wire safe TUI action launchers for execute, review, and close so the Textual shell can trigger the existing Grain workflow flows and immediately refresh its read-only state.

## Why This Task Exists
The TUI now shows status and inspector information, but operators still have to leave the shell to advance normal task lifecycle steps. This task adds the first real operator controls while preserving Grain’s existing workflow and review gates.

## Scope
- add testable launcher helpers for execute, review, and close flows
- bind those helpers into the Textual app through keyboard actions and an action panel
- refresh the shell snapshot after each launcher attempt and surface the result in the UI

## Constraints
- all actions must delegate to existing Grain services or commands, not duplicate workflow logic
- launcher failures and gates must surface as stateful feedback rather than hidden exceptions

## Escalation Conditions
- if the launcher needs to bypass review/close policy or invent new task state transitions, stop and re-scope
