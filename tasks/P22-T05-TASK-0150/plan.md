# Plan: TASK-0150

## Approach

Extend the TUI snapshot with prompt preview lines, compact context-bundle summary data, and full blocker/affected-artifact detail. Render those as dedicated panels beside the existing dashboard and inspector surfaces. Keep the previews compact, deterministic, and derived from existing Grain services so they stay fast and reviewable.

---

## Step 1 — Add compact preview/detail snapshot data

Read a few non-empty lines from the recommended prompt file, summarize the active task’s context bundle through existing context services, and capture affected-artifact detail from workflow evaluation.

---

## Step 2 — Render dedicated prompt/context/blocker panels

Add new panels for prompt preview, context composition, and blocker detail so operators can inspect the execution setup without leaving the TUI.

---

## Step 3 — Add focused preview/detail tests

Add focused tests for prompt preview, context summary, and blocker detail rendering to pin the operator contract without needing full interactive Textual tests.

---

## Verification

Run the focused TUI and related workflow/context test slice and verify the preview/detail panels stay aligned with real Grain service outputs.
