# Task: Crawler review and safety guidance

## Metadata
- **ID:** TASK-0173
- **Status:** done
- **Phase:** Phase 26 — Crawler Adapter
- **Backlog:** P26-T04 — Crawler review and safety guidance
- **Packet Path:** tasks/P26-T04-TASK-0173/
- **Dependencies:** TASK-0170, TASK-0172
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add shipped operator guidance for crawler review and safety so Grain makes robots constraints, rate-limit and retry risks, selector brittleness, and extraction drift explicit before crawler work is considered review-ready.

## Why This Task Exists
The crawler adapter now has useful context behavior, but safe operator use depends on clear review and validation guidance. This task makes those safety expectations explicit in the shipped docs before the phase closes.

## Scope
- add crawler-specific review and safety guidance to the shipped operator/runtime docs
- add regression assertions that the shipped guidance mentions the dedicated crawler adapter and its main review risks

## Constraints
- keep this task in guidance and shipped-doc surfaces; do not introduce new crawler execution features
- preserve the CLI-first, packet-first, file-backed workflow boundary in all review guidance

## Escalation Conditions
- if the guidance implies live crawling or hidden state rather than review/validation expectations, stop and narrow the language before implementation
