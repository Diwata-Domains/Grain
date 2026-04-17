# Task: Add forge task prepare

## Metadata
- **ID:** TASK-0066
- **Status:** done
- **Phase:** Phase 8 — Workflow Automation Runner Foundation
- **Backlog:** P8-T06
- **Packet Path:** tasks/P8-T06-TASK-0066/
- **Dependencies:** TASK-0062, TASK-0063, TASK-0064, TASK-0065
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add `forge task prepare` to verify packet/context/prompt prerequisites for one task and report missing inputs explicitly without mutating state.

## Why This Task Exists
Phase 8 requires a task-readiness command surface before one-step execution can be safely automated. This command closes the readiness-check gap between task selection and runner execution.

## Scope
- Add a read-only service that checks one task packet for required files and recommended prompt availability.
- Add `task prepare` command to expose readiness/missing-input signals in text and JSON.
- Add tests for ready, missing-input, JSON, and missing-task paths.

## Constraints
- Keep behavior read-only; do not create/update packet or working-doc files during checks.
- Surface missing inputs explicitly; do not infer hidden repair actions.

## Escalation Conditions
- If readiness criteria require canonical contract changes, route via change proposal.
- If required prompt mapping is ambiguous for a packet status, report the ambiguity rather than guessing.
