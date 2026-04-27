# Execute Task Loop

Deprecated convenience alias.
Prefer `prompts/task.execute.md`.

It wraps `prompts/task.execute.md`.

## Purpose

Carry out one scoped task packet at a time.

Prefer:

* continuing the active task if one already exists
* generating the next task packet only when no active task is in progress
* implementing narrowly
* recording results and blockers clearly

## Rules

* do not review your own work
* do not start a second task while one is active
* do not expand scope
* do not modify canonical docs directly
* stop and hand off if review is required

## Default Inputs

Read the current task, relevant working docs, and the task packet before acting.

## Output

Use the same output contract as `prompts/task.execute.md`.
