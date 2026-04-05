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

None currently deferred.
