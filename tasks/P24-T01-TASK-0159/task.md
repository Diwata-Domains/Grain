# Task: Local MCP wrapper scaffold for desktop invocation

## Metadata
- **ID:** TASK-0159
- **Status:** done
- **Phase:** Phase 24 — Desktop Integrations and Obsidian Support
- **Backlog:** P24-T01 — Local MCP wrapper scaffold for desktop invocation
- **Packet Path:** tasks/P24-T01-TASK-0159/
- **Dependencies:** Phase 23
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add the first thin local MCP wrapper surface for Claude/Desktop-style environments while keeping Grain CLI commands canonical. Scope this to local stdio tool exposure and shared action routing over existing Grain read-oriented workflow services.

## Why This Task Exists
Phase 24 starts the desktop integration slice. Grain needs a local-first wrapper surface that desktop MCP clients can invoke without bypassing the CLI-first, file-backed workflow model. This task establishes the scaffold and tool-routing boundary before broader desktop helpers or Obsidian work.

## Scope
- add a local MCP server scaffold over stdio plus a manifest/config surface for desktop clients
- expose a small read-oriented Grain tool set that routes to existing workflow, prompt, review, and office-review inspection behavior

## Constraints
- keep Grain CLI commands canonical; the MCP wrapper must stay a thin adapter over existing services
- do not open broad mutation or hosted orchestration behavior in this first scaffold

## Escalation Conditions
- if the scaffold requires a hosted service, background daemon, or a parallel workflow API instead of a thin local wrapper, stop and re-scope before implementation
