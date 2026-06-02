# Task: Crawl config and selector context selection

## Metadata
- **ID:** TASK-0171
- **Status:** done
- **Phase:** Phase 26 — Crawler Adapter
- **Backlog:** P26-T02 — Crawl config and selector context selection
- **Packet Path:** tasks/P26-T02-TASK-0171/
- **Dependencies:** TASK-0170
- **Primary Adapter:** crawler_adapter
- **Secondary Adapters:** none

## Objective
Implement the first crawler-specific context behavior so `crawler_adapter` can select and prioritize crawl configs, selector definitions, and extraction-schema artifacts ahead of unrelated application code while staying inside the existing file-backed context pipeline.

## Why This Task Exists
The crawler adapter scaffold exists, but it is not useful yet without a first real context behavior. This task turns the contract into a bounded selection rule so crawler work can load the right files before broader extraction-quality and validation hints land.

## Scope
- add the first `crawler_adapter` context-selection behavior for crawl configs, selectors, and extraction schemas
- add focused integration coverage that proves unrelated application code is excluded while crawler-relevant files are selected and ordered correctly

## Constraints
- keep the behavior additive inside the existing adapter selection pipeline; do not introduce a new crawl database, background state, or execution service
- keep output-validation and broader extraction-quality prioritization scoped out until `P26-T03`

## Escalation Conditions
- if the slice requires a general-purpose crawler graph or execution layer before crawl-config and selector selection is stable, stop and re-scope before implementation
