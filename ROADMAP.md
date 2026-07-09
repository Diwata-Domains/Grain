# Roadmap

This document outlines the planned direction for Grain. It is intentionally high-level — no release dates, no feature promises. It reflects current intent and will change as the project evolves.

---

## Unreleased

Grain is now licensed under [MIT](LICENSE), relicensed from Apache-2.0. Bootstrap fixes:
`grain init` and `grain onboard` produce workspaces that pass their own health checks, and
`grain orchestrate` no longer aborts on workspaces containing task packets or binary files.

---

## Current — v0.5.0

The recipe step-runner release. Grain gains a composable, file-backed engine for running multi-step workflows that stand parallel to the SDLC loop — the first substrate that treats a repeatable procedure, not a code change, as the unit of work.

**Shipped in this release:**
- `grain recipe run / next / status / resume / gate / scaffold / list / show` — an operator-mode step-runner that advances one step at a time, pauses for input, and honors per-step review gates
- `grain.recipe/v2` recipe definitions — typed, strict-key recipe schema with declared parameters and an ordered step list
- `grain.recipe-run/v1` run state — file-backed run records under `docs/recipes/runs/<run-id>/` for lossless, resumable runs with no database
- Bundled starter recipes: `explainer` and `research-brief` — runnable out of the box, discoverable via `grain recipe list` as `source: bundled`
- Relicensed from AGPL-3.0 to Apache-2.0

The recipe engine is deliberately decoupled from the packet lifecycle: recipes do not touch `evaluate_workflow_state` or the SDLC task loop. This keeps the two workflow substrates independent and is the groundwork for running Grain over non-code work.

See [CHANGELOG.md](CHANGELOG.md) for the full list.

---

## Shipped History

### v0.4.0 — Proactive Assistance

Grain learned to suggest what to work on next, surfaced workflow friction as actionable GitHub issues, and laid the telemetry foundation for the broader Diwata stack.

**`grain suggest`** — proactive task suggestion with a human approval gate. Grain reads the current workspace state — open questions, doc gaps, backlog shape, recent closures — and proposes concrete next tasks with draft context and plan seeds. Suggestions are proposals only; nothing is written until explicitly approved.
- `grain suggest` — analyze workspace and surface candidate tasks
- `grain suggest accept <id>` — promote a suggestion to a real packet
- `grain suggest --prune` — clear stale or rejected suggestions
- `grain workflow next` surfaces a suggestion automatically when no obvious next task exists

**Phase close task archiving** — `grain phase close` now automatically moves task packets to `tasks/archive/phase-N/` alongside the existing doc snapshot. Closing a phase fully seals it.
- Packets are moved, not copied — the active `tasks/` directory stays clean
- `--keep-tasks` skips the move when a task is being carried forward to the next phase
- `grain archive show --phase N` surfaces the full packet list from the archive

**`grain notes`** — the friction log graduated from a write-only stub to a queryable, actionable inbox.
- `grain notes list` — filterable by type (`bug` | `friction` | `question` | `note`) and status
- `grain notes resolve <id>` — mark a note addressed
- `grain notes publish <id>` — submit a note directly to GitHub Issues via the API; no browser required
- Open `bug`/`friction` notes surface as findings in `grain docs audit`
- Workspace GitHub repo configured in `docs_manifest.yaml`; token via `GRAIN_GITHUB_TOKEN`

**Workflow metrics** — `grain metrics` surfaces per-phase velocity and cost tracking.
- Phase duration, task count, and closure rate per phase
- Stop-reason frequency — which gates fire most often
- Exportable as JSON for external analysis

**Pulse telemetry foundation** — Grain laid the event emission contract for Pulse, the planned Diwata-wide telemetry layer. Grain's side is intentionally thin: structured, versioned events emitted at key workflow moments (phase close, task close, suggest accept, stop reasons). Transport and aggregation are Pulse's responsibility.
- Opt-in via `telemetry.enabled` in `docs_manifest.yaml` or `GRAIN_TELEMETRY_ENDPOINT`
- Events are typed and versioned — safe to evolve without breaking Pulse consumers
- No telemetry is emitted unless explicitly enabled

### v0.3.1 — Enforcement and Hardening

