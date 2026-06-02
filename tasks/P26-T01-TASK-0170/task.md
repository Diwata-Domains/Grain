# Task: `crawler_adapter` profile and contract scaffold

## Metadata
- **ID:** TASK-0170
- **Status:** done
- **Phase:** Phase 26 — Crawler Adapter
- **Backlog:** P26-T01 — `crawler_adapter` profile and contract scaffold
- **Packet Path:** tasks/P26-T01-TASK-0170/
- **Dependencies:** Phase 25
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Create the first dedicated `crawler_adapter` profile and shipped contract surface so Grain can model crawl-config, selector, extraction-schema, and output-validation work as a first-class adapter instead of leaving crawler workflows implied inside generic code or docs context.

## Why This Task Exists
Phase 26 exists because crawler and scraping workflows are a recurring domain with their own safety boundaries and context needs. This first task establishes the contract boundary before any crawl-config or extraction-aware behavior is added.

## Scope
- add the dedicated `crawler_adapter` profile to the runtime adapter docs and shipped runtime copy
- add focused parser assertions that prove the new crawler adapter contract is present and structurally correct

## Constraints
- keep this task structural; do not broaden into crawl-config or selector-selection behavior yet
- preserve the existing packet-first, file-backed workflow and avoid inventing crawler runtime tooling or hidden state in the scaffold task

## Escalation Conditions
- if the scaffold requires new adapter lifecycle semantics or broader crawl behavior before the contract exists, stop and narrow the slice before implementation
