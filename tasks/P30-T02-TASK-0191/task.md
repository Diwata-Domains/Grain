# Task: Define Grain ↔ Assay ↔ toolkit contract boundary

## Metadata
- **ID:** TASK-0191
- **Status:** draft
- **Phase:** Phase 30 — v0.4.0 Planning
- **Backlog:** P30-T02
- **Packet Path:** tasks/P30-T02-TASK-0191/
- **Dependencies:** TASK-0190
- **Primary Adapter:** docs

## Objective
Write the explicit contract spec for how sibling tools (Assay, and eventually Conclave and other Diwata toolkit members) interoperate with Grain without relying on chat memory as the integration layer. This is the boundary doc that makes Grain a composable toolkit component, not just a standalone CLI.

## Why This Task Exists
v0.4.0's "composable toolkit" theme only becomes real when the contracts are explicit. Phase 28 delivered the Assay verification bridge (`grain verify`), but the contract is currently defined at the CLI-command level. A transport-neutral contract — one that works across CLI, MCP, and file exchange — is required before `grain recipe` and other multi-tool workflows can be designed reliably.

## Scope
- Define what "toolkit contract" means at Grain's level: what Grain exposes, what format, what version model
- Specify the Grain ↔ Assay contract: what events/results Assay sends to Grain, what Grain does with them
- Specify the forward-compatible extension points: how future tools (Conclave, DAEMON) call Grain without requiring bespoke CLI wrappers per tool
- Decide on transport format (options: JSON file artifacts on disk, structured stdout, named pipe/socket, HTTP locally)
- Write `docs/canonical/toolkit_contract.md` — the public-facing inter-tool contract spec

## Deliverable
`docs/canonical/toolkit_contract.md` — inter-tool contract spec.

## Constraints
- Local-first: the contract must work without a running server or cloud service
- The transport decision must not force a network hop for Grain-to-Assay calls in the common case
- The contract must version gracefully — a future Grain can extend the contract without breaking existing Assay integrations
