# Task: HTTP wrapper pass-through fix (no auth)

## Metadata
- **ID:** P35-T07
- **Status:** draft
- **Phase:** Phase 35 — Grain-as-Engine Headless Contract
- **Backlog:** P35-T07
- **Packet Path:** tasks/P35-T07/
- **Dependencies:** P35-T01, P35-T02, P35-T06
- **Primary Adapter:** code
- **Secondary Adapters:** none
- **Engine-contract:** HTTP wrapper stays **deployment-only / out-of-contract** (§5.6, OD-3). This
  packet fixes the result-flattening bug and removes hardcoded version drift; it adds **NO** auth
  and **NO** new network surface. The contract-conformant MCP surface remains stdio (§5.1, §5.6).
- **Cross-product boundary:** `apps/grain-mcp/` lives at the **monorepo root**
  (`/Users/domicile/Diwata/Diwata-Labs/apps/grain-mcp/`), **outside** `products/grain/`. It is its
  own deployment app with its **own `pyproject.toml`** and FastAPI/uvicorn deps (depending on
  `grain` via `[tool.uv.sources]` path-editable), and is **NOT** under the grain SPDX regime. New
  files in this app (including its tests) follow the **app's** conventions — they do **NOT** carry
  the grain `Shaznay Sison` SPDX headers. The wrapper's tests live **with the app**
  (`apps/grain-mcp/`), **not** in `products/grain/tests/`.

## Objective
Fix `apps/grain-mcp/main.py` (the FastAPI HTTP MCP wrapper) so it returns the underlying MCP
`tools/call` result **verbatim** — preserving `structuredContent` (the `grain.engine/v1` envelope,
§5.1), `content`, and `isError` instead of flattening to a bare text string. Replace the hardcoded FastAPI
`version="0.1.0"` with `get_version()` (§5.2). At the **HTTP-wrapper boundary** only, map JSON-RPC
protocol errors to the §4 error shape rather than a bare string (§5.6) — the JSON-RPC transport
errors themselves remain protocol-level/unchanged inside `mcp_service` (§4.3). The wrapper gains
**no** authentication and **no** new network surface (§5.6): it remains a deployment-only
convenience, not a canonical contract surface.

`GET /mcp/tools` **already** derives its listing from `mcp_service.TOOLS` (it iterates `TOOLS`
today); P35-T06 makes `TOOLS`/`tools/list` a derived view of the registry, so the wrapper's
`/mcp/tools` reflects that automatically with **no code change** — this packet does not "un-hand-roll"
it. The substantive production changes are exactly two: the `call_tool` pass-through fix and the
`get_version()`-sourced version (plus the boundary error-shape map).

