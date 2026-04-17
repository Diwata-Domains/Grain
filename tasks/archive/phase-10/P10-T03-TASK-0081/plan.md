# Plan: TASK-0081

## Approach

Integrate Layer 3 graph outputs into `context_service` adapter-source selection. Build graph from packet-local plus adapter-candidate paths, then include only candidates reachable by graph traversal from packet files. Persist trace path metadata per inclusion.

---

## Step 1 — Replace Adapter Source Selection with Graph Traversal

Update context service helper flow to:
- build adapter candidate set from profile patterns
- build graph for packet + candidate paths
- select candidate files only when graph-connected
- emit per-file trace paths for included sources

---

## Step 2 — Preserve Adapter Context Output Contract

Keep existing adapter context fields and add traceability data while preserving deterministic ordering and source limits.

---

## Step 3 — Add/Update Tests

Update context-build tests to validate graph-assisted traceability and no-hidden-inclusion behavior for adapter-selected files.

---

## Verification

- `.venv/bin/pytest -q tests/test_context_build.py tests/test_adapter_context.py tests/test_context_build_cmd.py tests/test_graph_service.py`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0081`
- `.venv/bin/pytest -q`
