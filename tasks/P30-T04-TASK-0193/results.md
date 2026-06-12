# Results — TASK-0193

## Status
done — 2026-06-11

## Deliverable
`docs/working/apply_graduation.md` — graduation criteria and per-type assessment.

## Key Decisions

**Universal requirements (R1–R6):** All required validators pass, non-empty change summary, no unacknowledged risk flags, original backed up, review bundle in packet, `--confirm` required.

**Rollback mechanism:** `.grain/backups/<task_id>/` with backup manifest in packet. `grain task restore --backup <id>` command for recovery.

**Graduation verdicts:**
- `.docx` → Graduates; exclusion: >30% top-level heading deletion → auto-downgrade to propose
- `.csv` → Graduates unconditionally (no formulas)
- `.xlsx` data-only → Conditional graduation; formula columns in changed range → auto-downgrade to propose
- `.xlsx` formula range → Remains propose; deferred to v0.5.0
- Obsidian notes (link/frontmatter) → Conditional graduation; full rewrites remain propose
- PDF → Non-goal; read-only permanently

## Files Changed
- `docs/working/apply_graduation.md` — created
- `tasks/P30-T04-TASK-0193/task.md` — status set to done
