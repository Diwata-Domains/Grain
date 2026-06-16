# Task: `obsidian_adapter` domain profile and vault contract scaffold

## Metadata
- **ID:** TASK-0162
- **Status:** done
- **Phase:** Phase 24 — Desktop Integrations and Obsidian Support
- **Backlog:** P24-T03 — `obsidian_adapter` domain profile and vault contract scaffold
- **Packet Path:** tasks/P24-T03-TASK-0162/
- **Dependencies:** Phase 23
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Create the first dedicated `obsidian_adapter` profile and vault-specific contract surface. Define supported artifact patterns, wiki-link and frontmatter expectations, initial adapter rationale, and the first code/profile hooks needed so Obsidian support is no longer implicitly folded into `docs_adapter`.

## Why This Task Exists
Phase 24 explicitly promotes Obsidian into its own adapter. Grain already handles generic markdown and documents, but Obsidian vaults have wiki-links, frontmatter-heavy workflows, `.obsidian/` configuration, and vault-specific note adjacency that deserve a first-class contract before deeper context behavior lands.

## Scope
- add the first `obsidian_adapter` profile and code/domain scaffold with clear vault-specific boundaries
- document the supported patterns and contract expectations for later wiki-link-aware context behavior

## Constraints
- keep `docs_adapter` generic for markdown/docx/pdf and avoid broad note-vault behavior leaking into it
- do not broaden into full wiki-link-aware context selection yet; this task is the adapter scaffold and contract slice

## Escalation Conditions
- if the adapter scaffold requires redefining the canonical adapter model or broadening into full context-selection behavior prematurely, stop and re-scope before implementation
