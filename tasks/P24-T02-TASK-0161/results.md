# Results: TASK-0161

## Packet State
- **Current Task Status:** review
- **Review Readiness:** approved
- **Recommended Next Status:** done

## Files Changed
- `README.md` — added explicit Codex/CLI-first guidance and clarified when to use direct CLI versus the local MCP wrapper
- `docs/runtime/AGENTS.md` — added desktop invocation guidance that keeps the CLI canonical for Codex/tool-execution paths and positions `grain mcp` as the desktop-client wrapper
- `tests/test_release_surface.py` — added assertions that the shipped guidance covers the Codex direct-CLI path and the MCP desktop path
- `tasks/P24-T02-TASK-0161/task.md` — filled packet metadata and advanced status to `review`
- `tasks/P24-T02-TASK-0161/context.md` — recorded the scoped Codex/CLI guidance context for the task
- `tasks/P24-T02-TASK-0161/plan.md` — recorded the guidance-first implementation and verification approach
- `tasks/P24-T02-TASK-0161/deliverable_spec.md` — recorded the deliverable boundary for the Codex/CLI integration slice

## Summary
Completed the Codex and CLI integration guidance slice for Phase 24. Grain now explains the desktop/tool-execution split explicitly: Codex and similar environments should call `grain` directly and prefer JSON output for structured state, while Claude/Desktop-style environments may use the local MCP wrapper without changing the CLI-first workflow boundary.

## Test Results
- `/Users/barbaricum/diwata-labs/.venv/bin/python -m pytest -q tests/test_release_surface.py tests/test_mcp_cmd.py tests/test_cli_entrypoint.py tests/test_workflow_next_cmd.py tests/test_prompt_show_cmd.py`
- `30 passed in 1.10s`

## Efficiency
<!-- Fill in at close. Use "n/a" for any field not applicable to your project or agent model. -->
<!-- Tokens: use exact count if your runtime exposes it; otherwise record "n/a". -->

### Execute
- **Prompt Runs:** n/a
- **Conversation Restarts:** n/a
- **Files Read (est.):** n/a
- **Tokens:** n/a
- **Notes:** None

### Review
- **Prompt Runs:** [count or "n/a"]
- **Conversation Restarts:** [count or "n/a"]
- **Files Read (est.):** [count or "n/a"]
- **Tokens:** [count or "n/a"]
- **Notes:** ["None" until reviewer fills this in]

### Close
- **Prompt Runs:** [count or "n/a"]
- **Conversation Restarts:** [count or "n/a"]
- **Files Read (est.):** [count or "n/a"]
- **Tokens:** [count or "n/a"]
- **Notes:** ["None" until closer fills this in]

## Review Notes
- verify that the Codex path is clearly documented as direct CLI usage rather than a second wrapper layer
- verify that the MCP wrapper is still described as optional and local-first for desktop clients
- verify that this slice stayed guidance-heavy and did not broaden into unneeded helper commands

## User Review
<!-- reviewer fills this section — executor must leave all fields below as-is -->
- **State:** approved
- **Summary:** Approved to close and carry forward as the Codex and CLI integration guidance slice for the Phase 24 desktop path.
- **Resolution Mode:** close_task

### Required Fixes
- None

### Open Questions To Log
- None

### Proposal Candidates To Log
- None

### Follow-Ups To Log
- carry the dedicated vault-surface work into `P24-T03` and keep the Codex/CLI split explicit in later desktop docs

### Residual Risks
- full-suite verification is still deferred; this slice is validated through focused docs, MCP, and CLI tests only
- workflow-run duplicate packet drift remains a known platform issue even though active duplicates are being archived out of the task root as they occur

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
- [x] the Codex/CLI-first operating path is explicit in repo-facing guidance
- [x] any helper surface added stays thin and preserves the CLI as the canonical Grain interface
- [x] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Blockers
None.
