# Task: Define desktop integration strategy

## Metadata
- **ID:** TASK-0141
- **Status:** done
- **Mode:** simple
- **Phase:** Phase 21 — v0.3.0 Planning and Operator Surface Definition
- **Backlog:** P21-T04 — Define desktop-app integration strategy
- **Packet Path:** tasks/P21-T04-TASK-0141/
- **Dependencies:** TASK-0141 depends conceptually on P21-T01 milestone contract; no packet dependency
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Lock the desktop-app integration strategy for Grain v0.3.0 so later implementation work has a single canonical path for Codex-style CLI use, Claude/Desktop-style MCP use, and future ChatGPT/OpenAI app-style integration without forking the command model.

## Why This Task Exists
v0.3.0 requires a credible operator surface beyond raw terminal-only use. Desktop integration is part of the locked milestone contract, but the repo still needs an explicit decision on what remains CLI-native versus what should be wrapped through MCP or app-server boundaries.

## Scope
- define the canonical desktop integration path for Grain
- decide the role of CLI, local MCP, and app-server style integration
- record future adapter notes for database and crawler/scraping workflows only at a planning level

## Constraints
- remain local-first and file-backed
- do not introduce hosted service assumptions or a second bespoke command model

## Escalation Conditions
- if the desktop strategy requires cloud orchestration or a non-local control plane, stop and re-scope
