# Task: Backlog, task, and packet inspector views

## Metadata
- **ID:** TASK-0148
- **Status:** review
- **Phase:** Phase 22 — TUI Foundation and Workflow Surfaces
- **Backlog:** P22-T03 — Backlog, task, and packet inspector views
- **Packet Path:** tasks/P22-T03-TASK-0148/
- **Dependencies:** TASK-0146, TASK-0147
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add read-only backlog, task, and packet inspector views to the Textual shell so operators can see current phase tasks, the active packet path, and packet artifact presence without leaving the TUI.

## Why This Task Exists
The dashboard now shows top-level workflow status, but Phase 22 still lacks the first deeper inspection surfaces. This task makes the TUI operationally useful by exposing phase backlog state and packet artifact visibility before action launchers arrive.

## Scope
- add snapshot support for current-phase backlog tasks and active packet artifact presence
- render inspector panels for backlog, task pointer, and packet files inside the TUI
- add focused tests for inspector snapshot data and rendered inspector sections

## Constraints
- keep the inspector surfaces read-only and derived from existing docs/packet files
- do not add execute/review/close controls or editable packet operations in this task

## Escalation Conditions
- if inspector views require hidden indexing state or broad packet parsing beyond the current task path, stop and re-scope
