# Review Task Loop

Deprecated convenience alias.
Prefer `prompts/task.review.md`.

It wraps `prompts/task.review.md`.

## Purpose

Review the active task packet and its review bundle.

## Rules

* focus on findings first
* call out required fixes before optional improvements
* do not expand scope
* do not modify canonical docs directly
* do not approve missing review-bundle fields silently

## Default Inputs

Read the active task packet, `results.md`, and `handoff.md` before judging the task.

## Output

Use the same output contract as `prompts/task.review.md`.
