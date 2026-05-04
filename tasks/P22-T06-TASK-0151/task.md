# Task: TUI tests, smoke flow, and docs

## Metadata
- **ID:** TASK-0151
- **Status:** review
- **Phase:** Phase 22 — TUI Foundation and Workflow Surfaces
- **Backlog:** P22-T06 — TUI tests, smoke flow, and docs
- **Packet Path:** tasks/P22-T06-TASK-0151/
- **Dependencies:** TASK-0146, TASK-0147, TASK-0148, TASK-0149, TASK-0150
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add the Phase 22 closeout coverage and operator docs: one realistic TUI launcher smoke flow plus user-facing README guidance for the current `grain tui` surface and its explicit deferrals.

## Why This Task Exists
The functional TUI slices are implemented, but Phase 22 still needs a stronger confidence pass and operator-facing documentation before the phase can be considered complete.

## Scope
- add one launcher-oriented TUI smoke flow over a realistic packet lifecycle
- document the current TUI surface and explicit deferrals in the README
- keep the verification slice focused on the TUI and the workflow services it wraps

## Constraints
- smoke coverage should exercise real launcher helpers without requiring a live interactive terminal session
- docs must describe the current TUI honestly and avoid implying deeper editing surfaces that do not exist yet

## Escalation Conditions
- if meaningful smoke coverage requires a brittle fully interactive terminal harness, stop and re-scope
