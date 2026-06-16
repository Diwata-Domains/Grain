# Task: CLI entrypoints and workflow-safe mutation commands

## Metadata
- **ID:** TASK-0156
- **Status:** done
- **Phase:** Phase 23 — Writable Office Artifacts
- **Backlog:** P23-T05 — CLI entrypoints and workflow-safe mutation commands
- **Packet Path:** tasks/P23-T05-TASK-0156/
- **Dependencies:** TASK-0155
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add Grain CLI entrypoints for office artifact mutation and inspection that wrap the existing `.docx`, spreadsheet, and office review-bundle services while preserving packet-first workflow discipline and review-first mutation gates.

## Why This Task Exists
Phase 23 now has service-level office write and review machinery, but no operator-facing CLI surface to drive it. This task is the bridge from internal services to real Grain commands without bypassing the workflow or creating hidden state.

## Scope
- add CLI command surfaces for office artifact propose/export flows and review inspection
- surface operation mode, artifact outputs, validator results, and review-bundle summaries through packet-safe commands

## Constraints
- CLI must remain packet-first and file-backed; no direct mutation path may bypass the task packet and review lifecycle
- do not expand into end-to-end smoke docs or TUI-specific wiring yet; this task is limited to CLI/service integration

## Escalation Conditions
- if the CLI surface requires changing the office service contracts or introducing hidden execution state, stop and re-scope before implementation
