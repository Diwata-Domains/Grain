# Task: Add ranking domain model and score breakdown contracts

## Metadata
- **ID:** TASK-0117
- **Status:** done
- **Phase:** Phase 17 — Ranking and Decision Layer
- **Backlog:** P17-T01 — Add ranking domain model and score breakdown contracts
- **Packet Path:** tasks/P17-T01-TASK-0117/
- **Dependencies:** TASK-0109
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Define the ranking-layer domain model: deterministic score components, ranked-candidate result types, default signal weights, and authority scoring helpers that make Phase 17 inspectable before any service logic is added.

## Why This Task Exists
Phase 17 depends on a stable data contract before ranking logic is implemented. The service layer needs explicit breakdown structures so scoring remains explainable and proposal-only instead of becoming a hidden heuristic.

## Scope
- add ranking domain dataclasses and helper constants/functions
- export the new ranking contracts through `grain.domain`
- add focused domain tests for defaults, ordering, and inspectability behavior

## Constraints
- ranking signals must stay deterministic and inspectable
- semantic and authority inputs remain advisory scoring signals, not authority overrides

## Escalation Conditions
- ranking requires a canonical change to authority semantics
- required score signals cannot be expressed cleanly without changing existing Phase 16 contracts
