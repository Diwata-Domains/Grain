# Task: Crawler smoke tests, docs, and closeout

## Metadata
- **ID:** TASK-0174
- **Status:** done
- **Phase:** Phase 26 — Crawler Adapter
- **Backlog:** P26-T05 — Crawler smoke tests, docs, and closeout
- **Packet Path:** tasks/P26-T05-TASK-0174/
- **Dependencies:** TASK-0171, TASK-0172, TASK-0173
- **Primary Adapter:** none
- **Secondary Adapters:** none

## Objective
Add the final smoke coverage and closeout artifacts for the first crawler adapter slice so Phase 26 ends with an integrated proof that crawl configs, selectors, extraction schemas, output fixtures, normalization surfaces, and shipped safety guidance work together inside the packet-first Grain model.

## Why This Task Exists
Phase 26 now has the contract, context behavior, and safety guidance for `crawler_adapter`, but the phase is not complete until those surfaces are validated together through a small smoke slice and recorded in the phase closeout artifacts.

## Scope
- add one integrated crawler adapter smoke test covering export behavior across config, selector, schema, output, and normalization surfaces
- complete the packet and phase-closeout artifacts for the crawler adapter phase

## Constraints
- keep this task as closeout and validation work; do not introduce new crawler features
- preserve the CLI-first, packet-first, file-backed workflow boundary throughout the smoke slice and closeout docs

## Escalation Conditions
- if the closeout requires broader crawler runtime tooling or feature expansion rather than validation and documentation, stop and keep the slice narrow
