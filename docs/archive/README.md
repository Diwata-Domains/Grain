# docs/archive

Archived snapshots of working documents at key workflow boundaries.

## phases/

One directory per closed phase, created automatically by `grain phase close`. Each snapshot captures the state of `docs/working/` at the moment the phase was sealed.

```text
docs/archive/phases/
  phase-31/
    backlog.md
    current_focus.md
    open_questions.md
    tooling_notes.md
    metadata.json
```

Phase snapshots begin at Phase 31 — this feature was introduced in v0.3.1. Earlier phases do not have doc snapshots; their task packets are archived under `tasks/archive/`.

## milestones/

Point-in-time snapshots created manually via `grain archive milestone --name <label>`. Used to mark significant releases or decisions.

## Viewing archives

```bash
grain archive list
grain archive show --phase 31
grain archive show --milestone <name>
```
