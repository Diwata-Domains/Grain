# AGENTS.md

## Purpose

This repository contains `Grain`, a CLI-first toolkit for structuring AI-assisted software development workflows.

This system is a workflow orchestrator. It is not an autonomous coding agent.

Your role is to execute narrowly scoped work within the project’s documented workflow.

---

## Read Order

Before doing any work, read documents in this order:

1. `docs/runtime/PROJECT_RULES.md`
2. `docs/runtime/docs_index.md`
3. `docs/runtime/docs_manifest.yaml`
4. `docs/runtime/context_loading.md`
5. `docs/runtime/agent_profiles.md`
6. `docs/working/current_focus.md`
7. the active task packet
8. only the canonical docs relevant to that task
9. working docs only if needed for sequencing, blockers, or status

Do not read the entire repo unless explicitly required.

---

## Authority Rules

Use this authority order:

1. `docs/runtime/PROJECT_RULES.md`
2. `docs/canonical/*`
3. `docs/runtime/docs_manifest.yaml`
4. `docs/runtime/docs_index.md`
5. `docs/working/*`
6. `tasks/*`

If a lower-authority file conflicts with a higher-authority file, follow the higher-authority file.

---

## Core Operating Rules

1. Work through one scoped task at a time.
2. Use task packets as the main execution surface.
3. Prefer minimal edits over broad rewrites.
4. Do not silently change canonical behavior.
5. Do not introduce new architecture unless explicitly required.
6. Keep context narrow and relevant.
7. Record meaningful blockers and outcomes.
8. Keep the system model-agnostic.
9. If the active packet, review gate, or verification step becomes unclear mid-session, stop and return to `grain workflow next` instead of improvising from memory.

---

## Canonical Document Policy

Do not directly edit canonical docs unless explicitly instructed.

Canonical docs include files in `docs/canonical/`.

If a canonical change appears necessary:
- document the issue
- create a proposal in `docs/working/change_proposals.md` or task packet patches
- explain the reason and impact
- do not silently apply the change

---

## Working Document Policy

You may update working docs when appropriate.

Working docs include:
- `docs/working/implementation_plan.md`
- `docs/working/backlog.md`
- `docs/working/current_focus.md`
- `docs/working/open_questions.md`
- `docs/working/change_proposals.md`

Any update must remain consistent with canonical docs.

---

## Task Packet Policy

Every implementation action must map to a single task packet.

A valid task packet should define:
- scope
- objective
- source documents
- constraints
- expected files
- acceptance criteria
- tests
- documentation updates
- definition of done

Do not expand the task beyond the packet without documenting it.

---

## Execution Workflow

For each task:

1. Read required runtime docs
2. Read the active task packet
3. Read only the relevant canonical docs
4. Confirm scope and constraints
5. Make the smallest valid set of changes
6. Record results and blockers
7. Update working docs if required
8. Prepare handoff or review state

If you lose the thread mid-conversation:
- re-run `grain workflow next --format json`
- if Grain stops, run `grain workflow explain` before improvising
- if the explanation points to backlog/packet drift, run `grain workflow reconcile --dry-run`
- re-read `docs/working/current_task.md`
- re-open the active packet on disk
- do not continue from chat memory alone

If Assay verification is part of the loop:
- do not skip `grain verify submit` or `grain verify ingest` just because the task feels "done"
- do not attempt closeout while verification is still `pending`
- if verification fails, stop and surface the finding through the packet instead of overriding it conversationally

### Desktop Invocation Guidance

When this repository is used from external agent environments:

- Codex or any tool-execution environment that can run local commands should call `grain` directly
- prefer `grain workflow next --format json` and `grain prompt show --format json` when the caller wants structured state
- Claude/Desktop-style environments may use the local MCP wrapper instead of direct CLI execution
- `grain mcp manifest` is the local config surface for MCP clients
- `grain mcp serve` is the stdio transport surface

The CLI remains canonical even when the MCP wrapper is used.

For Obsidian vault work:

- prefer the dedicated `obsidian_adapter` instead of treating vault notes as generic docs by default
- preserve frontmatter blocks and wiki-links when summarizing or editing note content
- expect Grain context selection to prioritize the target note and nearby wiki-linked notes before unrelated vault markdown

For database work:

- prefer `database_adapter` when the task is about schema, migrations, queries, repositories, or persistence layers
- review destructive migration risk, downgrade expectations, and schema/query drift before marking database work review-ready
- keep database work file-backed and packet-first; do not improvise live mutation steps or hidden runtime state

For crawler work:

- prefer `crawler_adapter` when the task is about crawl configs, selectors, extraction schemas, fixtures, or output validation
- review robots constraints, rate limits, retry policy risk, selector brittleness, and extraction drift before marking crawler work review-ready
- keep crawler work file-backed and packet-first; do not improvise live crawl execution or hidden runtime state

---

## Model Routing Expectations

Use model roles, not vendor assumptions.

### open_model
Use for:
- narrow drafting
- formatting
- repetitive or mechanical work
- simple packet shaping

### frontier_model
Use for:
- architecture decisions
- ambiguity
- cross-file coordination
- workflow or design reasoning

### reviewer_model
Use for:
- critique
- acceptance checks
- consistency review
- patch review

If the task becomes ambiguous or structurally important, escalate rather than improvise.

---

## Context Discipline

Default to minimum necessary context.

### Always avoid by default
- full repo loading
- unrelated phase docs
- unused prompts
- broad historical context
- future-phase implementation details

### Prefer
- packet-scoped context
- cited canonical sections
- explicit file targets
- small, testable edits

---

## Completion Rules

Do not treat a task as complete unless all are true:

1. The task objective is satisfied
2. Acceptance criteria are met
3. Required tests are addressed
4. Results are recorded
5. Documentation updates are made if required
6. Any canonical changes are proposed, not silently applied
7. No unresolved conflicts are hidden

---

## Non-Goals

Do not:
- act as an autonomous product planner
- redesign the project without instruction
- rewrite stable docs without cause
- merge multiple backlog tasks into one packet
- replace the workflow with ad hoc execution

---

## Standard of Good Work

Good work in this repository is:
- scoped
- explicit
- reversible
- well-documented
- aligned with source-of-truth
- ready for review
