# Handoff — TASK-0206

## What Was Done

Fixed all 14 scaffold gaps. `grain init` on a fresh directory now produces a complete workspace that `grain workflow next` can operate on immediately.

Key additions:
- `open_questions.md` and `change_proposals.md` templates include a `Suggested Action` field per entry (user request)
- `CHANGELOG.md` skips if already present (additive only)
- `grain init --name <name>` replaces `[Your Project Name]` in all seeded files
- `grain init --type <type>` replaces the manifest type placeholder
- `grain upgrade` now surfaces absent seeded files; `grain upgrade --add-missing` seeds them

## State Left For Next Task

- `docs/working/proposals/` is created as an empty dir (gitkeep) — content written by `grain orchestrate plan` (future task)
- `grain upgrade --diff` still operates on `_UPGRADE_TARGETS` only (prompts/templates/runtime docs); it does not diff user-owned canonical/working docs
- `grain upgrade --add-missing` covers all `_SEED_FILE_SOURCES`; if a future task adds more seed files, both `_SEED_FILE_SOURCES` and `EXPECTED_SEED_FILES` in the test must be updated
