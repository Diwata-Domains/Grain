# Context: TASK-0227

## Required Documents

### Runtime (always load)
- `docs/runtime/PROJECT_RULES.md`

### Canonical (load for this task)
- `docs/canonical/recipe_engine_spec.md` — §3.1 outcome vocabulary the reducer re-expresses
- `../../Diwata-Infra/docs/canonical/capability_register.md` — Workflow capability is Grain's;
  Diwa consumes the port, never re-implements the semantics

### Working (load if needed)
- `docs/working/backlog.md` — P37-T14 entry (the authoritative acceptance criteria)
- `docs/superpowers/specs/2026-07-09-entity-boundaries-design.md` — §5.1 contract address,
  §11 types-not-code rule (why the reducer lives in engine/, not contracts/)

### Source anchors (the attested semantics being distilled)
- `src/grain/services/recipe_service.py:71-80` — VALID_NEXT_OUTCOMES
- `src/grain/services/recipe_service.py:340-349` — completion = artifact present AND non-empty
- `src/grain/services/recipe_service.py:569-581` — failed step/run never auto-completes
- `src/grain/services/recipe_service.py:612-686` — _complete_and_advance: done → gate/advance/complete
- `src/grain/services/recipe_service.py:716-749` — reject_gate: artifact unlink + re-arm (the
  delete that becomes the DiscardArtifact effect)
- `src/grain/contracts/workflow.py` — the vocabulary (re-export of grain_contracts.workflow)

### Packet Files
- `tasks/P37-T14-TASK-0227/task.md`
- `tasks/P37-T14-TASK-0227/plan.md`
- `tasks/P37-T14-TASK-0227/deliverable_spec.md`

## Adapter Context
- **Primary Adapter:** none
- **Secondary Adapters:** none
- **Adapter Rationale:** n/a — pure in-repo Python module, no external surface

## Excluded Context
- `docs/working/engine_contract_spec.md` — Phase 35 envelope/MCP surface; orthogonal to the kernel
- `services/recipe_store.py` layout details — that is P37-T15 (FilesystemRunStore), not this packet

## Context Sufficiency Note
The backlog entry, the five recipe_service source anchors, and the sealed contracts module fully
determine the reducer's semantics and the port's shape; no other context is needed.
