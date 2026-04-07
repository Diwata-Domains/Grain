# Task: Implement `abt docs index` baseline behavior

## Metadata
- **ID:** TASK-0018
- **Status:** done
- **Phase:** Phase 2 — Documentation Registry and Validation
- **Backlog:** P2-T08
- **Dependencies:** TASK-0012 (document registry), TASK-0015 (docs_service exists)

## Objective
Implement `abt docs index` as a generation command that writes or refreshes `docs/runtime/docs_index.md` from the manifest registry. Manifest is the authoritative source; the index is derived output. The generated file lists all registered documents grouped by layer with their key metadata fields.

## Why This Task Exists
Q5 resolved: manifest is primary, `docs_index.md` is generated. `implementation_plan.md` Phase 2 lists "`abt docs index` baseline behavior" as a deliverable. With Q5 resolved this can now be implemented.

## Scope
- Add `generate_index(root: Path) -> CommandResult` to `services/docs_service.py`
- Load manifest, build registry, format a structured markdown document grouped by layer (canonical, working, runtime)
- Each entry: `id`, `path`, `authority`, `editable_by_agents`, `purpose`
- Write output to `docs/runtime/docs_index.md` (overwrite)
- Wire `abt docs index` command in `cli/docs.py` (stub exists)
- Support `--dry-run` flag: print output without writing
- Write tests in `tests/test_docs_index_cmd.py`

## Constraints
- Lives in `services/docs_service.py` — CLI stays thin
- Must use `load_manifest` + `build_registry` — no direct YAML parsing in service
- Output must be valid markdown readable without the CLI
- `--dry-run` must not write any files
- Do not validate doc existence or authority in this command — that is `docs validate`
- Missing manifest returns failed `CommandResult`, not a crash

## Escalation Conditions
- Current `docs_index.md` contains human-authored sections (read order, principles) that would be lost on overwrite — scope decision needed if content should be preserved vs. replaced
