# Results — TASK-0191

## Status
done — 2026-06-11

## Deliverables
- `docs/canonical/toolkit_contract.md` — inter-tool contract spec
- `docs/canonical/workspace_model.md` — multi-repo and workspace context model spec

## Key Decisions

**Transport model:** File artifact drop + structured stdout. No network, no sockets, no daemons. Sibling tools write JSON artifacts to agreed paths, then call a Grain ingestion command.

**Contract schema:** `toolkit_contract.yaml` — bilateral declaration with `requires.capabilities` and `provides.events`. Grain publishes its own capability list at `docs/runtime/grain_capabilities.yaml`.

**Workspace resolution:** Nearest-ancestor walk from CWD, overridable by `--workspace` flag or `GRAIN_WORKSPACE` env var. Backwards-compatible — single-repo setups unaffected.

**Linking:** `grain context link <path>` registers external workspaces in `docs/runtime/workspace_links.yaml`. No file copying or symlinking. Linked docs accessible as `linked:<name>/` in context sources.

**Cross-workspace deps:** Declared in task.md metadata as `External-Dependencies:` list. `grain workflow guard --check-external` reads sibling workspace state; advisory only by default (not a hard gate unless opted into).

**Assay reference implementation:** Fully spec'd in `toolkit_contract.md` §5 — the v0.3.0 `grain verify` bridge is the canonical first instance of this contract.

## Files Changed
- `docs/canonical/toolkit_contract.md` — created
- `docs/canonical/workspace_model.md` — created
- `tasks/P30-T02-TASK-0191/task.md` — status set to done
