# Plan: TASK-0046

## Approach

Connect the existing review service to the CLI with a small wrapper that formats the result and structured report. Add tests that exercise both the human-readable and JSON output paths, plus missing-packet failure behavior.

---

## Step 1 — Wire the CLI command

Implement `review check` so it resolves the repository root, invokes the review service, and formats the resulting report using existing output conventions.

---

## Step 2 — Add tests

Add focused CLI tests that verify the command reports readiness, shows blockers, emits JSON, and returns a non-zero exit for missing packets.

---

## Step 3 — Verify behavior

Run the targeted review-command tests and then the full pytest suite.

---

## Verification

Confirm both command output and service-driven error handling with the existing test harness.
