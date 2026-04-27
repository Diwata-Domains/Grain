# Task: Add community adapter CI validation and author guidance

## Metadata
- **ID:** TASK-0133
- **Status:** done
- **Phase:** Phase 19 — Community Adapter Registry
- **Backlog:** P19-T05
- **Packet Path:** tasks/P19-T05-TASK-0133/
- **Dependencies:** TASK-0130, TASK-0132
- **Primary Adapter:** docs_adapter
- **Secondary Adapters:** none

## Objective
Add Phase 19 CI and author guidance for the reviewed community adapter registry. The repo must contain one additive workflow that runs the registry-related test coverage and one author-facing guide that explains package contents, validation expectations, maintainer review boundaries, and the separate Community-to-Official promotion boundary.

## Why This Task Exists
The package validator and registry scaffold exist now, but Phase 19 still lacks a visible automation hook and an author guide that explains how to prepare a compliant community adapter submission. This task adds both.

## Scope
- add a GitHub Actions workflow for the reviewed-registry validation/test slice
- add author-facing docs for package structure, validation expectations, and review/promotion boundaries
- add focused tests that the workflow and guide remain aligned with the Phase 19 contract

## Constraints
- keep the workflow additive and scoped to the Phase 19 registry surface
- keep the guidance aligned with the existing package validator, scaffold templates, and local install flow
- do not implement new adapter authoring commands in this task

## Escalation Conditions
- if CI coverage requires a broader test matrix than the current Phase 19 scope justifies, stop and log the gap
- if author guidance conflicts with the reviewed-registry trust contract or promotion boundary, stop and surface the mismatch
