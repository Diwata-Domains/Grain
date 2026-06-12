# Tooling Notes

Lightweight inbox for workflow friction, tool bugs, or observations noticed mid-session.
Agents write here; user reviews and escalates to the appropriate tracker.

| Date | Type | Command | Observation | Severity | Status |
|------|------|---------|-------------|----------|--------|
| 2026-04-21 | workflow_friction | `grain workflow next` | Active task with implementation recorded in `results.md` still routes to `task_execute` while the intended workflow is Execute -> Review -> Close; review is not being surfaced as the next legal step once execution artifacts exist. | medium | open |
| 2026-04-21 | tool_bug | `grain workflow run` / `grain task create` | Packet ID allocation reused `TASK-0001` for Phase 16 because `next_task_id()` only scans active directories under `tasks/` and ignores archived packets under `tasks/archive/`, so bare task IDs are not globally monotonic after archiving. | medium | open |
| 2026-06-11 | ux | `grain workflow next --format json` | `--format` flag is a global option and must come before the subcommand: `grain --format json workflow next`. Placing it after the subcommand returns "No such option: --format". The spec documents (v0.4.0 enforcement_spec, cli_ergonomics_spec) all reference `grain workflow next --format json` — these are wrong and should use global flag order. | medium | open |
| 2026-06-11 | missing-command | `grain notes add` | `grain notes add` does not exist yet (v0.4.0 planned in T09/feedback_spec). Agents cannot log tooling friction via CLI — must edit tooling_notes.md directly. This breaks the agent-agnostic logging pattern that T09 is designed to fix. | high | open |
