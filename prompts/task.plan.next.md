# Task Planning Loop

Use this to select or split the next task before packet generation.

This is the preferred stable task-planning entrypoint.

It wraps `prompts/tasks.plan.next.md`.

Metadata:
- scope: task
- stage: plan_next
- recommended_model_class: frontier_model
- escalation_model_class: reviewer_model

## Purpose

Keep the backlog executable by selecting the next concrete task or splitting a too-broad task before packetization.

## Output

Use the same output contract as `prompts/tasks.plan.next.md`.
