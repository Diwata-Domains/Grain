# Task: `database_adapter` profile and contract scaffold

## Metadata
- **ID:** TASK-0165
- **Status:** done
- **Phase:** Phase 25 — Database Adapter
- **Backlog:** P25-T01 — `database_adapter` profile and contract scaffold
- **Packet Path:** tasks/P25-T01-TASK-0165/
- **Dependencies:** Phase 24
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Create the first dedicated `database_adapter` profile and shipped contract surface so Grain can model schema, migration, query, and ORM-oriented work as a first-class adapter instead of leaving database tasks implied inside generic code context.

## Why This Task Exists
Phase 25 exists because database work is a recurring full-stack workflow for Grain users and needs explicit context, review, and validation guidance. This first task establishes the contract boundary before any schema-selection or query-surface behavior is added.

## Scope
- add the dedicated `database_adapter` profile to the runtime adapter docs and shipped runtime copy
- add focused parser assertions that prove the new adapter contract is present and structurally correct

## Constraints
- keep this task structural; do not broaden into schema/migration context-selection behavior yet
- preserve the existing packet-first, file-backed workflow and avoid inventing database runtime tooling or hidden state in the scaffold task

## Escalation Conditions
- if the scaffold requires new adapter lifecycle semantics or broader query/schema behavior before the contract exists, stop and narrow the slice before implementation
