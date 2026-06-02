# Task: Spec `apply` graduation criteria for office/Obsidian artifacts

## Metadata
- **ID:** TASK-0193
- **Status:** draft
- **Phase:** Phase 30 — v0.4.0 Planning
- **Backlog:** P30-T04
- **Packet Path:** tasks/P30-T04-TASK-0193/
- **Dependencies:** TASK-0190
- **Primary Adapter:** docs

## Objective
Define the exact conditions under which a writable artifact workflow graduates from `propose`/`export` (Phase 23) to safe in-place `apply`. This is the gating spec that determines which artifact types can have `apply` enabled in v0.4.0 execution phases.

## Why This Task Exists
Phase 23 shipped `propose` and `export-as-new-file` safety modes for `.docx` and spreadsheets. `apply` (in-place mutation) was intentionally deferred: the validation requirements were not clear enough to make it safe. v0.4.0 commits to defining the graduation criteria so at least one artifact type can safely graduate from propose-only to apply-ready.

## Scope
- Define the validation requirements for `apply` graduation:
  - What validators must pass?
  - What review evidence must be present?
  - What rollback mechanism must exist?
  - What is the human confirmation contract?
- Assess each artifact type against the criteria:
  - `.docx` — structural/textual changes
  - Spreadsheets (`.xlsx` / `.csv`) — cell/formula changes
  - Obsidian vault notes — wiki-link and frontmatter changes
  - PDF — remains read-only (explicit non-goal)
- Decide which artifact type(s) graduate in v0.4.0 (at least one, not necessarily all)
- Write `docs/working/apply_graduation.md` — criteria table + per-type assessment

## Deliverable
`docs/working/apply_graduation.md` — graduation criteria and per-type assessment.

## Constraints
- `apply` must always produce a review artifact before changes are considered closed
- `apply` must be recoverable: the original artifact state must be capturable before the apply runs
- Do not graduate an artifact type unless validators are strong enough to catch malformed changes deterministically
