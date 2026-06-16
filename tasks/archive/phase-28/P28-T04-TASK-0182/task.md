# Task: Wire verification gates into review and close flow

## Metadata
- **ID:** TASK-0182
- **Status:** done
- **Phase:** Phase 28 — Assay Verification Integration
- **Backlog:** P28-T04
- **Packet Path:** tasks/P28-T04-TASK-0182/
- **Dependencies:** TASK-0180, TASK-0181
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none

## Objective
Update the review and close path so pending verification stops closure, failed verification forces an explicit operator decision, and `workflow next` surfaces those verification gates before routing a review packet to close.

## Why This Task Exists
The verify bridge is incomplete unless verification state affects the workflow loop. Operators need the review and close layer to respect `pending` and `failed` verification outcomes instead of silently allowing a packet to close.

## Scope
- Block closure when verification is `pending` or `failed`.
- Surface verification-close blockers through `workflow next`.
- Make `task close` print verification blockers before exiting.

## Constraints
- Keep the gating file-backed and packet-local.
- Do not auto-waive failed verification or invent a background verification lifecycle.

## Escalation Conditions
- Stop if proper verification gating requires external provider polling or non-packet hidden state.
