# Deliverable Spec: TASK-0159

## Required Output

### New Files
- `src/grain/services/mcp_service.py` — stdio MCP scaffold and shared tool routing over existing Grain services
- `src/grain/cli/mcp.py` — CLI manifest and serve commands for local desktop invocation
- `tests/test_mcp_cmd.py` — focused MCP protocol and CLI coverage

### Modified Files
- `src/grain/cli/__init__.py` — wire the new MCP command group into the Grain CLI
- `tasks/P24-T01-TASK-0159/*` — complete the packet review artifacts for the MCP scaffold slice

## Acceptance Checklist
- [x] a local stdio MCP scaffold exists and keeps Grain CLI commands canonical
- [x] a small read-oriented tool surface is exposed through shared action routing over existing Grain services
- [ ] All new tests passing
- [ ] Full test suite passing with no regressions
- [ ] review bundle complete in `results.md` and `handoff.md`

## Not Required
- hosted orchestration or background services
- broad writable MCP mutation flows
- Obsidian-specific adapter behavior
