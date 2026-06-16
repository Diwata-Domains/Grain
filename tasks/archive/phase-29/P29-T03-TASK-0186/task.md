# Task: Reduce runner packet/template drift on activation

## Metadata
- **ID:** TASK-0186
- **Status:** done
- **Phase:** Phase 29 — Workflow Compliance Hardening
- **Backlog:** P29-T03
- **Packet Path:** tasks/P29-T03-TASK-0186/
- **Dependencies:** TASK-0185
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none

## Objective
Harden `workflow run` activation so auto-created packets are immediately usable instead of raw template stubs, and so activation syncs packet/backlog state into `in_progress` instead of leaving obvious drift behind.

## Why This Task Exists
The previous hardening slices exposed that the runner itself was a major source of drift: it created placeholder packets, left `task.md` in `draft`, and left backlog state at `ready`. That forced repeated manual packet rescue and caused avoidable workflow-state mismatches.

## Scope
- Hydrate auto-created packet templates during `workflow run`.
- Sync activated packet status and backlog status to `in_progress`.
- Add focused runner and integration coverage for the new bootstrap behavior.

## Constraints
- Keep the bootstrap deterministic and file-backed.
- Do not expand into broader diagnostics or task-splitting logic in this slice.

## Escalation Conditions
- Stop if fixing the runner drift requires redefining the task packet model rather than hydrating and syncing the existing one-step activation flow.
