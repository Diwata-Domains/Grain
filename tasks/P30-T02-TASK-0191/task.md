# Task: Define Grain ↔ toolkit contract boundary and multi-repo context model

## Metadata
- **ID:** TASK-0191
- **Status:** draft
- **Phase:** Phase 30 — v0.4.0 Planning
- **Backlog:** P30-T02
- **Packet Path:** tasks/P30-T02-TASK-0191/
- **Dependencies:** TASK-0190
- **Primary Adapter:** docs

## Objective
Write two related specs: (1) the explicit inter-tool contract for how sibling tools (Assay, Conclave, DAEMON) interoperate with Grain without relying on chat memory as the integration layer; and (2) the multi-repo and monorepo workspace context model that determines which Grain workspace is active and how cross-workspace context flows. Both are required before `grain recipe`, `grain suggest`, and multi-tool workflows can be designed reliably.

## Why This Task Exists
**Contract side:** v0.4.0's "composable toolkit" theme only becomes real when the contracts are explicit. Phase 28 delivered the Assay verification bridge (`grain verify`), but the contract is defined at the CLI-command level only. A transport-neutral contract is required before `grain recipe` and `grain suggest` can call sibling tools reliably.

**Multi-repo side:** Real-world Grain usage involves monorepos with multiple nested workspaces (`products/grain/`, `products/assay/`, `apps/apex/`, etc.). Running `grain workflow next` from the wrong directory silently operates on the wrong workspace. There is no mechanism to declare cross-workspace dependencies, link a product workspace to a company-level context repo, or see which workspace is currently active. This is a `medium`-severity friction item in active use (tooling_notes 2026-04-27).

## Scope

### Part 1 — Toolkit Contract
- Define what "toolkit contract" means at Grain's level: what Grain exposes, what format, what version model
- Specify the Grain ↔ Assay contract: what events/results Assay sends to Grain, what Grain does with them
- Specify forward-compatible extension points: how future tools (Conclave, DAEMON) call Grain without bespoke CLI wrappers per tool
- Decide on transport format (options: JSON file artifacts on disk, structured stdout, named pipe/socket); local-first, no network hop required
- Write `docs/canonical/toolkit_contract.md`

### Part 2 — Multi-Repo and Workspace Context Model
- Define workspace resolution order: how Grain picks the active workspace when invoked from any directory in a monorepo
- Define a `grain.toml` or manifest field for declaring: workspace name, parent context repo path, sibling workspace links
- Spec `grain context link <external-path>` (or equivalent): lets a product workspace reference a company-level canonical doc repo without duplicating its content
- Spec `grain workspace list` (or `grain --workspace` flag): lets an agent or operator explicitly select which workspace to operate on
- Define how cross-workspace dependencies appear in task packets — a task that depends on another workspace's phase completing
- Write `docs/canonical/workspace_model.md`

## Deliverables
- `docs/canonical/toolkit_contract.md` — inter-tool contract spec
- `docs/canonical/workspace_model.md` — multi-repo and workspace context model spec

## Constraints
- Local-first: both contracts must work without a running server or cloud service
- The workspace resolution change must be backwards-compatible — single-repo Grain use must be unaffected
- The toolkit contract must version gracefully — a future Grain can extend it without breaking existing Assay integrations
- Do not design a new persistence layer — workspace links are declared in existing config files
