# Scaffold Audit — `grain init` and `grain onboard` Seeding Gaps

**Status:** Working spec — v0.4.0 planning (Phase 30, TASK-0195)
**Implementation phase:** Phase 31 (DX Hardening)

---

## 1. Audit Summary

A full audit of `_SEED_FILE_SOURCES`, `_REQUIRED_DIRS`, and `docs_manifest.yaml` against the files that agents actually need at session start revealed 10 gaps. After `grain init`, a new workspace is missing critical files that `grain workflow next`, `grain orchestrate`, and `grain suggest` all depend on. Agents start sessions against a sparse workspace and must create or discover files that should have been there from day one.

---

## 2. Gap Inventory

| # | Gap | Impact | Fix |
|---|-----|--------|-----|
| G1 | `docs/canonical/product_scope.md` registered in manifest but never seeded | `grain task prepare` includes it; file is missing → broken context | Add template to `_SEED_FILE_SOURCES` |
| G2 | `docs/canonical/architecture.md` registered in manifest but never seeded | Same as G1 | Add template |
| G3 | `docs/working/backlog.md` not seeded | `grain workflow next` starts blind — no tasks, no phase | Add template with correct heading+bullet format |
| G4 | `docs/working/current_focus.md` not seeded | Phase context missing; `grain phase next` has no phase to read | Add template |
| G5 | `docs/working/open_questions.md` not seeded | OQ-driven features (suggest, guard) have nothing to read | Add template |
| G6 | `docs/working/change_proposals.md` not seeded | Proposal workflow broken from day one | Add template |
| G7 | No `docs/canonical/decisions.md` (ADR-style) | No canonical place for architecture decisions | Add new doc type + template |
| G8 | No `CHANGELOG.md` at project root | Standard expected file; agent attempts to log releases fail | Add to seeded root files |
| G9 | No `docs/working/roadmap.md` | Roadmap is a standard planning artifact; agents drift to ad-hoc files | Add new doc type + template |
| G10 | `docs/working/proposals/` dir not created | `grain orchestrate plan`, `grain suggest`, and OrchestratorPlan outputs all write here; dir absent causes errors | Add to `_REQUIRED_DIRS` |
| G11 | `tooling_notes.md` has `read_when: never` in manifest | Agents never load it → friction never surfaced → the purpose of the file is defeated | Fix to `["encountering_blockers", "logging_friction"]` |
| G12 | `docs_manifest.yaml` uses `[Your Project Name]` placeholder with no init-time substitution | Every workspace starts with wrong name | Add `--name` + `--type` flags to `grain init` |
| G13 | `docs/working/current_task.md` not in manifest entries | Missing from context assembly; agents don't read it | Add manifest entry |
| G14 | `docs/working/landscape.md` not seeded (only canonical landscape exists) | Working landscape analysis never surfaces | Add template |

---

## 3. Templates to Write (Phase 31)

Each template lives in `src/grain/data/runtime/`. Minimal structure: section headings and `[placeholder]` labels, no paragraph prose.

### New canonical templates

**`docs/canonical/product_scope.md`**
```markdown
# Product Scope

## Overview
[Brief one-paragraph description of what this project is.]

## Problem Statement
[What problem does this project solve, and for whom?]

## Target Users
[Who uses this product?]

## Core Capabilities
[Bulleted list of what the product does today.]

## What It Is Not
[Explicit non-goals and scope boundaries.]

## Success Criteria
[How will you know this product is working?]
```

**`docs/canonical/architecture.md`**
```markdown
# Architecture

## Stack
[Languages, frameworks, runtimes.]

## Directory Structure
[Annotated directory tree of key source locations.]

## Module Responsibilities
[One-sentence description per major module.]

## Key Interfaces
[CLI commands, API endpoints, or library APIs that external callers use.]

## Data Flow
[How data moves through the system — inputs, transformations, outputs.]

## Design Decisions Log
See [decisions.md](decisions.md) for ADR-style decision records.
```

