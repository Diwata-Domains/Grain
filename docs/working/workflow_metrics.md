# Workflow Metrics

## Project

Grain

---

## V1 Metrics (Phases 1–5)

### Phase 1

* Tasks completed: 9
* Blocked tasks: 0
* Prompt runs: 16
* Avg prompt runs per completed task: 1.8
* Manual interventions: 3
* First-pass success rate: 7/9
* Rework count: 2
* Drift incidents: 1
* Phase duration: Session 1

### Notes

### Phase 1
* What felt efficient: CLI scaffold went fast; error handling pattern established early
* What created friction: subprocess exit code mapping (standalone_mode vs cli() wrapper); test UnboundLocalError from import shadowing
* What to tighten next: establish exit code testing pattern before writing CLI tests

---

### Phase 2

* Tasks completed: 9 (P2-T01 through P2-T09, including P2-T08)
* Blocked tasks: 0 (P2-T08 unblocked after Q5 resolution and completed)
* Prompt runs: ~21 (tasks.packet.phase × 1, tasks.packet.next × 9, tasks.implement × 9, phase.review × 1, phase.close × 1)
* Avg prompt runs per completed task: 2.3
* Manual interventions: 4 (CP-001 approval, open_questions.md restructure, workflow_metrics.md creation, Q4+Q5 decisions)
* First-pass success rate: 7/9 (2 tests required fixes: exit code 3 mapping, docs show exit code)
* Rework count: 2
* Drift incidents: 0
* Phase duration: Session 2

### Notes

### Phase 2
* What felt efficient: validator pipeline composed cleanly; fixture refactor was straightforward once conftest pattern was set
* What created friction: CommandResult not designed for display-only commands (docs show needed custom text output path); exit code 2 from domain UsageError vs click.UsageError
* What to tighten next: clarify CommandResult usage pattern for inspection commands vs mutation commands before Phase 3 CLI work; resolve Q4 before P3-T09

---

### Phase 3

