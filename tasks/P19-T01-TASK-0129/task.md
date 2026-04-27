# Task: Define community registry hosting and trust contract

## Metadata
- **ID:** TASK-0129
- **Status:** done
- **Phase:** Phase 19 — Community Adapter Registry
- **Backlog:** P19-T01
- **Packet Path:** tasks/P19-T01-TASK-0129/
- **Dependencies:** TASK-0128
- **Primary Adapter:** docs_adapter
- **Secondary Adapters:** none

## Objective
Define the authoritative hosting and trust contract for Phase 19 community adapters. This task resolves where community adapters live, how Grain should distinguish official/community/local adapters operationally, what install sources are considered in-bounds for the first registry slice, and the high-level promotion criteria from Community to Official.

## Why This Task Exists
Phase 19 is blocked on a distribution decision. Without a clear registry home and trust boundary, `grain adapter install`, package validation, CI review flow, and author guidance would all be underspecified and likely drift.

## Scope
- resolve Q19 and record the hosting model
- update canonical and working docs with official/community/local adapter definitions and trust boundaries
- set the Phase 19 assumption for install-source addressing and promotion criteria at a high level
- keep the decision narrow enough that later tasks can implement validation/install mechanics against it

## Constraints
- preserve the existing adapter contract and local/private adapter workflow
- keep all Phase 19 outputs proposal-only until explicit install or review actions occur
- do not implement install or validation code in this task

## Escalation Conditions
- if the hosting decision would require changing the existing official/custom adapter contract rather than extending it, stop and log the canonical gap
- if no single hosting model can support deterministic install and review behavior, stop and surface the tradeoff explicitly
