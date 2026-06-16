# Task: Spreadsheet propose and export workflow

## Metadata
- **ID:** TASK-0154
- **Status:** done
- **Phase:** Phase 23 — Writable Office Artifacts
- **Backlog:** P23-T03 — Spreadsheet propose and export workflow
- **Packet Path:** tasks/P23-T03-TASK-0154/
- **Dependencies:** TASK-0152
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Implement the first spreadsheet mutation path for Grain with safe `propose` and `export-as-new-file` behavior, using the shared office-write contracts from `TASK-0152` and producing touched-sheet, touched-range, and formula-aware summary output suitable for review.

## Why This Task Exists
Phase 23 needs the second artifact-specific office workflow so the shared contract from `TASK-0152` is proven across both planned artifact types. After the `.docx` slice, spreadsheets are the next highest-value office surface and need the same explicit, reviewable mutation posture.

## Scope
- implement spreadsheet load, update, and save behavior for `propose` and `export-as-new-file`
- emit touched-sheet, touched-range, and formula-aware summaries for later review-bundle wiring

## Constraints
- use the shared office-write safety contract from `TASK-0152` rather than inventing spreadsheet-specific mode rules
- keep this task limited to `propose` and `export-as-new-file`; in-place `apply` remains deferred until validation and review surfaces are ready

## Escalation Conditions
- if spreadsheet mutation requires changing the shared contract from `TASK-0152`, stop and re-scope before implementation
