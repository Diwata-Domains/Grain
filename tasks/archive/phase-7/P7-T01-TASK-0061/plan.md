# Plan: TASK-0061

## Approach

Resolve each open onboarding planning question into explicit, scoped decisions, then propagate those decisions into Phase 7 sequencing docs so downstream tasks are concrete and bounded. Keep changes within working docs and avoid runtime/canonical contract modifications.

---

## Step 1 — Resolve onboarding planning questions

Update `docs/working/v2_onboarding.md` to replace open-question ambiguity with explicit decisions for the minimal new-project onboarding slice and clear deferral boundaries for existing-project adoption.

---

## Step 2 — Lock Phase 7 sequencing and readiness

Align `docs/working/implementation_plan.md`, `docs/working/backlog.md`, and `docs/working/current_focus.md` with the resolved decisions so the next execution tasks are concrete and the phase boundary is explicit.

---

## Step 3 — Validate planning artifacts and handoff

Run docs/task validation and full tests to confirm no regressions from planning updates, then produce `results.md` and `handoff.md` for review.

---

## Verification

Run:
- `./.venv/bin/forge --repo . docs validate`
- `./.venv/bin/forge --repo . task validate --id TASK-0061`
- `./.venv/bin/pytest -q`
