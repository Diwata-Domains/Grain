# Plan: TASK-0061

## Approach

Define the smallest enforceable Phase 8 runner contract in working docs, then align backlog/current-focus/open-questions so downstream tasks implement against one explicit boundary with no hidden assumptions.

---

## Step 1 — Lock Minimal Runner Slice

Add explicit minimal-slice scope in `docs/working/v2_plan.md`: what the runner does first, where it must stop, and what it must not automate yet.

---

## Step 2 — Align Sequencing State

Update `docs/working/backlog.md` and `docs/working/current_focus.md` to reflect `P8-T01` completion readiness and the next actionable task boundary.

---

## Step 3 — Persist Decision Trace

Record a resolved planning decision in `docs/working/open_questions.md` so the stop-condition rule and machine-readable output boundary remain discoverable.

---

## Verification

- `rg -n "minimal slice|stop condition|machine-readable|P8-T0" docs/working/v2_plan.md docs/working/backlog.md docs/working/current_focus.md docs/working/open_questions.md`
- `.venv/bin/forge docs validate`
- `.venv/bin/forge task validate --id TASK-0061`
- `.venv/bin/pytest -q`
