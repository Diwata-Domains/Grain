# Task: Obsidian vault context and wiki-link handling

## Metadata
- **ID:** TASK-0163
- **Status:** done
- **Phase:** Phase 24 — Desktop Integrations and Obsidian Support
- **Backlog:** P24-T04 — Obsidian vault context and wiki-link handling
- **Packet Path:** tasks/P24-T04-TASK-0163/
- **Dependencies:** TASK-0162
- **Primary Adapter:** obsidian_adapter
- **Secondary Adapters:** none

## Objective
Implement the first Obsidian-specific vault context behavior so `obsidian_adapter` can prioritize a target note and its wiki-linked neighbors ahead of unrelated markdown, while keeping the flow file-backed, additive, and safe for the existing context-selection pipeline.

## Why This Task Exists
Phase 24 promoted Obsidian into a dedicated adapter, but the scaffold alone does not yet provide vault-aware selection behavior. This task turns that contract into one bounded, real capability by teaching the context pipeline to recognize note adjacency through wiki-links without introducing a separate Obsidian service layer or hidden state.

## Scope
- add one vault-aware context-selection behavior for `obsidian_adapter`, centered on target-note and wiki-link neighbor prioritization
- add focused tests and packet artifacts that prove frontmatter- and wiki-link-bearing notes are selected and ordered correctly

## Constraints
- keep the implementation inside the existing context-selection and export flow; do not add a separate vault database, background index, or hidden cache
- do not broaden into Obsidian mutation helpers, full graph traversal, or desktop integration changes in this task

## Escalation Conditions
- if the first vault-aware behavior requires redefining the broader semantic reranking contract or broadening into a full Obsidian graph engine, stop and re-scope before implementation
