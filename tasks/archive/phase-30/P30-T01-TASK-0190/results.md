# Results — TASK-0190

## Status
done — 2026-06-11

## Deliverable
`docs/working/v0.4.0_contract.md` — written and locked.

## What Was Decided

**4 open questions resolved:**

1. **Recipe unit of reuse:** Workflow slice (execute → review → close + prompt template + packet scaffold). Individual templates are components, not recipes.
2. **Toolkit contract format:** YAML for authoring/storage, JSON for `--format json` CLI output. Consistent with existing Grain manifest conventions.
3. **Apply validation threshold:** 100% required validators pass + at least one non-empty change summary + zero unacknowledged residual risk flags. `advisory_only` validators downgrade to warnings.
4. **`grain suggest` quality bar:** Suggestions must cite a traceable input signal. Pick-up type: `ready` task in active/next phase, not current task. New-task type: traceable signal + concrete objective + no near-duplicate.

**Core deliverables locked (6):**
- 2.1 Agent enforcement hardening (T08)
- 2.2 Scaffold seeding fixes (T06)
- 2.3 `grain suggest` (T07)
- 2.4 Toolkit contract + workspace model (T02)
- 2.5 `grain recipe` execution (T03)
- 2.6 Apply graduation (T04)

**Candidate deliverables (2):** Dev/runtime alignment (T05), upstream feedback loop (T09).

**DX friction mapped to Phase 31:** 5 active defects (workflow routing bug, packet ID reuse, phase close flag missing, enforcement gaps, scaffold seeding gaps) — all fixed before feature phases.

**Execution phase order:** Phase 31 (DX hardening) → 32 (suggest) → 33 (toolkit contract) → 34 (recipe) → 35 (apply graduation) → 36–37 (candidate).

## Files Changed
- `docs/working/v0.4.0_contract.md` — created (milestone contract)
- `docs/working/current_focus.md` — Phase 30 status updated to "CONTRACT LOCKED"
- `tasks/P30-T01-TASK-0190/task.md` — status set to done
