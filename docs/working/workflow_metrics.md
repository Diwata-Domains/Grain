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

* Tasks completed: 0
* Blocked tasks: 0
* Prompt runs: 0
* Avg prompt runs per completed task: n/a
* Manual interventions: 0
* First-pass success rate: n/a
* Rework count: 0
* Drift incidents: 0
* Phase duration: active

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

* What to tighten next: use the metrics set above to track context quality, routing quality, and token efficiency while the phase is active
* This phase should produce enough data to support a future metrics dashboard without adding dashboard scope now

### Phase Retrospective Classification

At phase review or close, record:

* Fix now: workflow bugs or drift that should be corrected before the next task or next phase
* Batch next phase: repeated friction, validator ideas, prompt cleanup, metrics cleanup, or ergonomics improvements worth carrying forward
* Ignore: one-off noise or issues not worth system change

---

## Aggregate

* Total tasks completed: 31
* Total blocked: 0
* Total tests at end of Phase 3: 272
* Open questions at end of Phase 3: 2 (Q7, Q8 — not blocking Phase 4)
* Canonical change proposals applied: 2 (CP-001, CP-002)
