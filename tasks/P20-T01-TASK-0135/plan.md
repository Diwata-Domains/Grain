# Plan: TASK-0135

## Approach

Introduce an explicit `task_review` workflow action for the state where an active in-progress packet already has `results.md`. This preserves the existing execute gate for tasks still being worked, keeps the `review` status path mapped to close, and lets the runner and prompt surface route operators into the correct next step.

---

## Step 1 — Update workflow evaluation

Change the evaluator branch for active tasks with `results.md` so it returns `task_review` with the review prompt instead of falling back to `task_execute`.

---

## Step 2 — Align runner behavior

Teach the runner to treat `task_review` as a human/reviewer gate with a review-specific condition and message, parallel to the existing close gate.

---

## Step 3 — Add regression coverage

Update the workflow-state, workflow-run, prompt-show, and integration tests that previously encoded the old `task_execute` behavior after `results.md` exists.

---

## Verification

Run the targeted workflow regression suite covering state evaluation, workflow run, prompt show, and runner integration to confirm the new review routing is consistent across command surfaces.
