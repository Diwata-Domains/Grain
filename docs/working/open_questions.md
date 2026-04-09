# Open Questions

## 1. Purpose

Tracks unresolved implementation or design questions that may affect execution.

Questions here must not silently change canonical behavior.
If a question affects canonical rules, architecture, contracts, or workflow semantics, it must move through a change proposal before becoming authoritative.

---

## 2. Status Definitions

* `open` — unresolved, not currently blocking
* `blocking` — unresolved and preventing task or phase progress
* `decision_needed` — ready for human decision
* `escalated` — moved into change proposal flow
* `resolved` — decision made and applied
* `deferred` — intentionally postponed to a later phase

---

## 3. Open Questions

### Q7 — How should context export be represented in v1?

* **Status:** resolved
* **Resolution:** Single assembled markdown file with a metadata header listing sources. `--format json` emits structured source metadata only (not full content). No directory bundle or sidecar in v1.
* **Resolution Type:** working-doc update
* **Decision By:** agent (Phase 4 planning — recommend human confirm or override)
* **Decision Date:** 2026-04-03
* **Affected Docs:** `backlog.md` (P4-T07 ready)
* **Related Tasks:** P4-T07

---

### Q8 — Where should model profile configuration live?

* **Status:** resolved
* **Resolution:** Parse `docs/runtime/agent_profiles.md` (already exists, already manifest-registered) as the model profile source in v1. No new YAML config file needed. Dedicated config deferred to later phases if required.
* **Resolution Type:** working-doc update
* **Decision By:** agent (Phase 4 planning — recommend human confirm or override)
* **Decision Date:** 2026-04-03
* **Affected Docs:** `backlog.md` (P4-T08 ready)
* **Related Tasks:** P4-T08

---

## 4. Resolved Questions

### Q16 — What is the minimal runner slice and stop-condition contract for Phase 8?

* **Resolution:** Lock Phase 8 to a one-step runner slice: determine one next legal workflow action, execute at most one step per invocation, and stop explicitly at blocked/review/phase-gate/validation-conflict conditions. Require stable machine-readable outputs for automation-relevant workflow commands (`workflow next`, `workflow run`, `phase next`, `task next`, `task prepare`, `prompt show`).
* **Resolution Type:** working-doc update
* **Decision By:** Shaznay
* **Decision Date:** 2026-04-07
* **Applied By:** codex
* **Applied Date:** 2026-04-07
* **Affected Docs:** `docs/working/v2_plan.md`, `docs/working/backlog.md`, `docs/working/current_focus.md`
* **Related Tasks:** P8-T01, P8-T02 through P8-T09

### Q15 — What caused the `P7-T07` blocked-status drift after `P7-T06` closed?

* **Resolution:** The drift came from working-doc updates landing in separate steps without a final reconciliation pass. `P7-T06` was moved to `done`, later planning docs began treating the new-project onboarding slice as stable enough to move forward, but `P7-T07` kept an older `blocked until stable` state. This was a working-doc consistency error across `backlog.md`, `current_focus.md`, and `v2_onboarding.md`, not a runtime or CLI bug.
* **Resolution Type:** working-doc update
* **Decision By:** Shaznay
* **Decision Date:** 2026-04-07
* **Applied By:** codex
* **Applied Date:** 2026-04-07
* **Affected Docs:** `docs/working/backlog.md`, `docs/working/current_focus.md`, `docs/working/v2_onboarding.md`, `docs/working/workflow_metrics.md`
* **Related Tasks:** P8-T11
* **Follow-Up Direction:** solve this with three layers — checklist, explicit reconcile command, and runner validation

---

### Q14 — Is Sentinel the same thing as Forge self-improvement?

* **Resolution:** No. Forge self-improvement and Sentinel verification are separate but connected loops. Forge should improve itself by surfacing workflow friction, token waste, prompt drift, repeated manual fixes, and automation candidates as structured proposals. Sentinel should improve the overall system by producing structured verification evidence such as failed tests, bug findings, screenshots, traces, captured state, and human annotations. Both may create candidate follow-up work, but neither should bypass review or canonical change control.
* **Resolution Type:** working-doc update
* **Decision By:** Shaznay
* **Decision Date:** 2026-04-07
* **Applied By:** codex
* **Applied Date:** 2026-04-07
* **Affected Docs:** `docs/canonical/product_scope.md`, `docs/working/future_roadmap.md`, `docs/working/v2_plan.md`
* **Related Tasks:** future Sentinel bridge and advisory-planning work

---

### Q13 — Should every stable prompt have a matching CLI command?

* **Resolution:** No. Forge should not force a 1:1 mapping between prompts and commands. Commands should own deterministic operations, state transitions, validation, exports, and integration hooks. Prompts should remain the reasoning surface for planning, drafting, execution guidance, and judgment-heavy review. A prompt becomes a CLI candidate only when the step is repetitive, state-driven, and parameterizable without losing clarity.
* **Resolution Type:** working-doc update
* **Decision By:** Shaznay
* **Decision Date:** 2026-04-07
* **Applied By:** codex
* **Applied Date:** 2026-04-07
* **Affected Docs:** `docs/working/v2_plan.md`
* **Related Tasks:** future CLI automation planning

---

### Q12 — Should TUI/GUI work begin before CLI-first workflow automation?

