# Plan: TASK-0033

## Steps

1. Add `select_canonical_docs(registry, context_tags)` to `domain/context.py`.
   - Accepts a `DocumentRegistry` and a `set[str]` of context tags.
   - Returns canonical-layer records whose `read_when` intersects with context_tags.
   - Empty tags → empty list.

2. Add `select_canonical_docs_for_packet(root, task_id, context_tags)` to `services/context_service.py`.
   - Load manifest via `load_manifest(root)`.
   - Build registry via `build_registry(manifest)`.
   - Verify packet exists (task_id lookup via find_packet_dir).
   - Call `select_canonical_docs(registry, context_tags)`.
   - Return `(CommandResult, list[DocumentRecord])`.

3. Write `tests/test_canonical_doc_selection.py` with ~7 tests.

4. Run tests; confirm 0 regressions.
