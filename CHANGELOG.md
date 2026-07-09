## [Unreleased]

Phase 38 — tooling-friction remediation, sourced from a sweep of every
`docs/working/tooling_notes.md` on the machine and verified against 0.6.0.

### Features
- `grain review approve` / `grain review reject` — set the user review state that
  `grain task close` has always required. Previously the only path to a validated
  close was hand-editing the `## User Review` block in `results.md`.
- `--format [text|json]` now works **after** the subcommand on every command, not
  just as a global flag. `grain task list --format json` used to exit 2.
- `grain phase list` and `grain phase status` — read-only views of every phase, its
  status, and its task rollup. Both accept the numbered and unnumbered backlog
  heading forms.
- `grain task start <id>` — performs the full legal draft→ready→in_progress
  transition and syncs `backlog.md` and `current_task.md`, so `reconcile` reports
  no drift afterwards.
- `grain task show|validate|status|prepare|close` accept a positional TASK id or
  packet directory name, which is what `grain task list` prints. `--id` still works.
- `grain task backfill --id <TASK>` seeds missing planning files from templates so a
  legacy packet can migrate forward instead of failing validation forever.
- `grain notes triage` replays each open note's recorded command in a throwaway
  workspace and classifies it stale / open / needs-human. Dry-run by default.
- `grain notes list --fleet <roots...>` (and `triage --fleet`) aggregate friction
  across many workspaces, collapsing git-worktree copies and skipping archives and
  untouched templates. Friction is a fleet property; the inbox was per-repo.
- New workspaces stamp `phase_close_enforced_from: 1`, so the `previous_phase_not_closed`
  gate applies from phase 1. Workspaces without the stamp keep the old threshold of 15
  and are not suddenly blocked.

### Fixes
- `grain onboard` omitted `docs/working/proposals/`, so an onboarded repo failed
  `grain docs validate` with exit 3. Both scaffolders now consume one shared
  definition of the required directories and seed maps (`domain/scaffold.py`), so the
  init/onboard desync — this was its third instance — cannot recur.
- `grain upgrade --add-missing` printed `Added:` `- (none)` while writing the files.
- The `N Grain-managed file(s) are out of date` hint never cleared after `upgrade`
  skipped locally-customized files, and printed to stderr even under `--format json`.
- `grain phase close --dry-run` reported `"dry_run": false` on early-return paths.
- `grain workflow next` hard-blocked with `required_docs_invalid` when
  `## Current Phase` used a hyphen, en dash, or colon instead of an em dash. Both
  copies of the regex now accept all four, and `grain workflow reconcile --fix`
  detects and normalizes a malformed heading.
- `grain workflow reconcile` now reports orphan packets — backlog tasks marked
  done/in_progress with no packet directory.
- `grain task validate` honors an explicit `- **Mode:** simple` in a packet's
  metadata, so a partially-migrated legacy packet is no longer stuck failing.

## [0.6.0] — 2026-07-09

- Relicensed from Apache-2.0 to MIT.

### Features
- `grain phase close --allow-empty` — seal a phase that has no backlog tasks.
  Planning and deferred phases legitimately carry none, and refusing them meant
  such a phase permanently blocked the phase that followed it. The flag waives
  only the empty check; a phase whose tasks exist but are unfinished is still
  refused.
- `grain workflow reconcile` gained two phase-level checks, `phase_consistency`
  and `phase_close_chain`. Every prior check was packet-scoped, so reconcile
  reported `issues 0` on workspaces where `grain workflow next` refused to route
  with `workflow_state_drift` or `previous_phase_not_closed`. Both are reported,
  never auto-fixed — deciding whether a phase is finished is an operator call.

### Fixes
- `grain status` reported `Tasks: 0 total` on any workspace using the canonical
  `## Phase N —` backlog heading. Three phase-heading regexes (`cli/status.py`,
  `docs_audit_service.py`, `workflow_run_service.py`) required a numbered
  `## N. Phase N —` form, and `metrics_service.py` accepted only the unnumbered
  one. All four now accept both.
