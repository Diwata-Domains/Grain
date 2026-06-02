# Task: Implement `grain verify status` for pending checks

## Metadata
- **ID:** TASK-0180
- **Status:** done
- **Phase:** Phase 28 — Assay Verification Integration
- **Backlog:** P28-T02
- **Packet Path:** tasks/P28-T02-TASK-0180/
- **Dependencies:** TASK-0179
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none

## Objective
Implement a read-only `grain verify status` command that resolves a packet-local verification request by `verification_id` and reports its current state in text and JSON.

## Why This Task Exists
The submit bridge now creates a stable request artifact. Phase 28 needs a corresponding inspection surface before result ingestion and workflow gates can build on the verification lifecycle.

## Scope
- Add `grain verify status`.
- Reuse the existing `verification_request.json` artifact as the status source.
- Add focused tests for success, JSON output, and missing request behavior.

## Constraints
- Keep the command read-only.
- Do not introduce polling, networking, or external provider calls.

## Escalation Conditions
- Stop if the status surface requires anything beyond packet-local verification request artifacts.
