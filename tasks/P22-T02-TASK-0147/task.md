# Task: Workflow dashboard and status summary

## Metadata
- **ID:** TASK-0147
- **Status:** review
- **Phase:** Phase 22 — TUI Foundation and Workflow Surfaces
- **Backlog:** P22-T02 — Workflow dashboard and status summary
- **Packet Path:** tasks/P22-T02-TASK-0147/
- **Dependencies:** TASK-0146
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Turn the initial Textual shell into a real workflow dashboard that surfaces the active phase, current task pointer, next legal action, prompt recommendation, and queue or blocker status in one operator-friendly screen.

## Why This Task Exists
The first TUI scaffold proved the CLI and Textual boundary. Phase 22 now needs the first actual operator view so the TUI becomes useful for workflow navigation before later tasks add deeper inspectors and action launchers.

## Scope
- extend the TUI snapshot model to include current-task, prompt, and candidate-task status
- replace placeholder panels with real workflow dashboard sections
- add focused tests for dashboard snapshot and rendered summary content

## Constraints
- keep the dashboard read-only and derived from existing Grain services or working-doc state
- do not add packet inspection depth or workflow mutation controls in this task

## Escalation Conditions
- if the dashboard requires inventing new workflow state or bypassing existing service contracts, stop and re-scope
