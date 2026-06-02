# Grain — Project State

**Produced:** 2026-06-02
**Phase:** 30 (planning not started)
**Source:** Diwata-Infra Phase 17 audit (P17-T01)

---

## Versions Shipped

| Version | Theme | Key Deliverables |
|---|---|---|
| v0.1.0 | Foundation | CLI core, task packets, context assembly, document/spreadsheet adapters, model routing |
| v0.1.x (patches) | Stabilization | `grain upgrade`, notebook support, `--simple` task mode, stub detection, bootstrap state fix, tooling_notes, upgrade customization guard |
| v0.2.0 | Intelligence + Domain Expansion | Semantic enrichment (BM25/Ollama/Local/OpenAI embedding providers), ranking + decision layer, data adapter, community adapter registry, workflow hardening (`grain phase close`, `grain workflow reconcile`, `AGENTS.md` generation) |
| v0.3.0 | Operator Surface for Structured Knowledge Work | TUI (Textual), writable office artifacts (`propose`/`export`/`apply` safety modes), Obsidian adapter, database adapter, crawler adapter, Assay verification bridge (`grain verify`), workflow compliance hardening |

**Test count at v0.3.0 close:** 775+ tests passing across all phases.

---

## Current State

**Version:** v0.3.0 — complete  
**Active phase:** Phase 30 — v0.4.0 planning (not started, no task packets yet)  
**Branch state:** `main` is release state; `dev` is the execution branch; `hotfix` for v0.3.x patches

**What Phase 30 is:** The v0.4.0 milestone contract phase. Same structure as Phase 21 (v0.3.0 planning): lock the theme and core deliverables, define scope boundaries, seed execution phases. No implementation in Phase 30.

---

## v0.3.0 Delivery Summary (Phases 21–29)

| Phase | Scope | Status |
|---|---|---|
| Phase 21 | v0.3.0 planning — milestone contract, TUI stack (Textual), office write model, desktop integration strategy, Obsidian adapter decision | CLOSED |
| Phase 22 | TUI foundation — Textual shell, workflow dashboard, inspector views, action launchers, TUI preview panels | CLOSED |
| Phase 23 | Writable office artifacts — `.docx` and spreadsheet `propose`/`export`/`apply` flows, review bundles, validators | CLOSED |
| Phase 24 | Desktop integrations + Obsidian — MCP wrapper, Codex CLI guidance, `obsidian_adapter` | CLOSED |
| Phase 25 | Database adapter — `database_adapter` profile, schema context, migration awareness | CLOSED |
| Phase 26 | Crawler adapter — `crawler_adapter` profile, web resource context support | CLOSED |
| Phase 27 | Workflow recipes (stretch) — recipe planning layer, recipe packet scaffolds | CLOSED |
| Phase 28 | Assay verification bridge — `grain verify submit/status/ingest`, verification-aware review/close gating | CLOSED |
| Phase 29 | Workflow compliance hardening — stronger loop guidance in AGENTS.md/CLAUDE.md/prompts, runner sync improvements, `grain workflow explain` | CLOSED |

---

## v0.4.0 Direction

**Theme:** `Composable Workflow Toolkit and Safe Real Mutation`

**Core deliverables (from `current_focus.md`):**
- First-class recipe execution: `grain recipe ...` command group, not just recipe planning
- Explicit shared contracts between Grain and sibling toolkit apps (Assay, future Conclave)
- Safer in-place mutation paths for office and vault artifacts where validation is strong enough
- Dev/runtime alignment: active repo code and invoked CLI surface stop drifting apart
- Richer operator/debugging ergonomics built on the already-landed TUI and workflow diagnostics

**Candidate deliverables:**
- `grain recipe` command group and recipe packet scaffolds
- Toolkit contract artifacts and transport-neutral exchange model
- `.docx` / spreadsheet / Obsidian `apply` graduation criteria and first safe apply slices
- Source-tree or version-alignment diagnostics
- Cross-tool handoff examples that do not rely on chat memory

**Explicit non-goals for v0.4.0:**
- Hosted services or background daemons
- Broad new adapter families beyond what v0.3.0 introduced
- Replacing the CLI as the canonical surface
- Sentinel work (FR-005)
- Broad new adapter expansion

---

## Open Questions at Phase 30 Entry

From `docs/working/open_questions.md` — unresolved items that are relevant to v0.4.0:

- **Q20 (if exists)** — Tooling-notes schema migration (deferred from Phase 20; still draft status in P20-T07)
- **Recipe contract:** What exactly is the unit of reuse in `grain recipe`? Is it a prompt, a packet template, a workflow slice, or all three?
- **Toolkit contract format:** What serialization / transport does the Grain ↔ Assay ↔ Conclave contract use? JSON files? Event stream? CLI subprocess?
- **`apply` graduation:** What validation threshold must a change writer reach before `propose` → `apply` is safe?

These should be decided in Phase 30 task P30-T01 or P30-T02 before execution phases are seeded.

---

## Landscape Summary

See `docs/canonical/landscape.md` (seeded in P17-T02). Key reference points:
- Linear / GitHub Projects: task management, not workflow orchestration
- Claude Code / Cursor / Codex: execution surfaces, not workflow state managers
- LangGraph / AutoGen: agentic frameworks, not workflow kernels
- Obsidian: file-backed knowledge; influenced Grain's docs-as-files model
- GNU Make / git: discrete, reviewable units; influenced task close/review model

---

## What Is Not on the Roadmap

Hard non-goals (from ROADMAP.md):
- GUI or web dashboard
- Database-backed state
- Cloud-hosted workflow execution
- Vendor lock-in to any specific AI provider
- Multi-user collaboration / team features (explicitly deferred to v4+ if ever)

---

## Stale Documentation Alert

The public `ROADMAP.md` was NOT updated when v0.2.0 shipped or when v0.3.0 scope was locked. It still shows v0.2.0 under "Next" and lists `grain workflow reconcile` under "Under Consideration" — which shipped in Phase 15. The ROADMAP.md should be updated as part of Phase 30 or a v0.3.0 release finalization task.
