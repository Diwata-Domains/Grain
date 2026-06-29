# Deliverable Spec: P35-T06 — MCP surface expansion (full drive loop + recipe)

## Required Output

### Modified Files
- `src/grain/services/mcp_service.py` — envelope helpers, retyped errors, live version + `_meta`,
  extended `McpTool`, full read+write catalog, `create_task` hidden alias, derived `tools/list`.
- `src/grain/cli/mcp.py` — only if the live-version / catalog wiring requires it (do not add
  business logic).
- `tests/test_mcp_service.py` — new/updated cases (see below).

### New Files
- none expected (this is an EDIT packet). Any new `.py` test helper carries the SPDX header:
  ```
  # SPDX-License-Identifier: Apache-2.0
  ```

### Imported from dependencies (do NOT redefine)
- `from grain.domain.envelope import EngineEnvelope, ErrorEnvelope, envelope_to_dict, to_envelope` (T01)
- `from grain.version import get_version` (T02)
- `from grain.domain.capabilities import CAPABILITIES` (T03)
- `from grain.services.recipe_service import engine_error_to_forge` (T05)
- `from grain.domain.errors import MissingPathError, UsageError, ValidationError, ForgeError`

## Result envelope on the MCP surface (§5.1)

Every `tools/call` result is shaped:

```jsonc
{
  "content": [{ "type": "text", "text": "<pretty-printed envelope JSON>" }],
  "structuredContent": {
    "apiVersion": "grain.engine/v1",
    "kind": "<discriminator>",          // ∈ VALID_ENGINE_KINDS (T01)
    "status": "ok",                      // "ok" | "gate" | "error"
    "grain_version": "<get_version()>",  // NEVER hardcoded (§5.2)
    "command": "<tool name>",            // tool name rides here (§5.1)
    "data": { /* existing per-command dict, verbatim */ },
    "gate": null,
    "error": null,
    "warnings": []
  },
  "isError": false                       // == (status == "error")
}
```

MCP write tools never emit `status: "gate"` (§5.8) — they act immediately; `_gate` exists only
for parity/future use and is not invoked by any Phase-35 write tool.

## Helpers (replace `_tool_success`/`_tool_error`)

```python
def _ok(tool: str, kind: str, data: dict) -> dict:
    """Build a status='ok' grain.engine/v1 result. isError False."""

def _gate(tool: str, kind: str, data: dict, gate: dict) -> dict:
    """Build a status='gate' result (defined for parity; unused by Phase-35 MCP write tools)."""

def _err(tool: str, exc: ForgeError) -> dict:
    """Build a status='error' result; error block from to_envelope(exc); isError True."""
```

Each constructs an `EngineEnvelope`, serializes with `envelope_to_dict`, places it under
`structuredContent`, mirrors `json.dumps(env, indent=2, sort_keys=True)` in `content[0].text`,
and sets `isError = (env["status"] == "error")`.

## `McpTool` dataclass (§5.3)

```python
@dataclass(frozen=True)
class McpTool:
    name: str
    title: str
    description: str
    input_schema: dict
    write: bool = False          # read vs write (familiars gate on this)
    capability: str = ""         # reference into CAPABILITIES (carries since/stability/drive)
```

## Tool catalog (§5.4) — `TOOLS: tuple[McpTool, ...]`

Naming `noun_verb`, 1:1 with the CLI verb; each delegates to the same service function the CLI
command uses. `kind` column is the envelope discriminator each tool emits on success.

### Read tools (`write=False`)
| name | kind | delegates to (service) | data payload |
|---|---|---|---|
| `workflow_next` *(exists)* | `WorkflowState` | `workflow_service.evaluate_workflow_state` | evaluation dict |
| `workflow_explain` | `WorkflowDiagnostic` | workflow explain service fn | evaluation/diagnostic dict |
| `prompt_show` *(exists)* | (existing kind) | `prompt_service.show_prompt` | prompt dict |
| `task_list` | (task kind) | task list service fn | task list dict |
| `task_show` | (task kind) | task show service fn | task dict |
| `review_summary` *(exists)* | (review kind) | `review_service.build_packet_review_summary` | summary dict |
| `review_check` | (review kind) | review check service fn | check dict |
| `office_review_show` *(exists)* | (review kind) | office review reader | office_review dict |
| `recipe_list` | `RecipeList` | recipe list service fn | `{recipes:[...]}` |
| `recipe_show` | `RecipeDefinition` | `_definition_to_dict` (`grain.recipe/v2`) | definition dict |
| `recipe_status` | `RecipeRun` | run.json reader (`grain.recipe-run/v1`) | run dict |
| `capabilities_list` | `CapabilityList` | live `CAPABILITIES` serialization (§5.7) | registry dict |

