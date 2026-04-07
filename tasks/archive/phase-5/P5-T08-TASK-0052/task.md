# Task: Improve CLI help and ergonomics

## Metadata
- **ID:** TASK-0052
- **Status:** done
- **Phase:** Phase 5 — Review, Handoff, and Hardening
- **Backlog:** P5-T08
- **Packet Path:** tasks/P5-T08-TASK-0052/
- **Dependencies:** TASK-0051

## Objective
Refine CLI help text and default visibility so common command behavior is clearer at the command line without changing runtime semantics.

## Why This Task Exists
Phase 5 requires user-facing polish. The CLI already works, but help output still hides important defaults and cross-option requirements that users hit in daily operation.

## Scope
- Improve option help/default visibility in existing CLI modules.
- Clarify selector/default behavior for `task validate`.
- Add focused tests that lock the help ergonomics behavior.

## Constraints
- Preserve existing command behavior and exit semantics.
- Keep changes limited to CLI help metadata and related tests.
- Do not modify canonical docs.

## Escalation Conditions
- If a help-text improvement requires changing command behavior, stop and record the mismatch instead of broadening scope.
- If a wording change conflicts with existing test expectations in unrelated modules, resolve narrowly without rewriting unrelated tests.
