# Task: `grain onboard` CLI command + additive scaffold engine

## Metadata
- **ID:** TASK-0094
- **Status:** done
- **Phase:** Phase 13 — Existing Project Adoption
- **Backlog:** P13-T01
- **Packet Path:** tasks/P13-T01-TASK-0094/
- **Dependencies:** TASK-0093 (Phase 12 close)
- **Primary Adapter:** code_adapter
- **Secondary Adapters:** none

## Objective
Implement `grain onboard [path]` CLI command and `OnboardService` with additive scaffold logic. The command creates Grain's directory structure into an existing repo without overwriting anything that already exists, and returns a manifest of what was created versus skipped.

## Why This Task Exists
Phase 13 delivers existing project adoption (FR-013). The scaffold command is the entry point — it gives any existing repo a clean Grain directory structure in one pass. Everything else in Phase 13 (scanner, doc generation, prompt) builds on top of this scaffold foundation.

## Scope
- Implement `src/grain/cli/onboard.py` — `grain onboard [path]` command with `--dry-run` flag
- Implement `src/grain/services/onboard_service.py` — `OnboardService.scaffold(root)` method that:
  - Creates `docs/canonical/`, `docs/working/`, `docs/runtime/`, `tasks/`, `prompts/` if missing
  - Writes stub files marked `# DRAFT` for any canonical/working docs that don't exist yet
  - Never overwrites existing files — skip silently and record in manifest
  - Returns `ScaffoldManifest` with `created: list[str]`, `skipped: list[str]`
- Register command in `src/grain/cli/__init__.py`
- Text output: list created and skipped files in a clean two-section format
- JSON output: `{"created": [...], "skipped": [...]}` via `--format json`

## Constraints
- Additive only — never modify or overwrite existing files under any condition
- `--dry-run` must be safe: prints what would be created without touching the filesystem
- Stub file content must be minimal (title + `# DRAFT — replace with real content` line) — no hallucinated project details
- Do not run the codebase scanner in this task — scanner is P13-T02

## Escalation Conditions
- If stub file templates require canonical policy decisions (e.g., which canonical docs are mandatory), stop and log a change proposal
- If the CLI registration pattern differs from existing commands in a breaking way, stop and record blocker