> **`version_check` MCP tool is NOT registered in this packet.** It is owned by **T10** (which
> owns the `grain version` command and depends on T01,T02,T03,T06). T10 reuses this packet's
> `_ok`/`_err` helpers and the extended `McpTool` dataclass, and binds the tool to the
> **T03-seeded** `version_check` capability (no re-add). Do not add a `version_check` `McpTool`
> here.

### Write tools (`write=True`, `capability="workflow_drive"` for drive-loop/recipe)
| name | kind | delegates to | notes |
|---|---|---|---|
| `task_create` | (task kind) | `task_service.create_packet_directory` | `create_task` = hidden alias |
| `task_status` | (task kind) | task status service fn | single-call mutation |
| `task_close` | (task kind) | task close service fn | single-call mutation |
| `workflow_run` | `WorkflowStep` | `workflow_service.run_workflow_step` | exposed — OD-4 non-spawning (§5.5/§9) |
| `workflow_reconcile` | `ReconcileReport` | reconcile service fn | |
| `gate_decide` | `RecipeRun` (registered §3.2) | `recipe_service` recipe-gate fn — CLI-canonical `grain recipe gate` (§2.5) | `decision ∈ VALID_DECISIONS`; no unnamed delegate |
| `recipe_run` | `RecipeRun` | recipe run (operator mode) | `NextResult.to_dict()`; NOT auto-mode |
| `recipe_next` | `RecipeRun` | recipe next service fn | `NextResult.to_dict()` |
| `recipe_resume` | `RecipeRun` | recipe resume service fn | `NextResult.to_dict()` |
| `recipe_gate` | `RecipeRun` | recipe gate service fn | `decision ∈ VALID_DECISIONS` |

`create_task` is registered as a **hidden alias** of `task_create` (dispatch routes both to the
same service fn) for one minor cycle (§5.4); it is excluded from the advertised `tools/list` or
flagged hidden so familiars migrate to `task_create`.

### Validation
```python
VALID_DECISIONS: frozenset[str] = frozenset({"approve", "reject"})
```
A `decision` outside this set in `gate_decide`/`recipe_gate` → `UsageError` →
`_err(tool, UsageError(...))` (`error.code == "grain.usage"`). Empty/`!str`/`!int` args →
`UsageError`; packet/artifact/recipe/run not found → `MissingPathError`; recipe-engine failures
mapped via `engine_error_to_forge(exc)` (T05) then `_err`.

### NOT exposed (deferred §8)
`workflow_loop`, recipe **auto mode** (`--auto`), and a `suggest_accept` write tool are absent
from the catalog. No HTTP/auth/daemon surface is added here (§5.6).

## `tools/list` derived from `CAPABILITIES` (§5.3)

