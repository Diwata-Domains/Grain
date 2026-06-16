# Plan: TASK-0184

## Approach

Make the existing Grain and Assay loop harder to forget by strengthening the runtime docs and shipped execution prompts, then prove those guardrails with release-surface tests so the guidance stays firm across future edits.

---

## Step 1 — Harden runtime guidance

Update `AGENTS.md`, `CLAUDE.md`, and `PROJECT_RULES.md` so they explicitly tell agents to stop and return to `grain workflow next`, the active packet, or the verify loop when they detect drift mid-session.

---

## Step 2 — Harden prompt assets

Update the main execution and close prompts so they explicitly forbid continuing “from chat memory” or bypassing verification/review gates when the packet or workflow state says otherwise.

---

## Step 3 — Lock the behavior with tests

Extend release-surface tests to assert the new anti-drift wording in the runtime docs and shipped prompt assets.

---

## Verification

Run `/Users/barbaricum/diwata-labs/.venv/bin/python -m pytest -q tests/test_release_surface.py`.
