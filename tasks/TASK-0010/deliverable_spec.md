# Deliverable Spec: TASK-0010

## Definition of Done

This task is complete when all of the following are true:

1. `PyYAML` is a declared dependency in `pyproject.toml`
2. `src/ai_build_toolkit/adapters/manifest.py` exists with `load_manifest(root: Path) -> dict`
3. `load_manifest()` reads from `docs/runtime/docs_manifest.yaml` relative to `root`
4. `load_manifest()` raises `MissingPathError` when the file is absent
5. `load_manifest()` raises `ConfigError` when the file contains invalid YAML
6. Loader lives in `adapters/`, not in `services/` or `domain/`
7. Tests cover valid load, missing file, and malformed YAML — all passing

## Out of Scope
- Schema validation of manifest contents (TASK-0011)
- Document registry model (TASK-0012)
- Any CLI wiring (TASK-0015, TASK-0016)