* **Resolution:** No. The next operator-surface priority is CLI-first automation and machine-readable command outputs. Any future TUI should be a thin shell over the same file-backed state and command primitives. GUI work remains later and should follow proven demand outside the terminal-native user base.
* **Resolution Type:** working-doc update
* **Decision By:** Shaznay
* **Decision Date:** 2026-04-07
* **Applied By:** codex
* **Applied Date:** 2026-04-07
* **Affected Docs:** `docs/working/current_focus.md`, `docs/working/implementation_plan.md`, `docs/working/v2_plan.md`, `docs/working/future_roadmap.md`
* **Related Tasks:** future workflow automation / operator surface planning

---

### Q11 — What is the intended behavior of `forge context build` when no `--tag` flags are given?

* **Resolution:** When no `--tag` flags are supplied, `forge context build`, `forge context show`, and `forge context export` default canonical doc selection to the `running_tasks` tag set. Explicit `--tag` values replace that default for the invocation. Working docs remain opt-in through `--include-working`.
* **Resolution Type:** canonical update via CP-007
* **Decision By:** Shaznay
* **Decision Date:** 2026-04-05
* **Applied By:** codex
* **Applied Date:** 2026-04-05
* **Affected Docs:** `docs/canonical/cli_spec.md`, `docs/canonical/workflow_spec.md`
* **Related Tasks:** P4-T05, P4-T06, P4-T07

---

### Q5 — Should `docs index` be generated from manifest or validated as human-maintained?

* **Resolution:** Manifest is primary. `docs_index.md` is generated from manifest entries. `forge docs index` writes or refreshes the index; validators check consistency against the manifest.
* **Resolution Type:** working-doc update
* **Decision By:** Shaznay
* **Decision Date:** 2026-04-02
* **Applied By:** agent
* **Applied Date:** 2026-04-02
* **Affected Docs:** `backlog.md` (P2-T08 unblocked and rescoped), `open_questions.md`
* **Related Tasks:** P2-T08

---

### Q4 — How much packet metadata should be parsed from `task.md` in v1?

* **Resolution:** Parse `ID`, `status`, and `phase` from the `## Metadata` block in `task.md`. No deeper parsing (dependencies, etc.) required in v1.
* **Resolution Type:** working-doc update
* **Decision By:** Shaznay
* **Decision Date:** 2026-04-02
* **Applied By:** agent
* **Applied Date:** 2026-04-02
* **Affected Docs:** `backlog.md` (P3-T09, P3-T10 scoped accordingly)
* **Related Tasks:** P3-T09, P3-T10

---

### Q1 — CLI framework

* **Resolution:** Click 8.x chosen. Supports `forge <group> <subcommand>` natively.
* **Resolution Type:** working-doc update
* **Decision By:** Shaznay
* **Decision Date:** Phase 1
* **Applied By:** agent
* **Applied Date:** Phase 1
* **Affected Docs:** `pyproject.toml`, `cli/__init__.py`
* **Related Tasks:** TASK-0002

---

### Q2 — Repository root detection

* **Resolution:** Auto-detect by walking upward for `docs/runtime/PROJECT_RULES.md`; `--repo` override supported.
* **Resolution Type:** working-doc update
* **Decision By:** Shaznay
* **Decision Date:** Phase 1
* **Applied By:** agent
* **Applied Date:** Phase 1
* **Affected Docs:** `adapters/filesystem.py`
* **Related Tasks:** TASK-0004

---

### Q3 — `forge init` scope

* **Resolution:** Additive behavior — creates missing directories with `.gitkeep` placeholders, skips existing, `--force` flag available.
* **Resolution Type:** working-doc update
* **Decision By:** Shaznay
* **Decision Date:** Phase 1
* **Applied By:** agent
* **Applied Date:** Phase 1
* **Affected Docs:** `services/init_service.py`, `cli/init.py`
* **Related Tasks:** TASK-0005

---

### Q6 — JSON output surface

* **Resolution:** `--format text|json` global option implemented. Text is default; JSON serialises `CommandResult` fields. Applied to all implemented commands.
* **Resolution Type:** working-doc update
* **Decision By:** Shaznay
* **Decision Date:** Phase 1
* **Applied By:** agent
* **Applied Date:** Phase 1
* **Affected Docs:** `cli/output.py`
* **Related Tasks:** TASK-0007

---

### Q9 — Template rendering level

* **Resolution:** Plain markdown only. No rendering engine in v1. Loader reads and returns raw content.
* **Resolution Type:** working-doc update
* **Decision By:** Shaznay
* **Decision Date:** Phase 1
* **Applied By:** agent
* **Applied Date:** Phase 1
* **Affected Docs:** `templates/loader.py`
* **Related Tasks:** TASK-0006

---

### Q10 — `forge init` partial repo behavior

* **Resolution:** Additive with skip-existing. Canonical files protected. `--force` flag available.
* **Resolution Type:** working-doc update
* **Decision By:** Shaznay
* **Decision Date:** Phase 1
* **Applied By:** agent
* **Applied Date:** Phase 1
* **Affected Docs:** `services/init_service.py`
* **Related Tasks:** TASK-0005

---

## 5. Deferred Questions

### QD-01 — Where should `forge workflow reconcile` command spec land?

* **Status:** deferred
* **Context:** P8-T11 defined the three-layer reconciliation approach (manual checklist, reconcile command, runner validation) and documented the manual checklist. The `forge workflow reconcile` command spec and implementation are deferred until Phase 8 close or Phase 9 planning.
* **Planned Resolution:** Define the command in `docs/canonical/cli_spec.md` as a deferred surface (like the verify commands in P8-T10) during Phase 8 close or early Phase 9, then implement in a future task.
* **Blocking:** No current work is blocked.
* **Related Tasks:** P8-T11 (TASK-0071), P8-T10 (Sentinel bridge contract), future Phase 9 planning
