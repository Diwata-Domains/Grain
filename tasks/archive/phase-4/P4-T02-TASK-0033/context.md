# Context: TASK-0033

## Source Documents
- `docs/canonical/architecture.md` §4.5 (Context Selection System — must not load full repo)
- `docs/runtime/docs_manifest.yaml` (canonical entries with read_when metadata)
- `src/ai_build_toolkit/domain/documents.py` (DocumentRecord, DocumentRegistry, build_registry)
- `src/ai_build_toolkit/domain/context.py` (PacketSourceSet from P4-T01)
- `src/ai_build_toolkit/adapters/manifest.py` (load_manifest)
- `src/ai_build_toolkit/services/context_service.py` (existing discover_packet_sources)
- `tests/fixtures/valid_manifest.yaml` (test fixture)
