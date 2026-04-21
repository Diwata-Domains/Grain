# Task: Build deterministic ranking service

## Metadata
- **ID:** TASK-0118
- **Status:** done
- **Phase:** Phase 17 — Ranking and Decision Layer
- **Backlog:** P17-T02 — Build deterministic ranking service
- **Packet Path:** tasks/P17-T02-TASK-0118/
- **Dependencies:** TASK-0117, TASK-0114
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Implement the deterministic ranking service that turns graph distance, semantic similarity, authority level, and packet-local priority into stable weighted scores with full score breakdowns for each candidate.

## Why This Task Exists
Phase 17 needs one shared ranking engine before context selection and advisory outputs can consume ranked signals consistently. Without a central service, every caller would reimplement opaque heuristics.

## Scope
- add ranking-service input shape and weighted scoring logic
- normalize graph-distance and advisory signals into inspectable component scores
- add focused tests for ordering, tie-breaking, and score clamping

## Constraints
- ranking output must remain deterministic and explainable
- service output must use the explicit ranking contracts defined in P17-T01

## Escalation Conditions
- ranking needs signals that Phase 17 contracts cannot represent cleanly
- signal weighting requires a canonical policy decision before implementation can proceed