`tools/list` is built by joining `CAPABILITIES` (filter `surfaces ∋ "mcp"`) to the `McpTool`
schemas keyed by `McpTool.capability` (and tool name) — not a hand-maintained list. **The
`surfaces` field is pinned by T03** (every MCP-surfaced capability carries `surfaces ∋ "mcp"`),
so the filter is deterministic; this packet **consumes** that seed and does not compute surfaces
locally. Each entry serializes `{name, title, description, inputSchema}` as today, optionally
annotated with `write`. The hidden `create_task` alias is omitted/flagged. Because no
`version_check` `McpTool` is registered here (owned by T10), `version_check` does **not** appear
in this packet's derived listing even though its T03-seeded capability may carry `surfaces ∋
"mcp"` — the join requires a registered `McpTool`, which T10 adds.

## `initialize` (§5.2)

```jsonc
"result": {
  "protocolVersion": MCP_PROTOCOL_VERSION,
  "capabilities": { "tools": { "listChanged": false } },
  "serverInfo": { "name": "grain", "version": "<get_version()>" },
  "instructions": "Drive the loop file-backed: write artifacts to the output_path a tool returns, then call the next tool.",
  "_meta": { "grainContractVersion": "1.1", "engineApiVersion": "grain.engine/v1" }
}
```

`MCP_SERVER_INFO`/the hardcoded `"0.3.0-dev"` literal is removed; `serverInfo.version` resolves
through `get_version()` at call time.

## Out of scope for this packet (do NOT build here)
- `domain/envelope.py`, `grain/version.py`, `domain/capabilities.py`, `recipe_service.engine_error_to_forge`
  (owned by T01/T02/T03/T05 — import them).
- HTTP wrapper pass-through fix in `apps/grain-mcp/main.py` (sibling packet) and any HTTP/bearer
  auth / remote MCP (deferred, separate major revision, §5.6/§8).
- `suggest_accept` over MCP; recipe **auto mode** over MCP; `workflow_loop` over MCP (§8).
- The CLI-side `--envelope` flag / legacy bare-JSON sites (MCP is always-enveloped, §3.5/§5.1).
- `capabilities reconcile` verb (CLI-only/deferred, §6.5).

## Acceptance Checklist
- [ ] `_ok`/`_gate`/`_err` replace `_tool_success`/`_tool_error`; results are §3 envelopes in
      `structuredContent`, mirrored in `content[0].text`, `isError == (status=="error")`.
- [ ] The 5 existing tools carry payload under `data` (not root) and `status` (not `ok`);
      their failures emit typed `error.code` (`grain.missing_path` / `grain.usage`).
- [ ] `McpTool` gains `write: bool` and `capability: str`; write-catalog tools have `write=True`;
      drive-loop/recipe tools have `capability == "workflow_drive"`.
- [ ] Full read+write catalog registered (table above); `recipe_run` is operator-mode only;
      `workflow_run` exposed (OD-4); `workflow_loop`/auto-mode/`suggest_accept` absent.
- [ ] `create_task` is a hidden alias of `task_create` routing to the same service fn.
- [ ] `initialize` reports `serverInfo.version == get_version()` and the §5.2 `_meta`; no
      hardcoded version literal remains in the file.
- [ ] `tools/list` set equals the `McpTool`s **registered here** whose capability has
      `surfaces ∋ "mcp"` (T03-pinned surfaces consumed, not recomputed); `version_check` absent
      (owned by T10).
- [ ] `gate_decide`/`recipe_gate` reject `decision ∉ {approve,reject}` → `grain.usage`; a valid
      write call returns `status: "ok"` (never `"gate"`).
- [ ] JSON-RPC transport errors (`-32700/-32600/-32601/-32602`) unchanged.
- [ ] `uv run pytest tests/test_mcp_service.py` passes with the new cases; full suite green.

## Test cases to include (`tests/test_mcp_service.py`)
1. Read tool (`workflow_next`) success → `structuredContent` is a `grain.engine/v1` envelope
   with `status=="ok"`, `kind=="WorkflowState"`, `command=="workflow_next"`, payload under
   `data`; `content[0].text` round-trips to the same object; `isError` False.
2. `review_summary`/`office_review_show` on a missing packet → `status=="error"`,
   `error.code=="grain.missing_path"`, `isError` True.
3. A bad/empty arg (e.g. `task_show` with no/blank id) → `error.code=="grain.usage"`.
4. `initialize` → `serverInfo.version == get_version()`; `_meta` equals the §5.2 object; a grep
   asserts no hardcoded version literal (no `"0.3.0-dev"`, no inline `"0.5.0"`).
5. `tools/list` returned names == the set derived from `CAPABILITIES` (`surfaces ∋ "mcp"`,
   T03-pinned) joined to the `McpTool`s registered here; `workflow_loop`/auto-mode/
   `suggest_accept` not present; `version_check` not present (owned by T10).
6. `task_create` and the hidden `create_task` alias both create a packet via the same service
   function and return the same `kind`/`data` shape.
7. `workflow_run` success → `status=="ok"`, `kind=="WorkflowStep"` (asserts OD-4 exposure).
8. A recipe tool (`recipe_run` operator-mode) success → `kind=="RecipeRun"`, `data` is
   `NextResult.to_dict()`; a recipe-engine error maps via `engine_error_to_forge` to the §4
   `error.code`.
9. `gate_decide`/`recipe_gate` with `decision="maybe"` → `error.code=="grain.usage"`; with
   `decision="approve"` → `status=="ok"`, `kind=="RecipeRun"` (registered §3.2), routed through
   the `recipe_service` recipe-gate fn (never `"gate"`).
10. Every `McpTool` in the write catalog has `write=True`; every drive-loop/recipe tool has
    `capability=="workflow_drive"`.
