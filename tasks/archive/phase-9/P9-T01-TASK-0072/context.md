# Context: TASK-0072

## Canonical Sources
- `docs/canonical/data_contracts.md §18` — OrchestratorPlan schema and validation minimums
- `docs/canonical/architecture.md §4.14` — Orchestration Service responsibilities and output types

## Working Sources
- `docs/working/backlog.md` — P9-T01 description and field list

## Existing Domain Files Read
- `src/forge/domain/workflow.py` — pattern for dataclass structure in this module
- `src/forge/domain/adapters.py` — pattern for field defaults and typing style
- `src/forge/domain/packets.py` — pattern for status validation approach

## Key Constraints From Context
- All OrchestratorPlan outputs are proposals; no mutation logic
- status must be one of: draft, under_review, accepted, rejected, deferred
- PacketCandidate requires: candidate_id, title, scope_summary, primary_adapter, depends_on
- dependency_links holds CrossDomainDependency entries (not raw strings)
