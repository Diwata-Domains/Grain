# Task: Record existing-project adoption entry criteria and planning boundary

## Metadata
- **ID:** TASK-0067
- **Status:** done
- **Phase:** Phase 7 — New-Project Onboarding Flow
- **Backlog:** P7-T07
- **Packet Path:** tasks/P7-T07-TASK-0067/
- **Dependencies:** TASK-0066
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Record the concrete entry criteria and planning boundary for starting existing-project adoption work (FR-013) now that the new-project onboarding slice has stabilized.

## Why This Task Exists
Phase 7 intentionally deferred existing-project adoption until the new-project onboarding path was proven. With `P7-T06` complete, this task locks the handoff boundary so future adoption work can start without destabilizing the proven path.

## Scope
- Update `docs/working/v2_onboarding.md` with explicit entry criteria and non-goals for existing-project adoption kickoff.
- Update `docs/working/future_roadmap.md` (FR-013) with the same boundary and promotion conditions.
- Update `docs/working/current_focus.md` so immediate goals reflect review/close and boundary enforcement.

## Constraints
- Keep this packet planning-boundary only; do not implement existing-project adoption behavior.
- Do not modify canonical docs directly.
- Keep the new-project onboarding path as the only proven implementation path until a new phase starts.

## Escalation Conditions
- If boundary criteria require canonical workflow or data-contract changes, record a change proposal instead of editing canonical docs.
- If adoption kickoff criteria conflict with Phase 7 decisions, stop and log the conflict explicitly.

## Model Selection Rationale
`open_model` is appropriate because this is a bounded working-doc planning update with no architectural or CLI behavior changes.
