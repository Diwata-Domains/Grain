# Task: Spec the `grain recipe` command group

## Metadata
- **ID:** TASK-0192
- **Status:** draft
- **Phase:** Phase 30 — v0.4.0 Planning
- **Backlog:** P30-T03
- **Packet Path:** tasks/P30-T03-TASK-0192/
- **Dependencies:** TASK-0190, TASK-0191
- **Primary Adapter:** docs

## Objective
Write the full spec for `grain recipe` — what recipes are, how they are defined, how they are executed, and how they relate to the existing task packet + workflow loop model. This is the canonical design document for the recipe execution layer.

## Why This Task Exists
Phase 27 shipped the recipe planning layer (recipe packet scaffolds), but recipe *execution* was deferred as a v0.4.0 deliverable. Before implementation can begin, the design questions need answers: What is a recipe unit? How does `grain recipe run` work? How does it relate to `grain workflow loop`?

## Scope
- Define the recipe unit: is it a prompt, a packet template, a workflow slice, or a parameterized workflow?
- Specify `grain recipe list` — discover available recipes in the project
- Specify `grain recipe run <name>` — execute a recipe (parameterized, reviewable, traceable)
- Specify `grain recipe scaffold <name>` — create a new recipe from a template
- Define the recipe file format: what a recipe packet contains, where it lives, what parameters it accepts
- Define the relationship to `grain workflow loop` — do recipes run inside the loop or alongside it?
- Define the relationship to the toolkit contract — can a recipe call Assay or invoke a sibling tool?
- Write `docs/canonical/recipe_spec.md`

## Deliverable
`docs/canonical/recipe_spec.md` — recipe command group spec.

## Constraints
- Recipes must be file-backed and inspectable — no hidden state
- Recipe execution must produce a traceable artifact (what ran, what changed, review evidence)
- Recipes cannot mutate state outside the task packet system
- Do not design around a specific AI provider — recipes invoke Grain's existing prompt/agent infrastructure
