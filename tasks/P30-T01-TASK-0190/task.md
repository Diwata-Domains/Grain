# Task: Lock v0.4.0 milestone contract

## Metadata
- **ID:** TASK-0190
- **Status:** draft
- **Phase:** Phase 30 — v0.4.0 Planning
- **Backlog:** P30-T01
- **Packet Path:** tasks/P30-T01-TASK-0190/
- **Dependencies:** Phase 29 close
- **Primary Adapter:** docs

## Objective
Write the formal v0.4.0 milestone contract — the decisions document that locks theme, core deliverables, execution phase order, and non-goals before any implementation phases begin. This is the Phase 30 anchor task; all other planning tasks depend on it being done first.

## Why This Task Exists
Phase 21 (v0.3.0 planning) proved that a planning phase needs a locked milestone contract before breadth decisions are made. Without it, planning phases drift into speculative feature design. The v0.4.0 direction is already written in `docs/working/current_focus.md §v0.4.0 Direction` — this task formalizes it as the milestone contract and validates or adjusts the candidate deliverables list.

## Scope
- Read `current_focus.md §v0.4.0 Direction` and the candidate deliverables list
- Resolve or flag the three open questions for v0.4.0:
  1. What is the unit of reuse in `grain recipe`? (prompt, packet template, workflow slice, or all three)
  2. What serialization format does the Grain ↔ Assay ↔ toolkit contract use?
  3. What validation threshold must a change writer reach before `propose` → `apply` is safe?
- Write `docs/working/v0.4.0_contract.md` with: theme, core deliverables, candidate deliverables, non-goals, execution phase order sketch
- Update `docs/working/current_focus.md` Phase 30 status section to "contract locked"

## Deliverable
`docs/working/v0.4.0_contract.md` — formal milestone contract.

## Constraints
- Decisions must come from the operator, not from agent inference where the question is genuinely open
- Non-goals must be explicit — v0.4.0 is *not* the Sentinel phase, the database-expansion phase, or the cloud phase
