# Task: Database review and validation guidance

## Metadata
- **ID:** TASK-0168
- **Status:** done
- **Phase:** Phase 25 — Database Adapter
- **Backlog:** P25-T04 — Database review and validation guidance
- **Packet Path:** tasks/P25-T04-TASK-0168/
- **Dependencies:** TASK-0165, TASK-0167
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add shipped operator guidance for database review and validation so Grain makes destructive migration risk, rollback expectations, and schema/query drift explicit before database work is considered review-ready.

## Why This Task Exists
The database adapter now has useful context behavior, but safe operator use depends on clear review and validation guidance. This task makes those safety expectations explicit in the shipped docs before the phase closes.

## Scope
- add database-specific review and validation guidance to the shipped operator/runtime docs
- add regression assertions that the shipped guidance mentions the dedicated database adapter and its main review risks

## Constraints
- keep this task in guidance and shipped-doc surfaces; do not introduce new database execution features
- preserve the CLI-first, packet-first, file-backed workflow boundary in all review guidance

## Escalation Conditions
- if the guidance implies live database execution or hidden state rather than review/validation expectations, stop and narrow the language before implementation
