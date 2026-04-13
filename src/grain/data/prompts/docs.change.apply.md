# Apply Approved Change Proposal

You are applying an approved change proposal to the project documentation system.

## Objective

Take an already reviewed and approved change proposal and update the appropriate project documents so they reflect the approved decision.

## Step 1 — Read Files

Read:

* docs/runtime/PROJECT_RULES.md

* docs/runtime/docs_index.md

* docs/runtime/docs_manifest.yaml

* docs/runtime/context_loading.md

* docs/runtime/agent_profiles.md

* docs/working/change_proposals.md

* docs/working/open_questions.md

* docs/working/implementation_plan.md

* docs/working/backlog.md

* docs/working/current_focus.md

Read the specific approved proposal being applied.

Read only the canonical docs and working docs affected by that proposal.

Read relevant task artifacts only if they are needed to understand the proposal history or implementation impact.

## Step 2 — Confirm Proposal Status

Before applying anything, confirm that the proposal is:

* explicitly approved by the human
* clearly scoped
* specific enough to apply
* not in conflict with higher-authority rules

If approval or scope is unclear, stop and report that the proposal cannot yet be applied.

## Step 3 — Determine Update Scope

Identify exactly which documents need updates.

Possible targets include:

* canonical docs
* working docs
* runtime docs
* open questions
* backlog or implementation plan if sequencing changed

Do not update unrelated files.

## Step 4 — Apply the Approved Change

Generate updated contents or targeted patch-style updates for the affected files.

Rules:

* preserve existing terminology and structure
* update only what is required by the approved decision
* do not introduce additional design changes
* do not silently broaden the proposal
* keep canonical docs authoritative and clean

## Step 5 — Reconcile Proposal Tracking

Update proposal tracking appropriately:

* mark the proposal as applied or resolved
* remove or update related open questions if they are no longer unresolved
* update working docs if the approved change affects execution order or current focus

## Step 6 — Validate Consistency

Check that after applying the approved proposal:

* canonical docs remain internally consistent
* working docs align with the updated canonical state
* no stale contradictions remain in open_questions or change_proposals

## Constraints

* DO NOT apply unapproved proposals
* DO NOT invent new changes
* DO NOT modify unrelated docs
* DO NOT generate code
* DO NOT hide unresolved conflicts

## Output

Return ONLY:

1. proposal application decision
2. updated contents or targeted updates for affected docs
3. updates for proposal/open-question tracking
4. any remaining follow-up items

No explanation.
