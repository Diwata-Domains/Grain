# Task: Add adapter package validation service

## Metadata
- **ID:** TASK-0130
- **Status:** done
- **Phase:** Phase 19 — Community Adapter Registry
- **Backlog:** P19-T02
- **Packet Path:** tasks/P19-T02-TASK-0130/
- **Dependencies:** TASK-0129
- **Primary Adapter:** docs_adapter
- **Secondary Adapters:** none

## Objective
Implement the validation service for installable community adapter packages. The service must validate one registry-entry directory deterministically, enforce the minimum on-disk package shape for Phase 19, reuse the existing adapter-profile parser where possible, and return structured, inspectable errors before any install step runs.

## Why This Task Exists
Phase 19 now has a hosting/trust contract, but `grain adapter install` cannot be implemented safely until there is one machine-checkable validation surface for registry entries. This task establishes that gate.

## Scope
- define the minimum registry-entry package shape for Phase 19 validation
- implement a validation service and supporting domain result types
- validate package metadata presence plus adapter profile parse/shape compliance
- add focused tests for valid entries and clear failure cases

## Constraints
- do not implement install or fetch behavior in this task
- keep validation local-only and deterministic
- reuse existing adapter-profile parsing instead of inventing a separate profile schema

## Escalation Conditions
- if the minimum package shape cannot be expressed without widening the Q19 contract materially, stop and log the gap
- if validation requires network access or remote registry queries, stop and keep the service filesystem-only
