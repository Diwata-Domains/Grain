# Roadmap

This document outlines the planned direction for Grain. It is intentionally high-level — no release dates, no feature promises. It reflects current intent and will change as the project evolves.

---

## Current — v0.3.1

The enforcement and hardening release. Grain now actively guards the workflow rather than just describing it.

**Shipped in this release:**
- `grain workflow guard` — standalone enforcement command; callable from git hooks, CI, or any agent
- `grain hooks install / list / remove` — writes pre-commit and post-checkout hooks that run the guard automatically
- `grain docs audit` — 18 workspace health checks across 6 doc types; `--fix` flag; guard integration
- `grain archive` — phase close snapshots (automatic), milestone snapshots, point-in-time snapshots
- `grain status` — single command combining workflow state and docs health; cached reads stay under 1s
- `grain doctor` — install-mode detection, version alignment checks, workspace resolution report
- `grain upgrade --add-missing` — seeds absent files without overwriting existing ones
- `upgrade_policy` and `branch_policy` manifest blocks — workspaces declare minimum version and branch discipline rules
- `workflow.resume.md` prompt — agent-agnostic session resume protocol seeded in every new workspace
- 13 new scaffold templates seeded by `grain init`
- `grain --format json` coverage expanded across workflow, archive, status, and doctor commands

See [CHANGELOG.md](CHANGELOG.md) for the full list.

---

## Next — v0.4.0

The proactive assistance release. Grain learns to suggest what to work on next, surfaces workflow friction as actionable GitHub issues, and lays the telemetry foundation for the broader Diwata stack.

### `grain suggest`

Proactive task suggestion with a human approval gate. Grain reads the current workspace state — open questions, doc gaps, backlog shape, recent closures — and proposes concrete next tasks with draft context and plan seeds. Suggestions are proposals only; nothing is written until explicitly approved.

- `grain suggest` — analyze workspace and surface candidate tasks
- `grain suggest --accept <id>` — promote a suggestion to a real packet
- `grain suggest --prune` — clear stale or rejected suggestions
- `grain workflow next` surfaces a suggestion automatically when no obvious next task exists

### Phase close task archiving

`grain phase close` now automatically moves task packets to `tasks/archive/phase-N/` alongside the existing doc snapshot. Closing a phase fully seals it — no manual cleanup needed.

- Packets are moved, not copied — the active `tasks/` directory stays clean
- `--keep-tasks` flag skips the move when a task is being carried forward to the next phase
- `grain archive show --phase N` surfaces the full packet list from the archive

### `grain notes` — full implementation

The friction log graduates from a write-only stub to a queryable, actionable inbox.

- `grain notes list --open` — filterable by type (`bug` | `friction` | `question` | `note`) and status
- `grain notes resolve <id>` — mark a note addressed
- `grain notes publish <id>` — submit a note directly to GitHub Issues via the API; no browser required
- Open notes surface as findings in `grain docs audit`
- Workspace GitHub repo configured in `docs_manifest.yaml`; token via `GRAIN_GITHUB_TOKEN`

### Workflow metrics

Per-phase velocity and cost tracking surfaced through a new `grain metrics` command.

- Phase duration, task count, and closure rate per phase
- Stop-reason frequency — which gates fire most often
- Exportable as JSON for external analysis

### Pulse telemetry foundation

Grain lays the event emission contract for Pulse — the planned Diwata-wide telemetry layer. Grain's side is intentionally thin: structured, versioned events emitted at key workflow moments (phase close, task close, suggest accept, stop reasons). Transport and aggregation are Pulse's responsibility.

- Opt-in via `telemetry.enabled` in `docs_manifest.yaml` or `GRAIN_TELEMETRY_ENDPOINT` env var
- Events are typed and versioned — safe to evolve without breaking Pulse consumers
- No telemetry is emitted unless explicitly enabled

---

## Later

These are directions with enough signal to name but not yet scoped for a specific release.

- **Multi-adapter tasks** — tasks that span code, docs, and data domains simultaneously without adapter-switching overhead
- **`grain notes`** — structured friction and observation logging to `tooling_notes.md` with queryable history
- **Workflow metrics** — per-phase cost, velocity, and quality tracking; exportable summaries
- **Codex and Claude-native integration improvements** — tighter MCP tool surface for desktop clients that prefer tool calls over direct CLI invocation
- **`grain workspace`** — multi-project views and cross-workspace backlog queries

---

## Companion Project — Assay

[Assay](https://github.com/Diwata-Labs/Assay) is an independent verification layer built by the same team, using Grain as its own workflow system.

**What it is:** visual and functional verification for software projects. Assay runs Playwright tests in Docker, captures screenshots, computes pixel-level diffs against approved baselines, and surfaces results through a dashboard with a before/after slider.

**How it relates to Grain:** Grain ships a bridge contract (`grain verify` command group) that Assay implements. The two are decoupled — Grain works fully without Assay, and Assay is useful beyond Grain-managed projects.

**Status:** live at [pypi.org/project/assay-kit](https://pypi.org/project/assay-kit/).

---

## Not on the Roadmap

These are explicit non-goals for the foreseeable future:

- GUI or web dashboard
- Database-backed workflow state
- Cloud-hosted workflow execution
- Vendor lock-in to any specific AI provider or agent CLI
- Multi-user real-time collaboration
