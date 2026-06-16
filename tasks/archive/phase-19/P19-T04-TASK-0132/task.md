# Task: Scaffold community adapter registry artifacts

## Metadata
- **ID:** TASK-0132
- **Status:** done
- **Phase:** Phase 19 — Community Adapter Registry
- **Backlog:** P19-T04
- **Packet Path:** tasks/P19-T04-TASK-0132/
- **Dependencies:** TASK-0129
- **Primary Adapter:** docs_adapter
- **Secondary Adapters:** none

## Objective
Create the repo-side scaffold for the Phase 19 community adapter registry. The scaffold must define a submission layout, package metadata template, adapter profile template, contribution guidance, and review metadata/checklist artifacts that match the explicit local validation/install flow established by the earlier Phase 19 tasks.

## Why This Task Exists
Phase 19 now has a trust contract, package validation, and a local install flow, but there is still no concrete scaffold showing how a community adapter submission should be shaped in the reviewed registry repo. This task adds that missing repository-facing contract.

## Scope
- add a `contrib/community_adapter_registry/` scaffold with submission guidance and templates
- define package metadata, adapter profile, and review metadata template files
- add a review checklist artifact aligned with the reviewed-registry trust contract
- add focused tests for scaffold presence and template validity

## Constraints
- keep the scaffold declarative and repo-visible; do not introduce automation or CI in this task
- keep package templates aligned with the existing adapter profile parser and Phase 19 package validator
- do not define remote fetch or promotion automation in the scaffold

## Escalation Conditions
- if the scaffold requires a richer registry governance model than Q19 resolved, stop and log the gap instead of inventing policy
- if template requirements diverge from the existing package validator or install flow, stop and surface the mismatch
