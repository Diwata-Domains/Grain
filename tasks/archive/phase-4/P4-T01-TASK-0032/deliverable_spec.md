# Deliverable Spec: TASK-0032

## Required Deliverables

- [ ] `src/ai_build_toolkit/domain/context.py` exists with `PacketFile`, `PacketSourceSet`, `PACKET_FILENAMES`, `discover_packet_files`
- [ ] `src/ai_build_toolkit/services/context_service.py` exists with `discover_packet_sources`
- [ ] `find_packet_dir` is a public function in `domain/packets.py`
- [ ] `task_service.py` uses the public `find_packet_dir`
- [ ] `tests/test_context_sources.py` with ≥7 tests, all passing
- [ ] No regressions in existing test suite

## Acceptance Criteria

- `discover_packet_sources(root, "TASK-0001")` returns `(ok=True, PacketSourceSet)` for an existing packet
- `discover_packet_sources(root, "TASK-9999")` returns `(ok=False, None)` with error message
- `PacketSourceSet.present_files()` returns only files where `present=True`
- `PacketSourceSet.required_files()` returns exactly the 4 required packet files
- All 4 required files are reported as `present=True` for a newly created packet
- `results.md` and `handoff.md` are reported as `present=False` for a packet created without them
