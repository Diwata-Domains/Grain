# Task: Expand forge init scaffolding to write baseline seed files from templates

## Metadata
- **ID:** TASK-0063
- **Status:** done
- **Phase:** Phase 7 — New-Project Onboarding Flow
- **Backlog:** P7-T03
- **Packet Path:** tasks/P7-T03-TASK-0063/
- **Dependencies:** TASK-0061
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Update `forge init` so it creates missing baseline runtime docs and task template files from seed templates, while preserving additive-only behavior and dry-run safety.

## Why This Task Exists
Phase 7 onboarding requires `forge init` to produce usable starter artifacts instead of only creating directories. Without seeded runtime and task-template files, initialized repos are incomplete for normal workflow usage.

## Scope
- Expand init service to seed runtime and task-template files when missing.
- Preserve skip-existing behavior and add force-aware update reporting for seed files.
- Keep dry-run behavior non-mutating while still reporting planned create/update actions.
- Add tests proving file skip behavior and dry-run correctness.

## Constraints
- Do not overwrite protected files silently.
- Keep initialization additive by default.
- Keep changes limited to init scaffolding and tests.

## Escalation Conditions
- If required seed templates are unavailable at runtime, report blocked files rather than guessing file content.
- If implementation requires canonical contract changes, log a change proposal instead of editing canonical docs directly.

## Model Selection Rationale
`frontier_model` is appropriate because this task touches CLI/service behavior and needs careful cross-file coordination to preserve initialization and dry-run contracts.
