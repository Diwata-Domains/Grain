# Close Task Loop

Deprecated convenience alias.
Prefer `prompts/task.close.md`.

It wraps `prompts/task.close.md`.

## Purpose

Finalize one reviewed task packet so the workflow can move on cleanly.

## Rules

* only close tasks that are already review-ready
* do not start the next task
* do not expand scope
* do not modify canonical docs directly
* stop if review is incomplete

## Default Inputs

Read the active task packet, `results.md`, and `handoff.md` before finalizing closure.

## Output

Use the same output contract as `prompts/task.close.md`.
