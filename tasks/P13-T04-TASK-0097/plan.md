# Plan: TASK-0097

## Approach

Author a practical, command-driven onboarding prompt for existing repositories. Keep it explicit about required CLI calls, draft-first behavior, and question-driven clarification before finalizing documentation content.

---

## Step 1 — Add prompt entrypoint

Create `prompts/workflow.onboard.existing.md` with metadata, scope boundary, required inputs, and run mode guidance.

---

## Step 2 — Add mandatory CLI sequence

Include non-optional commands for onboard scaffold, docs validation, workflow evaluation, and task validation when applicable.

---

## Step 3 — Add prompt-surface tests

Add focused tests that assert the prompt exists and contains mandatory CLI command steps.

---

## Verification

- `.venv/bin/pytest -q tests/test_workflow_onboard_existing_prompt.py`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0097`
- `.venv/bin/pytest -q`
