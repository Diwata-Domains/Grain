# Deliverable Spec: P37-T07 — HTTP wrapper pass-through fix (no auth)

## Required Output

> **Cross-product paths.** `apps/grain-mcp/` is a **root-level app outside `products/grain/`** with
> its own `pyproject.toml`/deps and **no grain SPDX regime**. Its tests live **with the app**, not in
> `products/grain/tests/`. Paths prefixed `src/grain/...` or `products/grain/...` are inside the grain
> product (reference only).

### New Files
- `tasks/P37-T07/task.md` — packet metadata/scope ✓
- `tasks/P37-T07/deliverable_spec.md` — this file ✓
- A wrapper test module **inside the app**, e.g. `apps/grain-mcp/test_main.py` (or
  `apps/grain-mcp/tests/test_main.py`) — does **NOT** carry the grain SPDX header (follows the app's
  own conventions; current `main.py` has none); covers pass-through, version, error-shape,
  route-enumeration cases. It must **not** live in `products/grain/tests/`.

### Modified Files
- `apps/grain-mcp/main.py` — the only production file changed (root-level app).

### NOT Modified (referenced only)
- `products/grain/src/grain/services/mcp_service.py` — envelope + registry-derived `TOOLS`/
  `tools/list` are delivered by P37-T06; this packet relays them, it does not build them.
- `products/grain/src/grain/version.py` — `get_version()` is delivered by P37-T02.
- `products/grain/src/grain/domain/envelope.py` — §4.2 `ErrorEnvelope`/`envelope_to_dict` delivered
  by P37-T01; the boundary error map mirrors that shape.

## Context: the bug being fixed (spec §1, §5.6)

Current `apps/grain-mcp/main.py::call_tool` (the flattening bug):

```python
result = response.get("result", {})
content = result.get("content", [])
text = "\n".join(c.get("text", "") for c in content if c.get("type") == "text")
return {"result": text or result, "error": None}   # DROPS structuredContent + isError
```

and the bare-string error map:

```python
if "error" in response:
    return {"result": None, "error": response["error"].get("message", "unknown error")}
```

and the hardcoded version:

```python
app = FastAPI(title=..., description=..., version="0.1.0")   # stale, hardcoded
```

`GET /mcp/tools` is **already** a derived view (it iterates `mcp_service.TOOLS`) and is **not** part
of the bug — it needs no code change (see §4 below).

## Module contract: `apps/grain-mcp/main.py`

### 1. Version from `get_version()` (§5.2)
- `from grain.version import get_version`.
- `app = FastAPI(title="Grain MCP Server", description=..., version=get_version())`.
- No version literal anywhere in the file (no `"0.1.0"`, `"0.3.0-dev"`, `"0.5.0"`).

### 2. `POST /mcp/call` — verbatim pass-through (§5.1, §5.6)
On a successful JSON-RPC response, return the MCP `result` object **unchanged**:

```python
response = handle_request(root, rpc_request)

if response is None:
    return {"result": None, "error": None}

if "error" in response:
    # JSON-RPC PROTOCOL error → §4 error shape (see §3 below)
    return {"result": None, "error": _rpc_error_to_engine(response["error"])}

# SUCCESS: relay result verbatim — preserves structuredContent + content + isError
return {"result": response.get("result", {}), "error": None}
```

- The returned `result` MUST retain, exactly as produced by `mcp_service` (P37-T06):
  - `result["structuredContent"]` — the `grain.engine/v1` envelope
    (`apiVersion`, `kind`, `status` ∈ `{ok, gate, error}`, `data`, `gate`, `error`, `grain_version`,
    `warnings`) — §3.1.
  - `result["content"]` — the `content[*]` blocks (the JSON mirror in `content[0].text`) — §5.1.
  - `result["isError"]` — `true` iff `status == "error"` — §5.1.
- The wrapper does NOT read, re-key, flatten, filter, or re-serialize the envelope. No
  `"\n".join(... content ... text ...)` extraction remains.
- A **tool-execution** error is NOT a JSON-RPC `error`; it arrives as a normal `result` with
  `isError == true` and `status == "error"`, and therefore flows through the success branch verbatim
  (§4.3 — the two error axes are never conflated).

### 3. JSON-RPC protocol errors → §4 error shape at the wrapper boundary (§4.2, §5.6)
JSON-RPC *transport* errors stay protocol-level/unchanged inside `mcp_service` (§4.3); the mapping
to the §4.2 shape happens **only here, at the out-of-contract HTTP-wrapper boundary** (§5.6). A small
pure mapper turns a JSON-RPC transport error into the §4.2 `ErrorEnvelope` dict shape:

```python
def _rpc_error_to_engine(err: dict) -> dict:
    """Map a JSON-RPC protocol error to the §4.2 portable error shape."""
    code_map = {
        -32700: "grain.general",   # parse error
        -32600: "grain.usage",     # invalid request
        -32601: "grain.usage",     # method not found
        -32602: "grain.usage",     # invalid params
        -32603: "grain.general",   # internal error
    }
    grain_code = code_map.get(err.get("code"), "grain.general")
    exit_map = {"grain.general": 1, "grain.usage": 2}
    return {
        "apiVersion": "grain.error/v1",
        "code": grain_code,
        "message": err.get("message", "protocol error"),
        "detail": "",
        "exit_code": exit_map[grain_code],
    }
```

