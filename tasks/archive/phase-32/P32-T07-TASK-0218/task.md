# Task: Workflow metrics — grain metrics command

## Metadata
- **ID:** TASK-0218
- **Status:** done
- **Phase:** Phase 32 — v0.4.0 Proactive Assistance
- **Backlog:** P32-T07
- **Packet Path:** tasks/P32-T07-TASK-0218/
- **Dependencies:** none
- **Primary Adapter:** code
- **Secondary Adapters:** none

## Objective
Implement `grain metrics` for per-phase velocity and cost tracking, computed from the task/doc archives and workflow-state history. Read-only, cached, JSON-exportable.

## Why This Task Exists
There is no current way to see how the workflow actually performs over time (phase duration, task counts, which gates fire most). Metrics lay the measurement base the Pulse telemetry foundation (P32-T08) and future tuning depend on.

## Scope / Implementation Steps
1. Create `src/grain/services/metrics_service.py`: compute per-phase duration (open→close from metadata), task count per phase, closure rate, and stop-reason frequency (from `.grain` workflow-state history).
2. Create `src/grain/cli/metrics.py`: `grain metrics` (summary), `grain metrics --phase N` (single-phase detail), `grain metrics export` (full JSON history); `--format json` on all. Register in `cli/__init__.py`.
3. Cache to `.grain/metrics_cache.json` with a 1-hour TTL; recompute on miss.

## Acceptance Criteria
- `grain metrics` shows per-phase duration, task count, and closure rate.
- `grain metrics --phase N` shows single-phase detail; `grain metrics export` dumps full history JSON.
- Stop-reason frequency is reported from workflow-state history.
- Cache respects a 1-hour TTL; `--format json` stable on all subcommands.
- No regression: full suite green.

## Tests
- `tests/test_metrics_service.py` — duration/count/closure/stop-reason computation, cache TTL.
- `tests/test_metrics_cmd.py` — summary, `--phase`, `export`, JSON.

## Constraints
- Read-only; never mutates archives.
- Degrade gracefully when history/metadata is sparse (e.g. pre-v0.4.0 phases).

## Escalation Conditions
- Required metadata fields are absent across most phases — report partial metrics with a clear coverage note rather than failing.