**`docs/canonical/decisions.md`**
```markdown
# Architecture Decisions

## Decision Log

| ID | Decision | Status | Date | Rationale |
|----|----------|--------|------|-----------|
| D-001 | [Decision title] | accepted | YYYY-MM-DD | [One-line rationale] |

---

## Decision Template

### D-NNN — [Short decision title]

**Status:** proposed | accepted | superseded | deprecated
**Date:** YYYY-MM-DD
**Supersedes:** D-NNN (if applicable)

**Context:** [What situation forced this decision?]

**Decision:** [What was decided?]

**Rationale:** [Why this option over alternatives?]

**Consequences:** [What changes, what stays the same, what becomes harder?]
```

**`docs/canonical/landscape.md`**
```markdown
# Competitive Landscape

## Competitors

| Name | Approach | Strengths | Gaps relative to [Project Name] |
|------|----------|-----------|----------------------------------|

## Inspirations

| Name | What we took from it |
|------|----------------------|

## References
[Links to analysis docs, research, or prior art.]
```

### New working templates

**`docs/working/backlog.md`**
```markdown
# Backlog

## 1. Purpose

Execution inventory for [Project Name]. Grouped by phase.

Status values: `draft` | `ready` | `in_progress` | `blocked` | `review` | `done`

NOTE: This file must use heading+bullet format (not tables) for `grain workflow next` to parse it correctly.

---

## 2. Phase 1 — [Phase name]

> **Status:** not_started

### P1-T01 — [First task]
- **Status:** draft
- **Description:** [What this task does.]
```

**`docs/working/current_focus.md`**
```markdown
# Current Focus

## Current Phase
Phase 1 — [Phase name] — Not Started

## Phase Goal
[One sentence: what does this phase accomplish?]

## Status
[What is the current state? What's done, what's in progress, what's blocked?]

## Active Constraints
[What must not change during this phase?]

## Immediate Priorities
1. [First priority]
2. [Second priority]
```

**`docs/working/open_questions.md`**
```markdown
# Open Questions

## Purpose

Tracks unresolved design or implementation questions.

Status: `open` | `blocking` | `decision_needed` | `escalated` | `resolved` | `deferred`

---

## Open Questions

*(none yet)*

---

## Resolved Questions

*(none yet)*
```

**`docs/working/change_proposals.md`**
```markdown
# Change Proposals

## Purpose

Tracks proposed changes to canonical docs, architecture, or workflow semantics.

| ID | Target | Proposed Change | Status | Raised | Approved By |
|----|--------|----------------|--------|--------|-------------|

---

## Active Proposals

*(none yet)*
```

**`docs/working/roadmap.md`**
```markdown
# Roadmap

NOTE: Items here are directions being considered, not committed or scheduled work.
For scheduled work, see `backlog.md`.

## Strong Candidates
[Features or work likely to be prioritized in the next 1-2 planning cycles.]

## Under Consideration
[Ideas being evaluated — no commitment yet.]

## Explicitly Deferred
[Things that will not happen until a named condition changes.]

## Not on the Roadmap
[Things we have decided not to build — and why.]
```

**`docs/working/current_task.md`**
```markdown
# Current Task

Task ID: none
Task Path: (unset)
Status: unset

No task is currently active. Run `grain workflow next` to determine the next step.
```

### Root file

**`CHANGELOG.md`** — Keep a Changelog format:
```markdown
# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
### Changed
### Fixed
### Removed

---

## [0.1.0] — YYYY-MM-DD

### Added
- Initial release.
```

---

## 4. Manifest Changes (Phase 31)

File: `src/grain/data/runtime/docs_manifest.yaml`

Changes:
1. Add `decisions` canonical doc entry
2. Add `landscape` canonical doc entry  
3. Add `roadmap` working doc entry
4. Add `current_task` working doc entry with `read_when: ["session_start", "workflow_check"]`
5. Fix `tooling_notes` `read_when` from `never` to `["encountering_blockers", "logging_friction"]`
6. Add `proposals/` as a known working directory entry

---

## 5. `grain init` CLI Changes (Phase 31)

File: `src/grain/cli/init.py`

New flags:
```
--name <project-name>    Substitute [Your Project Name] in all seeded files
--type <project-type>    Substitute [project type] in docs_manifest.yaml
```

If `--name` is not passed: print a post-init reminder after completion.

Placeholder substitution: simple string replace in all seeded file contents before writing. No template engine required.

`grain init --no-templates` continues to work — seeds empty files with correct headings only, no body content.

