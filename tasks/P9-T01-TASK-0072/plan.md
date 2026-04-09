# Plan: TASK-0072

## Steps

1. Create `src/forge/domain/orchestrator.py`
   - Define `PacketCandidate` dataclass (candidate_id, title, scope_summary, primary_adapter, depends_on)
   - Define `CrossDomainDependency` dataclass (from_candidate, to_candidate, adapter_domains)
   - Define `OrchestratorPlan` dataclass with all §18.2 fields + status validation

2. Update `src/forge/domain/__init__.py`
   - Export `PacketCandidate`, `CrossDomainDependency`, `OrchestratorPlan`

3. Create `tests/test_orchestrator_domain.py`
   - Test OrchestratorPlan construction with minimal fields
   - Test PacketCandidate construction
   - Test CrossDomainDependency construction
   - Test status validation rejects invalid values
   - Test all list fields default to empty list

4. Run test suite to confirm no regressions
