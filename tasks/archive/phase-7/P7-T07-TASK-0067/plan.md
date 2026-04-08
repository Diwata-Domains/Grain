# Plan: TASK-0067

## Approach

Capture a concrete, low-ambiguity planning boundary for existing-project adoption by synchronizing entry criteria across onboarding and roadmap working docs, then align current-focus guidance to prevent premature implementation drift.

---

## Step 1 — Define Entry Criteria In Onboarding Plan

Update `docs/working/v2_onboarding.md` with explicit conditions that must hold before existing-project adoption implementation can start.

---

## Step 2 — Align Roadmap Contract

Update FR-013 in `docs/working/future_roadmap.md` so roadmap status and promotion criteria mirror the onboarding boundary.

---

## Step 3 — Align Current Focus And Validate

Update `docs/working/current_focus.md` immediate goals for post-boundary review/close flow, then run docs/task validation checks.

---

## Verification

- `rg -n "P7-T07|existing-project adoption|entry criteria|promotion" docs/working/v2_onboarding.md docs/working/future_roadmap.md docs/working/current_focus.md`
- `.venv/bin/forge docs validate`
- `.venv/bin/forge task validate --id TASK-0067`
