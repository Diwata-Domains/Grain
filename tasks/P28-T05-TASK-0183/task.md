# Task: Operator docs and integration examples (Grain + Assay)

## Metadata
- **ID:** TASK-0183
- **Status:** done
- **Phase:** Phase 28 — Assay Verification Integration
- **Backlog:** P28-T05
- **Packet Path:** tasks/P28-T05-TASK-0183/
- **Dependencies:** TASK-0179, TASK-0180, TASK-0181, TASK-0182
- **Primary Adapter:** docs_adapter
- **Secondary Adapters:** code_adapter

## Objective
Update the public and runtime-facing docs so the live Assay verification loop is explicit, packet-local, and consistent with the newly enforced review/close gates.

## Why This Task Exists
The command surface and workflow gates are now implemented, but the operator-facing docs still contained stale Sentinel language and did not yet describe the actual `grain verify` loop or its closeout constraints.

## Scope
- Document the Assay verification loop in the README and runtime project rules.
- Update the canonical CLI spec to describe the live Assay bridge rather than deferred Sentinel stubs.
- Tighten the close prompt and release-surface tests around verification guidance.

## Constraints
- Keep the docs aligned with the current packet-local implementation.
- Do not describe remote polling, background services, or automatic verifier execution that Grain does not actually provide.

## Escalation Conditions
- Stop if the docs would need to promise capabilities beyond the current packet-local Assay bridge.
