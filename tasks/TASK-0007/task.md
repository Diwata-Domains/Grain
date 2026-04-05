# Task: Add CLI output formatting base

## Metadata
- **ID:** TASK-0007
- **Status:** done
- **Phase:** Phase 1 — Repository Foundation and Core CLI
- **Dependencies:** TASK-0002 (CLI entrypoint must exist)

## Objective
Implement shared output formatting for text output and prepare a stable interface for optional JSON output. All CLI commands should use this shared formatter rather than calling `click.echo` directly with ad-hoc strings.

## Why This Task Exists
`implementation_plan.md` Phase 1 lists "CLI output formatting base" as a major deliverable. `cli_spec.md` Sections 4.3, 9, and 10 define output rules and expected fields. Without a shared formatter, each command produces inconsistent output and JSON support is difficult to add later without touching every command.

## Scope
- Implement a shared output formatter in `src/ai_build_toolkit/cli/`
- Support text output (default) and a stable interface for JSON output
- Define a standard result structure matching `cli_spec.md` Section 10 fields
- Update `abt init` to use the formatter instead of direct `click.echo` calls

## Constraints
- Must align with `cli_spec.md` Section 4.3 (`--format text|json`), Section 9 (human-readable expectations), Section 10 (structured output fields)
- Formatter must live in `cli/` — it is a presentation concern, not a service concern (`architecture.md` Section 4.1)
- v1 minimum: text always, JSON interface prepared but only required for `abt init` at this stage
- Must not introduce rendering logic into services or domain layers

## Escalation Conditions
- Q6 (JSON output surface) remains open — if scope of JSON support is disputed, default to text-only with a stub JSON path
