# Task: Define workflow recipes and expand adapter scope

## Metadata
- **ID:** TASK-0144
- **Status:** draft
- **Mode:** simple
- **Phase:** Phase 21 — v0.3.0 Planning and Operator Surface Definition
- **Backlog:** P21-T07 — Define reusable workflow recipes
- **Packet Path:** tasks/P21-T07-TASK-0144/
- **Dependencies:** none
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Lock the first recipe layer for Grain and update the v0.3.0 contract so `database_adapter` and `crawler_adapter` are explicitly in scope rather than deferred to the future roadmap.

## Why This Task Exists
The user wants database and crawler workflows in v0.3.0, and Grain still needs a concrete decision on whether recipes belong in the first operator surface. Without this task, those domains remain split between future-roadmap intent and active-release planning.

## Scope
- define the initial recipe layer
- promote `database_adapter` into v0.3.0 scope
- promote `crawler_adapter` into v0.3.0 scope and choose the preferred adapter name

## Constraints
- recipes must stay thin over the existing workflow and packet model
- adapter-scope expansion here is planning only, not implementation

## Escalation Conditions
- if the recipe layer starts acting like a second orchestration engine, stop and re-scope
