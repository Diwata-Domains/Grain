# Deliverable Spec: P2-T08-TASK-0018

## Definition of Done

1. `generate_index(root, dry_run)` added to `services/docs_service.py`
2. `abt docs index` exits 0 and writes `docs/runtime/docs_index.md`
3. Written file contains all manifest-registered doc IDs grouped by layer
4. `abt docs index --dry-run` exits 0 and does NOT write any files
5. Missing manifest returns non-zero with clear error
6. `--format json` produces valid JSON
7. CLI stays thin — formatting logic in service
8. All tests passing, no regressions

## Out of Scope
- Validating existence or authority of listed docs (that is `docs validate`)
- Preserving human-authored sections from the current `docs_index.md`
- Incremental/merge updates to the index