## Why This Task Exists
The HTTP wrapper today flattens the MCP result: `call_tool` joins only the `content[*].text` blocks
and returns `{"result": text, "error": <string>}`, **dropping** `structuredContent` and `isError`
(spec §1, §5.6). A familiar driving Grain over HTTP therefore cannot read the versioned envelope or
detect tool-execution errors. The wrapper also hardcodes `version="0.1.0"` (a third stale version
string alongside MCP's `"0.3.0-dev"`, which §5.2 retires). `GET /mcp/tools` is **already** a derived
view (it iterates `mcp_service.TOOLS`), so it needs no fix — once P35-T06 makes `TOOLS` registry-
derived (§5.3, X4) the wrapper's listing tracks it for free. Per OD-3/§5.6 the conflict over
HTTP+auth is resolved by **retreat**: HTTP stays out-of-contract, so this packet is strictly the
pass-through bug fix (plus dropping the hardcoded version) — no auth — letting the deployment wrapper
faithfully relay the stdio contract surface it wraps.

## Scope
- EDIT `apps/grain-mcp/main.py`:
  - **`POST /mcp/call` (`call_tool`) — verbatim pass-through (§5.1, §5.6).** On a successful
    JSON-RPC response, return the MCP `result` object **unchanged** so `structuredContent`,
    `content`, and `isError` all survive to the HTTP caller. Stop joining/extracting only
    `content[*].text`; stop collapsing the result into `{"result": text, "error": null}`.
  - **JSON-RPC protocol errors → §4 error shape at the wrapper boundary (§5.6).** JSON-RPC
    *transport* errors stay protocol-level/unchanged inside `mcp_service` (§4.3); the mapping to the
    §4 error shape happens **only at the HTTP-wrapper boundary** (§5.6, the out-of-contract seam).
    When the underlying response carries a JSON-RPC `error` (transport-level
    `-32700/-32600/-32601/-32602/-32603`), return the §4 `ErrorEnvelope`-shaped object
    (`apiVersion: grain.error/v1`, `code`, `message`, `detail`, `exit_code`) instead of the current
    bare `error: <string>`. Map the JSON-RPC code to the appropriate `grain.`-namespaced code
    (`grain.usage` for invalid request / unknown method / invalid params, `grain.general` for
    parse/internal). Do not invent a new error shape — reuse the §4.2 shape (and prefer the shared
    serializer from P35-T01 if conveniently importable, §4.2).
  - **Version from `get_version()` (§5.2).** Replace the hardcoded FastAPI `version="0.1.0"` with
    `get_version()` (the single resolver from P35-T02). **`GET /mcp/tools` needs no change** — it
    already derives from `mcp_service.TOOLS` (§5.3 derived view); once P35-T06 makes `TOOLS`
    registry-backed, the listing tracks it automatically. Do not introduce a hand-rolled second
    list (there is none today).
  - Keep `GET /health` and the workspace-resolution behavior as-is.
- ADD/UPDATE tests under the wrapper app (or `tests/`) proving the round-trip preserves
  `structuredContent`/`content`/`isError`, the version is non-hardcoded, and protocol errors emit
  the §4 shape.

## Constraints
- **NO auth, NO new network surface (§5.6, OD-3).** Do not add bearer tokens, API keys, or any
  authentication; do not add new HTTP endpoints beyond the existing `/health`, `/mcp/tools`,
  `/mcp/call`. The wrapper stays deployment-only/out-of-contract; it is NOT promoted to canonical.
- **No business logic in the wrapper (§5.5/§5.6).** The wrapper only relays; all tool behavior and
  envelope construction live behind `mcp_service.handle_request` (CLI-canonical, §2 principle 5,
  §5.5). Do not
  re-wrap, re-key, or re-validate the envelope in `main.py`.
- **No hardcoded version strings anywhere (§5.2).** The only version source is `get_version()`.
- **MVP only (§8).** Pass-through fix + version-from-`get_version()` only. Remote MCP, HTTP+bearer
  auth, and any control/data-channel distinction are explicitly **deferred** (§8 "Deferred", OD-3).
- **Cross-product SPDX:** `apps/grain-mcp/` is a root-level app **outside** `products/grain/` and is
  **not** under the grain SPDX regime. New files here (including the test module) do **NOT** carry
  the grain `# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison` header — they follow the app's own
  conventions (current `main.py` carries no SPDX header). The tests live in `apps/grain-mcp/`, not
  `products/grain/tests/`.

## Deliverable
- Edited `apps/grain-mcp/main.py` with verbatim result pass-through, registry-derived `tools/list`,
  `get_version()`-sourced version, and §4-shaped JSON-RPC protocol errors — exactly as enumerated in
  `deliverable_spec.md`.
- Tests proving the pass-through, version, and error-shape behavior.

## Acceptance Criteria
- A `POST /mcp/call` for a successful tool returns a body whose `result` contains **both**
  `structuredContent` (the `grain.engine/v1` envelope with `apiVersion`/`kind`/`status`/`data`) and
  `content`, and an `isError` field — a test asserts all three keys are present and
  `structuredContent` is the unmodified envelope object (not a flattened string).
- A `POST /mcp/call` for a tool whose execution fails returns the underlying result with
  `isError == true` and the §3/§4 error envelope under `structuredContent` (`status == "error"`,
  `error.apiVersion == "grain.error/v1"`, `error.code` ∈ the 7 `grain.`-namespaced tokens) —
  asserted by a test; the wrapper does NOT collapse it to a bare error string.
- A JSON-RPC **protocol** error (e.g. unknown method or invalid params) yields a body whose `error`
  matches the §4.2 error shape (keys `apiVersion="grain.error/v1"`, `code`, `message`, `detail`,
  `exit_code`) with a `grain.`-namespaced `code` — not a bare `{"error": "<string>"}` — asserted by
  a test. This mapping is at the wrapper boundary (§5.6); the JSON-RPC transport error is unchanged
  upstream (§4.3).
- The FastAPI app's advertised `version` equals `get_version()` (P35-T02); `grep` finds no
  hardcoded version literal (no `"0.1.0"`, `"0.3.0-dev"`, or `"0.5.0"`) in `apps/grain-mcp/main.py`
  — asserted by a test.
- `GET /mcp/tools` returns a listing derived from `mcp_service.TOOLS` (§5.3) — as it already does; a
  regression test asserts the returned tool-name set equals `{t.name for t in TOOLS}` (confirming no
  hand-maintained second list is introduced).
- No authentication is added and no new endpoints exist beyond `/health`, `/mcp/tools`, `/mcp/call`
  — asserted by a test enumerating `app.routes` (or equivalent) and confirming no auth dependency.
- `uv run pytest` for the wrapper's tests (run from `apps/grain-mcp/`) passes and the full Grain
  suite shows no regressions.

## Dependencies
- **P35-T01** — provides the shared `domain/envelope.py` (`ErrorEnvelope` + `to_envelope`/
  `envelope_to_dict` and the §4.2 portable error shape). The wrapper's boundary error map reproduces
  that §4.2 shape (or reuses the serializer if conveniently importable).
- **P35-T02** — provides `grain/version.py::get_version()`, the single version source the wrapper
  must use for its advertised version and `serverInfo`.
- **P35-T06** — expands `mcp_service` to emit the `grain.engine/v1` envelope
  (`structuredContent`/`isError`) and the registry-derived `TOOLS`/`tools/list` that this wrapper
  relays; without it there is no enveloped result to pass through verbatim.

## Relevant Files

> Paths below are **monorepo-root-relative**. `apps/grain-mcp/` is a root-level app outside
> `products/grain/`; `src/grain/...` and `products/grain/tests/...` are inside the grain product.

- `apps/grain-mcp/main.py` (edit) — root-level FastAPI HTTP wrapper (own app, own `pyproject.toml`,
  no grain SPDX). The flattening bug lives in `call_tool` (extracts only `content[*].text`, drops
  `structuredContent`/`isError`) and the bare-string error map; plus the hardcoded
  `version="0.1.0"`. `GET /mcp/tools` already derives from `TOOLS` (no change needed).
- `apps/grain-mcp/` (new test module here, e.g. `test_main.py`) — wrapper tests live **with the
  app**, not in `products/grain/tests/`; no grain SPDX header.
- `apps/grain-mcp/pyproject.toml` (reference) — wrapper app deps (fastapi/uvicorn/pydantic + path-
  editable `grain`); do not add auth/network deps.
- `products/grain/src/grain/services/mcp_service.py` (reference, not edited here) — `handle_request`,
  `TOOLS`; the source of the enveloped result and the registry-derived tool list (delivered by
  P35-T06).
- `products/grain/src/grain/version.py` (reference, from P35-T02) — `get_version()`.
- `products/grain/src/grain/domain/envelope.py` (reference, from P35-T01) — §4.2 `ErrorEnvelope` /
  `envelope_to_dict` the boundary error map mirrors.
- `products/grain/docs/working/engine_contract_spec.md` §4.2 (error shape), §4.3 (transport errors
  stay protocol-level), §5.1/§5.3/§5.6 (envelope, derived registry view, HTTP pass-through + no-auth
  + boundary error map), §5.2 (version), §8 (MVP/deferred), §9 OD-3.
- `products/grain/tests/test_mcp_cmd.py` (reference only) — existing MCP test patterns to mirror;
  the new tests do NOT live here.

## Escalation Conditions
- If P35-T06 has not yet landed the enveloped MCP result / registry-derived `tools/list`, stop and
  record a blocker rather than reconstructing the envelope inside the wrapper (that would put
  business logic in `main.py`, violating §2 principle 5 / §5.5 / §5.6).
- If preserving the result verbatim surfaces a downstream HTTP consumer that depended on the old
  flattened `{"result": text}` shape, log a change proposal noting the one-time pre-1.0 break
  (parallel to the §5.1 structuredContent break) rather than keeping a compatibility shim.
- If any requirement appears to need auth or a new endpoint to satisfy, stop — that is out of
  contract per §5.6/OD-3 and belongs to a future **major** revision, not this packet.

## Model Recommendation
Sonnet-class. This is a small, mechanical edit to one file plus targeted tests; the design
decisions (no auth, verbatim pass-through, §4 error shape, registry-sourced version) are fully
resolved in the spec and this packet. Follow `deliverable_spec.md` literally.
