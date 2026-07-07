# Task: Surface assay review findings on verify ingest + test coverage

## Metadata
- **ID:** TASK-0223
- **Status:** review
- **Mode:** simple
- **Phase:** Phase 36 — v0.5.0 Release Readiness & Fleet Hardening
- **Backlog:** P36-T14 — Close the assay bridge loop: surface review findings on ingest
- **Packet Path:** tasks/P36-T14-TASK-0223/
- **Dependencies:** none
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Close the last gap in the grain↔assay agent-to-agent verification loop. A live
end-to-end round trip (2026-07-07) proved `grain verify submit` → assay-schema-valid
payload → `grain verify ingest` works, including `issue_type=code_review` — but the
structured `review.findings` (file/line/severity/message) and `followup_candidates`
were dropped on ingest: only the one-line summary reached `results.md`, and the
`review` block was not persisted in `verification_result.json`. On a failed review
those findings are exactly what the operator or next agent needs. Render them into
the packet's `## Verification Review → ### Findings` section and persist the review
block.

## Why This Task Exists
Assay P32-T06 / P30-T01 track "close the assay→grain loop" and cite CP-002
("`grain verify ingest` does not exist") — that claim is stale: the command shipped
with the Phase 28 bridge and CP-005 (applied 2026-06-25) already makes assay emit
`code_review` payloads with the structured review block. The loop was closed in code
but lossy in rendering, and its docs said it didn't exist.

## Scope
- `VerificationResultRecord`: persist optional `review` block (dict | None)
- `_apply_results_verification_outcome`: render review findings as `file:line [severity] message` and followups as `follow-up: title — description`
- Tests: review-block rendering + no-review-block regression (TDD; watched fail first)
- Out of scope: workflow-gate wiring (`workflow next` blocking on pending verification — v2-plan FR-006 behavior, still unimplemented), assay MCP `get_status` states

## Constraints
- Ingest stays additive/idempotent on the packet; no changes to payload validation (unknown fields were already tolerated)
- Rendering must not break packets whose payloads have no review block

## Escalation Conditions
- None encountered
