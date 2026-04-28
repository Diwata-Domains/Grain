# Task: Define non-code review and safety model

## Metadata
- **ID:** TASK-0143
- **Status:** draft
- **Mode:** simple
- **Phase:** Phase 21 — v0.3.0 Planning and Operator Surface Definition
- **Backlog:** P21-T06 — Define reviewable diffs, validators, and safety modes for non-code artifacts
- **Packet Path:** tasks/P21-T06-TASK-0143/
- **Dependencies:** TASK-0143 depends conceptually on the locked office workflow and Obsidian direction; no packet dependency
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Lock the review and safety model for non-code artifact updates so later `.docx`, spreadsheet, and Obsidian implementation work has a clear standard for review bundles, validators, and safety-mode escalation.

## Why This Task Exists
v0.3.0 includes writable office artifacts and Obsidian workflows. Without an explicit review/safety model, implementation could drift into opaque binary mutation or under-specified validation. This planning task defines the minimum review artifacts and fallback rules before implementation starts.

## Scope
- define the minimum review bundle for non-code writes
- define validator families for `.docx`, spreadsheet, and Obsidian workflows
- define when Grain must refuse or downgrade `apply`

## Constraints
- remain local-first and file-backed
- do not permit opaque binary mutation without a human-readable review surface

## Escalation Conditions
- if the proposed model requires hidden state or trust-without-review behavior, stop and re-scope
