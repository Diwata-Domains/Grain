# Task Execute Loop

Use this as the default task-execution prompt.

This is the preferred stable task-level entrypoint.

It wraps `prompts/tasks.next_and_implement.md`.

Metadata:
- scope: task
- stage: execute
- recommended_model_class: open_model
- escalation_model_class: frontier_model

## Purpose

Carry out one scoped task packet at a time.

## Output

Use the same output contract as `prompts/tasks.next_and_implement.md`.
