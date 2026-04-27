# Task: Add Working-Doc Reconciliation Checks for State Drift

## Metadata
- **ID:** TASK-0071
- **Status:** done
- **Phase:** Phase 8 — Workflow Automation Runner Foundation
- **Backlog:** P8-T11
- **Packet Path:** tasks/P8-T11-TASK-0071/
- **Dependencies:** P8-T01 (done)
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective

Fix current working-doc drift between `backlog.md` (shows P8-T09 done) and `current_focus.md` (shows P8-T09 in_progress). Document the three-layer reconciliation approach — manual checklist, explicit `forge workflow reconcile` command spec, and runner-level validation signal — formally in working docs so future task closeouts can follow a consistent pattern.

## Why This Task Exists

Working docs fell out of sync after P8-T09 closed. `current_focus.md` still shows P8-T09 as in_progress and the Immediate Goals haven't been updated to reflect that only P8-T10 (blocked) and P8-T11 remain. This is the exact drift problem Q15 identified and P8-T11 was designed to address. Formalizing the reconciliation approach prevents the same drift from accumulating in Phase 9 and later.

## Scope
- Fix current_focus.md: update Phase 8 progress, Immediate Goals, and phase status to reflect actual state (P8-T09 done, P8-T10 blocked, P8-T11 in_progress)
- Update backlog.md: mark P8-T11 status from draft → in_progress
- Add a reconciliation checklist note to `docs/working/v2_plan.md` §9 (if the existing text is insufficient — it already has the three-layer description; formalize the manual checklist items)
- Update `docs/working/workflow_metrics.md` with Phase 8 completion state
- Record in `docs/working/open_questions.md` that `forge workflow reconcile` command spec is a planned follow-up (if not already noted)

## Constraints
- Do not modify canonical docs directly
- Do not implement CLI commands or src/ changes (out of scope for this packet)
- Do not expand to Phase 9 planning work
- Keep all changes additive and targeted; no broad rewrites

## Escalation Conditions
- If the drift spans additional working docs not identified here, document the additional scope rather than silently fixing it

## Closure Requirements

Before the packet can move to review, the task artifacts must include:

- `results.md` with current task status, review readiness, recommended next status, files changed, summary, test results, efficiency metrics, review notes, deliverable checklist, and blockers
- `handoff.md` with packet identity, phase, status, review readiness, recommended next status, summary, what was built, what review should check, known issues or follow-ups, files changed, reviewer notes, and closeout intake

Before the packet can move from review to done, the review artifacts must include:

- explicit `open_questions_to_log`
- explicit `proposal_candidates_to_log`
- explicit `followups_to_log`

Use `None` when a category has no items.

## Reviewer Focus
- Verify current_focus.md accurately reflects Phase 8 actual state
- Verify the three-layer reconciliation approach is coherent and actionable in v2_plan.md
- Confirm no canonical docs were modified
