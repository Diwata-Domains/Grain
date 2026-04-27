# Context: TASK-0140

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md` — workflow and repo-operation constraints

### Canonical (load for this task)
- `docs/canonical/workflow_spec.md` — packet lifecycle expectations and active-task discipline
- `docs/canonical/cli_spec.md` — command surface expectations for workflow progression

### Working (load if needed)
- `docs/working/backlog.md` — Phase 20 contract for P20-T06
- `docs/working/tooling_notes.md` — source signal for resumed-session packet skipping

### Packet Files
- `tasks/P20-T06-TASK-0140/task.md`
- `tasks/P20-T06-TASK-0140/plan.md`
- `tasks/P20-T06-TASK-0140/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Adapter Rationale:** n/a

## Excluded Context
- Upgrade customization behavior from P20-T05
- Tooling-notes schema normalization from P20-T07
- Any change to workflow engine state transitions beyond prompt/instruction guardrails

## Context Sufficiency Note
The execution prompts, generated agent instructions, runtime guidance, and focused release-surface tests are sufficient to harden packet-first behavior without changing the workflow engine itself.