- Output keys and values match §4.2 exactly: `apiVersion="grain.error/v1"`, `code` ∈
  `VALID_ERROR_CODES` (the 7 `grain.`-namespaced tokens), `message`, `detail` (default `""`),
  `exit_code` consistent with the §4.1 code↔exit table.
- This replaces the current `response["error"].get("message", "unknown error")` bare string.
- NOTE: this packet does not need to import `domain/errors.py`; reproducing the §4.2 shape is
  sufficient at the wrapper boundary (the wrapper is out-of-contract, §5.6). If a shared serializer
  (`envelope_to_dict`) is conveniently importable from the contract foundation, prefer reusing it
  over the inline dict; either satisfies acceptance.

### 4. `GET /mcp/tools` — already derived from the shared registry (§5.3) — NO change
- The listing **already** iterates `mcp_service.TOOLS` (today's `main.py` builds it from
  `for t in TOOLS`). P37-T06 makes `TOOLS`/`tools/list` a derived view of `CAPABILITIES`, so the
  wrapper's listing reflects the registry **automatically with no code change**. Do not "un-hand-roll"
  anything — there is no parallel hand-maintained list to remove.
- Leave the endpoint as-is; the only requirement is a **regression** assertion that the returned
  **name set** still equals `{t.name for t in TOOLS}`. Each entry continues to expose at least
  `name`, `description`, `input_schema`.

### 5. Unchanged
- `GET /health` → `{"status": "ok", "service": "grain-mcp"}`.
- Workspace resolution via `GRAIN_WORKSPACE_DIR` (`_workspace()`), including the `503` on missing dir.
- The JSON-RPC request construction passed to `handle_request`.

## Out of scope for this packet (do NOT build here — §8 Deferred, OD-3)
- ANY authentication (bearer tokens, API keys, OAuth) — §5.6/OD-3 forbid it this phase.
- ANY new endpoint beyond `/health`, `/mcp/tools`, `/mcp/call`; remote MCP transport.
- Promoting the HTTP wrapper to a canonical contract surface; a "control vs data channel"
  distinction.
- Modifying `mcp_service.py` envelope construction or the registry (P37-T06's job).
- Modifying `get_version()` (P37-T02's job).
- A streaming/SSE transport, batching, or a `tools/call` schema change.

## Acceptance Checklist
- [ ] `POST /mcp/call` success body `result` contains `structuredContent` (full `grain.engine/v1`
      envelope object), `content`, and `isError` — none flattened/dropped.
- [ ] Tool-execution failure flows through verbatim: `result.isError == true`,
      `result.structuredContent.status == "error"`,
      `result.structuredContent.error.apiVersion == "grain.error/v1"`,
      `error.code` ∈ the 7 `grain.`-namespaced tokens.
- [ ] JSON-RPC protocol error → §4.2 shape (`apiVersion="grain.error/v1"`, `code` namespaced,
      `message`, `detail`, `exit_code`), not a bare string — mapped at the wrapper boundary (§5.6),
      transport error unchanged upstream (§4.3).
- [ ] `app.version == get_version()`; no hardcoded version literal in `main.py` (grep-clean).
- [ ] `GET /mcp/tools` name set == registry (`TOOLS`) name set (already derived; regression guard, no
      code change to the endpoint).
- [ ] No auth dependency added; `app.routes` expose only `/health`, `/mcp/tools`, `/mcp/call`
      (plus framework defaults), enumerated by a test.
- [ ] New test module lives in `apps/grain-mcp/` (NOT `products/grain/tests/`) and does **NOT** carry
      the grain SPDX header.
- [ ] `uv run pytest` (wrapper tests, run from `apps/grain-mcp/`) passes; full Grain suite shows no
      regressions.

## Test cases to include
1. **Pass-through (success):** mock/stub `handle_request` to return a result with
   `structuredContent` (a valid `grain.engine/v1` envelope, `status="ok"`), `content`, and
   `isError=false`; assert the HTTP body's `result` is the same object with all three keys intact.
2. **Pass-through (tool error):** stub a result with `isError=true` and
   `structuredContent.status="error"`; assert it relays verbatim (no collapse to a string).
3. **Protocol error mapping:** stub a JSON-RPC `error` (`code=-32601`); assert the body matches the
   §4.2 shape with `code="grain.usage"`, `exit_code=2`, `apiVersion="grain.error/v1"`.
4. **Version:** assert `app.version == get_version()` and grep the source for no version literal.
5. **Registry-derived tools:** assert `GET /mcp/tools` name set equals `{t.name for t in TOOLS}`.
6. **No new surface / no auth:** enumerate `app.routes` and assert path set ⊆
   `{/health, /mcp/tools, /mcp/call}` (plus framework defaults) and no auth dependency is wired.
