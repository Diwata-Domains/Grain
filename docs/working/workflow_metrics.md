# Workflow Metrics

## Project

Forge

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

## V2 Aggregate (to date)

* Total v2 tasks completed: 47 (Phase 6: 7, Phase 7: 7, Phase 8: 11, Phase 9: 7, Phase 10: 6)
* Total v2 blocked: 0
* Tests at v2 Phase 6 close: 399; at Phase 7 close: 419; at Phase 8 close: 494; at Phase 9 close: 561; at Phase 10 close: 575
* Open questions resolved during v2 (to date): Q12–Q16 (5 questions); QD-01 deferred; no new questions opened in Phases 9–10
* Canonical change proposals raised during v2: 1 (P8-T10 `cli_spec.md §6.9` addition); CP-009 applied (Forge→Grain, Sentinel→Assay rename); CP-010 raised and resolved (superseded by CP-009)
* Major Phase 6 additions: adapter profiles runtime doc, AdapterProfile domain model, adapter loader/parser, packet adapter metadata fields, adapter-aware context biasing, adapter hint surfacing in context outputs, adapter system tests
* Major Phase 7 additions: stable new-project onboarding prompt, init seed-file scaffolding, adapter selection, starter packet bootstrap, onboarding integration tests, existing-project adoption boundary docs
* Major Phase 8 additions: workflow state evaluator, grain workflow next/run, grain task next/prepare, grain phase next, grain prompt show, machine-readable JSON contract for automation commands, runner integration tests, Assay bridge contract (`cli_spec.md §6.9` + `v2_plan.md §11`), working-doc reconciliation approach
* Major Phase 9 additions: OrchestratorPlan domain model (PacketCandidate, CrossDomainDependency), AdapterCapabilityProtocol + NullAdapterCapability + 6 result types, orchestration service (task-level + phase-level), grain adapter list/show, grain orchestrate scope/plan, OrchestratorPlan validator, orchestration integration tests, proposal artifacts in `docs/working/proposals/`
* Major Phase 10 additions: structural extraction service (Layer 1, tree-sitter via language packs — T06 replaced T01's AST/regex), knowledge graph builder (Layer 3, NetworkX + deterministic fallback), graph-assisted context selection (Layer 4, per-source trace paths), graph-aware adapter capabilities (detect_scope + analyze_impact wired), Phase 10 integration + rebuild-determinism tests

---

## Combined Aggregate

* Total tasks completed: 100 (53 v1 + 47 v2)
* Total blocked (all phases): 0
* Total tests at v1 close: 379; at Phase 6 close: 399; at Phase 7 close: 419; at Phase 8 close: 494; at Phase 9 close: 561; at Phase 10 close: 575
* Open questions resolved total: Q1–Q16 (16 resolved); QD-01 deferred; no new questions in Phases 9–10
* Canonical change proposals applied total: CP-001 through CP-008 (8 applied in v1); 1 scoped addition in v2 (P8-T10 `cli_spec.md §6.9`); CP-009 applied (Forge→Grain, Sentinel→Assay); CP-010 resolved (superseded)
* V1 phases closed: 5 (Phases 1–5)
* V2 phases closed: 5 (Phase 6, Phase 7, Phase 8, Phase 9, Phase 10)
* V2 planning docs created: v2_plan.md, v2_adapters.md, v2_onboarding.md
