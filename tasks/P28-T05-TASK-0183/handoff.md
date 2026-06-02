# Handoff: TASK-0183

## What Changed
- Documented the live `grain verify submit/status/ingest` Assay loop in the README
- Added packet-local verification rules to runtime guidance
- Replaced stale deferred Sentinel wording in the canonical CLI spec
- Added verification-close guidance to the shipped close prompt

## Verification
- `102 passed in 11.96s` across focused verify bridge, workflow gate, close-command, and release-surface tests

## Operator Notes
- Phase 28 implementation work is complete; the next strict workflow step is phase review/close.
- The docs intentionally describe only the current packet-local Assay bridge, not remote transport or polling.
