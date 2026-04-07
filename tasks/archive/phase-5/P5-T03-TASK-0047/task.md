# Task: Implement handoff artifact support

## Metadata
- **ID:** TASK-0047
- **Status:** done
- **Phase:** Phase 5 — Review, Handoff, and Hardening
- **Backlog:** P5-T03
- **Packet Path:** tasks/P5-T03-TASK-0047/
- **Dependencies:** TASK-0045, TASK-0046

## Objective
Implement service-level support for generating and validating packet handoff artifacts so review-ready and completed packets can produce a structured handoff summary without CLI wiring yet.

## Why This Task Exists
Phase 5 needs a reusable handoff artifact surface before `forge review handoff` is exposed. This task creates the underlying artifact generation and validation logic for task packets.

## Scope
- Add `src/forge/services/handoff_service.py` with handoff artifact generation, validation, and markdown rendering helpers.
- Add focused tests for review-ready, done, incomplete, and missing-packet cases.
- Keep the work packet-scoped and filesystem-local.

## Constraints
- Do not implement `forge review handoff` or `forge review summary` CLI wiring in this task.
- Do not modify canonical docs.
- Handoff support must work for review-ready or completed packets only.

## Escalation Conditions
- If the handoff artifact structure cannot be derived from existing packet artifacts without inventing new workflow semantics, stop and record the ambiguity rather than improvising.
- If the task requires changing canonical closure rules, escalate through the proposal flow instead of editing canonical docs directly.
