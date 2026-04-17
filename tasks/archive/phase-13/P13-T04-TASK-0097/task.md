# Task: Existing-project onboarding workflow prompt

## Metadata
- **ID:** TASK-0097
- **Status:** done
- **Phase:** Phase 13 — Existing Project Adoption
- **Backlog:** P13-T04
- **Packet Path:** tasks/P13-T04-TASK-0097/
- **Dependencies:** TASK-0096
- **Primary Adapter:** docs_adapter
- **Secondary Adapters:** code_adapter

## Objective
Author `prompts/workflow.onboard.existing.md` as the stable agent prompt for existing-project adoption, including mandatory CLI call steps and a clear draft-first review flow.

## Why This Task Exists
Phase 13 requires an explicit prompt entrypoint for existing repositories so operators and agents follow a deterministic adoption sequence: scaffold, validate, clarify unknowns, and draft docs with human review gates.

## Scope
- Add `prompts/workflow.onboard.existing.md`
- Include prompt metadata and scope boundary for existing-project adoption
- Include mandatory CLI steps with explicit command examples
- Define required behavior for additive-only updates and unresolved-gap handling
- Define required output contract for command summary, assumptions, questions, and follow-ups
- Add prompt-surface tests to lock prompt presence and mandatory CLI command coverage

## Constraints
- Prompt must not redefine canonical truth; it operationalizes existing docs
- Prompt must preserve human authority and review gates
- Existing-project flow only; no new-project onboarding behavior in this prompt

## Escalation Conditions
- If prompt requirements conflict with canonical workflow/runtime rules, stop and log proposal in `docs/working/change_proposals.md`
