# Task: MCP surface expansion (full drive loop + recipe)

## Metadata
- **ID:** P35-T06
- **Status:** draft
- **Phase:** Phase 35 — Grain-as-Engine Headless Contract
- **Backlog:** P35-T06
- **Packet Path:** tasks/P35-T06/
- **Dependencies:** P35-T01, P35-T02, P35-T03, P35-T05
- **Primary Adapter:** code
- **Secondary Adapters:** none
- **Engine-contract:** MCP surface area of `engine_contract_spec.md` §5 — stdio-only,
  no-network, file-backed (no HTTP auth, no daemon, locked `toolkit_contract.md` §2/§4.3).
  Every `tools/call` result is the §3 `grain.engine/v1` envelope; CLI stays canonical (§2.5)
  and each tool delegates to the same service function the CLI command uses.

## Objective
Expand and re-frame `services/mcp_service.py` so the MCP surface speaks the one
`grain.engine/v1` engine envelope (§3) and the one typed error model (§4), and exposes the
full familiar drive loop + recipe verbs (§5.4). Replace `_tool_success`/`_tool_error` with
the envelope helpers `_ok`/`_gate`/`_err` (§5.1); retype the 5 existing tools' failure paths
to §4 typed `ForgeError`s; report the live `serverInfo.version` and advertise the contract in
`_meta` (§5.2); add the `write` flag + `capability` reference to the `McpTool` dataclass
(§5.3); register the read+write tool catalog (§5.4) with each tool delegating to its canonical
service function; and **derive** `tools/list` from `CAPABILITIES` (filter `surfaces ∋ "mcp"`,
§5.3) — the join is deterministic only because **T03 pins each capability's `surfaces`** (every
MCP-surfaced capability carries `surfaces ∋ "mcp"`), so this packet **consumes** the T03 seed and
does not re-derive surfaces locally. Recipe auto-mode and `workflow_loop` are NOT exposed
(deferred, §8). **The `version_check` MCP tool is NOT registered here** — it is owned by **T10**
(which owns `grain version` and depends on T01,T02,T03,T06). T06 provides the `_ok`/`_gate`/`_err`
helpers and the extended `McpTool` dataclass that T10 reuses to add the `version_check` tool
against the T03-seeded `version_check` capability (no re-add).

## Why This Task Exists
Today MCP exposes only 5 tools (4 read + `create_task`), with a stale hardcoded
`serverInfo.version` `"0.3.0-dev"` and an untyped `{"errors":[...]}` blob (spec §1). A familiar
cannot (a) know which schema/version it received, (b) distinguish error classes the same way it
does over CLI, (c) discover what is drivable from MCP alone, or (d) complete the SDLC/recipe
loop without dropping to interactive prompts. This packet makes the MCP surface a versioned,
typed, discoverable, non-interactive view of the same engine the CLI drives (§5.1, §5.3,
linchpin role §1), realizing the locked doc's forward-declared `workflow_drive` capability as
the drive-loop + recipe tools (§5.4). It is the MCP layer of the Phase 35 contract; it consumes
the foundation landed by T01 (envelope + errors), T02 (version), T03 (capabilities) and the
recipe-error mapping landed by T05.