---

## 6. `grain upgrade` Behavior for New and Existing Doc Types

`grain upgrade` must handle two cases for existing workspaces:

### Adding missing docs (new doc types)

When Grain 0.4.0 ships new seeded templates (`decisions.md`, `CHANGELOG.md`, `roadmap.md`, etc.), existing workspaces that were initialized before v0.4.0 will be missing those files. `grain upgrade` must:

1. Compare the current `_SEED_FILE_SOURCES` list against the workspace's existing files
2. For any seeded file that is **absent**, offer to add it — this is always safe (additive only, nothing is overwritten)
3. For any seeded file that is **present but stale** (content version in manifest is newer), offer a diff-and-update via `grain upgrade --diff`

The `--diff` mode already exists (shipped in v0.1.6). The gap is that it currently compares existing files against bundled templates but **does not surface absent files**. The Phase 31 implementation must add absent-file detection.

`grain upgrade` output for a workspace missing new docs:
```
grain upgrade

Checking 14 registered docs...
  ✓  docs/canonical/product_scope.md        up to date
  ✓  docs/working/backlog.md                up to date
  +  docs/canonical/decisions.md            NOT PRESENT — new in v0.4.0
  +  docs/working/roadmap.md                NOT PRESENT — new in v0.4.0
  +  CHANGELOG.md                           NOT PRESENT — new in v0.4.0
  +  docs/working/proposals/               DIRECTORY NOT PRESENT — new in v0.4.0

3 missing docs, 1 missing directory. Run 'grain upgrade --add-missing' to seed them.
```

`grain upgrade --add-missing` seeds only the absent files — existing files are never touched.

### Updating existing docs

`grain upgrade --diff` continues to work as before: compares each present file against the bundled template, shows a colored diff, and asks `[a]pply / [s]kip / [q]uit`. The operator decides per file.

Docs that have been substantively filled in (non-stub content) are flagged as "customized" — the diff shows what changed but recommends skip unless the operator specifically wants the template update.

### Upgrade constraint from T06 task.md — clarified

The original constraint "new seeded templates must not be auto-applied without operator request" means:

- `grain upgrade` alone (no flags) → reports what's missing and stale, **does not write**
- `grain upgrade --add-missing` → adds absent files only, no overwrites
- `grain upgrade --diff` → shows stale-file diffs, operator decides each one
- `grain upgrade --add-missing --diff` → does both in one pass

There is no flag that silently overwrites existing content. The operator always sees what will change before it changes.

---

## 7. Implementation Checklist (Phase 31)

**Templates:**
- [ ] Write all 14 template files listed in §3 (11 new + 3 updated)
- [ ] Add each to `_SEED_FILE_SOURCES` in `init_service.py`
- [ ] Add `docs/working/proposals/` to `_REQUIRED_DIRS`

**`grain init` CLI:**
- [ ] Add `--name` and `--type` flags to `init.py` and thread through `init_service.py`
- [ ] Post-init reminder if `--name` not passed

**Manifest:**
- [ ] Update `docs_manifest.yaml` bundle per §4

**`grain upgrade` — absent-file detection (new):**
- [ ] Add absent-file scan to `upgrade_service.py`: compare `_SEED_FILE_SOURCES` against workspace files, collect absent entries
- [ ] Report absent files in `grain upgrade` output (`+  filename  NOT PRESENT — new in vX.Y.Z`)
- [ ] Implement `grain upgrade --add-missing` flag: seeds absent files only, no overwrites
- [ ] Implement `grain upgrade --add-missing --diff` combined mode

**Tests:**
- [ ] New files seeded by `grain init`
- [ ] `--name` substitution works in seeded files
- [ ] `--type` substitution works in manifest
- [ ] Existing files not overwritten by `grain init` (additive)
- [ ] `CHANGELOG.md` skip-if-present
- [ ] `grain upgrade` output lists absent docs
- [ ] `grain upgrade --add-missing` adds only absent files

**Verification:**
- [ ] Run `grain init` on a clean temp directory; verify all expected files exist
- [ ] Verify `grain workflow next` returns a useful state after a fresh `grain init`
- [ ] Run `grain upgrade` on a pre-v0.4.0 workspace; verify absent-file report appears
