# Context: TASK-0032

## Source Documents
- `docs/canonical/architecture.md` §4.5 (Context Selection System), §6.3 (domain layer)
- `docs/canonical/architecture.md` §7.3 (Context Bundle minimum fields)
- `docs/runtime/docs_manifest.yaml` tasks.packet_files (canonical file list)
- `src/ai_build_toolkit/domain/packets.py` (existing packet domain, _find_packet_dir pattern)
- `src/ai_build_toolkit/services/task_service.py` (_ALL_PACKET_FILES constant, _find_packet_dir)
- `src/ai_build_toolkit/cli/output.py` (CommandResult)
- `tests/conftest.py` (packet_repo fixture)