- `grain orchestrate scope` / `grain orchestrate plan` no longer abort with
  `dictionary changed size during iteration` when the workspace contains a task
  packet. The graph builder mutated its node map while iterating it, and treated
  the literal `none` adapter sentinel as a real adapter name.
- `grain init` now seeds `prompts/tasks.next_and_implement.md`,
  `prompts/tasks.review.md`, `prompts/tasks.close.md`, and
  `docs/working/tooling_notes.md`. A freshly initialized workspace no longer
  reports Grain-managed files as out of date, and passes `grain docs audit`.
- `grain onboard` now seeds the four canonical/working docs registered in
  `docs_manifest.yaml` that it previously omitted, plus the same prompt set as
  `grain init`. An onboarded workspace no longer reports audit errors.
- Structural extraction no longer aborts on binary files. A workspace holding a
  `.xlsx`, `.docx`, or image killed `grain orchestrate` with a `UnicodeDecodeError`;
  such files are now reported with no extractable entities and the scan continues.

## [0.5.0] — 2026-06-28

- Relicensed from AGPL-3.0-only to Apache-2.0.

### Features
- recipe step-runner MVP: `grain.recipe/v2` definitions driven through
  `grain.recipe-run/v1` run state (`docs/recipes/runs/<run-id>/`) by a parallel
  engine that never touches the SDLC packet loop. Operator mode (`grain recipe
  run | next | status | resume | gate`) is offline and deterministic; resume on
  explicit validation failure; bundled gateless `research-brief` recipe. The
  step-runner supersedes the single-packet recipe model.
- bundled 3-step `explainer` starter recipe — `grain recipe list` now shows
  `explainer` + `research-brief`.

## [0.4.0] — 2026-06-25

### Chores
- add root 'trace' script to avoid macOS /usr/bin/trace collision
- clear ruff lint (unused imports, f-string placeholder)
- add agent-triggerable release + server-side convention lint
- close Phase 32 (v0.4.0) — archive 10 packets
- merge staging → main — v0.4.0 Proactive Assistance
- add publish-pypi workflow (mirror of public Scry repo)
- sync monorepo to published mirror (scry-kit / import scry)
- consolidate prospects into diwa; add Apollo→Scry migration backlog
- add data-lake stack compose, env example, and CLAUDE.md for CCX21

### Bug Fixes
- emit bracketed '## [version]' changelog heading
- accept '## Phase N —' backlog headings in phase parsers
- parse Closed-Phase Ledger table rows in phase audit
- make telemetry emission non-blocking and guard builders
- recompute corrupt metrics cache; atomic write
- cap publish issue title and fix notes status filter
- make notes round-trip safe and ID-stable
- preserve backlog tasks_done and surface packet move failures
- gate suggest accept pick-up on active task

### Documentation
- finalize v0.4.0 Phase 32 status; add v0.5.0 backlog items
- correct to plan-only reality; de-risk WARDRIVE prep
- WARDRIVE prep — Scry Core publish plan, status reconcile, Apollo migration packet, IP separation
- sync diwa product docs with FI decisions
- plan v0.4.0 Proactive Assistance (Phase 32, 10 packets)
- update ip_and_licensing
- add source-available positioning; extend landscape (Webrecorder, Firecrawl, Crawlee)
- define open-core boundary; mark BSL + boundary done

### Features
- extract publishable public Scry Core; correct plan-only doc errors
- add phase_status_consistency docs-audit check
- add opt-in Pulse telemetry emission foundation
- add grain metrics for per-phase velocity tracking
- add github feedback report and notes publish
- implement queryable notes friction inbox
- archive task packets on phase close and surface in show
- add suggest engine and workflow-next surfacing
- add POST /skills/create_grain_task to execute the confirmed task-creation skill
- add create_task MCP write tool + create_grain_task Grimoire skill
- add GET /overview endpoint for the Sovereign Today screen
- wire Today screen onto Ironvale shell with mocked overview data
- add ChatSurface and ItemCard to the app shell tier
- add app shell tier — AppShell, AppNav, ScrollArea for the Sovereign/Sanctum apps
- scaffold Phase 1 — fleet manifest + status/deploy/logs CLI; fix datalake CCX23

