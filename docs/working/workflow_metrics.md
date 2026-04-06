# Workflow Metrics

## Project

Forge

---

## Phase Metrics

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

## Aggregate

* Total tasks completed: 53
* Total blocked: 0
* Total tests at v1 close: 379
* Open questions resolved total: Q1–Q11 (all 11 resolved)
* Canonical change proposals applied total: CP-001 through CP-008 (all 8 applied)
* V1 phases closed: 5 (all complete)
* Major v1 additions: full CLI (init/docs/task/context/model/review), packet lifecycle, doc registry, context assembly, model routing, review/handoff/summary commands, integration tests, golden fixtures
* V2 planning docs created: v2_plan.md, v2_adapters.md, v2_onboarding.md