* Tasks completed: 13
* Blocked tasks: 0
* Prompt runs: ~28 (tasks.packet.phase × 1, tasks.next_and_implement × 13, phase.review_and_close × 1)
* Avg prompt runs per completed task: 2.2
* Manual interventions: 2 (Q4 decision, Q9 decision)
* First-pass success rate: 9/13 (4 tests required rework)
* Rework count: 4 (metadata regex colon placement, TASK-#### not substituted on create, print_result missing status field, _advance_to "done" left packets at review)
* Drift incidents: 0
* Phase duration: Session 3

## Notes

### Phase 3
* What felt efficient: service/validator/domain separation stayed clean throughout; subprocess exit code pattern from Phase 2 was directly reusable
* What created friction: metadata regex colon placement (`**key:**` vs `**key**:`) caused 5 test failures; TASK-#### substitution gap in create; custom text output needed for status command (CommandResult.status not rendered by print_result)
* What to tighten next: verify template substitution targets in integration test immediately after create; add status field to print_result or document the custom text output pattern before Phase 4 commands

---

### Phase 4

* Tasks completed: 13
* Blocked tasks: 0
* Prompt runs: ~5 recorded (T09–T13, 1 each); T01–T08 not captured retroactively
* Avg prompt runs per completed task: 1.0 (for tasks with recorded data)
* Manual interventions: 6 (CP-005 decision, CP-008 decision, CP-007 decision, Q11 decision, backlog sync fixes ×2)
* First-pass success rate: 11/13 (T09 required review rework; T12 self-loop bug caught at review)
* Rework count: 2
* Drift incidents: 0
* Phase duration: Session 4
* Tests at phase close: 349 (77 new tests added this phase)
* Conversation model: multi-agent (separate executor / reviewer / closer conversations)
* Token tracking: proxy metrics only — exact counts not available from runtime

### Phase 4 Measurement Focus

* Context bundle build success rate
* Average canonical docs selected per packet
* Optional working-doc inclusion rate
* Export success rate
* Model selection counts by class
* Escalation count between model classes
* Open-question turnaround time
* Exact prompt-run count per packet
* Exact drift count per packet and per phase
* Tokens per task when exact counts are available
* Tokens by stage: execute, review, close
* Conversation restart count
* Files read per stage
* Artifact rewrite count caused by format drift
* Review rework rate
* Context reload or restart events caused by contract changes

### Phase 4 Measurement Rules

* Use exact counts, not approximations
* Record denominators for every percentage or ratio
* Tag every metric entry with the relevant task packet ID
* Separate content metrics from routing metrics
* Record exact token counts when the runtime exposes them
* When exact token counts are unavailable, record proxy measures instead:
  * prompt runs
  * conversation restarts
  * files read estimated
  * artifact rewrites
* Count manual interventions by type:
  * approval decision
  * scope clarification
  * doc fix
  * schema or contract change

### Per-Task Efficiency Capture

Record the following in each task packet `results.md`:

* prompt runs
* conversation restarts
* files read estimated
* exact tokens if available
* short efficiency notes explaining major waste or savings

### Phase 4 Notes

* What felt efficient: routing domain composed cleanly from parsed profiles; context assembly reused doc registry from Phase 2 without friction; T10–T12 were thin CLI wiring tasks once domain was in place
* What created friction: stale backlog caused executor to select completed tasks (T09 selected by fresh executor after already done); per-stage efficiency tracking absent (single-agent template didn't match multi-agent reality)
* What to tighten next: per-stage efficiency now in template and prompts; backlog sync now in tasks.close.md; error message assertions in escalate/select tests deferred to Phase 5 hardening

### Phase Retrospective Classification

* **Fix now:** T13 task.md status (resolved during phase close)
* **Batch next phase:** error message assertions in model escalate/select tests; `test_model_show_missing_profile_file_exits_four` exit code specificity; workflow_metrics.md T01–T08 proxy data gap (not worth retroactive reconstruction)
* **Ignore:** `_ESCALATE_TO` parsing scope note from T08 handoff

---

### Phase 5

* Tasks completed: 9 (P5-T01 through P5-T09)
* Blocked tasks: 0
* Prompt runs: 19 (9 execute × 1 each + 9 review × 1 each + 1 close for TASK-0046)
* Avg prompt runs per completed task: 2.1
* Manual interventions: 1 (reviewer inline fix on TASK-0046 — CP-005 stubs + duplicate output)
* First-pass success rate: 8/9 (TASK-0046 required review fixes; all applied inline)
* Rework count: 0 (fixes applied during review, no executor rework required)
* Drift incidents: 0
* Phase duration: Session 5
* Tests at phase close: 379 (+30 new tests added this phase)
* Conversation model: multi-agent (separate executor / reviewer / closer conversations)
* Token tracking: proxy metrics only

### Phase 5 Notes

* What felt efficient: service/validator pattern from Phase 4 reused cleanly for review and handoff services; all review commands thin over existing services; CP-005 inline fix during review saved an executor rework round-trip
* What created friction: executor pre-filled review intake as "ready" before actual review ran — not wrong but slightly misleading; TASK-0046 reviewer found duplicate output bug and CP-005 violations that executor missed
* What to tighten next: executor should not pre-fill Review Decision; consider adding a CP for reviewer inline fix policy now that it is formalized in tasks.review.md

### Phase Retrospective Classification

* **Fix now:** none
* **Batch v2:** executor pre-filling Review Decision (low friction but slightly misleading); per-provider cli_cmd field in agent_profiles.md (see v2 planning discussion)
* **Ignore:** minor test count discrepancy in TASK-0046 results.md (6 actual vs 7 claimed by executor)

---

## V1 Aggregate

* Total tasks completed: 53 (Phases 1–5)
* Total blocked: 0
* Tests at v1 close: 379
* Open questions resolved during v1: Q1–Q11 (11 questions)
* Canonical change proposals applied during v1: CP-001 through CP-008 (8 applied)
* Major v1 additions: full CLI (init/docs/task/context/model/review), packet lifecycle, doc registry, context assembly, model routing, review/handoff/summary commands, integration tests, golden fixtures

---

## V2 Metrics (Phases 6–)

### Phase 6

* Tasks completed: 7 (P6-T01 through P6-T07)
* Blocked tasks: 0
* Prompt runs: 20 (7 execute × 1 each + 7 review × 1 each + 6 close × 1 each; P6-T01 close pre-filled as 0 by executor)
* Avg prompt runs per completed task: 2.9
* Manual interventions: 0 (no human decisions required; all review fixes applied inline by reviewer agent)
* First-pass success rate: 7/7 implementation ✓; review intake pre-fill error on all 7 tasks (Recommended Next Status incorrectly set to `review` by executor, corrected by reviewer inline)
* Rework count: 0 (implementation rework); 7 inline review corrections (systematic executor pre-fill)
* Drift incidents: 0
* Phase duration: Session 6
* Tests at phase close: 399 (+20 new tests from 379 at v1 close)
* Conversation model: multi-agent (separate executor / reviewer / closer conversations)
* Token tracking: proxy metrics only

### Phase 6 Notes

* What felt efficient: adapter domain/loader/context extension stayed additive throughout; model-loader pattern from Phase 4 reused directly; no canonical changes required; clean close sequence with no rework
* What created friction: executor systematically pre-fills `Recommended Next Status: review` in Packet State and `Definition of Done Met: no` before review runs — reviewer corrects inline, but it is a recurring artifact; executors also pre-fill Close efficiency section as `0 / execute stage only` which closer corrects
* What to tighten next: consider removing executor pre-fill of Review Intake and Close stage entirely from the execute template, or marking those sections as reviewer/closer-only to eliminate systematic correction overhead

### Phase Retrospective Classification

* **Fix now:** none
* **Batch next phase:** executor pre-fill of Review Intake fields (Recommended Next Status, Definition of Done Met) — remove or mark as reviewer-only in execute prompt template; executor pre-fill of Close efficiency section — mark as closer-only; `secondary_adapters` raw string normalization deferred until context services consume it
* **Ignore:** P6-T01 Close stage pre-filled as 0 (task was doc-only; no closer conversation used)

---

### Phase 7

* Tasks completed: 7 (P7-T01 through P7-T07)
* Blocked tasks: 0
* Prompt runs: 21 (7 execute × 1 each + 7 review × 1 each + 7 close × 1 each)
* Avg prompt runs per completed task: 3.0
* Manual interventions: 0
* First-pass success rate: 7/7 implementation and review-ready handoffs
* Rework count: 0
* Drift incidents: 0
* Phase duration: Session 7
* Tests at phase close: 419 (+20 new tests from 399 at Phase 6 close)
* Conversation model: multi-agent (separate executor / reviewer / closer conversations)
* Token tracking: proxy metrics only

### Phase 7 Notes

* What felt efficient: the onboarding slice stayed bounded across prompt, init, bootstrap, integration, and boundary-doc work; no canonical drift surfaced
* What created friction: recurring packet-template prefill noise in review/close fields persists across tasks, but it did not block closure
* What to tighten next: remove or relabel reviewer/closer-only fields in packet templates to reduce repetitive correction work

### Phase Retrospective Classification

* **Fix now:** none
* **Batch next phase:** packet-template prefill cleanup for review/close fields
* **Ignore:** none

---

### Phase 8

* Tasks completed: 11 (P8-T01 through P8-T11)
* Tasks blocked: 0 (P8-T10 was unblocked and completed)
* Prompt runs: ~33 (11 execute × 1 + 11 review × 1 + 11 close × 1)
* Avg prompt runs per completed task: 3.0
* Manual interventions: 0
* First-pass success rate: 11/11
* Rework count: 0
* Drift incidents: 1 (working-doc drift after P8-T09 — repaired by P8-T11)
* Phase duration: Sessions 8–9

---

### Phase 20

* Tasks completed: 6 (P20-T01 through P20-T06)
* Blocked tasks: 0
* Prompt runs: ~18 (6 execute/documentation passes + 6 review handoffs + 6 close passes)
* Avg prompt runs per completed task: 3.0
* Manual interventions: 0 (all review approvals were inline operator approvals, no design decisions required)
* First-pass success rate: 6/6 implementation slices landed without follow-up task splits
* Rework count: 0
* Drift incidents: 3 (stale `current_task.md` after close on TASK-0139 and TASK-0140; bundled/runtime context-loading drift surfaced during TASK-0140 activation)
* Phase duration: Session 20 hardening closeout on 2026-04-23
* Tests run during phase: targeted regression slices only (59 + 9 + 29 + 15 + 25 + 20 passing across task-local runs)
* Token tracking: proxy metrics only

### Phase 20 Notes

* What felt efficient: the workflow runner and reconciliation surfaces were strong enough to let six correctness fixes land and close in one continuous pass; the new review-routing and stale-task handling reduced manual state cleanup immediately.
* What created friction: immediate post-create `workflow run` occasionally needed a retry to activate a newly created packet; `workflow reconcile --fix` was still needed after task close to sync backlog/current_task state; phase-close still depends on a manually maintained metrics section.
* What to tighten next: remove the post-create runner retry quirk; reduce close-time doc drift so reconcile is exceptional rather than routine; consider making phase metrics easier to seed or derive.

### Phase Retrospective Classification

* **Fix now:** none required before Phase 21 planning starts
* **Batch next phase:** tooling-notes schema normalization, phase-close ergonomics, runner retry quirk after packet creation, broader release-surface once-over before v0.2.0 publish
* **Ignore:** one-off `__pycache__` churn from local test runs
* Tests at phase close: 494 (+75 new tests from Phase 7 close)
* Conversation model: multi-agent (separate executor / reviewer / closer conversations)
* Token tracking: proxy metrics only

### Phase 8 Notes

* What felt efficient: workflow state evaluator, runner, and command surfaces composed cleanly on top of the Phase 4 context assembly service; machine-readable JSON contract established early (P8-T01) kept later tasks aligned; P8-T10 unblocked cleanly once runner stop conditions were defined
* What created friction: working-doc drift between backlog.md and current_focus.md after P8-T09 close — P8-T09 marked done in backlog but current_focus.md kept it as in_progress; required explicit reconciliation task (P8-T11) to fix
* What to tighten next: apply the manual reconciliation checklist (v2_plan.md §9) at every task close to prevent this class of drift from recurring; `forge workflow reconcile` CLI implementation deferred to Phase 9+ (QD-01)

### Phase Retrospective Classification

* **Fix now:** none
* **Batch next phase:** `forge workflow reconcile` CLI implementation (QD-01); packet template cleanup for review/close prefill fields (carries over from Phase 7); `_find_packet_dir_for_ref` prefix-match robustness if task_ref format changes
* **Ignore:** exit code wording imprecision in P8-T08 deliverable_spec acceptance criterion 5 (functional behavior correct)

---

### Phase 9

* Tasks completed: 7 (P9-T01 through P9-T07)
* Blocked tasks: 0
* Prompt runs: ~21 (7 execute × 1 + 7 review × 1 + 7 close × 1)
* Avg prompt runs per completed task: 3.0
* Manual interventions: 0
* First-pass success rate: 7/7 implementation; systematic handoff.md Recommended Next Status pre-fill error on all 7 tasks (corrected inline by reviewer)
* Rework count: 0 (implementation rework); 7 inline review corrections (systematic executor pre-fill of handoff.md Recommended Next Status)
* Drift incidents: 1 (forge→grain package rename applied to T03-T07 without a change proposal — tracked as CP-009)
* Phase duration: Sessions 10–11
* Tests at phase close: 561 (+67 new tests from Phase 8 close)
* Conversation model: multi-agent (separate executor / reviewer / closer conversations)
* Token tracking: proxy metrics only

### Phase 9 Notes

* What felt efficient: domain model (T01) and capability protocol (T02) composed cleanly as pure domain tasks; service (T03-T04) built directly on the typed surface; CLI (T05-T06) thin wiring over existing services; validator + integration tests (T07) narrow and command-surface aligned; all 7 tasks ran 1 prompt per stage with no restarts
* What created friction: package rename (forge→grain) was applied incrementally starting at T03 without a formal change proposal; T01-T02 still reference `src/forge/` while T03-T07 reference `src/grain/`; this split needs resolution before Phase 10 to avoid compounding the divergence
* What to tighten next: resolve CP-009 (forge→grain) at start of Phase 10; packet-template prefill cleanup for review/close fields (carries over from Phases 7-8); `forge workflow reconcile` CLI (QD-01, carries over from Phase 8)

### Phase Retrospective Classification

* **Fix now:** CP-009 (forge→grain rename) should be decided before Phase 10 execution begins — new Phase 10 code will compound the split if not resolved
* **Batch next phase:** packet-template prefill cleanup for handoff.md Recommended Next Status (carries over from Phases 7, 8); `forge workflow reconcile` CLI (QD-01)
* **Ignore:** phase-vs-task planner keyword heuristics (simple and intentional; refinement is Phase 10+ scope)

---

### Phase 10

* Tasks completed: 6 (P10-T01 through P10-T05 + T06 remediation)
* Blocked tasks: 0
* Prompt runs: ~19 (6 execute × 1 + 6 review × 1 + 6 close × 1, plus T06 execute had 1 restart = +1)
* Avg prompt runs per completed task: ~3.2
* Manual interventions: 1 (human reopened Phase 10 after T01-T05 accepted — tree-sitter spec was not actually satisfied)
* First-pass success rate: 5/6 (T01 required remediation via T06; T02-T06 first-pass); systematic handoff.md pre-fill errors on T01-T04; T04 review intake template placeholders not replaced with explicit "None"
* Rework count: 1 (T01 — ast/regex accepted by reviewer but did not meet tree-sitter spec; replaced in full by T06)
* Drift incidents: 0 (CP-009 applied before Phase 10 began; all code correctly under `grain`)
* Phase duration: Sessions 12–13
* Tests at phase close: 575 (T01 +5, T02 +4, T03 +0 net, T04 +3, T05 +2, T06 +0 net — T06 replaced T01 tests in-place)
* Conversation model: multi-agent (separate executor / reviewer / closer conversations)
* Token tracking: proxy metrics only

### Phase 10 Notes

* What felt efficient: T02-T05 and T06 all ran 1 prompt per stage; graph service, context update, and capability wiring stayed additive without touching unrelated surfaces; T06 remediation was focused (one module + dep update + test assertions) and kept all downstream graph/context/orchestration contracts intact
* What created friction: T01 reviewer accepted "API-equivalent" AST/regex fallback without checking that tree-sitter was actually invoked — phase required reopening and a remediation task (T06); 1 conversation restart during T06 execute; NetworkX declared but not installed in venv — fallback used; T04 reviewer left template placeholder text in review intake
* What to tighten next: reviewer must verify declared key technologies are actually used, not just that the API surface is compatible; install project deps before Phase 11; template cleanup for review intake placeholders (carries over from Phases 7-10)

### Phase Retrospective Classification

* **Fix now:** Install project deps (`pip install -e .`) before Phase 11 starts; add "verify declared key technologies are actually invoked" to reviewer checklist (tree-sitter gap is the lesson)
* **Batch next phase:** packet-template prefill cleanup for handoff.md and review intake placeholder text (carries over from Phases 7-10); `grain workflow reconcile` CLI (QD-01, carries over from Phase 8)
* **Ignore:** T04 placeholder text in review intake (minor, no functional impact)

---

### Phase 11

* Tasks completed: 4 (P11-T01 through P11-T04)
* Tasks blocked: 1 (P11-T05 — Homebrew formula, deferred by operator)
* Prompt runs: ~12 (4 execute × 1 + 4 review × 1 + 4 close × 1)
* Avg prompt runs per completed task: 3.0
* Manual interventions: 1 (operator decision to defer P11-T05 after Homebrew install errors)
* First-pass success rate: 4/4 completed tasks (T05 not attempted — deferred before execution)
* Rework count: 0
* Drift incidents: 0
* Phase duration: Session 14
* Tests at phase close: 577 (+2 new tests from Phase 10 close — T02 added bump_version tests)
* Conversation model: multi-agent (separate executor / reviewer / closer conversations)
* Token tracking: proxy metrics only

### Phase 11 Notes

* What felt efficient: T01-T04 were tight, docs-and-config-focused tasks that ran cleanly with 1 prompt per stage; no canonical drift surfaced; install paths verified in isolation without global environment mutation
* What created friction: Homebrew formula validation failed due to external infrastructure requirements (source tarball pinning, resource checksums, tap publication) — not solvable in-repo scope; operator correctly deferred rather than accepting a partial formula
* What to tighten next: README uses absolute local paths throughout (pre-existing pattern, T03 residual risk) — convert to relative paths before public distribution; packet-template prefill cleanup carries over

### Phase Retrospective Classification

* **Fix now:** none
* **Batch next phase:** README absolute local path links → relative paths before public distribution; packet-template prefill cleanup for review/close fields (carries over from Phases 7-10); `grain workflow reconcile` CLI (QD-01, carries over from Phase 8)
* **Ignore:** T05 pending test markers (intentional — blocked before validation ran; formula file exists as starting point for future tap work)

---

### Phase 12

* Tasks completed: 4 (P12-T01 through P12-T04)
* Tasks blocked: 0
* Prompt runs: ~12 (4 execute × 1 + 4 review × 1 + 4 close × 1)
* Avg prompt runs per completed task: 3.0
* Manual interventions: 0
* First-pass success rate: 4/4
* Rework count: 0
* Drift incidents: 0
* Phase duration: Session 15
* Tests at phase close: 595 (+18 new tests from Phase 11 close)
* Conversation model: multi-agent (separate executor / reviewer / closer conversations)
* Token tracking: proxy metrics only

### Phase 12 Notes

* What felt efficient: T01-T04 each ran 1 prompt per stage with no restarts; loop domain model (T01), loop service + command (T02), guardrails (T03), and orchestrator integration (T04) composed cleanly as a linear dependency chain; accepted-plan ordering activated only on conflicting-ready states, preserving normal deterministic single-ready selection
* What created friction: gated mode gates at task_close only (not task_review) — residual risk noted in T02/T03 but not fully resolved; carries over as batch-next-phase item
* What to tighten next: clarify whether gated mode should also gate at task_review (currently does not); packet-template prefill cleanup carries over from Phases 7–11; `grain workflow reconcile` CLI (QD-01, carries over from Phase 8)

### Phase Retrospective Classification

* **Fix now:** none
* **Batch next phase:** gated-mode gate-at-review question (QD-02 candidate); packet-template prefill cleanup (carries over from Phases 7–11); `grain workflow reconcile` CLI (QD-01)
* **Ignore:** none

---

### Phase 13

* Tasks completed: 5 (P13-T01 through P13-T05)
* Tasks blocked: 0
* Prompt runs: ~15 (5 execute × 1 + 5 review × 1 + 5 close × 1)
* Avg prompt runs per completed task: 3.0
* Manual interventions: 0
* First-pass success rate: 5/5
* Rework count: 0
* Drift incidents: 0
* Phase duration: Session 16
* Tests at phase close: 638 (+43 new tests from Phase 12 close — T01: +10, T02: +7, T03: +5, T04: +2, T05: +16 integration)
* Conversation model: multi-agent (separate executor / reviewer / closer conversations)
* Token tracking: proxy metrics only

### Phase 13 Notes

* What felt efficient: T01-T05 composed cleanly as a linear dependency chain; scanner (T02) and doc generator (T03) are pure service tasks with no CLI wiring overhead; T04 (prompt authoring) was a focused docs task; T05 integration tests hit all three new services in one module plus an e2e flow
* What created friction: none reported — all tasks ran 1 prompt per stage with no restarts
* What to tighten next: generated draft docs require human review before treating as canonical (by design, not a deficiency); packet-template prefill cleanup carries over from Phases 7–12; `grain workflow reconcile` CLI (QD-01, carries over from Phase 8)

### Phase Retrospective Classification

* **Fix now:** none
* **Batch next phase:** packet-template prefill cleanup for review/close fields (carries over from Phases 7–12); `grain workflow reconcile` CLI (QD-01); gated-mode gate-at-review question (carries over from Phase 12)
* **Ignore:** none

---

### Phase 14

* Tasks completed: 4 (P14-T01 through P14-T04)
* Tasks blocked: 0
* Prompt runs: ~12 (4 execute × 1 + 4 review × 1 + 4 close × 1)
* Avg prompt runs per completed task: 3.0
* Manual interventions: 0
* First-pass success rate: 4/4
* Rework count: 0
* Drift incidents: 0
* Phase duration: Session 17
* Tests at phase close: 662 (+24 new tests from Phase 13 close — T01: +8, T02: +8, T03: +8, T04: +0 net in full suite; T04 integration tests counted via T03 run)
* Conversation model: multi-agent (separate executor / reviewer / closer conversations)
* Token tracking: proxy metrics only

### Phase 14 Notes

* What felt efficient: T01-T03 are three parallel extraction services with identical structure (extractor class + adapter profile update + context wiring); each ran 1 prompt per stage; T04 integration tests covered all three extractors plus mixed-type bundles in one module
* What created friction: none reported
* What to tighten next: PDF graceful degradation behavior is best-effort (by design); packet-template prefill cleanup carries over; QD-01 `grain workflow reconcile` carries over from Phase 8

### Phase Retrospective Classification

* **Fix now:** none
* **Batch next phase:** packet-template prefill cleanup (carries over from Phases 7–13); `grain workflow reconcile` CLI (QD-01); gated-mode gate-at-review question (carries over from Phase 12); embedding infrastructure decision required before Phase 15 tasks can be seeded
* **Ignore:** none

---

## v0.1.0 Close Summary

* v0.1.0 scope complete — Phases 6–14 all closed (Phase 11-T05 Homebrew deferred by operator)
* Total v2 tasks: 64 (Phase 6: 7, Phase 7: 7, Phase 8: 11, Phase 9: 7, Phase 10: 6, Phase 11: 4, Phase 12: 4, Phase 13: 5, Phase 14: 4)
* Tests at v0.1.0 close: 662 (up from 379 at v1 close; +283 new tests across Phases 6–14)
* Active install paths: `pip install grain`, `uv tool install grain`
* v0.2.0 gate: embedding infrastructure decision required before Phase 15 (Semantic Enrichment) can be seeded

---

## v0.1.x Patch Series Summary (v0.1.0–v0.1.11)

Released between Phase 14 close and Phase 15 start. Not tracked as formal phases — all patches were hotfix-style incremental work.

* v0.1.2 — Jupyter notebook support (NotebookExtractor)
* v0.1.3 — grain onboard seeding fixes, custom adapter hints
* v0.1.4 — hollow wrapper prompt fixes, implementation_plan seeding
* v0.1.5 — grain upgrade command
* v0.1.6 — grain upgrade --diff / --interactive, bundled doc content fixes
* v0.1.7 — grain: config block, upgrade_check wiring, bundled doc cleanup
* v0.1.8 — grain task close --quick, execution_in_flight gate, code-ahead-of-backlog detection
* v0.1.9 — review state hardening (needs_fix, structured review bundle, completion policy)
* v0.1.10 — grain task create --simple, stub detection in task prepare, bootstrap state fix
* v0.1.11 — tooling_notes structure, upgrade customization guard, empty-phase fix
* Tests at v0.1.11: ~713 (patch series added tests alongside each fix; exact split not captured per patch)

---

### Phase 15

* Tasks completed: 6 (P15-T01 through P15-T06)
* Tasks blocked: 0
* Prompt runs: 1 (single continuous session — single-agent conversational model; no separate executor/reviewer/closer conversations)
* Avg prompt runs per completed task: n/a (single-agent model; all stages in one session)
* Manual interventions: 4 (scope additions T05 and T06 added mid-phase; archiving request for Phases 8–14; TUI/v0.3.0 timeline decision)
* First-pass success rate: 6/6 (multiple implementation bugs fixed inline during development — reconcile `ok` post-fix logic, `needs_fix_invisible` regex pattern — no task required a separate rework round)
* Rework count: 0 (no separate rework rounds; all fixes applied inline during task execution)
* Drift incidents: 1 (agent bypassed grain workflow at session start — T01/T02 briefly progressed without formal packets; corrected; AGENTS.md generation (T05) added specifically to close this bypass vector)
* Phase duration: Session 18
* Tests at phase close: 775 (+113 net from Phase 14 close; includes v0.1.x patch series test additions and all 6 Phase 15 tasks)
* Conversation model: single-agent conversational (Claude Code in-session; all tasks executed, reviewed, and closed in one continuous conversation — departure from multi-agent Phases 6–14)
* Token tracking: proxy metrics only

### Phase 15 Notes

* What felt efficient: T01–T06 were a tightly scoped hardening sequence; each task had a clear deliverable boundary; grain's own workflow tooling was used to build grain (workflow discipline validated against itself); T06 (phase archive) landed cleanly as the formal close ceremony for the phase
* What created friction: agent bypassed the grain workflow at session start (no prior constraint existed for conversational sessions) — this spawned T05 (AGENTS.md); reconcile service had two subtle bugs requiring inline diagnosis (ok post-fix computation, ID regex format mismatch); integration tests required a `_seed_templates()` helper not obvious from the task spec
* What to tighten next: AGENTS.md is now in place — monitor whether agents honor it in subsequent sessions; single-agent model lacks a natural review gate (reviewer/closer stages are collapsed); consider whether Phase 16 reintroduces multi-agent stages or formalizes the single-agent review pattern

### Phase Retrospective Classification

* **Fix now:** none
* **Batch next phase:** verify AGENTS.md is honored in Phase 16 session start; confirm single-agent vs multi-agent model for v0.2.0 phases; `grain workflow reconcile` QD-01 is now delivered (closed here in T03)
* **Ignore:** v0.1.x patch test count split (not worth retroactive reconstruction)

---

### Phase 16

* Tasks completed: 8 (P16-T01 through P16-T08)
* Tasks blocked: 0
* Prompt runs: 1 (single continuous session — single-agent conversational model)
* Avg prompt runs per completed task: n/a (single-agent model; all stages in one session)
* Manual interventions: 3 (global task-ID renumbering correction from TASK-0001 to TASK-0109; workflow-next execute/review friction logged; P16-T08 backlog status corrected manually when reconcile did not update it)
* First-pass success rate: 8/8 (all task slices landed and closed without a separate rework round; one BM25 integration fixture needed tightening inline)
* Rework count: 0 (no task was reopened or routed back from review)
* Drift incidents: 3 (`workflow next` kept routing to execute after `results.md`; packet ID allocation ignored `tasks/archive/`; reconcile missed the final P16-T08 backlog sync)
* Phase duration: Session 19
* Tests at phase close: 33 targeted semantic/context/CLI tests passing; full repo suite not run in this phase-close session
* Conversation model: single-agent conversational (Codex in-session; tasks executed, reviewed, and closed in one continuous conversation)
* Token tracking: proxy metrics only

### Phase 16 Notes

* What felt efficient: provider work split cleanly into resolver, baseline BM25, three optional backends, context integration, CLI inspection, and integration coverage; each task was small enough to close and commit independently; fake-provider seams kept optional-backend testing deterministic
* What created friction: local `grain` entrypoint was behind repo source (`0.1.5` vs required `>=0.1.9`), so repo-local CLI invocation was needed for newer workflow commands; two workflow/tooling bugs surfaced inside the phase (`workflow next` execute/review routing and packet-ID reuse); reconcile did not sync the final P16-T08 backlog state
* What to tighten next: upgrade the local Grain CLI entrypoint before Phase 17 work; fix the logged workflow/tooling bugs before leaning harder on automation; decide whether phase-close docs should also require/update `current_focus.md` status summaries instead of only appending a seal marker

---

### Phase 17

* Tasks completed: 6 (P17-T01 through P17-T06)
* Tasks blocked: 0 (Q17 was resolved mid-phase and did not remain a terminal blocker)
* Prompt runs: 1 (single continuous session — single-agent conversational model)
* Avg prompt runs per completed task: n/a (single-agent model; all stages in one session)
* Manual interventions: 3 (Q17 logged and then resolved to unblock advisory task ranking; P17-T06 backlog status corrected manually when reconcile did not update it; workflow review/close commands had to be replayed sequentially when parallel invocations raced packet status transitions)
* First-pass success rate: 6/6 (all task slices landed and closed without a separate rework round; two test failures were fixed inline during implementation)
* Rework count: 0 (no task was reopened or routed back from review)
* Drift incidents: 2 (`workflow reconcile` again missed the final backlog sync for a closed task; close/handoff commands were sensitive to ordering when invoked in parallel)
* Phase duration: Session 20
* Tests at phase close: 31 targeted ranking/context/orchestration tests passing; full repo suite not run in this phase-close session
* Conversation model: single-agent conversational (Codex in-session; tasks executed, reviewed, and closed in one continuous conversation)
* Token tracking: proxy metrics only

### Phase 17 Notes

* What felt efficient: the ranking work decomposed cleanly into contracts, service, context integration, advisory task surface, impact ranking, and integration coverage; the shared ranking service made later consumer tasks narrow and reusable; existing orchestration surfaces provided a clean home for advisory-only task and impact ranking
* What created friction: task-ranking needed an explicit contract decision before implementation; backlog reconciliation again missed one closed task status; packet review/handoff/close commands are order-sensitive and do not compose safely under parallel execution
* What to tighten next: teach reconcile to repair final closed-task backlog drift consistently; avoid parallel packet lifecycle commands in agent automation; decide whether advisory surfaces like task advice should graduate from orchestration payloads into dedicated commands in a later phase

---

### Phase 18

* Tasks completed: 6 (P18-T01 through P18-T06)
* Tasks blocked: 0
* Prompt runs: 1 (single continuous session — single-agent conversational model)
* Avg prompt runs per completed task: n/a (single-agent model; all stages in one session)
* Manual interventions: 3 (Q18 resolved up front to unblock planning; closed-task backlog drift had to be corrected during phase execution; stale workflow-next output required explicit rechecks after reconcile)
* First-pass success rate: 6/6 (all slices landed and closed without reopening; one integration test fixture failure was corrected inline during implementation)
* Rework count: 0 (no task was reopened or routed back from review)
* Drift incidents: 2 (closed-task backlog state lagged the packet state; workflow-next briefly surfaced stale candidate output after reconcile)
* Phase duration: Session 21
* Tests at phase close: 76 targeted Phase 18 tests passing; full repo suite not run in this phase-close session
* Conversation model: single-agent conversational (Codex in-session; tasks executed, reviewed, and closed in one continuous conversation)
* Token tracking: proxy metrics only

### Phase 18 Notes

* What felt efficient: the phase decomposed cleanly into contract, extractor, notebook migration, context/orchestration integration, onboarding detection, and one end-to-end proof gate; existing extractor and orchestration seams kept the implementation additive
* What created friction: backlog reconciliation still lagged closed-task status; tracked `__pycache__` artifacts created repetitive cleanup noise during test runs; phase-boundary state still depends on explicit `current_focus.md` advancement after `grain phase close`
* What to tighten next: stop tracking generated `__pycache__` artifacts in the repo; teach reconcile to catch the final closed-task drift consistently; consider making phase-close advance the active-phase summary block in `current_focus.md` or fail until it is updated

---

### Phase 19

* Tasks completed: 6 (P19-T01 through P19-T06)
* Tasks blocked: 0
* Prompt runs: 1 (single continuous session — single-agent conversational model)
* Avg prompt runs per completed task: n/a (single-agent model; all stages in one session)
* Manual interventions: 4 (Q19 resolved before execution; stale repo test environment required direct Python execution instead of `pytest`; workflow-next skipped P19-T06 and had to be overridden manually; final P19-T06 backlog drift was corrected manually before phase close)
* First-pass success rate: 6/6 (all slices landed and closed without reopening)
* Rework count: 0 (no task was reopened or routed back from review)
* Drift incidents: 2 (`workflow next` surfaced the phase-close boundary before the remaining draft integration task was executed; reconcile did not repair the final P19-T06 backlog status drift)
* Phase duration: Session 22
* Tests at phase close: 57 targeted Phase 19 checks passing; full repo suite not run in this phase-close session
* Conversation model: single-agent conversational (Codex in-session; tasks executed, reviewed, and closed in one continuous conversation)
* Token tracking: proxy metrics only

### Phase 19 Notes

* What felt efficient: the phase broke cleanly into contract, package validation, explicit install flow, registry scaffold, CI/docs, and one integrated proof gate; keeping the install surface local-only avoided a large remote-registry detour while still landing the full reviewed-registry contract
* What created friction: the repo-local test environment stayed stale, forcing direct Python execution checks instead of `pytest`; tracked `__pycache__` artifacts continued to dirty the worktree; workflow selection and reconcile both missed the final Phase 19 task state once
* What to tighten next: repair the stale local test runner path so targeted `pytest` runs work again; stop tracking generated `__pycache__` artifacts; teach workflow-next and reconcile not to skip or miss the final remaining draft/done task in a phase

---

## V2 Aggregate (to date)

* Total v2 tasks completed: 96 (Phase 6: 7, Phase 7: 7, Phase 8: 11, Phase 9: 7, Phase 10: 6, Phase 11: 4, Phase 12: 4, Phase 13: 5, Phase 14: 4, Phase 15: 6, Phase 16: 8, Phase 17: 6, Phase 18: 6, Phase 19: 6; v0.1.x patches not counted as formal tasks)
* Total v2 blocked: 1 (P11-T05 deferred)
* Tests at v2 Phase 6 close: 399; at Phase 7 close: 419; at Phase 8 close: 494; at Phase 9 close: 561; at Phase 10 close: 575; at Phase 11 close: 577; at Phase 12 close: 595; at Phase 13 close: 638; at Phase 14 close: 662; at Phase 15 close: 775; at Phase 16 close: 33 targeted semantic/context/CLI tests (full suite not run); at Phase 17 close: 31 targeted ranking/context/orchestration tests (full suite not run); at Phase 18 close: 76 targeted data-adapter tests (full suite not run); at Phase 19 close: 57 targeted community-registry checks (full suite not run)
* Open questions resolved during v2 (to date): Q12–Q19 (8 questions); QD-01 (grain workflow reconcile) delivered in Phase 15
* Canonical change proposals raised during v2: 1 (P8-T10 `cli_spec.md §6.9` addition); CP-009 applied (Forge→Grain, Sentinel→Assay rename); CP-010 raised and resolved (superseded by CP-009); no new proposals in Phases 11–15
* Major Phase 6 additions: adapter profiles runtime doc, AdapterProfile domain model, adapter loader/parser, packet adapter metadata fields, adapter-aware context biasing, adapter hint surfacing in context outputs, adapter system tests
* Major Phase 7 additions: stable new-project onboarding prompt, init seed-file scaffolding, adapter selection, starter packet bootstrap, onboarding integration tests, existing-project adoption boundary docs
* Major Phase 8 additions: workflow state evaluator, grain workflow next/run, grain task next/prepare, grain phase next, grain prompt show, machine-readable JSON contract for automation commands, runner integration tests, Assay bridge contract (`cli_spec.md §6.9` + `v2_plan.md §11`), working-doc reconciliation approach
* Major Phase 9 additions: OrchestratorPlan domain model (PacketCandidate, CrossDomainDependency), AdapterCapabilityProtocol + NullAdapterCapability + 6 result types, orchestration service (task-level + phase-level), grain adapter list/show, grain orchestrate scope/plan, OrchestratorPlan validator, orchestration integration tests, proposal artifacts in `docs/working/proposals/`
* Major Phase 10 additions: structural extraction service (Layer 1, tree-sitter via language packs — T06 replaced T01's AST/regex), knowledge graph builder (Layer 3, NetworkX + deterministic fallback), graph-assisted context selection (Layer 4, per-source trace paths), graph-aware adapter capabilities (detect_scope + analyze_impact wired), Phase 10 integration + rebuild-determinism tests
* Major Phase 11 additions: finalized pyproject.toml distribution metadata, GitHub Actions OIDC PyPI publish workflow, semver version bump script, uv tool install compatibility verified, install verification and troubleshooting docs in README; Homebrew formula (contrib/homebrew/Formula/grain.rb) exists as deferred starting point
* Major Phase 12 additions: per-stage agent/model config (`workflow_loop.yaml` + `WorkflowLoopConfig` domain model), `grain workflow loop` command, supervised/gated/autonomous supervision levels, `--dry-run` mode, 25-step cap, per-step structured logging, `grain orchestrate accept --plan <id>` command, accepted-plan loop ordering for conflicting ready tasks, loop safety guardrails documentation
* Major Phase 13 additions: `grain onboard` CLI + `OnboardService` additive scaffold engine (dry-run, JSON/text output), `CodebaseScanner` (language/adapter/key-file/CI/docs detection), `OnboardDocGenerator` (draft canonical docs from scan, all marked `# DRAFT`), `workflow.onboard.existing.md` agent-driven adoption prompt, Phase 13 integration test suite (16 tests covering onboard/scanner/generator/e2e)
* Major Phase 14 additions: `SpreadsheetExtractor` (xlsx/xls/csv via openpyxl), `DocsExtractor` (docx + md via python-docx), `PdfExtractor` (pdf via pdfplumber, graceful degradation), context assembly integration for all three, adapter profiles updated, Phase 14 integration tests (12 tests, mixed-type context bundles)
* Major Phase 15 additions: `grain phase close` (hard lifecycle gate, grain-verified sealed marker), `grain workflow run` auto-packet bootstrap (packet auto-created on first run if missing), `grain workflow reconcile` (drift detection across backlog/packet/current_task/needs_fix; --fix mode), Phase 15 integration test suite (10 tests), `AGENTS.md` generation via `grain init`/`grain onboard`/`grain init --update-agents` (idempotent block, multi-agent safe), `grain phase archive <N>` (validated move of closed phase packets to archive dir)
* Major Phase 16 additions: embedding-provider domain contracts and manifest config surface, `BM25Provider`, `OllamaProvider`, `LocalProvider`, `OpenAIProvider`, semantic reranking inside context selection, `grain embedding show`, Phase 16 integration coverage, and tooling notes for workflow-next/reconcile/task-ID drift discovered during execution
* Major Phase 17 additions: ranking domain contracts and weighted scoring service, ranked context-selection metadata, advisory ranked task suggestions on orchestration scope output, ranked impacted-file advisory signals, Q17 resolution for advisory-only task ranking, and Phase 17 integration coverage
* Major Phase 18 additions: `data_adapter` runtime contract and Q18 metadata-only boundary, `DataArtifactExtractor`, notebook ownership migration from `code_adapter` to `data_adapter`, data-artifact context export wiring, orchestration scope activation for data workflows, onboarding/scanner promotion of `data_adapter` to an official applicable adapter, and Phase 18 integration coverage
* Major Phase 19 additions: reviewed community-registry trust contract, package validation service, explicit local-only `grain adapter install`, registry scaffold/templates/checklist, dedicated CI/doc guidance for community adapter authors, and Phase 19 integration coverage

---

## Combined Aggregate

* Total tasks completed: 149 (53 v1 + 96 v2; v0.1.x patches not counted as formal tasks)
* Total blocked (all phases): 1 (P11-T05 Homebrew, deferred)
* Total tests at v1 close: 379; at Phase 6 close: 399; at Phase 7 close: 419; at Phase 8 close: 494; at Phase 9 close: 561; at Phase 10 close: 575; at Phase 11 close: 577; at Phase 12 close: 595; at Phase 13 close: 638; at Phase 14 close: 662; at Phase 15 close: 775; at Phase 16 close: 33 targeted semantic/context/CLI tests (full suite not run); at Phase 17 close: 31 targeted ranking/context/orchestration tests (full suite not run); at Phase 18 close: 76 targeted data-adapter tests (full suite not run); at Phase 19 close: 57 targeted community-registry checks (full suite not run)
* Open questions resolved total: Q1–Q19 (19 resolved); QD-01 (grain workflow reconcile) delivered Phase 15
* Canonical change proposals applied total: CP-001 through CP-008 (8 applied in v1); 1 scoped addition in v2 (P8-T10 `cli_spec.md §6.9`); CP-009 applied (Forge→Grain, Sentinel→Assay); CP-010 resolved (superseded); no new proposals in Phases 11–15
* V1 phases closed: 5 (Phases 1–5)
* V2 phases closed: 14 (Phase 6, Phase 7, Phase 8, Phase 9, Phase 10, Phase 11, Phase 12, Phase 13, Phase 14, Phase 15, Phase 16, Phase 17, Phase 18, Phase 19)
* V2 planning docs created: v2_plan.md, v2_adapters.md, v2_onboarding.md
* **v0.1.0 status: COMPLETE** — all planned phases closed; 662 tests passing; version tagged and PyPI published
* **v0.1.x patch series: COMPLETE** — v0.1.0 through v0.1.11; ~713+ tests at v0.1.11
* **v0.2.0 status: COMPLETE** — Phases 15 through 20 closed; release shipped

---

### Phase 22

* Tasks completed: 6 (P22-T01 through P22-T06)
* Tasks blocked: 0
* Prompt runs: 1 (single continuous session — single-agent conversational model)
* Avg prompt runs per completed task: n/a (single-agent model; all stages in one session)
* Manual interventions: 3 (Phase 21 seal was missing and had to be restored manually before close; P22 packet review approvals were normalized before close; one stale backlog status for P22-T06 required manual correction)
* First-pass success rate: 6/6 (all TUI slices landed without reopening; tests and docs closeout completed in the same phase stream)
* Rework count: 0 (no task was reopened or routed back from review)
* Drift incidents: 1 (phase-close readiness was blocked by a missing Phase 21 seal marker even though planning work was complete)
* Phase duration: Session 23
* Tests at phase close: 58 targeted TUI/workflow/context checks passing; full repo suite not run in this phase-close session
* Conversation model: single-agent conversational (Codex in-session; tasks executed, reviewed, and closed in one continuous conversation)
* Token tracking: proxy metrics only

### Phase 22 Notes

* What felt efficient: the TUI broke cleanly into shell, dashboard, inspectors, action launchers, preview/detail panels, and closeout coverage; the Textual layer stayed thin over existing Grain services and commands; packet-level commits kept the new Trace convention useful without fragmenting the phase across many branches
* What created friction: historical phase-close state drift still depends on explicit working-doc updates; review normalization was still manual; backlog text lagged the packet state once at the end of the phase
* What to tighten next: reduce manual review-state normalization, make phase-close markers less fragile, and carry the same testable thin-shell discipline into the writable office artifact work

---

### Phase 23

* Tasks completed: 6 (P23-T01 through P23-T06)
* Tasks blocked: 0
* Prompt runs: 1 (single continuous session — single-agent conversational model)
* Avg prompt runs per completed task: n/a (single-agent model; all stages in one session)
* Manual interventions: 4 (backlog status drift had to be normalized at multiple task boundaries; `P23-T06` packet creation was duplicated, producing `TASK-0157` and `TASK-0158`; review approvals were normalized manually before close; phase-close docs required explicit sync before closure)
* First-pass success rate: 6/6 (all office slices landed without reopening; smoke/docs closeout completed in the same phase stream)
* Rework count: 0 (no task was reopened or routed back from review)
* Drift incidents: 2 (workflow state selected stale backlog status after task closure; `P23-T06` duplicate packet drift after manual create plus workflow auto-create)
* Phase duration: Session 24
* Tests at phase close: 26 focused office CLI/service tests passing; full repo suite not run in this phase-close session
* Conversation model: single-agent conversational (Codex in-session; tasks executed, reviewed, and closed in one continuous conversation)
* Token tracking: proxy metrics only

### Phase 23 Notes

* What felt efficient: the office slice broke cleanly into shared contracts, artifact-specific write services, shared review logic, CLI exposure, and closeout smoke/docs work; packet-first review artifacts kept non-code writes inspectable without inventing hidden state; the focused office test slice stayed fast while covering meaningful workflow behavior
* What created friction: workflow/backlog drift still required manual normalization; the manual `task create` before `workflow run` caused duplicate packet drift for `P23-T06`; full-suite verification remained deferred because the phase stayed tightly scoped
* What to tighten next: make workflow activation idempotent when a packet already exists, reduce manual backlog/status normalization, and carry the same packet-first discipline into desktop and Obsidian surfaces

---

### Phase 24

* Tasks completed: 5 (P24-T01 through P24-T05)
* Tasks blocked: 0
* Prompt runs: 1 (single continuous session — single-agent conversational model)
* Avg prompt runs per completed task: n/a (single-agent model; all stages in one session)
* Manual interventions: 4 (duplicate task drift had to be archived before continuing; stale `current_task.md` pointers required reconcile after task close; backlog task state had to be normalized before activating `P24-T05`; phase close required an explicit metrics entry before sealing)
* First-pass success rate: 5/5 (desktop and Obsidian slices landed without reopening; closeout smoke/docs completed in the same phase stream)
* Rework count: 0 (no task was reopened or routed back from review)
* Drift incidents: 2 (duplicate packet drift near the phase start; stale runner/backlog state after task close remained a recurring manual fix)
* Phase duration: Session 25
* Tests at phase close: 32 focused MCP, Obsidian integration, adapter profile, and release-surface checks passing; full repo suite not run in this phase-close session
* Conversation model: single-agent conversational (Codex in-session; tasks executed, reviewed, and closed in one continuous conversation)
* Token tracking: proxy metrics only

### Phase 24 Notes

* What felt efficient: the phase broke cleanly into wrapper scaffold, CLI/Desktop guidance, Obsidian adapter scaffold, first vault-aware context behavior, and closeout smoke/docs work; the local MCP layer stayed thin over the existing CLI; Obsidian support advanced through bounded, file-backed slices instead of a broad vault rewrite
* What created friction: packet and backlog drift still required manual reconcile; the Obsidian selection fix had to preserve anchor ordering after semantic reranking; full-suite verification remained intentionally deferred in favor of a tighter phase-close slice
* What to tighten next: reduce runner drift after task close, keep desktop/tooling documentation synchronized with shipped surfaces, and carry the same bounded-adapter discipline into the upcoming database and crawler phases

---

### Phase 25

* Tasks completed: 5 (P25-T01 through P25-T05)
* Tasks blocked: 0
* Prompt runs: 1 (single continuous session — single-agent conversational model)
* Avg prompt runs per completed task: n/a (single-agent model; all stages in one session)
* Manual interventions: 5 (runner/task template drift required packet fill-in on every activated task; stale `current_task.md` pointers required reconcile after each task close; backlog task state repeatedly lagged packet status; Phase 25 required explicit `ready` promotion before each downstream task; phase close required an explicit metrics entry before sealing)
* First-pass success rate: 5/5 (all database slices landed without reopening; closeout smoke/docs completed in the same phase stream)
* Rework count: 0 (no task was reopened or routed back from review)
* Drift incidents: 2 (activation produced template-only task packets that required manual packet completion; stale runner/backlog state after task close remained recurring manual fix)
* Phase duration: Session 26
* Tests at phase close: 30 focused database integration, adapter profile, and release-surface checks passing; full repo suite not run in this phase-close session
* Conversation model: single-agent conversational (Codex in-session; tasks executed, reviewed, and closed in one continuous conversation)
* Token tracking: proxy metrics only

### Phase 25 Notes

* What felt efficient: the phase broke cleanly into scaffold, schema/migration selection, persistence-oriented query/repository hints, review guidance, and closeout smoke work; `database_adapter` advanced through bounded slices without needing live database tooling; focused integration tests kept the validation loop fast while still proving meaningful end-to-end behavior
* What created friction: task packet activation still yielded template-only packets that had to be filled manually; backlog and `current_task.md` drift required reconcile after every close; the shipped runtime copy needed continuous alignment with the live adapter contract as the phase grew
* What to tighten next: reduce packet-template drift on activation, keep bundled/runtime adapter docs synchronized automatically where possible, and carry the same bounded-adapter pattern into the crawler phase

---

### Phase 26

* Tasks completed: 5 (P26-T01 through P26-T05)
* Tasks blocked: 0
* Prompt runs: 1 (single continuous session — single-agent conversational model)
* Avg prompt runs per completed task: n/a (single-agent model; all stages in one session)
* Manual interventions: 5 (runner/task template drift required packet fill-in on every activated task; stale `current_task.md` pointers required reconcile after each task close; backlog task state repeatedly lagged packet status; Phase 26 required explicit `ready` promotion before each downstream task; phase close required an explicit metrics entry before sealing)
* First-pass success rate: 5/5 (all crawler slices landed without reopening; closeout smoke/docs completed in the same phase stream)
* Rework count: 0 (no task was reopened or routed back from review)
* Drift incidents: 2 (activation produced template-only task packets that required manual packet completion; stale runner/backlog state after task close remained recurring manual fix)
* Phase duration: Session 27
* Tests at phase close: 34 focused crawler integration, adapter profile, and release-surface checks passing; full repo suite not run in this phase-close session
* Conversation model: single-agent conversational (Codex in-session; tasks executed, reviewed, and closed in one continuous conversation)
* Token tracking: proxy metrics only

### Phase 26 Notes

* What felt efficient: the phase broke cleanly into scaffold, config/selector selection, extraction-quality hints, review guidance, and closeout smoke work; `crawler_adapter` advanced through bounded slices without needing live crawler tooling; focused integration tests kept the validation loop fast while still proving meaningful end-to-end behavior
* What created friction: task packet activation still yielded template-only packets that had to be filled manually; backlog and `current_task.md` drift required reconcile after every close; the shipped runtime copy needed continuous alignment with the live adapter contract as the phase grew
* What to tighten next: reduce packet-template drift on activation, keep bundled/runtime adapter docs synchronized automatically where possible, and carry the same bounded-adapter pattern into the recipe/ergonomics phase

---

### Phase 27

* Tasks completed: 3 (P27-T01 through P27-T03)
* Tasks blocked: 0
* Prompt runs: 1 (single continuous session — single-agent conversational model)
* Avg prompt runs per completed task: n/a (single-agent model; all stages in one session)
* Manual interventions: 4 (runner task activation still created template-only packets that required manual packet completion; backlog task state repeatedly lagged packet status after close; `current_task.md` still needed reconcile after close; phase close still requires an explicit metrics entry before sealing)
* First-pass success rate: 3/3 (all observability, budget, and TUI slices landed without reopening)
* Rework count: 0 (no task was reopened or routed back from review)
* Drift incidents: 2 (runner-created placeholder packets still needed manual completion; stale runner/backlog state after task close remained a recurring manual fix)
* Phase duration: Session 28
* Tests at phase close: 52 focused TUI, context, observability, and workflow command tests passing; full repo suite not run in this phase-close session
* Conversation model: single-agent conversational (Codex in-session; tasks executed, reviewed, and closed in one continuous conversation)
* Token tracking: file-size and line-count proxy metrics only

### Phase 27 Notes

* What felt efficient: observability, budget reporting, and TUI wiring stacked cleanly because each slice reused packet-local files and existing service metadata instead of inventing new state channels; focused command tests stayed fast while still proving meaningful operator-facing behavior
* What created friction: runner activation still yielded placeholder packets that had to be filled manually; reconcile remained necessary after each close; review check surfaced the known status drift because packet closure is still being driven directly after packet completion in-session
* What to tighten next: make runner-created packets ready for real execution without manual fill-in, reduce post-close reconcile work, and reuse the same file-backed patterns when wiring the upcoming Assay verification bridge

---

### Phase 28

* Tasks completed: 5 (P28-T01 through P28-T05)
* Tasks blocked: 0
* Prompt runs: 1 (single continuous session — single-agent conversational model)
* Avg prompt runs per completed task: n/a (single-agent model; all stages in one session)
* Manual interventions: 5 (runner/task template drift required manual packet completion for the mid-phase tasks; stale `current_task.md` required manual reset; backlog phase labels lagged actual execution state; a missing CLI import broke the first ingest test pass; phase close still requires an explicit metrics entry before sealing)
* First-pass success rate: 3/5 (submit and status landed cleanly; ingest needed one CLI import fix; verification gates needed one focused test/CLI-output refinement pass; docs closeout landed in one pass)
* Rework count: 2 (P28-T03 ingest fix; P28-T04 gate-output refinement)
* Drift incidents: 2 (placeholder packet drift remained on activation; working docs still lagged actual task completion until manually normalized)
* Phase duration: Session 29
* Tests at phase close: 102 focused verification, workflow-gate, close-command, and release-surface checks passing; full repo suite not run in this phase-close session
* Conversation model: single-agent conversational (Codex in-session; tasks executed, reviewed, and closed in one continuous conversation)
* Token tracking: proxy metrics only

### Phase 28 Notes

* What felt efficient: the verification bridge stacked cleanly once it stayed packet-local; submit, status, ingest, workflow gating, and docs each built on the same small artifact set (`verification_request.json`, `verification_result.json`, and `results.md`) without introducing hidden state
* What created friction: the repo shell binary was behind the source tree at first, placeholder packets still needed manual fill-in, and one missing `Path` import plus one missing close-command error print delayed the focused verification slice
* What to tighten next: reduce packet-template drift on activation, keep the installed CLI entrypoint aligned with the repo code during active development, and decide the next post-bridge execution phase before reopening implementation

---

### Phase 29

* Tasks completed: 5 (P29-T01 through P29-T05)
* Tasks blocked: 0
* Prompt runs: 1 (single continuous session — single-agent conversational model)
* Avg prompt runs per completed task: n/a (single-agent model; all stages in one session)
* Manual interventions: 6 (manual task approvals/closeouts still required; `current_task.md` and backlog state still needed normalization between tasks; duplicate `P29-T04` packet drift had to be archived; the installed CLI entrypoint was behind the repo code; phase close still required an explicit metrics entry before sealing)
* First-pass success rate: 3/5 (prompt/runtime hardening, workflow misuse blockers, and runner-drift hardening landed cleanly; `workflow explain` needed one phase-guard refinement in tests; phase closeout needed one parser-edge fix when the final ready task was hidden behind a non-phase section)
* Rework count: 2 (P29-T04 fixture/stop-reason refinement; P29-T05 parser edge fix)
* Drift incidents: 3 (manual current-task reset after close, duplicate packet drift on `P29-T04`, and the backlog parser inheriting status from the later `Future` section)
* Phase duration: Session 30
* Tests at phase close: 80 focused workflow explain/next/state, command-group, and release-surface checks passing; full repo suite not run in this phase-close session
* Conversation model: single-agent conversational (Codex in-session; tasks executed, reviewed, and closed in one continuous conversation)
* Token tracking: proxy metrics only

### Phase 29 Notes

* What felt efficient: the hardening slices stayed tightly layered — prompt/runtime guardrails, misuse blockers, runner drift reduction, operator diagnostics, then closeout smoke/docs — so each fix built directly on the last one without reopening earlier feature phases
* What created friction: the installed CLI entrypoint lagged the repo code, duplicate packet drift still appeared when manual and automatic activation mixed, and the backlog parser edge only surfaced at the very end of the phase
* What to tighten next: keep the active CLI path pinned to the current source tree during development, further reduce manual backlog/current-task normalization after close, and continue adding explicit guidance whenever new workflow stop reasons are introduced

---

### Phase 30

* Tasks completed: 14
* Blocked tasks: 0
* Prompt runs: 1 (single agent session)
* Avg prompt runs per completed task: 0.07
* Manual interventions: 0
* First-pass success rate: 14/14
* Rework count: 0
* Drift incidents: 0
* Phase duration: 2026-06-11 (single session)

### Phase 30 Notes

* What felt efficient: planning phase with a locked milestone contract first meant every subsequent spec task had a clear decision anchor; tasks that needed design decisions had those resolved in T01 before any spec writing began
* What created friction: `grain workflow next --format json` flag order is global not per-command (`grain --format json workflow next`); `grain notes add` command not yet implemented (v0.4.0 planned); 4 bundled files out of date requiring upgrade
* What to tighten next: the `--format` flag placement inconsistency is a UX friction point that T12 (CLI ergonomics) addresses; `grain notes add` is needed immediately for agents to log friction correctly

---

### Phase 31

* Tasks completed: 8 (T01–T08: agent enforcement, guard refactor, scaffold gaps, docs audit, archiving, CLI ergonomics, upgrade enforcement, branch policy)
* Blocked tasks: 0
* Prompt runs: 2 (two context windows; compacted mid-phase)
* Avg prompt runs per completed task: 0.25
* Manual interventions: 1 (template field addition — Suggested Action on OQ/CP templates)
* First-pass success rate: 8/8
* Rework count: 0
* Drift incidents: 0
* Phase duration: 2026-06-03 – 2026-06-12

### Phase 31 Notes

* What felt efficient: the spec-first approach from P30 paid off — T07 and T08 had complete specs (upgrade_enforcement_spec.md, branch_policy_spec.md) that made implementation mechanical; stop reason constants were the right call before building enforcement gates
* What created friction: macOS sed -i arg parsing tripped up a string replacement step; CliRunner(mix_stderr=False) not available in the installed Click build; phase 31 tests required phase < 16 to avoid previous_phase_not_closed gate
* What to tighten next: warrant explicit phase number check in test helpers to avoid routing gate surprises; sed should always be replaced with Python for multi-pattern replacements on macOS

---

### Phase 32

* Tasks completed: 10 (T01 suggest-spec confirm, T02 suggest engine, T03 phase-close archiving, T04 archive show, T05 workflow-next surfacing, T06 notes inbox, T07 metrics, T08 telemetry foundation, T09 GitHub feedback, T10 docs hygiene)
* Blocked tasks: 0
* Prompt runs: multi-agent — recon (8) + implement (7) + adversarial review (7) + fix (7) sequential/parallel agent workflows
* Manual interventions: founder decisions (v0.4.0-first scoping; T09 = report + publish both surfaces; v0.5.0 backlog adds; grain-only-to-main split from local Scry work)
* First-pass success rate: 7/7 features built green, but adversarial review then found 23 real defects unit tests missed
* Rework count: 23 review findings fixed (8 high / 5 medium / 10 low), +43 regression tests
* Drift incidents: 2 — v0.4.0 contract had drifted to the composable-toolkit theme (reconciled; toolkit work moved to v0.5.0); phase-heading regex bug class (`## N. Phase N —` vs real `## Phase N —`) surfaced at phase close (fixed in 4 modules)
* Phase duration: 2026-06-24 – 2026-06-25

### Phase 32 Notes

* What felt efficient: spec-first paid off again (locked suggest_spec/feedback_spec made implementation mechanical); the recon -> implement -> adversarial-review -> fix pipeline caught and fixed real state-corruption/data-loss bugs before merge; test-gated per-feature commits kept the suite monotonically green (1192 -> 1414)
* What created friction: the `_PHASE_HEADING` regex required a leading list number (`## N. Phase N —`) but the backlog uses `## Phase N —`, silently breaking backlog parsing in 4 modules and blocking phase close (the hygiene task fixed only the docs_audit twin); node/pnpm/git-cliff unavailable in the agent sandbox blocked `trace lint-commit`/`trace release` (validated commit format by hand); pushing main risked sweeping unrelated local Scry/WARDRIVE work onto origin (caught pre-push, split onto scry-wip)
* What to tighten next: DRY the phase-heading regex into ONE shared definition instead of 4 copies, and add a guard/docs-audit check that the backlog heading format matches what the parsers expect; build the v0.5.0 quick-lane so trivial work skips full packet ceremony; expose a token-budget proxy so the efficiency claim is measured, not assumed