## Scope
- **EDIT `src/grain/services/mcp_service.py`:**
  - **Envelope helpers (§5.1).** Replace `_tool_success`/`_tool_error` with
    `_ok(tool, kind, data)` (`status="ok"`, `isError` False), `_gate(tool, kind, data, gate)`
    (`status="gate"`, `isError` False), `_err(tool, exc: ForgeError)` (`status="error"`,
    error from `exc`, `isError` True). Each builds the §3 `EngineEnvelope` (imported from
    `domain/envelope.py`, T01), serializes it via `envelope_to_dict`, places it under
    `structuredContent`, mirrors it as pretty JSON in `content[0].text`, and sets
    `isError = (status == "error")`. The tool name rides the envelope `command` field; `kind`
    is the discriminator. The existing 5 tools' payloads move from `structuredContent` root to
    `data`, and `ok` becomes `status` (the one accepted MCP back-compat break, §5.1).
  - **Retype the 5 existing tools' failures to §4 typed errors (§4.3 MCP bullet).** Replace
    `_tool_error({"errors":[...]})` paths: packet/artifact not found → `MissingPathError`
    (`grain.missing_path`); empty/`!str`/`!int` args → `UsageError` (`grain.usage`); unknown
    tool → `UsageError`. Route every failure through `_err(tool, exc)`.
  - **Live version + contract advertisement (§5.2).** Replace the hardcoded
    `MCP_SERVER_INFO`/`"0.3.0-dev"` with `serverInfo.version = get_version()` (from
    `grain/version.py`, T02). `initialize` advertises `_meta = {"grainContractVersion": "1.1",
    "engineApiVersion": "grain.engine/v1"}` and the file-backed `instructions` string (§5.2).
  - **`McpTool` dataclass (§5.3).** Add `write: bool = False` and `capability: str = ""`
    (reference into `CAPABILITIES`). Drive-loop + recipe tools carry
    `capability="workflow_drive"`.
  - **Tool catalog (§5.4).** Register the read tools (`workflow_explain`, `task_list`,
    `task_show`, `review_check`, `recipe_list`, `recipe_show`, `recipe_status`,
    `capabilities_list`) alongside the retained `workflow_next`, `prompt_show`,
    `review_summary`, `office_review_show`; and the write tools (`task_create`, `task_status`,
    `task_close`, `workflow_run`, `workflow_reconcile`, `gate_decide`, `recipe_run` [operator],
    `recipe_next`, `recipe_resume`, `recipe_gate`). `create_task` becomes a **hidden alias** of
    `task_create` for one minor cycle (§5.4). Each tool delegates to the **same service
    function** the CLI verb uses (CLI canonical, §2.5) — no business logic added here.
  - **`workflow_run` is exposed (OD-4 resolved, §5.5/§9).** `run_workflow_step` does not shell
    out, so it is a deterministic single call; expose it. `workflow loop` / recipe auto-mode
    stay CLI-only (NOT exposed).
  - **`gate_decide` / recipe verbs.** `decision` enums validate against
    `VALID_DECISIONS = frozenset({"approve","reject"})`; a bad value → `UsageError` →
    `grain.usage` (§5.4). MCP write tools act immediately and do NOT emit `status: gate`
    (§5.8). **`gate_decide` is fully pinned (no unnamed delegate, CLI-canonical §2.5):** it
    emits `kind = "RecipeRun"` — a member already registered in `VALID_ENGINE_KINDS` via the
    §3.2 `recipe ... gate` row (T01 owns the frozenset; this packet only uses a registered
    member, never an ad-hoc kind that would trip `__post_init__`) — and delegates to the
    recipe-engine gate-decision service function in `recipe_service` (the **same** fn the
    canonical CLI verb `grain recipe gate` calls). Recipe-engine failures map through
    `engine_error_to_forge` (T05) → `_err`.
  - **`tools/list` derived from `CAPABILITIES` (§5.3).** Build the listing by filtering
    `CAPABILITIES` to `surfaces ∋ "mcp"` and joining each capability id to its `McpTool`
    schema — not a hand-maintained second source.
- **EDIT `src/grain/cli/mcp.py` only if needed** to surface the live version / catalog wiring.
- **Tests** in `tests/` covering the criteria below.

## Constraints
- **MVP only (§8).** Do NOT expose recipe **auto mode** or `workflow_loop` over MCP; do NOT
  expose a `suggest_accept` write tool (the §5.8 MCP↔CLI boundary stays — a pure-MCP familiar
  drops to CLI for `suggest accept`). Do NOT add HTTP/bearer auth or any daemon/network
  transport (stdio only, §5.6, OD-3). The HTTP wrapper pass-through fix lives in a sibling
  packet, not here.
- **CLI is canonical (§2.5).** No business logic in `mcp_service.py`; every tool delegates to
  the existing service function the CLI command calls. Recipe verbs reuse existing dicts
  verbatim under `data`: `NextResult.to_dict()` (recipe verbs), `run.json`
  `grain.recipe-run/v1` (`recipe_status`), `_definition_to_dict` `grain.recipe/v2`
  (`recipe_show`) (§5.4).
- **One frame, one error (§2.2).** Import `EngineEnvelope`/`ErrorEnvelope`/`envelope_to_dict`
  from `domain/envelope.py` (T01); import `get_version` from `grain/version.py` (T02); import
  `CAPABILITIES` from `domain/capabilities.py` (T03). Do NOT redefine a frame, error shape,
  version resolver, or capability registry in `mcp_service.py`.
- **JSON-RPC transport errors are untouched (§4.3).** `-32700/-32600/-32601/-32602`
  (malformed request / unknown method / bad params) stay protocol-level; only tool-execution
  errors get the §4 envelope.
- Grain idioms: frozen dataclass + `__post_init__` + `VALID_*` frozensets; `ForgeError`
  taxonomy; any new `.py` file carries the SPDX Apache-2.0 header
  (`# SPDX-License-Identifier: Apache-2.0`).

## Deliverable
- Edited `src/grain/services/mcp_service.py` (envelope helpers, retyped errors, live version +
  `_meta`, extended `McpTool`, full read+write catalog, `create_task` hidden alias, `tools/list`
  derived from `CAPABILITIES`) per `deliverable_spec.md`.
- Edited `src/grain/cli/mcp.py` if required by the version/catalog wiring.
- Tests covering the criteria below.

## Acceptance Criteria
- A `tools/call` for **every** tool in the catalog returns a result whose `structuredContent`
  is a `grain.engine/v1` envelope: it has top-level keys `apiVersion == "grain.engine/v1"`,
  `kind`, `status`, `grain_version`, `data`, `gate`, `error`; `content[0].text` is the same
  object pretty-printed; and `isError == (status == "error")`. (Asserted for at least one read,
  one write, and one recipe tool.)