Grain moved from describing the workflow to actively guarding it.
- `grain workflow guard` — standalone enforcement command; callable from git hooks, CI, or any agent
- `grain hooks install / list / remove` — writes pre-commit and post-checkout hooks that run the guard
- `grain docs audit` — 18 workspace health checks across 6 doc types; `--fix` flag; guard integration
- `grain archive` — phase close, milestone, and point-in-time snapshots
- `grain status` — combined workflow state and docs health; cached reads under 1s
- `grain doctor` — install-mode detection, version alignment checks, workspace resolution report
- `grain upgrade --add-missing` — seeds absent files without overwriting existing ones
- `upgrade_policy` and `branch_policy` manifest blocks; `workflow.resume.md` prompt; expanded `--format json` coverage

---

## Next — v0.6.0

The general-agentic-workflow release. The through-line is that Grain's real product is the deterministic workflow substrate, not the code loop — the code path is one instance. This release relaxes the code-repo assumptions that still bind the substrate and expands the surfaces a headless agent (a "familiar") can drive with no human and no browser.

Scope is candidate-only and sourced from the working v0.5.0 contract (§2) and the Phase 36 backlog. It will be narrowed during a dedicated planning pass.

**General-purpose / non-code workspaces** — the headline direction. Introduce `workspace_kind: code | knowledge | mixed` and relax the git/branch/AST assumptions so Grain runs knowledge, research, and ops workflows, not just code repos. Includes promoting `grain.toml` to the single authoritative workspace marker and manifest home (carrying `workspace_kind` and version/branch policy), with a migration to backfill markerless workspaces and resolve stray stubs. This is a resolver change with a migration — not an ad-hoc flip.

**`grain recipe suggest`** — propose which recipes to create or run from workspace signals, reusing the v0.4.0 suggest proposal model on top of the shipped recipe engine.

**External signal inbox** — a local-first, file-backed signal inbox (`docs/working/signals/`) that an external driver writes into, so calendar/email/document-derived signals can influence `grain suggest` with no network code inside Grain.

**Safe-apply graduation** — gated in-place `apply` for `.docx` / spreadsheet / Obsidian artifacts when validators fully pass and a packet-scoped backup exists, graduating the propose/export path to a reviewed real write.

**Grain-as-engine contract** — a versioned, expanded MCP surface (`grain.engine/v1` envelope + typed error model, capability registry) so external drivers can run the full loop headlessly rather than only creating tasks. This is the machine interface familiars depend on; the per-command structured-output contract (`print_result` / `CommandResult` migration) is the plumbing beneath it.

**Context token-budget proxy** — make the token-efficiency claim measurable rather than assumed. `grain context build/show` emits an estimated token cost for the assembled bundle, ranks the heaviest sources, and surfaces trimming hints, with an optional per-task/per-phase token-cost column in `grain metrics`. Matters most for unattended familiars that need a visible context budget.

**Dependency-extras slimming** (backlog P36-T02) — move already-lazy heavy dependencies (`textual`, `pdfplumber`, `python-docx`, `openpyxl`, `networkx`, `tree-sitter`) out of the mandatory install into `[tui]` / `[office]` / `[scan]` extras, dropping the install footprint at near-zero runtime cost with helpful ImportError guidance.

**Workspace staleness check** (backlog P36-T06) — `check_staleness(root, installed_version)` pairing version comparison with a file-drift scan, wired into `doctor` and `status`, so a workspace whose files have drifted from the installed CLI is reported instead of going silently stale. Reports stale-applyable versus customized-skipped separately and never auto-writes.

Guiding principle: every surface should be drivable end-to-end by a familiar — file-backed and structured-JSON over interactive prompts.

---

## Later

These are directions with enough signal to name but not yet scoped for a specific release.

- **Multi-adapter tasks** — tasks that span code, docs, and data domains simultaneously without adapter-switching overhead
- **Codex and Claude-native integration improvements** — tighter MCP tool surface for desktop clients that prefer tool calls over direct CLI invocation
- **`grain workspace`** — multi-project views and cross-workspace backlog queries

---

## Companion Project — Assay

[Assay](https://github.com/Diwata-Domains/Assay) is an independent verification layer built by the same team, using Grain as its own workflow system.

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

Note: general-purpose (non-code) workspaces are a goal, not a non-goal — Grain runs from the CLI over file-backed state regardless of domain. Widening the substrate beyond code does not imply a hosted service, a dashboard, or a database.
