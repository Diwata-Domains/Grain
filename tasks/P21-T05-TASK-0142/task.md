# Task: Decide Obsidian support shape

## Metadata
- **ID:** TASK-0142
- **Status:** done
- **Mode:** simple
- **Phase:** Phase 21 — v0.3.0 Planning and Operator Surface Definition
- **Backlog:** P21-T05 — Decide Obsidian support shape
- **Packet Path:** tasks/P21-T05-TASK-0142/
- **Dependencies:** none
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Lock the Obsidian support direction for v0.3.0 and record the planning decision that Grain should treat Obsidian as a dedicated adapter domain rather than as generic markdown under `docs_adapter`. Also seed future adapter direction for database and scraping/crawler workflows.

## Why This Task Exists
Obsidian is part of the locked v0.3.0 core. The repo needs an explicit adapter boundary so later implementation can build vault-aware behavior intentionally. Database and crawler workflows are also important recurring domains and should be recorded as dedicated future adapter directions rather than buried in generic notes.

## Scope
- decide whether Obsidian stays in `docs_adapter` or becomes `obsidian_adapter`
- record the minimum intended Obsidian surface for v0.3.0
- seed future dedicated adapter direction for database and scraping/crawler workflows

## Constraints
- remain within planning scope; do not implement adapter code in this task
- preserve local-first, file-backed Grain behavior

## Escalation Conditions
- if Obsidian support would require broad GUI or hosted-service assumptions, stop and re-scope
