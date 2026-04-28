# Task: Scaffold Textual app shell

## Metadata
- **ID:** TASK-0146
- **Status:** draft
- **Phase:** Phase 22 — TUI Foundation and Workflow Surfaces
- **Backlog:** P22-T01 — Scaffold Textual app shell
- **Packet Path:** tasks/P22-T01-TASK-0146/
- **Dependencies:** none
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Create the base Textual application shell and TUI structure for Grain so later Phase 22 tasks can add workflow views and action wiring without inventing a second application architecture.

## Why This Task Exists
Phase 22 begins the actual v0.3.0 implementation. The first TUI slice is already locked at the planning level, and the stack choice is settled as Python + Textual. This task is the minimal bootstrapping step that makes the rest of the TUI phase buildable.

## Scope
- create the TUI module and app bootstrap
- establish the base shell layout and view boundaries
- keep service access thin and reuse existing Grain logic where possible

## Constraints
- no hidden workflow state
- no duplicate workflow engine or JS/TS frontend runtime

## Escalation Conditions
- if the TUI bootstrap requires changing the locked stack or app boundary, stop and re-scope
