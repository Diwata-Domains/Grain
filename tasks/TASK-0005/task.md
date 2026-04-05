# Task: Implement `abt init`

## Metadata
- **ID:** TASK-0005
- **Status:** done
- **Phase:** Phase 1 — Repository Foundation and Core CLI
- **Dependencies:** TASK-0003 (init stub must exist), TASK-0004 (repo root resolution must exist)

## Objective
Implement the `abt init` command. It must scaffold the required repository directory structure and write seed files from templates where they are missing. It must not silently overwrite protected artifacts. If the repository is already initialized, it must report existing state and exit cleanly.

## Why This Task Exists
`implementation_plan.md` Phase 1 lists the "repository init command" as a major deliverable. `current_focus.md` lists delivering the first working version of `abt init` as immediate goal #5. This is the first command that performs real filesystem work and exercises the services and templates layers.

## Scope
- Implement the `init` command in `src/ai_build_toolkit/cli/init.py`
- Implement an initialization service in `src/ai_build_toolkit/services/`
- Create the required directory structure: `docs/canonical/`, `docs/working/`, `docs/runtime/`, `tasks/`, `templates/docs/`, `templates/tasks/`, `templates/prompts/`
- Write minimal seed files from templates where files are absent
- Protect existing files — do not overwrite without `--force`
- Support `--dry-run`: report intended actions without writing anything
- Report files created, skipped, and blocked

## Constraints
- Must follow `cli_spec.md` Section 6.1: responsibilities, must-nots, and recommended options
- Must use `resolve_repo_root()` from `adapters/filesystem.py` for path resolution (or use cwd when initializing a fresh repo)
- Init logic must live in `services/`, not in `cli/` (`architecture.md` Section 4.1 and 4.2)
- Must not invent project-specific scope or content in seed files
- Must not create hidden runtime state
- Canonical docs must be treated as protected — never overwritten silently

## Escalation Conditions
- Template content for seed files is not yet defined (P1-T06 handles templates — coordinate if needed)
- Ambiguity about which directories are required vs optional at init time
