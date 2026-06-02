# Task: Implement `grain verify submit` bridge command

## Metadata
- **ID:** TASK-0179
- **Status:** done
- **Phase:** Phase 28 — Assay Verification Integration
- **Backlog:** P28-T01
- **Packet Path:** tasks/P28-T01-TASK-0179/
- **Dependencies:** none
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none

## Objective
Implement the first real Assay verification bridge command so Grain can create a packet-local verification request, assign a stable `verification_id`, and mark the packet review bundle as pending external verification.

## Why This Task Exists
Phase 28 starts by making the verification bridge tangible without introducing hidden services. The submit command creates the packet-local artifact that later status and ingest commands will build on.

## Scope
- Add a new `grain verify submit` CLI surface.
- Persist a packet-local `verification_request.json` artifact.
- Update `results.md` verification state from `not_run` to `pending`.

## Constraints
- Keep all verification state packet-local and file-backed.
- Support only the explicit `assay` provider in this first bridge slice.

## Escalation Conditions
- Stop if implementing submit requires network calls, Assay internals, or cross-packet state.
