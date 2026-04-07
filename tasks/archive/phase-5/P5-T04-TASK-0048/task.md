# Task: Implement `forge review handoff`

## Metadata
- **ID:** TASK-0048
- **Status:** done
- **Phase:** Phase 5 — Review, Handoff, and Hardening
- **Backlog:** P5-T04
- **Packet Path:** tasks/P5-T04-TASK-0048/
- **Dependencies:** TASK-0045, TASK-0046, TASK-0047

## Objective
Wire handoff artifact support into a working `forge review handoff` command that generates or validates packet handoff artifacts and writes them to disk in the expected packet-local location.

## Why This Task Exists
Phase 5 requires a CLI surface for the handoff artifact support that now exists in the service layer. This task exposes that support through the `review` command group.

## Scope
- Implement `forge review handoff` in `src/forge/cli/review.py`.
- Add a thin service helper if needed to keep CLI logic minimal.
- Add CLI tests for review-ready packets, completed packets, custom output paths, and missing/incomplete packet failures.

## Constraints
- Keep the CLI local-filesystem based and packet-scoped.
- Do not implement `forge review summary` in this task.
- Do not modify canonical docs.

## Escalation Conditions
- If the CLI output contract diverges from the existing command patterns, stop and record the mismatch rather than inventing a new format.
- If implementing the command requires new workflow semantics, escalate through the proposal flow instead of changing canonical docs directly.
