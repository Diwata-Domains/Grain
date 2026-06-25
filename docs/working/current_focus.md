# Current Focus

## Current Phase
Phase 32 — v0.4.0 Proactive Assistance

> **Status:** ACTIVE (seeded — 10 tasks, P32-T01 through P32-T10)
> **Milestone:** v0.4.0 (Theme: Proactive Assistance)
> **Last shipped:** v0.3.1 (Phase 31 close, 2026-06-12)

All execution phases through Phase 31 are CLOSED. The Closed-Phase Ledger below is the
authoritative one-line status of every closed phase; full task detail lives in
`tasks/archive/phase-{N}/` and `docs/archive/phases/phase-{N}/`. This file names the
focus; `docs/working/backlog.md` owns task state.

## Immediate Priorities
1. P32-T02 — implement `grain suggest` engine (foundation; gates T05)
2. P32-T06 — `grain notes` full implementation (gates T09 GitHub feedback)
3. P32-T03/T04 — phase-close task archiving + `grain archive show` packet list
4. P32-T10 — docs hygiene: `phase_status_consistency` check (founder-requested)

(P32-T01 — `grain suggest` spec — is satisfied by the canonical `suggest_spec.md` and is
marked done. See `backlog.md` Phase 32 for the full task list and dependencies.)

## Active Constraints
- local filesystem only; no background services or hidden state
- preserve the stable v1 workflow as the core
- keep workflow automation narrow: one guarded step per runner invocation
- preserve machine-readable CLI outputs for all automation-relevant commands
- all orchestration / suggestion outputs are proposals — no auto-creation of packets

## Do Not Work On Right Now
- Homebrew/tap distribution (deferred unless release priorities change)
- Assay internals — separate repo; only the Grain-side bridge contract is in scope
- telemetry transport/aggregation — Grain only emits (P32-T08); Pulse owns transport
- recipe / toolkit contract / apply graduation / non-code workspaces — these are v0.5.0
  (`docs/working/v0.5.0_contract.md`), not this release
- autonomous multi-step execution without an explicit operator gate

## Milestone Direction (v0.4.0)
- Theme: Proactive Assistance
- Core: `grain suggest`, phase-close task archiving, `grain notes` inbox, `grain metrics`,
  opt-in Pulse telemetry foundation, GitHub feedback (`grain report` + `grain notes publish`),
  docs hygiene
- Contract of record: `docs/working/v0.4.0_contract.md`
- Next milestone: `docs/working/v0.5.0_contract.md` (composable toolkit + general-purpose
  workspaces + safe apply)

---

## Closed-Phase Ledger
One line per closed phase. This is the single authoritative status list.
Anything described as "active" above must NOT appear here, and vice versa.

| Phase | Title | Closed | Tasks | Milestone |
|-------|-------|--------|-------|-----------|
| 1–5   | v1 core (foundation → review/hardening) | v1 close | 53 | v1 |
| 6     | Adapter System Foundation | 2026-04-06 | 7 | v0.1.0 |
| 7     | New-Project Onboarding Flow | 2026-04-08 | 7 | v0.1.0 |
| 8     | Workflow Automation Runner Foundation | 2026-04-09 | 11 | v0.1.0 |
| 9     | Orchestration Service Foundation | 2026-04-11 | 7 | v0.1.0 |
| 10    | Structural Intelligence (tree-sitter + graph) | 2026-04-11 | 6 | v0.1.0 |
| 11    | Distribution and Global Install (T05 deferred) | 2026-04-11 | 5 | v0.1.0 |
| 12    | Automated Workflow Loop | 2026-04-10 | 7 | v0.1.0 |
| 13    | Existing Project Adoption | 2026-04-12 | 8 | v0.1.0 |
| 14    | Document and Spreadsheet Adapters | 2026-04-12 | 7 | v0.1.0 |
| 15    | Workflow Hardening and Automation | 2026-04-17 | 6 | v0.2.0 |
| 16    | Semantic Enrichment Layer | 2026-04-21 | 8 | v0.2.0 |
| 17    | Ranking and Decision Layer | 2026-04-21 | 6 | v0.2.0 |
| 18    | Data Adapter | 2026-04-21 | 6 | v0.2.0 |
| 19    | Community Adapter Registry | 2026-04-22 | 6 | v0.2.0 |
| 20    | Workflow Drift Remediation | 2026-04-23 | 6 | v0.2.x |
| 21    | v0.3.0 Planning / Operator Surface | 2026-05-04 | 5 | v0.3.0 |
| 22    | TUI Foundation and Workflow Surfaces | 2026-05-04 | 6 | v0.3.0 |
| 23    | Writable Office Artifacts | 2026-05-05 | 6 | v0.3.0 |
| 24    | Desktop Integrations and Obsidian Support | 2026-05-06 | 5 | v0.3.0 |
| 25    | Database Adapter | 2026-05-06 | 5 | v0.3.0 |
| 26    | Crawler Adapter | 2026-05-06 | 5 | v0.3.0 |
| 27    | Recipe Layer and Operator Ergonomics | 2026-05-06 | 3 | v0.3.0 |
| 28    | Assay Verification Integration | 2026-05-07 | 5 | v0.3.0 |
| 29    | Workflow Compliance Hardening | 2026-05-07 | 5 | v0.3.0 |
| 30    | v0.4.0 Planning / Toolkit Boundary | 2026-06-11 | 14 | v0.4.0 |
| 31    | DX Hardening and v0.4.0 Foundation | 2026-06-12 | 8 | v0.3.1 |

v0.1.x (v0.1.0–v0.1.11) and v0.2.0 are COMPLETE and PyPI-published.
v0.3.0 and v0.3.1 shipped (v0.3.1 at Phase 31 close).

## Upcoming Phase Sequence
1. Phase 32 — v0.4.0 Proactive Assistance ← active now
2. v0.5.0 — composable toolkit + general-purpose workspaces + safe apply (see `v0.5.0_contract.md`);
   phase breakdown locked in a dedicated v0.5.0 planning pass after v0.4.0 merges.
