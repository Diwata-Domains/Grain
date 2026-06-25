# Results — TASK-0219

## Summary

Shipped the Pulse telemetry foundation: an opt-in, fire-and-forget, typed and
versioned event-emission contract for Grain. Default off — nothing is emitted
and no queue file is written unless telemetry is explicitly enabled
(`telemetry.enabled: true` in docs_manifest.yaml) or `GRAIN_TELEMETRY_ENDPOINT`
is set. When enabled, events POST to the configured Pulse endpoint; on no/
unreachable endpoint they append to `.grain/telemetry_queue.jsonl` for later
drain. Four moments are instrumented strictly side-band (never change control
flow, return values, or raise): phase close, task close, `grain suggest accept`,
and `grain workflow next` stop reason.

## Deliverables

- `TelemetryEvent` domain dataclass (`event_type`, `version`, `timestamp`,
  `payload`) plus `EVENT_*` type constants and `TELEMETRY_EVENT_VERSION`.
- `telemetry_service.emit(root, event)` — never raises; opt-in gate via
  `is_enabled(root)`; endpoint POST (stdlib urllib) with queue fallback; typed
  `make_*_event` builders for the four moments.
- `TelemetryConfig` + `load_telemetry_config(root)` manifest loader (never
  raises, default `enabled: false`).
- `telemetry:` block seeded into both docs_manifest.yaml files.
- Instrumentation of the four moments.

## Files Changed

- src/grain/domain/telemetry.py (new)
- src/grain/services/telemetry_service.py (new)
- src/grain/adapters/manifest.py (TelemetryConfig + load_telemetry_config)
- src/grain/services/phase_close_service.py (emit on successful close)
- src/grain/services/task_service.py (emit on close_packet + quick_close_packet)
- src/grain/services/suggest_service.py (emit on successful accept)
- src/grain/cli/workflow.py (emit stop reason on `workflow next`)
- docs/runtime/docs_manifest.yaml + src/grain/data/runtime/docs_manifest.yaml
  (telemetry block, default enabled: false)
- tests/test_telemetry_service.py (new)
- tests/test_telemetry_instrumentation.py (new)

## Test Results

`uv run --with pytest python -m pytest -q` → 1365 passed, 1 xfailed.
New telemetry tests: 19 passed. Ruff clean on all new files.

## Closure Decision

- **Decision:** closed
- **Reason:** Acceptance criteria met; full suite green.

### Closure Blockers

- None