- The 5 previously-existing tools (`workflow_next`, `prompt_show`, `review_summary`,
  `office_review_show`, `create_task`/`task_create`) carry their former payload under `data`
  (not at `structuredContent` root) and on failure return `status: "error"` with
  `error.code ∈ {grain.missing_path, grain.usage}` matching the §4 table — asserted: a missing
  packet → `grain.missing_path`, a bad/empty arg → `grain.usage`.
- `initialize` returns `serverInfo.version == get_version()` (NOT `"0.3.0-dev"` and not any
  hardcoded literal) and `_meta == {"grainContractVersion": "1.1", "engineApiVersion":
  "grain.engine/v1"}`; a test greps `mcp_service.py` to assert no hardcoded version string
  remains.
- `tools/list` is derived from `CAPABILITIES` and consumes the **T03-pinned `surfaces`**: the set
  of returned tool names equals the set of `McpTool` names **registered in this packet** whose
  referenced capability has `surfaces ∋ "mcp"` (deterministic because T03 pins surfaces; this
  packet does not recompute them). `workflow_loop`, recipe auto-mode, and `suggest_accept` are
  absent; the `version_check` MCP tool is **absent in this packet** (owned by T10 — its
  T03-seeded `version_check` capability may carry `surfaces ∋ "mcp"`, but no matching `McpTool` is
  registered here until T10 lands); `create_task` is present but flagged hidden while
  `task_create` is listed.
- `gate_decide` / recipe gate tools reject a `decision` outside
  `VALID_DECISIONS = {"approve","reject"}` with `status: "error"`, `error.code == "grain.usage"`
  — and a valid write tool call returns `status: "ok"` (never `status: "gate"`, per §5.8). A
  valid `gate_decide` returns `kind == "RecipeRun"` (a registered `VALID_ENGINE_KINDS` member,
  §3.2) and routes through the `recipe_service` recipe-gate fn (CLI-canonical `grain recipe gate`).
- The `McpTool` dataclass exposes `write: bool` and `capability: str`; every write-catalog tool
  has `write=True` and every drive-loop/recipe tool has `capability == "workflow_drive"`
  (asserted by iterating `TOOLS`).
- `uv run pytest tests/test_mcp_service.py` (or the touched MCP test module) passes with the new
  cases and the full suite shows no regressions.

## Dependencies
- **P35-T01** — `domain/envelope.py` (`EngineEnvelope`, `ErrorEnvelope`, `envelope_to_dict`,
  tri-state `status`, `VALID_ENGINE_KINDS`) + the §4 typed `ForgeError` codes. Required by the
  `_ok`/`_gate`/`_err` helpers and the retyped errors.
- **P35-T02** — `grain/version.py::get_version()`. Required for live `serverInfo.version`.
- **P35-T03** — `domain/capabilities.py::CAPABILITIES` + the `Capability` dataclass. Required
  for `McpTool.capability` references and the derived `tools/list`.
- **P35-T05** — `recipe_service.engine_error_to_forge` (recipe engine-error → `ForgeError`).
  Required so the MCP recipe tools map failures to the same §4 taxonomy as `recipe.py::_drive`.

## Relevant Files
- `src/grain/services/mcp_service.py` (edit) — the MCP surface: helpers, catalog, dispatch,
  `tools/list`, `initialize`.
- `src/grain/cli/mcp.py` (edit if needed) — CLI entry that runs the stdio server.
- `src/grain/domain/envelope.py` (dependency, T01) — `EngineEnvelope`/`ErrorEnvelope` imported.
- `src/grain/version.py` (dependency, T02) — `get_version()` imported.
- `src/grain/domain/capabilities.py` (dependency, T03) — `CAPABILITIES` imported.
- `src/grain/services/recipe_service.py` (dependency, T05) — `engine_error_to_forge`,
  `NextResult.to_dict()`, `_definition_to_dict` reused.
- `tests/test_mcp_service.py` (edit/new) — MCP envelope/error/catalog tests.
- `docs/working/engine_contract_spec.md` §4.3, §5, §8, §9 (contract).

## Escalation Conditions
- If `run_workflow_step` is found to shell out to an external agent (contradicting OD-4's code
  check, §9), STOP and defer `workflow_run` from the catalog rather than exposing a
  non-deterministic spawn over MCP — log a change proposal.
- If a CLI verb in the catalog has no reusable service function (logic only in the `cli/*.py`
  command body), log a blocker — extracting the service is a prerequisite, not in-scope
  business logic for `mcp_service.py`.
- If T01/T02/T03/T05 have not landed the imported symbols, record a dependency blocker rather
  than re-defining envelope/version/registry/error-map locally.

## Model Recommendation
Opus-class. The envelope re-frame, the retyped error mapping, and the `tools/list`-derived-from-
`CAPABILITIES` wiring have cross-area invariants (frame parity with the CLI, the one back-compat
break, the §5.8 no-gate asymmetry) worth getting right once. Mechanical catalog entries can be
filled by a Sonnet-class model once the helpers and one read/write/recipe exemplar are in place.
