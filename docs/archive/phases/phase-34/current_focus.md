# Current Focus

## Current Phase
Phase 34 — v0.5.0 Recipe Engine (Step-Runner) MVP

> **Status:** v0.5.0 (recipe step-runner + Apache-2.0 relicense) is **shipped** — grain-kit
> 0.5.0 live on PyPI (2026-07-07, release run 28845125357: test → build → publish → mirror
> sync → GH Release). Phase 36 closes the punch-list between a working 0.5.0 and a clean
> public release. Active packets `P36-T14-TASK-0223` and `P36-T15-TASK-0224` are in review.
> **Next:** demo readiness for the late-July 2026 live demo, then lock v0.6.0 scope —
> see `docs/working/v0.5.0_contract.md` §2 (general-purpose workspaces, `grain recipe
> suggest`, signal inbox, apply graduation, engine contract).
> **Last shipped:** v0.5.0 (2026-06-28, published to PyPI 2026-07-07)

All execution phases through Phase 32 are CLOSED. The Closed-Phase Ledger below is the
authoritative one-line status of every closed phase; full task detail lives in
`tasks/archive/phase-{N}/` and `docs/archive/phases/phase-{N}/`. This file names the
focus; `docs/working/backlog.md` owns task state.

## Immediate Priorities
1. Demo readiness for the late-July 2026 live demo: fix the bootstrap health errors, the
   `grain init` staleness nag, and the `grain orchestrate` graph crash.
2. Close the two in-review packets (`P36-T14-TASK-0223`, `P36-T15-TASK-0224`).
3. Refresh public docs to match shipped reality: `ROADMAP.md` (still claims v0.3.1),
   `README.md` command coverage, GitHub org links.
4. Start the v0.6.0 scope pass — see `docs/working/v0.5.0_contract.md` §2 (general-purpose
   workspaces, recipes, signals, apply graduation, engine contract, token-budget proxy).
5. (Separately) push the `scry-wip` branch's Scry/WARDRIVE commits via their own path.

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
| 32    | v0.4.0 Proactive Assistance | 2026-06-25 | 10 | v0.4.0 |

v0.1.x (v0.1.0–v0.1.11) and v0.2.0 are COMPLETE and PyPI-published.
v0.3.0 and v0.3.1 shipped (v0.3.1 at Phase 31 close); v0.4.0 implementation complete
on main, pending `trace release`.

## Upcoming Phase Sequence
1. v0.5.0 — composable toolkit + general-purpose workspaces + safe apply (see
   `v0.5.0_contract.md`); phase breakdown locked in a dedicated v0.5.0 planning pass.

Phase 32 closed: 2026-06-25 — 10 tasks done (grain-verified)

Phase 34 closed: 2026-07-09 — 9 tasks done (grain-verified)
