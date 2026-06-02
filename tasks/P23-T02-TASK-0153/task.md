# Task: .docx propose and export workflow

## Metadata
- **ID:** TASK-0153
- **Status:** done
- **Phase:** Phase 23 — Writable Office Artifacts
- **Backlog:** P23-T02 — `.docx` propose and export workflow
- **Packet Path:** tasks/P23-T02-TASK-0153/
- **Dependencies:** TASK-0152
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Implement the first `.docx` mutation path for Grain with safe `propose` and `export-as-new-file` behavior, using the shared office-write contracts from `TASK-0152` and producing a structural change summary suitable for review.

## Why This Task Exists
Phase 23 needs the first real artifact-specific write workflow. `.docx` is the narrowest office artifact to start with because the repo already has document extraction support; this task adds the corresponding safe write/update surface without opening in-place mutation yet.

## Scope
- implement `.docx` load, update, and save behavior for `propose` and `export-as-new-file`
- emit a structural change summary that later review-bundle plumbing can consume

## Constraints
- use the shared office-write safety contract from `TASK-0152` rather than inventing docx-specific mode rules
- keep this task limited to `propose` and `export-as-new-file`; in-place `apply` remains deferred until validation and review surfaces are ready

## Escalation Conditions
- if `.docx` mutation requires changing the shared contract from `TASK-0152`, stop and re-scope before implementation
