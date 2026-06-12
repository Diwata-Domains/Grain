# Results — TASK-0194

## Status
done — 2026-06-11

## Deliverable
`docs/working/dev_runtime_alignment.md` — diagnostic design and spec.

## Key Decisions

**Approach:** Option C — install type flag in `grain --version` + dedicated `grain doctor` command. No overhead on normal command invocations.

**`grain --version` change:** Appends install mode: `grain 0.4.0 (editable)`, `grain 0.4.0 (installed)`, or `grain 0.4.0 (dev)`. Detected via `importlib.metadata` dist-info.

**`grain doctor` checks:** version match (installed vs. pyproject.toml), source mtime vs. install mtime (detects source files modified after last install), install mode validity, workspace resolution.

**Integration:** `grain workflow guard --check-dev-alignment` calls doctor internally and reports drift as a warning. `workflow.resume.md` mentions `grain doctor` for unexpected CLI behavior.

## Files Changed
- `docs/working/dev_runtime_alignment.md` — created
- `tasks/P30-T05-TASK-0194/task.md` — status set to done
