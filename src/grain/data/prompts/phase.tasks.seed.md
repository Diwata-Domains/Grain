# Phase Task Seeding Loop

Use this when a new phase exists but its initial backlog slice has not been generated yet.

This is the preferred stable entrypoint for phase-start task generation.

It wraps `prompts/phase.tasks.generate.md`.

Metadata:
- scope: phase
- stage: seed_tasks
- recommended_model_class: frontier_model
- escalation_model_class: reviewer_model

## Purpose

Turn a newly planned phase into a concrete backlog slice before task execution begins.

## Output

Use the same output contract as `prompts/phase.tasks.generate.md`.
