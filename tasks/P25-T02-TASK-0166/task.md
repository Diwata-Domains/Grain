# Task: Schema and migration context selection

## Metadata
- **ID:** TASK-0166
- **Status:** done
- **Phase:** Phase 25 — Database Adapter
- **Backlog:** P25-T02 — Schema and migration context selection
- **Packet Path:** tasks/P25-T02-TASK-0166/
- **Dependencies:** TASK-0165
- **Primary Adapter:** database_adapter
- **Secondary Adapters:** none

## Objective
Implement the first database-specific context behavior so `database_adapter` can select and prioritize schema files, migration directories, and nearby model artifacts ahead of unrelated application code while staying inside the existing file-backed context pipeline.

## Why This Task Exists
The database adapter scaffold exists, but it is not useful yet without a first real context behavior. This task turns the contract into a bounded selection rule so database work can load the right files before broader query and ORM hints land.

## Scope
- add the first `database_adapter` context-selection behavior for schema, migration, and model artifacts
- add focused integration coverage that proves unrelated application code is excluded while the database-relevant files are selected and ordered correctly

## Constraints
- keep the behavior additive inside the existing adapter selection pipeline; do not introduce a new schema index, background scanner, or database runtime tooling
- keep query-file and broader ORM-repository behavior scoped out until `P25-T03`

## Escalation Conditions
- if the slice requires a general-purpose database graph engine or broader persistence reasoning before schema/migration selection is stable, stop and re-scope before implementation
