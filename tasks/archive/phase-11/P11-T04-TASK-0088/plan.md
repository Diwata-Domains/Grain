# Plan: TASK-0088

## Approach

Extend the README installation section with concrete verification commands and a concise troubleshooting matrix for common install/runtime issues across major operating systems.

---

## Step 1 — Add Verification Instructions

Document `grain --version` and `grain init --help` checks with expected output cues.

---

## Step 2 — Add Troubleshooting Guidance

Document PATH repair steps, Python version mismatch checks, and venv/tool conflict resolution steps with macOS/Linux and Windows basics.

---

## Step 3 — Validate and Finalize Artifacts

Run docs/task/full test validation and finalize packet/working docs for review.

---

## Verification

- `.venv/bin/grain --version`
- `.venv/bin/grain init --help`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0088`
- `.venv/bin/pytest -q`
