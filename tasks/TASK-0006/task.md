# Task: Create template directory structure

## Metadata
- **ID:** TASK-0006
- **Status:** done
- **Phase:** Phase 1 — Repository Foundation and Core CLI
- **Dependencies:** TASK-0001 (src/ai_build_toolkit/templates/ must exist), TASK-0005 (abt init creates template dirs in repo)

## Objective
Add `templates/docs/`, `templates/tasks/`, and `templates/prompts/` to the repository with placeholder template files. Add template loading support in `src/ai_build_toolkit/templates/` so the rest of the system can resolve and read template content by name.

## Why This Task Exists
`implementation_plan.md` Phase 1 lists "template directory structure" as a major deliverable. Templates are required for `abt init` to write seed files and for the packet system to scaffold task packets. Without a stable template loader, downstream tasks (P3-T02 packet templates) have no resolution mechanism to build on.

## Scope
- Add placeholder template files under `templates/docs/`, `templates/tasks/`, `templates/prompts/`
- Implement a template loader in `src/ai_build_toolkit/templates/` that resolves templates by name from the repository's `templates/` directory
- Templates must not encode project-specific logic

## Constraints
- Must align with `data_contracts.md` Section 14: templates are source artifacts, not live project state
- Must align with `architecture.md` Section 4.9: must not encode project-specific logic
- Template loader must live in `src/ai_build_toolkit/templates/` (`architecture.md` Section 6.6)
- Placeholder content must be minimal and generic
- Must not require manifest or packet logic

## Escalation Conditions
- Template format (plain markdown vs. Jinja2 etc.) introduces a dependency not yet approved
- Conflict between placeholder content and later Phase 3 packet template requirements
