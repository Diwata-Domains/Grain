# Handoff: TASK-0140

## Final State
`Strengthen packet-first guidance in bundled prompts and agent instructions` is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0140
- **Phase:** Phase 20 — Workflow Drift Remediation from Field Usage
- **Status:** review

### Outcome
- **Review Readiness:** blocked
- **User Review State:** pending
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Implemented the Phase 20 prompt hardening slice. The shipped execution prompts, bundled runtime guidance, and generated AGENTS instructions now all treat packet creation or packet activation as a prerequisite for implementation. This reduces the chance that resumed sessions will treat backlog context or chat history as sufficient authority to start coding without a task packet on disk.

## What Was Built
- Packet handoff support is ready.

## What Review Should Check
- - Confirm the new wording is strong enough to stop resumed sessions from coding before a packet exists, without implying new hidden workflow commands.
- - Confirm the AGENTS block and bundled prompt assets stay aligned on packet-first language.
- 

## What Was Not Done
- [follow-up, or "None"]

## Known Issues or Follow-ups
- [risk, or "None"]

## Files Changed
- - `prompts/task.execute.md` and `src/grain/data/prompts/task.execute.md` — added packet-first execution guardrails before any code change
- - `prompts/tasks.next_and_implement.md` and `src/grain/data/prompts/tasks.next_and_implement.md` — clarified that execution requires an on-disk packet and matching `current_task.md`
- - `src/grain/services/agents_md_service.py` — strengthened generated AGENTS guidance against coding from chat context without a packet
- - `src/grain/data/runtime/context_loading.md` and `docs/runtime/context_loading.md` — added implementation-time stop conditions when no packet exists yet
- - `docs/runtime/CLAUDE.md` — reinforced active-packet-first behavior for local repo instructions
- - `tests/test_agents_md_cmd.py` and `tests/test_release_surface.py` — added regression coverage for packet-first guardrails
- 

## Reviewer Notes
- - Confirm the new wording is strong enough to stop resumed sessions from coding before a packet exists, without implying new hidden workflow commands.
- - Confirm the AGENTS block and bundled prompt assets stay aligned on packet-first language.
- 

## Closeout Intake

### Open Questions To Log
- [question, or "None"]

### Proposal Candidates To Log
- [proposal, or "None"]

### Follow-Ups To Log
- [follow-up, or "None"]
