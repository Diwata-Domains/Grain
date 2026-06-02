# Task: Shared office write contracts and safety modes

## Metadata
- **ID:** TASK-0152
- **Status:** done
- **Mode:** simple
- **Phase:** Phase 23 — Writable Office Artifacts
- **Backlog:** P23-T01 — Shared office write contracts and safety modes
- **Packet Path:** tasks/P23-T01-TASK-0152/
- **Dependencies:** none
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Define the shared Grain domain and service contracts for writable office artifacts so `.docx` and spreadsheet mutation flows can reuse the same operation modes, review-bundle model, validator result shape, and artifact-operation metadata.

## Why This Task Exists
Phase 23 starts the first non-code mutation slice in v0.3.0. Before Grain can safely write `.docx` documents or spreadsheets, it needs one shared contract for `propose`, `apply`, and `export-as-new-file` behavior plus a consistent review and validation model that later tasks can build on.

## Scope
- define shared office write operation modes and metadata
- define the review-bundle and validator result contracts reused by `.docx` and spreadsheet flows

## Constraints
- `propose` remains the default mutation posture
- the contract must stay packet-first and review-first so later CLI surfaces do not bypass Grain workflow gates

## Escalation Conditions
- if the shared contract implies changing the locked Phase 23 safety modes or review model, stop and re-scope before implementation
