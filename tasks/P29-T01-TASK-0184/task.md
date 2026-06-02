# Task: Harden runtime and prompt guidance for Grain/Assay loop discipline

## Metadata
- **ID:** TASK-0184
- **Status:** done
- **Phase:** Phase 29 — Workflow Compliance Hardening
- **Backlog:** P29-T01
- **Packet Path:** tasks/P29-T01-TASK-0184/
- **Dependencies:** TASK-0183
- **Primary Adapter:** docs_adapter
- **Secondary Adapters:** none

## Objective
Tighten the runtime docs and shipped prompt assets so long agent sessions are more likely to stay inside the Grain and Assay loop, with clearer “stop and return to workflow” rules when the active packet, review gate, or verification step is being bypassed.

## Why This Task Exists
Recent live usage showed that agents sometimes drift mid-conversation and need manual redirection back to Grain and Assay. The first hardening move should target the surfaces agents actually read during execution, review, and close before adding heavier enforcement code.

## Scope
- Strengthen runtime guidance in `AGENTS.md`, `CLAUDE.md`, and `PROJECT_RULES.md`.
- Strengthen executor/close prompt assets to stop and return to the Grain/Assay loop when drift is detected.
- Add release-surface coverage so these guardrails do not regress.

## Constraints
- Keep the rules file-backed and aligned with the current CLI/workflow behavior.
- Do not invent new command surfaces or hidden workflow state in this slice.

## Escalation Conditions
- Stop if the guidance changes would require new canonical workflow semantics instead of restating the existing Grain/Assay loop more clearly.
