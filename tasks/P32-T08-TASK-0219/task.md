# Task: Pulse telemetry foundation — opt-in event emission contract

## Metadata
- **ID:** TASK-0219
- **Status:** ready
- **Phase:** Phase 32 — v0.4.0 Proactive Assistance
- **Backlog:** P32-T08
- **Packet Path:** tasks/P32-T08-TASK-0219/
- **Dependencies:** none
- **Primary Adapter:** code
- **Secondary Adapters:** none

## Objective
Lay the Grain-side, opt-in event emission contract for Pulse (the planned Diwata-wide telemetry layer). Grain only emits typed, versioned events at key workflow moments; transport and aggregation are Pulse's responsibility. Default off.

## Why This Task Exists
Pulse will aggregate workflow telemetry across the Diwata stack. Grain's side must be a thin, stable, versioned emission contract so it can evolve without breaking consumers — and emit nothing unless explicitly enabled.

## Scope / Implementation Steps
1. Create `src/grain/domain/telemetry.py`: `TelemetryEvent` dataclass (`event_type`, `version`, `timestamp`, `payload`).
2. Create `src/grain/services/telemetry_service.py`: `emit(root, event)` — fire-and-forget, NEVER raises; on unreachable/disabled endpoint, append to `.grain/telemetry_queue.jsonl`.
3. Opt-in gate: enabled only when `telemetry.enabled: true` in `docs_manifest.yaml` OR `GRAIN_TELEMETRY_ENDPOINT` is set; default off (no events).
4. Instrument key moments: phase close, task close, `grain suggest accept`, and `grain workflow next` stop reason — each emits a typed, versioned event when enabled.

## Acceptance Criteria
- With telemetry disabled (default), no events are emitted and no queue file is written.
- When enabled, the four instrumented moments emit typed, versioned `TelemetryEvent`s; unreachable endpoint falls back to `.grain/telemetry_queue.jsonl`.
- `emit` never raises and never blocks the workflow.
- Event schema is versioned.
- No regression: full suite green.

## Tests
- `tests/test_telemetry_service.py` — off by default, emits when enabled, falls back to queue, never raises.
- Instrumentation tests — phase close / task close / suggest accept / stop reason emit when enabled.

## Constraints
- Default off; opt-in only.
- Never raise from emission; never leak data when disabled.
- Versioned events — safe to evolve.

## Escalation Conditions
- Instrumentation would change workflow control flow or timing — keep emission strictly side-band.
