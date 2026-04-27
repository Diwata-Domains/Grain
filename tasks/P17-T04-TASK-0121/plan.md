# Plan: TASK-0121

## Approach

Implement a small task-advice helper that reads the active phase backlog, selects the currently eligible pool (`ready` if present, otherwise `draft`), and ranks those tasks against a supplied scope summary. Expose that result inside `orchestrate scope` so operators can inspect ranked task suggestions without affecting workflow routing.

---

## Step 1 — Add advisory task-ranking helper

Read the active phase and backlog tasks, select the eligible candidate pool, semantically score task titles against the supplied scope, and pass normalized inputs into the shared ranking service.

---

## Step 2 — Attach advice to orchestration scope output

Add the ranked task-advice payload to `analyze_scope_signals()` so the orchestration surface exposes ranked task suggestions alongside adapter and impact signals.

---

## Step 3 — Add focused tests

Add helper-level tests for eligible-pool selection and ranking order, plus orchestration tests that assert the task-advice payload is included.

---

## Verification

Run task-advice, orchestration, ranking-service, and import tests with the local virtualenv interpreter.
