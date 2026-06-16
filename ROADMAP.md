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

The proactive assistance release. The focus shifts from enforcing the workflow to making it easier to feed.

### `grain suggest`

Proactive task suggestion with a human approval gate. Grain reads the current workspace state — open questions, doc gaps, backlog shape, recent closures — and proposes concrete next tasks with draft context and plan seeds. Suggestions are proposals only; nothing is written until explicitly approved.

- `grain suggest` — analyze workspace and surface candidate tasks
- `grain suggest --accept <id>` — promote a suggestion to a real packet
- `grain suggest --prune` — clear stale or rejected suggestions
- Suggestion quality improves as the workspace accumulates richer canonical docs and closed packet history

### DX Hardening Foundation

Before feature work begins, known friction points are addressed:

- `grain workflow next` routing fix — active execution artifacts correctly surface review instead of re-entering execute
- `grain phase close --phase <N>` flag now accepted consistently
- Packet ID allocation correctly skips archived packets — no more ID reuse after archiving
- `grain upgrade --add-missing` covers all 14 scaffold gaps identified in the current audit
- `grain docs audit` and `grain archive` ergonomics improvements
- `grain status` reads `.grain/last_workflow_state.json` and `.grain/last_docs_audit.json` caches when fresh
- `--format json` flag-order canonicalized across all commands

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
