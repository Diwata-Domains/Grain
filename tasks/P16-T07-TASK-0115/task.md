# Task: Add grain embedding show

## Metadata
- **ID:** TASK-0115
- **Status:** done
- **Phase:** Phase 16 — Semantic Enrichment Layer
- **Backlog:** P16-T07 — Add `grain embedding show`
- **Packet Path:** tasks/P16-T07-TASK-0115/
- **Dependencies:** TASK-0109, TASK-0111, TASK-0112, TASK-0113
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add a dedicated `grain embedding show` command that reports configured provider, active provider, configured and active models, provider availability, and fallback state in both text and JSON output.

## Why This Task Exists
Phase 16 needs an operator-visible way to inspect semantic-provider resolution. Without a CLI command, fallback behavior and provider reachability stay implicit and are harder to debug.

## Scope
- add an embedding inspection command group and show command
- expose runtime provider resolution through a small service boundary
- add text and JSON command coverage

## Constraints
- preserve provider-agnostic CLI semantics
- report fallback behavior explicitly instead of relying on hidden defaults

## Escalation Conditions
- the command requires a broader canonical change to CLI structure or semantics
- provider inspection needs secrets or network checks beyond the existing status contracts
