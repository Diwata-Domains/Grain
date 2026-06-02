# Task: Output-validation and extraction-surface hints

## Metadata
- **ID:** TASK-0172
- **Status:** done
- **Phase:** Phase 26 — Crawler Adapter
- **Backlog:** P26-T03 — Output-validation and extraction-surface hints
- **Packet Path:** tasks/P26-T03-TASK-0172/
- **Dependencies:** TASK-0171
- **Primary Adapter:** crawler_adapter
- **Secondary Adapters:** none

## Objective
Extend `crawler_adapter` context behavior so output schemas, normalization steps, and validation fixtures are included as secondary context when the task objective is explicitly about extraction quality or downstream crawl outputs, while preserving the narrower config/selector-first bundle for other crawler tasks.

## Why This Task Exists
The first crawler context slice established crawl-config and selector selection, but recurring crawler work often targets extraction quality and output validation rather than only crawl planning. This task broadens the adapter just enough to cover that objective-driven validation context without dragging in unrelated application code.

## Scope
- add objective-sensitive output, fixture, normalization, and extraction-surface prioritization on top of the existing crawler adapter selection rules
- add focused integration coverage that proves quality-oriented objectives bring output and normalization context ahead of schema artifacts

## Constraints
- keep the behavior additive inside the existing direct-selection crawler adapter flow; do not introduce crawler graph reasoning or runtime tooling
- preserve the narrower config/selector-first bundle when the task objective is not about extraction quality or validation

## Escalation Conditions
- if output-validation selection requires a deeper crawler execution model instead of objective-sensitive file prioritization, stop and narrow the slice before implementation
