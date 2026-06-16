# Task: Implement `grain verify ingest` for Assay payloads

## Metadata
- **ID:** TASK-0181
- **Status:** done
- **Phase:** Phase 28 — Assay Verification Integration
- **Backlog:** P28-T03
- **Packet Path:** tasks/P28-T03-TASK-0181/
- **Dependencies:** TASK-0179
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none

## Objective
Implement `grain verify ingest --verification-id --payload <path>` so Grain can validate an Assay result payload, persist a packet-local verification result artifact, update verification request state, and reflect the outcome in the packet review bundle.

## Why This Task Exists
Phase 28 needs a real result-ingestion bridge before verification can influence review and close behavior. Submission and status inspection are already in place; ingestion is the step that turns an external verifier result into packet-local workflow state.

## Scope
- Add `grain verify ingest` to the verify command group.
- Validate required Assay payload fields and reject malformed input cleanly.
- Persist `verification_result.json` and update `verification_request.json` plus `results.md`.

## Constraints
- Keep the bridge packet-local and file-backed.
- Do not auto-close tasks or auto-create follow-up packets from verifier output.

## Escalation Conditions
- Stop if Assay payload handling requires networking, daemon state, or canonical-doc mutation beyond the active packet workflow artifacts.
