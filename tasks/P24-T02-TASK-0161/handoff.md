# Handoff: TASK-0161

## Final State
`Codex and CLI integration guidance/helpers` is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0161
- **Phase:** Phase 24 — Desktop Integrations and Obsidian Support
- **Status:** review

### Outcome
- **Review Readiness:** blocked
- **User Review State:** pending
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Completed the Codex and CLI integration guidance slice for Phase 24. Grain now explains the desktop/tool-execution split explicitly: Codex and similar environments should call `grain` directly and prefer JSON output for structured state, while Claude/Desktop-style environments may use the local MCP wrapper without changing the CLI-first workflow boundary.

## What Was Built
- Packet handoff support is ready.

## What Review Should Check
- - verify that the Codex path is clearly documented as direct CLI usage rather than a second wrapper layer
- - verify that the MCP wrapper is still described as optional and local-first for desktop clients
- - verify that this slice stayed guidance-heavy and did not broaden into unneeded helper commands
- 

## What Was Not Done
- [follow-up note, or "None"]

## Known Issues or Follow-ups
- full-suite verification is still deferred; this slice is validated through focused docs, MCP, and CLI tests only
- workflow-run duplicate packet drift remains a known platform issue even though active duplicates are being archived out of the task root as they occur

## Files Changed
- - `README.md` — added explicit Codex/CLI-first guidance and clarified when to use direct CLI versus the local MCP wrapper
- - `docs/runtime/AGENTS.md` — added desktop invocation guidance that keeps the CLI canonical for Codex/tool-execution paths and positions `grain mcp` as the desktop-client wrapper
- - `tests/test_release_surface.py` — added assertions that the shipped guidance covers the Codex direct-CLI path and the MCP desktop path
- - `tasks/P24-T02-TASK-0161/task.md` — filled packet metadata and advanced status to `review`
- - `tasks/P24-T02-TASK-0161/context.md` — recorded the scoped Codex/CLI guidance context for the task
- - `tasks/P24-T02-TASK-0161/plan.md` — recorded the guidance-first implementation and verification approach
- - `tasks/P24-T02-TASK-0161/deliverable_spec.md` — recorded the deliverable boundary for the Codex/CLI integration slice
- 

## Reviewer Notes
- - verify that the Codex path is clearly documented as direct CLI usage rather than a second wrapper layer
- - verify that the MCP wrapper is still described as optional and local-first for desktop clients
- - verify that this slice stayed guidance-heavy and did not broaden into unneeded helper commands
- 

## Closeout Intake

### Open Questions To Log
- [question summary, or "None"]

### Proposal Candidates To Log
- [proposal summary, or "None"]

### Follow-Ups To Log
- [follow-up note, or "None"]
