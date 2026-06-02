# Task: Add landscape.md and roadmap.md to grain init templates

## Metadata
- **ID:** TASK-0195
- **Status:** draft
- **Phase:** Phase 30 — v0.4.0 Planning
- **Backlog:** P30-T06
- **Packet Path:** tasks/P30-T06-TASK-0195/
- **Dependencies:** TASK-0190
- **Primary Adapter:** code

## Objective
Extend `grain init` and `grain onboard` to seed `docs/canonical/landscape.md` and `docs/working/roadmap.md` with proper structural templates. Also improve the existing seeded doc templates so newly initialized projects get immediately useful structure, not empty headings.

## Why This Task Exists
Currently, `grain init` seeds docs that are either empty or have minimal content. A product that gets `grain init` run on it should have docs with real sections and placeholder guidance — so the first task is filling in content, not inventing a format. `landscape.md` and `roadmap.md` are two new standard doc types that every Grain-managed product should have.

## Scope

**New doc types to seed:**

`docs/canonical/landscape.md`:
```markdown
# [Product] — Landscape

## Competitors
| Name | What it does | How we differ |
|---|---|---|

## Inspirations
| Name | What it is | What we drew from it |
|---|---|---|

## References
- [Name](url) — why it's worth reading
```

`docs/working/roadmap.md` (internal future directions, distinct from public ROADMAP.md):
```markdown
# [Product] — Future Roadmap

Items here are not committed or scheduled.
They may become phases when current work stabilizes.

## Strong Candidates

## Under Consideration

## Explicitly Deferred

## Not on the Roadmap
```

**Existing template improvements:**
- `docs/canonical/product_scope.md` — add sections: Overview, Problem, Target Users, Core Capabilities, What It Is Not, Success Criteria
- `docs/canonical/architecture.md` — add sections: Stack, Directory Structure, Module Responsibilities, Key Interfaces, Data Flow
- `docs/working/backlog.md` — add sections: Active Phase, Upcoming Phases, Icebox
- `docs/working/current_focus.md` — add sections: Current Phase, Active Priority, Immediate Work, Active Constraints
- `docs/working/open_questions.md` — table format: ID | Question | Status | Resolution

**Implementation steps:**
- Find where seeded file content is defined (`src/grain/services/init_service.py`, `src/grain/services/onboard_service.py`, bundled template data)
- Add `landscape.md` and `roadmap.md` to the file seed list
- Update template content for the docs listed above
- Verify with `grain init` on a test directory — assert all seeded docs have the expected section structure
- Add tests covering: new files are seeded, existing section structure is present

## Deliverable
Grain codebase updated so `grain init` seeds `landscape.md` and `roadmap.md`, and existing seeded docs have proper section structure. Tests passing.

## Constraints
- Additive only — seeded templates must not be auto-applied to existing repos via `grain upgrade` unless the operator explicitly requests it
- Keep template content minimal — sections and heading placeholders, not paragraph prose
- `grain init --no-templates` flag should still work (skip template content but seed empty files)
