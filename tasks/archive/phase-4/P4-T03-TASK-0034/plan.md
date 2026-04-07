# Plan: TASK-0034

## Steps

1. Add a pure domain helper in `src/forge/domain/context.py` that filters `working` layer records by `read_when` intersection only when opt-in is enabled.
2. Add a service wrapper in `src/forge/services/context_service.py` that loads the manifest, verifies packet existence, and returns selected working docs or a graceful failure.
3. Add tests that prove:
   - default exclusion
   - opt-in inclusion
   - tag-based filtering
   - service-layer failure behavior for missing manifest or missing packet
4. Run the relevant test subset and then the full test suite if the subset passes.
