# Task: Add ranked next-task advisory signals

## Metadata
- **ID:** TASK-0121
- **Status:** done
- **Phase:** Phase 17 — Ranking and Decision Layer
- **Backlog:** P17-T04 — Add ranked next-task advisory signals
- **Packet Path:** tasks/P17-T04-TASK-0121/
- **Dependencies:** TASK-0118
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add a proposal-only advisory surface for ranked next-task suggestions by attaching ranked current-phase task advice to orchestration scope analysis without changing authoritative `workflow next` or `task next` behavior.

## Why This Task Exists
Q17 resolved the contract gap for Phase 17: ranked next-task suggestions must remain advisory-only. This task implements that contract on an existing proposal surface so task advice becomes available without changing workflow law.

## Scope
- add a task-advice helper that ranks already-eligible phase tasks
- attach ranked task advice to orchestration scope payloads
- keep workflow and task selection commands unchanged

## Constraints
- rank only already-eligible candidate tasks from the active phase
- advisory task ranking must remain separate from authoritative workflow routing

## Escalation Conditions
- implementing task advice requires changing `workflow next` or `task next`
- advisory task signals need a canonical workflow semantics change before they can ship
