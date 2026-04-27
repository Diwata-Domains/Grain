# Plan: TASK-0071

## Approach

Fix working-doc drift left over from P8-T09 closeout: update current_focus.md to match actual Phase 8 state, promote P8-T11 to in_progress in backlog.md, formalize the three-layer reconciliation checklist in v2_plan.md §9, update workflow_metrics.md, and note the forge workflow reconcile command spec as a follow-up in open_questions.md.

---

## Step 1 — Fix current_focus.md

Update:
- Phase 8 Progress: change "P8-T09 in progress" to "P8-T09 done; P8-T11 in_progress. 494 tests passing."
- Immediate Goals: remove "complete P8-T09" goal; update to reflect P8-T11 (TASK-0071) as the active task
- Do Not Work On: confirm P8-T10 remains blocked; no change needed there

---

## Step 2 — Update backlog.md

Change P8-T11 status from `draft` → `in_progress`.

---

## Step 3 — Formalize reconciliation checklist in v2_plan.md §9

The existing §9 already describes the three-layer approach at a high level. Add a concrete checklist under the "Reconciliation strategy" subsection so future task closeouts have actionable items to follow:

Manual checklist items:
- [ ] backlog.md status matches actual task state
- [ ] current_focus.md Phase N Progress reflects completed/active/blocked tasks
- [ ] current_focus.md Immediate Goals matches current_task.md and backlog status
- [ ] workflow_metrics.md updated if phase or significant milestone changed
- [ ] open_questions.md has no stale "resolved" items that should move to deferred or archived

---

## Step 4 — Update workflow_metrics.md

Add Phase 8 progress entry: tasks P8-T01–P8-T09 done (9 tasks), P8-T11 in_progress, 494 tests passing.

---

## Step 5 — Check open_questions.md for reconcile command note

If there is no existing note about the `forge workflow reconcile` command being a planned CLI follow-up, add one as an open question or deferred item to make it discoverable in future planning.

---

## Verification

After all edits:
- current_focus.md shows P8-T09 done and P8-T11 in_progress
- backlog.md shows P8-T11 status = in_progress
- v2_plan.md §9 has a concrete checklist section
- workflow_metrics.md has a Phase 8 entry
- No canonical docs were modified
