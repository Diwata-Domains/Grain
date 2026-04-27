# Results: TASK-0140

## Packet State
- **Current Task Status:** in_progress
- **Review Readiness:** pending
- **Recommended Next Status:** review

## Files Changed
- `prompts/task.execute.md` and `src/grain/data/prompts/task.execute.md` — added packet-first execution guardrails before any code change
- `prompts/tasks.next_and_implement.md` and `src/grain/data/prompts/tasks.next_and_implement.md` — clarified that execution requires an on-disk packet and matching `current_task.md`
- `src/grain/services/agents_md_service.py` — strengthened generated AGENTS guidance against coding from chat context without a packet
- `src/grain/data/runtime/context_loading.md` and `docs/runtime/context_loading.md` — added implementation-time stop conditions when no packet exists yet
- `docs/runtime/CLAUDE.md` — reinforced active-packet-first behavior for local repo instructions
- `tests/test_agents_md_cmd.py` and `tests/test_release_surface.py` — added regression coverage for packet-first guardrails

## Summary
Implemented the Phase 20 prompt hardening slice. The shipped execution prompts, bundled runtime guidance, and generated AGENTS instructions now all treat packet creation or packet activation as a prerequisite for implementation. This reduces the chance that resumed sessions will treat backlog context or chat history as sufficient authority to start coding without a task packet on disk.

## Test Results
2/2 targeted test files passing. 20 targeted tests passed.

## Efficiency
<!-- Fill in at close. Use "n/a" for any field not applicable to your project or agent model. -->
<!-- Tokens: use exact count if your runtime exposes it; otherwise record "n/a". -->

### Execute
- **Prompt Runs:** n/a
- **Conversation Restarts:** n/a
- **Files Read (est.):** n/a
- **Tokens:** n/a
- **Notes:** Focused on shipped prompt surfaces, generated AGENTS guidance, and release-surface regression tests only.

### Review
- **Prompt Runs:** n/a
- **Conversation Restarts:** n/a
- **Files Read (est.):** n/a
- **Tokens:** n/a
- **Notes:** None

### Close
- **Prompt Runs:** n/a
- **Conversation Restarts:** n/a
- **Files Read (est.):** n/a
- **Tokens:** n/a
- **Notes:** None

## Review Notes
- Confirm the new wording is strong enough to stop resumed sessions from coding before a packet exists, without implying new hidden workflow commands.
- Confirm the AGENTS block and bundled prompt assets stay aligned on packet-first language.

## User Review
<!-- reviewer fills this section — executor must leave all fields below as-is -->
- **State:** approved
- **Summary:** Approved to continue.
- **Resolution Mode:** close_task

### Required Fixes
- None

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- None

### Residual Risks
- None

## Verification Review
<!-- verifier fills this section when applicable; otherwise leave defaults -->
- **State:** [not_run / pending / passed / failed / inconclusive / waived]
- **Summary:** [verifier fills, or "No verifier configured"]

### Findings
- [finding, or "None"]

## Closure Decision
<!-- closer fills this section during final closeout -->
- **Decision:** closed
- **Reason:** Closed via grain task close.

### Closure Blockers
- None

## Deliverable Checklist
- [x] Stable execution prompts explicitly require packet creation or activation before code changes
- [x] Generated agent instructions warn against implementing from chat context without a packet on disk
- [x] Bundled runtime guidance tells agents to stop if no active packet exists yet
- [x] Focused packet-first guardrail tests passing
- [ ] Full test suite passing

## Blockers
Full-suite validation was not run in this turn; only the focused prompt/agent-instruction tests were executed.
