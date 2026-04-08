# Plan: TASK-0062

## Approach

Implement the Phase 7 prompt entrypoint directly in `prompts/` with minimal churn: add the new stable onboarding prompt file, convert the prior init prompt into a compatibility alias, and update onboarding references in user-facing docs so the preferred entrypoint is clear without breaking existing usage.

---

## Step 1 — Add Stable Onboarding Prompt

Create `prompts/workflow.onboard.new.md` with a question-first flow, explicit adapter-selection inputs, and strict new-project scope boundaries aligned with locked Phase 7 planning decisions.

---

## Step 2 — Convert Legacy Entry To Compatibility Guidance

Update `prompts/workflow.init.md` to point to the new prompt while preserving compatibility for users still invoking the legacy name.

---

## Step 3 — Align User-Facing Onboarding Docs

Update onboarding instructions in `README.md` (and prompt index) so documentation consistently points to the new prompt entrypoint and states the compatibility/deferred-existing-project boundaries.

---

## Verification

Run targeted checks to confirm references and docs integrity:
- `rg -n "workflow\\.onboard\\.new|workflow\\.init" README.md prompts/README.md prompts/workflow.init.md prompts/workflow.onboard.new.md`
- `.venv/bin/forge docs validate`
- `.venv/bin/pytest -q`
