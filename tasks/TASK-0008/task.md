# Task: Add exit code and error handling conventions

## Metadata
- **ID:** TASK-0008
- **Status:** done
- **Phase:** Phase 1 — Repository Foundation and Core CLI
- **Dependencies:** TASK-0002 (CLI entrypoint), TASK-0007 (output formatter)

## Objective
Implement shared error types and exit code mapping aligned with `cli_spec.md` Section 5. Commands should raise typed exceptions that the CLI layer catches and maps to the correct exit code and user-facing message. This replaces ad-hoc error handling with a consistent, inspectable convention.

## Why This Task Exists
`implementation_plan.md` Phase 1 lists "exit code and error handling conventions" as a major deliverable. `cli_spec.md` Section 4.6 requires commands to fail clearly. Without shared error types, each command invents its own failure path, making the exit code contract impossible to enforce consistently across the growing command surface.

## Scope
- Define shared exception classes in `src/ai_build_toolkit/domain/`
- Define exit code mapping aligned with `cli_spec.md` Section 5
- Add a top-level error handler in the CLI that catches domain exceptions and exits with the correct code and message
- Update `abt init` to raise typed exceptions rather than printing and returning

## Constraints
- Exit codes must exactly match `cli_spec.md` Section 5
- Error types must live in `domain/` — they are domain-level error categories, not CLI concerns (`architecture.md` Section 6.3)
- Exit code mapping must live in `cli/` — it is a presentation/dispatch concern
- Error messages must state what failed, where, and what artifact caused it (`cli_spec.md` Section 4.6)
- Must not swallow or mask filesystem or contract failures

## Escalation Conditions
- A required error category is missing from `cli_spec.md` Section 5 and a new code would be needed
