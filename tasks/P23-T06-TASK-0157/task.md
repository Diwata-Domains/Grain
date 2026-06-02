# Task: Office artifact tests, smoke flow, and docs

## Metadata
- **ID:** TASK-0157
- **Status:** done
- **Phase:** Phase 23 — Writable Office Artifacts
- **Backlog:** P23-T06 — Office artifact tests, smoke flow, and docs
- **Packet Path:** tasks/P23-T06-TASK-0157/
- **Dependencies:** TASK-0156
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add end-to-end tests, smoke flow coverage, and operator-facing documentation for the first office-artifact slice so `.docx` and spreadsheet commands, validator gating, and persisted review-bundle behavior are verified as one coherent workflow.

## Why This Task Exists
Phase 23 now has shared write contracts, artifact-specific write services, a shared office review-bundle layer, and the first CLI surface. This final task hardens that slice by proving it works as a packet-first operator flow and documenting how to use it without bypassing review.

## Scope
- add end-to-end or smoke-flow coverage across office CLI commands and review inspection
- document the first office-artifact workflow in repo-facing docs and runtime guidance

## Constraints
- keep the workflow packet-first and file-backed; tests and docs must reflect review-first mutation gates
- do not expand into new write capabilities beyond the current `.docx` and spreadsheet propose/export surface

## Escalation Conditions
- if the smoke flow reveals that the current CLI surface cannot be tested or documented without changing the workflow model or enabling in-place `apply`, stop and re-scope before implementation
