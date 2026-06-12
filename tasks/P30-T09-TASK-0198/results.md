# Results — TASK-0198

## Status
done — 2026-06-11

## Deliverable
`docs/canonical/feedback_spec.md` — upstream feedback loop spec.

## Key Decisions

**`grain report`:** URL-mode only (no Grain network call). Constructs GitHub issue URL from tooling_notes row. Marks row `reported` after user confirms. Never sends project content.

**Telemetry:** User-level config (`~/.grain/config.toml`), default `false`. Queues to `.grain/telemetry_queue.jsonl`. Ask-before-send on next invocation. No stack traces by default. No file contents, no user identity.

**`grain notes add`:** The agent-callable tooling notes interface. Any agent running this command produces a correctly-formatted row. Replaces direct file editing for all agents.

**GitHub endpoint:** Issues on `Diwata-Domains/grain`. URL mode requires no Grain API key. Telemetry uses Issues API, falls back to URL mode.

## Files Changed
- `docs/canonical/feedback_spec.md` — created
- `tasks/P30-T09-TASK-0198/task.md` — status set to done
