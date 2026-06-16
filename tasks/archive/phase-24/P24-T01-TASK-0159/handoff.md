# Handoff: TASK-0159

## Final State
`Local MCP wrapper scaffold for desktop invocation` is ready for handoff.

## Review Bundle

### Packet Identity
- **Task ID:** TASK-0159
- **Phase:** Phase 24 — Desktop Integrations and Obsidian Support
- **Status:** review

### Outcome
- **Review Readiness:** blocked
- **User Review State:** pending
- **Verification State:** not_run
- **Recommended Next Status:** review
- **Short Summary:** Implemented the first local MCP wrapper scaffold for Grain. The repo now exposes `grain mcp manifest` for desktop-client config and `grain mcp serve` for stdio transport, backed by a narrow read-oriented tool surface over existing workflow, prompt, review, and office-review inspection behavior. The wrapper stays local-first and file-backed, and it does not introduce a parallel workflow API or background service.

## What Was Built
- Packet handoff support is ready.

## What Review Should Check
- - verify that the MCP wrapper stays a thin local adapter over existing Grain services and does not introduce hidden state
- - verify that the tool surface is intentionally narrow and read-oriented for this first desktop slice
- - verify that the manifest and stdio transport are enough to begin Claude/Desktop-style local invocation without broadening into hosted orchestration
- 

## What Was Not Done
- [follow-up note, or "None"]

## Known Issues or Follow-ups
- full-suite verification is still deferred; this slice is validated through focused MCP and CLI tests only
- workflow-run duplicate packet drift still exists as a known platform issue, though the active duplicates were moved out of the task root before this task began

## Files Changed
- - `src/grain/services/mcp_service.py` — added the local stdio MCP scaffold, tool catalog, and shared read-oriented action routing over existing Grain services
- - `src/grain/cli/mcp.py` — added `grain mcp manifest` and `grain mcp serve` as the local desktop wrapper surface
- - `src/grain/cli/__init__.py` — wired the new `mcp` command group into the main Grain CLI
- - `tests/test_mcp_cmd.py` — added focused coverage for MCP manifest output, initialize/tools/list, routed workflow/prompt tools, and stdio serve behavior
- - `tasks/P24-T01-TASK-0159/task.md` — filled packet metadata and advanced status to `review`
- - `tasks/P24-T01-TASK-0159/context.md` — recorded the scoped desktop-wrapper context for the task
- - `tasks/P24-T01-TASK-0159/plan.md` — recorded the MCP scaffold and verification approach
- - `tasks/P24-T01-TASK-0159/deliverable_spec.md` — recorded the deliverable boundary for the local MCP scaffold
- 

## Reviewer Notes
- - verify that the MCP wrapper stays a thin local adapter over existing Grain services and does not introduce hidden state
- - verify that the tool surface is intentionally narrow and read-oriented for this first desktop slice
- - verify that the manifest and stdio transport are enough to begin Claude/Desktop-style local invocation without broadening into hosted orchestration
- 

## Closeout Intake

### Open Questions To Log
- [question summary, or "None"]

### Proposal Candidates To Log
- [proposal summary, or "None"]

### Follow-Ups To Log
- [follow-up note, or "None"]
