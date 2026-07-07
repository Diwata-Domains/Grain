# Task: FR-006 verification gate in workflow evaluator

## Metadata
- **ID:** TASK-0224
- **Status:** review
- **Mode:** simple
- **Phase:** Phase 36 — v0.5.0 Release Readiness & Fleet Hardening
- **Backlog:** P36-T15 — FR-006 verification gate in workflow evaluator
- **Packet Path:** tasks/P36-T15-TASK-0224/
- **Dependencies:** P36-T14 (findings rendering; `_followup_lines` reuse)
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Implement the machine-readable half of the v2-plan FR-006 verification gate. The
closure validator already blocked review→close on pending/failed verification via
results.md state, but agents only saw a generic `review_close_blocked` — no dedicated
stop reason, no verification_id, no findings. Add first-class gate semantics to the
workflow evaluator: `verification_pending` / `verification_failed` stop reasons keyed
off the packet's `verification_request.json`, `verification_id` populated on the
evaluation (including on `task_close` after a completed verification), failure
summary + follow-up candidates surfaced in blocking_reasons, and the exact
`grain verify ingest` resume command in the pending stop.

## Why This Task Exists
v2_plan §11 FR-006: "workflow run returns a gate stop with stop_reason
verification_pending and verification_id in the JSON output … outcome fail — runner
surfaces the finding; followup_candidates are surfaced for operator review." Logged
as a proposal candidate in TASK-0223 after the loop-closure work.

## Scope
- `WorkflowEvaluation.verification_id` field (additive)
- `STOP_VERIFICATION_PENDING` / `STOP_VERIFICATION_FAILED` stop reasons
- `_verification_gate()` in the review branch, before closure validation; malformed artifacts fall through to closure validation
- Evaluator stays read-only — no packet status mutation; "task moves to blocked" is delivered as guidance ("set the task to needs_fix, or re-run grain verify submit"), not auto-mutation, to avoid backlog-sync drift stops
- Tests: pending stop, failed stop with follow-ups, gate lift to task_close (TDD; watched fail first)

## Constraints
- Read-only evaluator contract preserved
- Packets without a verification request are untouched (gate is opt-in)
- Existing results.md-based closure blocking retained as fallback (regression test untouched)

## Escalation Conditions
- None encountered
