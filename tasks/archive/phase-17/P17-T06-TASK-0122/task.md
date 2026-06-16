# Task: Add Phase 17 integration tests

## Metadata
- **ID:** TASK-0122
- **Status:** done
- **Phase:** Phase 17 — Ranking and Decision Layer
- **Backlog:** P17-T06 — Phase 17 integration tests
- **Packet Path:** tasks/P17-T06-TASK-0122/
- **Dependencies:** TASK-0119, TASK-0121, TASK-0120
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add integration coverage for the full Phase 17 ranking layer across context selection, ranked next-task advice, and ranked impacted-file advice so the new scoring surfaces are validated together.

## Why This Task Exists
Phase 17 is only complete once the ranking pieces are verified together under real repo/config conditions. This task proves the ranking layer is coherent across its production consumers.

## Scope
- add Phase 17 integration coverage for ranked context selection
- add integration coverage for advisory task suggestions and impacted-file ranking
- keep the suite deterministic with fake provider builders

## Constraints
- tests must remain deterministic and avoid live provider dependencies
- integration coverage must preserve the advisory-only boundary for task and impact ranking

## Escalation Conditions
- integration behavior requires a canonical change to the ranking/advisory contract
- provider seams are insufficient to test the ranking layer deterministically