# Changelog

All notable changes to grain-kit are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
Versioning: [Semantic Versioning](https://semver.org/)

---

## [0.3.1] — 2026-06-12

### Added
- **`grain workflow guard`** — standalone enforcement command; runs packet, phase, branch, and docs checks; callable from git hooks, CI, or any agent without invoking the full workflow runner
- **`grain hooks install`** — writes pre-commit and post-checkout git hooks that run `grain workflow guard` automatically; `grain hooks list` and `grain hooks remove` included
- **`grain docs audit`** — 18 read-only workspace health checks across 6 doc types; `--doc`, `--severity`, and `--fix` flags; `grain workflow guard --check-docs` integration
- **`grain archive`** — phase close snapshots (automatic), milestone snapshots, and point-in-time snapshots; `grain archive snapshot`, `grain archive milestone`, `grain archive list`, `grain archive show`, `grain archive prune`
- **`grain doctor`** — install-mode detection (`editable`/`installed`/`dev`), version/source alignment checks, workspace resolution report; `--format json` output
- **`grain status`** — single workspace-state command combining workflow state and docs health; reads caches (<5 min / <10 min TTL) to stay under 1s; `--format json` output
- **`grain notes add/list`** — stub for logging workflow friction and observations to `docs/working/tooling_notes.md` with structured table rows; full implementation in Phase 37
- **`grain init --name/--type` flags** — substitute project name and type into the seeded `docs_manifest.yaml` at init time; reminder banner when `--name` is omitted
- **`grain upgrade --add-missing`** — detects and seeds absent seeded files without overwriting existing ones
- **`upgrade_policy` manifest block** — workspaces declare `min_version`, `enforce`, and `enforce_after_days`; Grain warns on version mismatch or blocks with exit code 2 in enforce mode; `GRAIN_SKIP_VERSION_CHECK=1` escape hatch logs to `tooling_notes.md`; `grain upgrade` ratchets `min_version` after every successful run
- **`branch_policy` manifest block** — opt-in branch enforcement (`mode: phase`, `mode: task`, or `off`); warn-only or `wrong_branch` stop reason with a suggested branch name; `GRAIN_SKIP_BRANCH_CHECK=1` escape hatch; `grain workflow guard` check #5
- **Stop reason constants** — 18 module-level string constants in `workflow_service.py` replacing all inline string literals; `STOP_WRONG_BRANCH` added
- **`WorkflowEvaluation.suggested_branch`** — new field populated on `wrong_branch` stop reason; gives agents an actionable `git checkout -b` target without prose parsing
- **`grain --version` install mode** — version output now includes `(editable)`, `(installed)`, or `(dev)` suffix
- **13 new scaffold templates** — `product_scope.md`, `architecture.md`, `decisions.md`, `landscape_canonical.md`, `landscape_working.md`, `backlog.md`, `current_focus.md`, `open_questions.md`, `change_proposals.md`, `roadmap.md`, `current_task.md`, `CHANGELOG.md`, `workflow_metrics.md` — seeded by `grain init`
- **`Suggested Action` field** on open question and change proposal templates
- **`workflow.resume.md` prompt** — agent-agnostic session resume protocol seeded in every new workspace
- **Phase close archives** — `grain phase close` now automatically snapshots working docs to `docs/archive/phases/phase-{N}/`

### Changed
- `grain workflow next` evaluation post-processed by `_apply_branch_policy_check` — branch warning added to `evaluation.warnings` in warn mode; text output renders warnings to stderr
- `grain workflow guard` refactored from a stub to a real enforcement service with 5 named checks; `--check-docs` and `--check-dev-alignment` flags added
- `PROJECT_RULES.md` hardened with packet-first and branch discipline rules
- `docs_manifest.yaml` gains `branch_policy` and `upgrade_policy` blocks (seeded off/empty by default)
- `AGENTS.md` generation updated to reference `workflow.resume.md`
- `docs/runtime/docs_manifest.yaml` `tooling_notes read_when` fixed from `never` to `["encountering_blockers", "logging_friction"]`

### Fixed
- `grain workflow next` stale `current_task.md` pointer to a done-task packet now produces `stale_task_pointer` stop reason instead of blocking the runner silently
- `grain phase close` `--phase` flag now accepted correctly (was incorrectly rejected in some invocations)
- `grain --format json workflow next` flag-order fix (`--format` is a group-level flag, not a subcommand flag)

---

## [0.3.0] — 2026-06-11

### Added
- **TUI foundation** (`grain tui`) — Textual-based terminal operator shell with workflow dashboard, current task/phase view, backlog-by-phase list, packet artifact inspector, prompt preview, and context bundle inspector
- **Writable office workflows** — `.docx` and spreadsheet `propose`/`export`/`apply` write modes with review bundles, structural validators, and safety modes; every write is packet-scoped and requires a review surface before close
- **Verification bridge** — `grain verify submit`, `grain verify status`, `grain verify ingest`; verification-aware review/close gating so the workflow runner stops at a verification gate when a result is pending
- **`grain workflow explain`** — surfaces the current workflow state and reasoning in human-readable form; useful for onboarding and debugging stuck workflows
- **Writable office adapters** — shared `.docx` and spreadsheet write contracts, validators, and review-bundle pipeline; `office_adapter` and `spreadsheet_adapter` extended with propose/export write surfaces
- **Non-code review model** — every non-code artifact write emits a structured review bundle (touched paths, operation mode, change summary, validator results, residual risk notes) before the task can close

### Changed
- Grain/Assay operator loop guidance hardened in prompts and runtime docs — earlier misuse blockers, clearer packet-local verification flow
- Runner packet/template hydration and activation state sync improved — reduces live-session agent redirection
- Workflow engine more resilient to drift: stale `current_task.md` pointers to done-task packets no longer block or confuse the runner
- `grain workflow reconcile --fix` extended to cover office-artifact state drift
- Packet-first guardrails tightened across execution prompts and agent instructions

### Fixed
- Archived-packet-aware task ID allocation — `TASK-XXXX` counter stays globally monotonic even after packets are archived
- Terminal project-complete workflow state now routes cleanly without blocking future workflow queries
- Safer upgrade behaviour for repos with customised managed files — skips with warning instead of overwriting

### Notes
- `Development Status :: 3 - Alpha` retained — TUI is first slice; no embedded agent terminals, multi-project views, or live collaboration yet
- Homebrew remains deferred; `pip install grain-kit` and `uv tool install grain-kit` are the supported install paths
- v0.4.0 direction: composable recipe execution, explicit Grain ↔ toolkit contracts, safer in-place mutation paths

---

## [0.2.0] — 2026-04-23

### Added
- `grain phase close`, `grain phase archive`, and stronger phase-boundary enforcement so phases must be explicitly sealed before the workflow advances
- `grain workflow run` auto-activation/bootstrap behavior, `grain workflow reconcile --fix`, and broader runner integration coverage for state drift repair
- semantic enrichment and ranking layers for context selection, including embedding-provider support and ranked decision scaffolding across Phases 16 and 17
- `data_adapter` support for richer notebook/data-project context and Phase 18 data-surface handling
- community adapter registry foundations from Phase 19, including install/discovery work for community-shared adapters
- real CI coverage in GitHub Actions for test execution plus build and `twine check`
- release-surface regression tests for shipped prompt indexes, formula metadata, and packet-first prompt/runtime guardrails

### Changed
- active tasks with execution artifacts now route to review instead of continuing to report `task_execute`
- task ID allocation now scans archived packets so `TASK-XXXX` stays globally monotonic
- workflow evaluation now ignores stale `current_task.md` pointers to packets already marked `done`
- `grain upgrade` skips customized managed files by default in non-interactive mode and reports them as `skipped_customized`
- shipped execution prompts, runtime guidance, and generated AGENTS instructions now enforce packet-first execution more explicitly
- bundled prompt/docs indexes, README, and release guidance were hardened for public distribution and CI visibility

### Fixed
- completed projects can now use a terminal `complete` state without breaking phase parsing
- shipped prompt/docs assets no longer leak local absolute paths or stale repo identity references
- workflow-state surfaces are more resilient to real-world drift discovered across multiple Grain-managed repos

### Notes
- `Development Status :: 3 - Alpha` remains intentional for `0.2.0`; TUI/GUI work is still deferred
- Homebrew remains deferred as a release path; the in-repo formula still needs a real `0.2.0` artifact URL and sha256 before it should be treated as publish-ready

---

## [0.1.11] — 2026-04-16

### Added
- `grain upgrade` now seeds missing working docs added in later Grain versions (`tooling_notes.md`, `workflow_metrics.md`) — existing projects get them on next upgrade without overwriting anything
- `grain upgrade` now detects locally customized Grain-managed files (user-added content in prompts/templates) and warns before overwriting with a prompt to use `--interactive`; `customized` field added to JSON output
- `grain workflow next` now distinguishes a phase with no tasks defined yet (`stop_reason: phase_has_no_tasks`) from a completed phase awaiting close (`phase_boundary_review_close_required`)
- `grain workflow next` tips updated: suggests `grain task create` when a ready backlog task has no packet yet

### Changed
- `tooling_notes.md` now has structured columns: `Type` (`bug | friction | question | note`) and `Status` (`open | addressed | wontfix | escalated`) — enables Assay to triage entries later
- `grain upgrade` always computes diffs internally to power customization detection; diffs only surfaced in output when `--diff` or `--interactive` is passed

---

## [0.1.10] — 2026-04-15

### Added
- `grain task create --simple`: minimal packet mode (task.md + results.md only) for small mechanical tasks; sets `Mode: simple` in task metadata so `grain task prepare` skips planning file requirements
- `docs/working/tooling_notes.md` bundled in every onboarded project: lightweight agent-writable inbox for mid-session workflow friction and tool observations (pre-formatted markdown table)
- `docs/working/workflow_metrics.md` now created by `grain onboard` — was missing, causing `docs validate` to fail on freshly onboarded repos

### Changed
- `grain task prepare` now detects stub planning files: if `context.md`, `plan.md`, or `deliverable_spec.md` still contain `TASK-####` template placeholders, they are reported as `stub packet file: <name>` and block `ok` status
- `grain task prepare` outputs a tip suggesting the execute prompt when stub files are detected — non-blocking, user choice
- `grain onboard` no longer triggers the managed-file upgrade staleness hint: suppressed for `onboard` invocations since files are seeded fresh from the current bundled version
- `grain workflow next` now returns `stop_reason: bootstrap_incomplete` with `recommended_prompt: prompts/workflow.onboard.existing.md` after fresh onboarding, instead of a hard parse error
- `docs/working/current_task.md` onboard stub now uses machine-parseable bootstrap fields (`Task ID: none / Task Path: none / Status: unset`) instead of prose placeholder
- `docs/working/current_focus.md` onboard stub now includes `Phase 0 — Bootstrap` marker so the workflow engine parses it cleanly
- `prompts/workflow.onboard.existing.md` now documents the two-phase onboarding boundary and expected bootstrap-state outputs

### Fixed
- `docs validate` no longer fails immediately after `grain onboard` due to missing `workflow_metrics.md`
- `grain workflow next` no longer hard-errors on bootstrap state after fresh onboarding
- Managed-file drift warnings no longer appear at the top of `grain onboard` output

---

## [0.1.9] — 2026-04-14

### Added
- first-class review hardening for conversational workflows:
  - `needs_fix` packet state in the seeded manifest and task lifecycle contract
  - structured `User Review`, `Verification Review`, and `Closure Decision` sections in `results.md`
  - explicit completion-policy fields for user approval and optional verification gating
- review and handoff services now surface `user_review_state` and `verification_state` as first-class output fields

### Changed
- seeded runtime manifests now define the stable close policy explicitly:
  - `require_user_approval: true`
  - `require_verification_pass: false`
  - `allow_close_when_verification_not_run: true`
- task templates and bundled prompts now use the structured review bundle instead of the older `Review Intake` wording
- `grain task close --quick` now writes a closure-ready structured review bundle compatible with the stricter completion policy

### Fixed
- closure, review, and handoff flows now agree on the same review-state model instead of mixing legacy prose-only review fields with newer parser logic
- bundled docs and canonical data-contract docs now document `needs_fix` and the expanded completion policy expected by the stable runtime

---

## [0.1.8] — 2026-04-14

### Added
- `grain task close --quick` — minimal closure for conversational and voice workflows
  - Accepts `--summary TEXT` and optional `--files PATH` (repeatable)
  - Writes a lightweight `results.md` and marks the packet `done` without requiring `handoff.md` or efficiency metrics
- `grain workflow next` gate for incomplete tasks: if an active task is `in_progress` and has no `results.md`, the workflow surfaces a `execution_in_flight` stop signal before allowing any further action — prevents agents from silently skipping task closure in voice-chat workflows
- `grain onboard` now detects existing code modules and warns of code-ahead-of-backlog risk
  - `CodebaseScanner` detects top-level packages under `src/`, `lib/`, `app/`, and repo root; stored in `ScanResult.detected_modules`
  - `backlog.md` gains a "Retrospective Review Required" section listing detected modules when code is found, with explicit instructions to audit before treating the generated backlog as authoritative
  - `open_questions.md` adds a structured question surfacing detected modules and risk when code is ahead of backlog

### Fixed
- `grain onboard` now pre-populates canonical draft docs from existing repo content instead of leaving blank placeholders
  - `product_scope.md` pulls from README, `package.json` description, or `pyproject.toml` metadata
  - `architecture.md` pulls from existing `architecture.md`, `design.md`, or similar docs if found
  - Both fall back to clearly labelled placeholders when no source is available
- `open_questions.md` now surfaces a structured question listing all existing docs found outside the canonical layer, so maintainers know exactly what to incorporate
- `CodebaseScanner` extended with content extraction: reads README, architecture docs, scope/vision docs, `package.json`, and `pyproject.toml`; content capped at 2000 chars per file
- `ScanResult` gains `existing_doc_content` field (`dict[str, str]`) and `detected_modules` field (`list[str]`) carrying extracted content and module signals into the generator
- Draft marker changed from `# DRAFT` comment to HTML comment (`<!-- DRAFT — ... -->`) so it doesn't render as a heading
- `grain workflow loop` correctly routes `execution_in_flight` state: supervised mode stops with `supervision_required`, autonomous/gated modes invoke the executor so the agent can complete the task

---

## [0.1.7] — 2026-04-14

### Added
- `grain:` config block in `docs_manifest.yaml` — project-level defaults for `default_supervision`, `default_format`, `upgrade_check`, and `embedding_provider`
- `load_grain_config()` in `manifest.py` — reads the `grain:` block with safe defaults for any missing or invalid field
- `upgrade_check: warn` support — when set in project manifest, any `grain` command prints a one-line hint if Grain-managed files are stale
- `--format` now falls back to `grain.default_format` from project config when not passed as a CLI flag

### Fixed
- `PROJECT_RULES.md` §11 "Non-Goals for v1" replaced with a generic placeholder — the previous list described Grain's own non-goals, not the user's project
- `workflow_loop.yaml` — removed internal `Assay (FR-005)` reference; replaced `codex`/`gpt-5.4` example agent config with `claude`/`claude-opus-4-5` and clear comments that these should be customized
- `docs_manifest.yaml` template — `project.name: Grain` and `project.type: cli_toolkit` replaced with user-facing placeholders; `read_when: planning_v2` removed from adapter_profiles entry
- `phase.plan.next.md` — removed hardcoded references to Grain's internal `v2_plan.md`, `v2_adapters.md`, `v2_onboarding.md`; replaced with a generic instruction to read any planning docs declared in the manifest

---

## [0.1.6] — 2026-04-14

### Added
- `grain upgrade --diff` — shows unified diffs (red/green lines) for stale files without writing anything
- `grain upgrade --interactive` (`-i`) — walks each stale file, shows its diff, and prompts accept/skip/quit per file; only accepted files are written
- `grain upgrade --format json` now includes a `diffs` key with per-file diff strings when used with `--diff`

### Fixed
- Bundled `PROJECT_RULES.md` no longer contains "The project is a CLI-first toolkit..." — that line described Grain itself and was wrong in user project contexts
- Bundled `agent_profiles.md` no longer says "routing behavior for Grain" — changed to "for this project"

---

## [0.1.5] — 2026-04-13

### Added
- `grain upgrade` command — updates Grain-managed prompts, task templates, and safe runtime docs to the current installed version without touching user-owned files
  - `--dry-run` to preview what would change
  - `--format json` for machine-readable output
  - Never touches: canonical docs, working docs, task packets, `docs_manifest.yaml`, `adapter_profiles.md`

---

## [0.1.4] — 2026-04-13

### Added
- Wrapper prompts (`task.execute.md`, `task.review.md`, `task.close.md`, `task.plan.next.md`) now explicitly dispatch to their full implementation prompts — no more hollow stubs
- `docs/working/implementation_plan.md` is now seeded by both `grain init` and `grain onboard` — fixes missing file on first execute run
- `context.md` task template now includes an Adapter Context section (primary adapter, secondary adapters, rationale)
- `results.md` efficiency tracking fields now marked optional with `n/a` fallback for non-Grain projects

---

## [0.1.3] — 2026-04-13

### Added
- `grain onboard` now seeds runtime docs, task templates, and prompt files additively — existing project users get a fully functional Grain setup, not just directory stubs
- Codebase scanner now detects specialized project domains and suggests custom adapters in `open_questions.md`:
  - DevOps/infrastructure (Dockerfile, Terraform, HCL) → suggests `devops_adapter`
  - Data science (notebooks, parquet, HDF5) → suggests `data_adapter`
  - Mobile (Swift, Kotlin) → suggests `ios_adapter` / `android_adapter`
- `ScanResult` domain model gains `custom_adapter_hints` field

### Fixed
- `grain onboard` stub files used escaped newlines (`\\n`) instead of real newlines — stubs now render correctly
- Removed residual `forge` references from bundled runtime docs

### Changed
- README rewritten for clarity — tighter structure, added Why Grain section, agent CLI usage guidance
- README badges updated: PyPI version, Python versions, license, CI, downloads

---

## [0.1.2] — 2026-04-13

### Added
- Jupyter notebook (`.ipynb`) support — `NotebookExtractor` extracts markdown cells, code cells with outputs, and raw cells
- `.ipynb` added to `code_adapter` relevant file patterns
- Contributing / Feedback section added to README with GitHub Issues link

### Changed
- `export.py` renders `.ipynb` sources through `NotebookExtractor` alongside existing extractors

---

## [0.1.1] — 2026-04-12

### Fixed
- Bundled runtime, template, and prompt files are now correctly included in the PyPI package — `grain init` and `grain onboard` work after `pip install` or `uv tool install`
- PyPI project URLs corrected in `pyproject.toml`

---

## [0.1.0] — 2026-04-12

Initial public release.

### Included
- `grain init` — scaffold new projects with canonical, working, runtime, task, and prompt layers
- `grain onboard` — additive scaffold for existing repos with codebase scanning and draft doc generation
- `grain workflow next/run/loop` — state-driven workflow runner with supervised, gated, and autonomous modes
- `grain task create/list/show/next/prepare/validate/status` — task packet lifecycle management
- `grain context build/show/export` — minimal context assembly with graph-assisted source selection
- `grain docs validate` — doc manifest and structure validation
- `grain orchestrate scope/plan/accept` — orchestration proposals and plan ordering
- `grain adapter list/show` — adapter profile inspection
- `grain prompt show` — recommended prompt for current workflow state
- Adapters: `code_adapter`, `frontend_adapter`, `docs_adapter`, `spreadsheet_adapter`
- Extractors: `SpreadsheetExtractor`, `DocsExtractor`, `PdfExtractor`
- Tree-sitter knowledge graph for graph-assisted context selection
- Automated workflow loop with per-step logging and supervision levels
- PyPI publish workflow via GitHub Actions with OIDC trusted publishing
