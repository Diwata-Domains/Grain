# Task: Add phase 19 integration tests

## Metadata
- **ID:** TASK-0134
- **Status:** done
- **Phase:** Phase 19 — Community Adapter Registry
- **Backlog:** P19-T06
- **Packet Path:** tasks/P19-T06-TASK-0134/
- **Dependencies:** TASK-0130, TASK-0131, TASK-0132, TASK-0133
- **Primary Adapter:** docs_adapter
- **Secondary Adapters:** none

## Objective
Add focused end-to-end coverage for the completed Phase 19 community adapter registry contract. The integration tests must exercise a reviewed-registry style submission from package validation through install, and verify the scaffold, CI workflow, and author guidance stay aligned to the same package/install contract.

## Why This Task Exists
Phase 19 implementation slices are individually covered, but the phase still needs one integrated test layer that proves the registry scaffold, package validator, install flow, and CI/doc artifacts agree on one contract.

## Scope
- add one focused Phase 19 integration test module
- cover reviewed-registry submission validation plus install by handle
- cover consistency between scaffold templates, author guide, and CI workflow references

## Constraints
- keep the integration coverage local-only and deterministic
- reuse the existing package validator and install command instead of duplicating validation logic
- do not add remote registry or network assumptions

## Escalation Conditions
- if the integrated artifacts disagree on package shape or install semantics, stop and log the mismatch instead of masking it in tests
- if Phase 19 requires broader cross-platform CI coverage to be credible, stop and surface the missing scope
