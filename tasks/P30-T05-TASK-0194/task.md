# Task: Spec source-tree / version-alignment diagnostics

## Metadata
- **ID:** TASK-0194
- **Status:** draft
- **Phase:** Phase 30 — v0.4.0 Planning
- **Backlog:** P30-T05
- **Packet Path:** tasks/P30-T05-TASK-0194/
- **Dependencies:** TASK-0190
- **Primary Adapter:** docs

## Objective
Design a diagnostic surface that surfaces the gap between the active Grain source tree (what the developer is editing) and the installed CLI binary (what is actually running). This solves real friction in active Grain development: changes to the repo don't automatically appear in the running CLI, and the mismatch is silent.

## Why This Task Exists
During active development of Grain itself, the installed CLI binary (`grain`) often lags the source code being edited. This creates confusing behavior: a developer edits `src/grain/services/workflow_service.py`, runs `grain workflow next`, and the old behavior runs instead. There is no current signal that this gap exists. `current_focus.md` explicitly calls this out as v0.4.0 development friction to eliminate.

## Scope
- Define what "dev/runtime alignment" means for a Python CLI installed via `pip install -e .` or `uv tool install`
- Design the diagnostic: how does Grain detect a drift between the installed binary and the repo source?
  - Option A: version hash comparison (installed wheel hash vs. repo HEAD hash)
  - Option B: source file mtime comparison against installed package
  - Option C: `grain --version` surface that includes a "dev mode" flag when running from editable install
- Decide which option to implement in v0.4.0 (or a combination)
- Spec `grain doctor` or an extension to `grain --version` that surfaces alignment state
- Write `docs/working/dev_runtime_alignment.md` — design decision + spec for the diagnostic surface

## Deliverable
`docs/working/dev_runtime_alignment.md` — diagnostic design and spec.

## Constraints
- The diagnostic must not require a network call — local-only check
- The check must be optional and not add latency to normal CLI invocations
- Must not break when Grain is installed globally via `uv tool install` (non-editable mode)
