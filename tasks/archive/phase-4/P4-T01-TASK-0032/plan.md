# Plan: TASK-0032

## Steps

1. Add `find_packet_dir(tasks_root, task_id)` as a public function in `domain/packets.py`.
   Update `task_service.py` to use it (remove private `_find_packet_dir`).

2. Create `src/ai_build_toolkit/domain/context.py`:
   - `PACKET_FILENAMES` tuple (6 filenames)
   - `PacketFile` dataclass: `name`, `path`, `present`
   - `PacketSourceSet` dataclass: `task_id`, `packet_dir`, `files`; helpers: `present_files()`, `required_files()`
   - `discover_packet_files(packet_dir) -> list[PacketFile]`

3. Create `src/ai_build_toolkit/services/context_service.py`:
   - `discover_packet_sources(root, task_id) -> tuple[CommandResult, PacketSourceSet | None]`

4. Create `tests/test_context_sources.py` with ~7 tests covering:
   - present/absent file reporting
   - PacketSourceSet helpers
   - not-found packet error
   - integration with packet_repo fixture

5. Run tests to confirm all passing.
