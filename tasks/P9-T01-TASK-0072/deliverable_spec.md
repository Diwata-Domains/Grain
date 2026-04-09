# Deliverable Spec: TASK-0072

## Required Deliverables

- [ ] `src/forge/domain/orchestrator.py` exists with `PacketCandidate`, `CrossDomainDependency`, `OrchestratorPlan`
- [ ] `OrchestratorPlan` has all 9 required fields from §18.2: `plan_id`, `scope_summary`, `produced_by`, `status`, `active_adapters`, `packet_candidates`, `dependency_links`, `cross_domain_flags`, `split_recommendations`
- [ ] `PacketCandidate` has all 5 fields from §18.2: `candidate_id`, `title`, `scope_summary`, `primary_adapter`, `depends_on`
- [ ] `OrchestratorPlan.status` raises `ValueError` for values outside the allowed set
- [ ] New types exported from `src/forge/domain/__init__.py`
- [ ] `tests/test_orchestrator_domain.py` exists with passing tests
- [ ] Full test suite passes with no regressions

## Explicitly Out of Scope
- No service logic
- No CLI commands
- No canonical doc changes
- No adapter capability protocol (that is P9-T02)
