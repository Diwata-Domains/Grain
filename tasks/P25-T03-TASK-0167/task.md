# Task: Query and ORM surface hints

## Metadata
- **ID:** TASK-0167
- **Status:** done
- **Phase:** Phase 25 — Database Adapter
- **Backlog:** P25-T03 — Query and ORM surface hints
- **Packet Path:** tasks/P25-T03-TASK-0167/
- **Dependencies:** TASK-0166
- **Primary Adapter:** database_adapter
- **Secondary Adapters:** none

## Objective
Extend `database_adapter` context behavior so query files, ORM models, and repository/data-access layers are included as secondary context when the task objective is clearly about persistence or query work, while preserving the narrower schema/migration-first database bundle for other tasks.

## Why This Task Exists
The first database context slice established schema and migration selection, but recurring database work often targets query behavior and data-access layers rather than only schema files. This task broadens the adapter just enough to cover that objective-driven persistence context without dragging in unrelated application code.

## Scope
- add objective-sensitive query, repository, and data-access prioritization on top of the existing database adapter selection rules
- add focused integration coverage that proves persistence-oriented objectives bring query and repository context ahead of model-adjacent files

## Constraints
- keep the behavior additive inside the existing direct-selection database adapter flow; do not introduce database graph reasoning or runtime database tooling
- preserve the narrower schema/migration-focused bundle when the task objective is not about persistence or queries

## Escalation Conditions
- if persistence-oriented selection requires a deeper database graph or execution layer instead of objective-sensitive file prioritization, stop and narrow the slice before implementation
