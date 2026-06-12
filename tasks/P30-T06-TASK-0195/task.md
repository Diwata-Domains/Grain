# Task: Scaffold audit — fix seeding gaps and add standard doc types

## Metadata
- **ID:** TASK-0195
- **Status:** draft
- **Phase:** Phase 30 — v0.4.0 Planning
- **Backlog:** P30-T06
- **Packet Path:** tasks/P30-T06-TASK-0195/
- **Dependencies:** TASK-0190
- **Primary Adapter:** code

## Objective
Audit every file that `grain init` and `grain onboard` scaffold, fix the seeding gaps found in that audit, and add the standard doc types that every Grain-managed project should have from day one. The goal is that a project initialized with `grain init` is immediately useful — not a collection of empty directories and placeholder headings that require another 30 minutes of manual setup before the first `grain workflow next` call works.

## Why This Task Exists
A full audit of `_SEED_FILE_SOURCES` and `docs_manifest.yaml` revealed several significant gaps:

1. `docs/canonical/product_scope.md` and `docs/canonical/architecture.md` are registered in the manifest but **never seeded** — `docs/canonical/` is empty after `grain init`.
2. `docs/working/backlog.md`, `current_focus.md`, `open_questions.md`, and `change_proposals.md` are registered in the manifest but **never seeded** — so `grain workflow next` starts blind.
3. `docs/manifest.yaml` lands with `[Your Project Name]` and `[project type]` placeholders; there is no `--name` or `--type` flag on `grain init` to fill them at init time.
4. `docs/working/workflow_metrics.md` seeds as `# DRAFT` with no structure.
5. No `docs/canonical/decisions.md` for recording architecture decisions (ADR-style).
6. No `CHANGELOG.md` at project root — standard expected file for any released tool.
7. No `docs/working/roadmap.md` for internal future directions (distinct from public ROADMAP.md).
8. No `docs/canonical/landscape.md` for competitor/inspiration analysis.
9. `docs/working/proposals/` is not created as a seed directory, but Phase 9 orchestrator and `grain suggest` write there.
10. `tooling_notes.md` has `read_when: never` in the manifest — it should surface when agents encounter friction.

## Scope

### Audit and fix seeding gaps

**Canonical docs to seed (new templates in `src/grain/data/runtime/`):**
- `docs/canonical/product_scope.md` — sections: Overview, Problem Statement, Target Users, Core Capabilities, What It Is Not, Success Criteria
- `docs/canonical/architecture.md` — sections: Stack, Directory Structure, Module Responsibilities, Key Interfaces, Data Flow, Design Decisions Log (link to decisions.md)
- `docs/canonical/decisions.md` — ADR-style table: ID | Decision | Status | Date | Rationale; plus template for individual decision entries
- `docs/canonical/landscape.md` — sections: Competitors (table), Inspirations (table), References

**Working docs to seed:**
- `docs/working/backlog.md` — sections: Active Phase (heading+bullet format, not table), Upcoming Phases, Icebox; note at top explaining heading+bullet requirement for workflow parser
- `docs/working/current_focus.md` — sections: Current Phase (name + number), Phase Goal, Status, Active Constraints, Immediate Priorities
- `docs/working/open_questions.md` — table header: ID | Question | Raised | Status | Resolution
- `docs/working/change_proposals.md` — table header: ID | Target Doc | Proposed Change | Status | Approved By
- `docs/working/roadmap.md` — sections: Strong Candidates, Under Consideration, Explicitly Deferred, Not on the Roadmap; note that items here are not committed or scheduled
- `docs/working/current_task.md` — minimal placeholder (Task ID: none, Status: unset)

**Root files to seed:**
- `CHANGELOG.md` — Keep a Changelog format (https://keepachangelog.com); sections: Unreleased, template for version entries with Added/Changed/Fixed/Removed

**Existing templates to improve:**
- `docs/working/workflow_metrics.md` — replace `# DRAFT` with real structure: sections per phase (Phase N: tasks done, tests passing, notes), summary table
- `docs/working/implementation_plan.md` — already reasonable; add a "Constraints" section and remove the comment asking users to replace the file
- `docs/runtime/docs_index.md` — verify it reflects all new doc types

**New seed directory:**
- `docs/working/proposals/` — created with `.gitkeep`; standard write location for `grain orchestrate plan`, `grain suggest`, and OrchestratorPlan outputs

### Manifest improvements (`docs/runtime/docs_manifest.yaml`)
- Add entries for new canonical docs: `decisions`, `landscape`
- Add entries for new working docs: `roadmap`, `current_task`
- Change `tooling_notes` `read_when` from `never` to `["encountering_blockers", "logging_friction"]`
- Add entry for `proposals/` as a known working directory

### `grain init` CLI improvements
- Add `--name <project-name>` flag: substitutes `[Your Project Name]` in all seeded files at init time
- Add `--type <project-type>` flag: substitutes `[project type]` in `docs_manifest.yaml`
- If `--name` is not provided, print a post-init reminder: "Update `[Your Project Name]` in docs_manifest.yaml before running grain workflow commands"

### Implementation steps
1. Write new template files under `src/grain/data/runtime/` for each new/updated doc
2. Add each new file to `_SEED_FILE_SOURCES` in `init_service.py`
3. Add `docs/working/proposals/` to `_REQUIRED_DIRS`
4. Add `--name` and `--type` flags to the `grain init` CLI (`src/grain/cli/init.py`) and thread through `init_service.py` with placeholder substitution
5. Update `src/grain/data/runtime/docs_manifest.yaml` with new entries and manifest fixes
6. Verify with `grain init` on a test directory — assert all new files are created with expected section structure
7. Add tests for: new files seeded, `--name` substitution works, `--type` substitution works, existing files not overwritten

## Deliverable
- New and updated template files in `src/grain/data/runtime/`
- `init_service.py` with expanded `_SEED_FILE_SOURCES`, `--name`/`--type` substitution, `proposals/` in `_REQUIRED_DIRS`
- `src/grain/cli/init.py` with `--name` and `--type` flags
- Updated `docs_manifest.yaml` bundle with new entries and corrected `tooling_notes` `read_when`
- Tests passing

## Constraints
- Additive only — new seeded templates must not be auto-applied to existing repos via `grain upgrade` unless the operator explicitly requests it
- Template content must be minimal: sections and heading placeholders, not paragraph prose
- `grain init --no-templates` must still work (skip template body content, seed empty files with correct headings only)
- `CHANGELOG.md` at project root must not overwrite an existing one (skip if present)
- Seeded `backlog.md` must use heading+bullet format, not table format — this is a hard workflow parser requirement
