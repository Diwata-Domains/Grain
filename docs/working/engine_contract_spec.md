# Grain-as-Engine Headless Contract (Phase 35)

**Status:** Working draft (v0.5.0) — **EXTENDS the locked canonical `toolkit_contract.md`
v1.0** (additively) and amends `cli_spec.md` §5/§10 and `recipe_engine_spec.md` §6. Promote
to canonical via change proposal during the v0.5.0 planning pass. Authored 2026-06-28.

This spec unifies five Phase 35 area designs (versioned envelope, typed errors, expanded MCP,
capability registry/discovery, non-interactive completeness + version check) into **one**
familiar-facing contract, and resolves the cross-area incoherence the adversarial critique
surfaced (four incompatible frames, four error shapes, a broken envelope invariant, a
double-specified command, and one genuine canonical conflict).

**One-line:** make every Grain surface — CLI `--format json` and MCP — speak **one versioned
frame, one typed error, one capability registry, one version resolver**, so a familiar (agent)
can drive the entire loop end-to-end with no human and no browser.

**Not demo-critical.** The July-21 demo is a simple recipe and does not depend on the envelope.
Envelope + typed errors are the foundational slice; everything else layers on them.

---

## 0. Status & relationship to canonical

- **Extends, does not contradict, `toolkit_contract.md` v1.0 (LOCKED).** The locked doc forward-
  declares three artifacts as doc-only: `docs/runtime/grain_capabilities.yaml` (with `since:`),
  `grain workspace list`, and the `workflow_drive` capability. This phase **builds** them. Every
  field/path the locked doc names is preserved verbatim; everything new is additive. The contract
  bumps **1.0 → 1.1 (minor)**.
- **One canonical conflict is resolved by retreat, not override** (see §5.6, C1): the FastAPI
  HTTP MCP wrapper + auth is declared **out-of-contract / deployment-only**. The contract-
  conformant MCP surface is **stdio**, honoring locked §2 (no auth, same OS user) and §4.3 (no
  network transport). Remote MCP, if ever wanted, is a separate **major** contract revision.
- **The change proposal must edit THREE canonical docs**, not just `toolkit_contract.md`:
  `cli_spec.md` (§5 exit-code ratification, §10 `errors`→`error` and the envelope), and
  `recipe_engine_spec.md` §6 (un-defer recipe verbs over MCP). See §8.

This is v0.5.0 contract deliverable **#6** (grain-as-engine), carrying **#11** (`grain version
--check`) and the headless half of **#7** (capability declarations / workspace resolution).

---

## 1. Motivation & the linchpin role

Today the headless surface is incoherent. `--format json` exists broadly but every command hand-
rolls a bare dict (~15 distinct top-level shapes, no version, no discriminator, no uniform error).
MCP exposes only 5 tools (4 read + `create_task`), with a stale hardcoded `serverInfo.version`
`"0.3.0-dev"` and an untyped `{"errors":[...]}` blob. The HTTP wrapper flattens MCP results and
**drops** `structuredContent`/`isError`. Three CLI write paths (`suggest accept`, `docs audit
--fix`, `upgrade`) are interactive dead-ends headlessly — one (`docs audit --fix --format json`)
is a **silent no-op**. A familiar cannot reliably (a) know which schema/version it received, (b)
distinguish error classes across surfaces, (c) discover what is drivable, or (d) complete the SDLC
loop without dropping to interactive prompts.

This is the **linchpin** for hosted Apex and agent routing: DAEMON/Sovereign and future familiars
can only orchestrate Grain if its surface is a versioned, typed, discoverable, non-interactive
contract. Fix the frame once and the rest of the stack composes on it.

---

## 2. Principles (the contract)

1. **Familiar-drivable end-to-end.** Every state read and every deterministic mutation is
   reachable by an agent with no human and no browser. `--format json` never calls
   `click.confirm`/`click.prompt`. (v0.5.0 guiding principle.)
2. **One frame, one error, one registry, one version resolver.** CLI and MCP serialize the **same**
   envelope (§3), embed the **same** error object (§4), read the **same** capability registry (§6),
   and report the **same** version via one `get_version()` (§10). No surface re-invents these.
3. **Versioned.** The frame carries `apiVersion: grain.engine/v1`. Payloads that already self-
   version (`grain.recipe/v2`, `grain.recipe-run/v1`) keep their own `apiVersion` *inside* `data`.
   The frame evolves far slower than grain-kit's semver.
4. **File-backed / pull-first / no network / no daemon.** The envelope is a stdout/structuredContent
   **transport frame only** — it changes no on-disk artifact. The recipe drive loop moves bytes
   through the filesystem (the familiar writes the artifact). Honors locked `toolkit_contract.md`
   §2/§4.1/§4.3. The one network exception (PyPI freshness check, §7) is flag-gated, fail-silent,
   and is *not* inter-tool transport.
5. **CLI is canonical.** The CLI reading the in-code registry is the source of truth; MCP, the HTTP
   wrapper, and `grain_capabilities.yaml` are **derived views**. No business logic lives in
   `mcp_service.py` — every tool delegates to the same service function the CLI command uses.
6. **Additive & negotiated.** New behavior is opt-in or new-command-only; existing scripts keep
   working through a committed deprecation window (§3.5). Mirrors locked §2 principle 4.

---

## 3. The engine envelope (`grain.engine/v1`)

### 3.1 The frame — recommended shape

A single frozen dataclass `EngineEnvelope` (in a new shared `domain/envelope.py`) wraps every
`--format json` payload **and** every MCP `tools/call` result. The current per-command dict moves
**verbatim** under `data` — no field renaming — so migration is mechanical.

```jsonc
{
  "apiVersion": "grain.engine/v1",   // FRAME version, NOT grain-kit version
  "kind": "WorkflowState",            // closed-vocabulary discriminator (picks the data schema)
  "status": "ok",                     // tri-state: "ok" | "gate" | "error"  (see §3.3)
  "grain_version": "0.5.0",           // grain-kit version, from get_version() — NEVER hardcoded
  "command": "workflow next",         // optional annotation; on MCP this carries the tool name
  "data": { /* the existing command-specific shape, unchanged */ },
  "gate": null,                       // populated only when status == "gate" (see §7)
  "error": null,                      // populated only when status == "error" (verbatim §4 object)
  "warnings": []                      // optional; promoted from per-command warnings
}
```

**Resolves the critique's four-frames / four-errors incoherence (X1, X2):**
- **One `apiVersion` (`grain.engine/v1`) and one discriminator (`kind`) on BOTH CLI and MCP.** MCP
  does not use a separate `grain.mcp/v1` or a `tool` discriminator; the tool name rides in the
  optional `command` field. A familiar parses **one** shape on both transports — the parity claim
  is now true.
- **snake_case everywhere except `apiVersion`** (matches the on-disk idiom: `run_id`,
  `recipe_apiVersion`, but `apiVersion` itself is camel). This kills the camelCase `grainVersion`/
  `exitCode` the envelope-area draft used.
- The `error` block is the §4 `ErrorEnvelope` embedded **verbatim** (same keys, same casing, same
  `grain.`-namespace). No area redefines it.

### 3.2 `kind` registry (the ~15 shapes)

`kind` is a `VALID_ENGINE_KINDS` frozenset on the dataclass; an unregistered kind is a programming
error caught in `__post_init__`. Each emit site declares its `kind`; `data` is its *current* dict.

| Command | kind | data = today's shape |
|---|---|---|
| `workflow next` | `WorkflowState` | result + `evaluation`/`observability`/`suggestion` |
| `workflow run` | `WorkflowStep` | result + `workflow_run` |
| `workflow loop` | `WorkflowLoop` | result + `workflow_loop` |
| `workflow explain` | `WorkflowDiagnostic` | result + `evaluation`/`diagnostic` |
| `workflow reconcile` | `ReconcileReport` | issues/fixed |
| `workflow guard` | `GuardReport` | checks/status |
| `recipe list` | `RecipeList` | `{recipes: [...]}` (was a bare array — see note) |
| `recipe show` | `RecipeDefinition` | normalized definition (`grain.recipe/v2`) |
| `recipe run/next/status/resume/gate` | `RecipeRun` | `NextResult.to_dict()` / `run.json` |
| `recipe scaffold` | `RecipeScaffold` | id/path/files/created |
| `capabilities` (list/show) | `CapabilityList` / `Capability` | §6 payloads |
| `workspace list/resolve` | `WorkspaceList` | §6 payload |
| `version` (`--check`) | `VersionInfo` | §7 payload (embeds `grain.version/v1`) |
| `task *`, `review *`, `suggest *`, `docs audit`, `status` | one kind each | existing dict |

**Top-level arrays:** `recipe list` currently emits a bare JSON array. Under the envelope it
becomes `data: {"recipes": [...]}`. This is the one structural change, acceptable because the
envelope is opt-in for legacy sites (§3.5).

### 3.3 Tri-state `status` — replaces the broken XOR invariant

**Resolves X3 (a hard correctness bug).** The envelope-area draft mandated a binary
`error XOR data` invariant with `ok` mirroring exit 0. Two sibling areas legitimately produce a
**successful negative answer with data and exit 0**: a non-interactive confirmation gate
(`status: confirmation_required`, exit 0, data present, no error) and a capabilities reconcile
verdict (`drivable: false`, an answer, not a failure). The XOR dataclass would *raise on
legitimate output*.

The frame uses a **tri-state `status`** discriminator instead:

| `status` | meaning | `data` | `gate` | `error` | process exit |
|---|---|---|---|---|---|
| `ok` | success | present | null | null | 0 |
| `gate` | expected pause: awaiting consent / negative-but-valid answer | present | present (§7) | null | **0** |
| `error` | failure | null | null | present (§4) | `error.exit_code` (1–7) |

`__post_init__` enforces: `status ∈ {ok, gate, error}`; `error` non-null **iff** `status == error`;
`gate` non-null **iff** `status == gate`; `data` non-null **iff** `status ∈ {ok, gate}`; and
`kind ∈ VALID_ENGINE_KINDS`. This is representable and never raises on a valid output.

**Philosophy decision, ratified here (resolves the noninteractive ↔ capabilities split):**
*expected-negative and awaiting-consent results are `status: gate`, exit 0 — never an error code.*
This aligns with the recipe engine's `awaiting_gate` outcome. So the capabilities `reconcile`
"not drivable" verdict is `status: gate` exit 0 (when it ships — deferred, §6), NOT
`ValidationError` exit 3. Only genuine failures (malformed file, bad args) are `status: error`.

### 3.4 `kind` on error responses (resolves X6)

The error block is produced centrally in `error_handler.py::handle_error`, which is command-
agnostic and cannot know the emitting command's `kind`. Mechanism: the active command stores its
`kind` on `ctx.obj["kind"]` at entry (next to `ctx.obj["fmt"]`/`["repo"]`); `handle_error` reads
it. If unset (e.g. an error before any command body runs), `kind` is `null` on the error envelope —
explicitly permitted. Consumers route on `status` first; `kind` is best-effort on errors.

### 3.5 Migration (scoped down from the draft's Option B — resolves the over-scoping note)

The critique judged the draft's full deprecation apparatus (a 3-version `--api` negotiator + env
var + default-flip + removal) over-engineered for ~2 known consumers (one of which discards
output). **Adopted, simplified:**

- **Pre-existing JSON sites** (`workflow *`, `recipe *`, `task *`, `review *`, `suggest *`, `docs
  audit`, `status`) are enveloped behind a **single opt-in flag** in 0.5.0; default stays bare.
  - Negotiation, precedence high→low: `--envelope` global flag → `GRAIN_ENGINE_ENVELOPE=1` env →
    default bare. Stored once on `ctx.obj["envelope"]`; emit sites build `data` exactly as today and
    hand it to one helper that prints bare or wrapped.
  - **0.6.0:** default flips to enveloped; `--envelope=0` / `GRAIN_ENGINE_ENVELOPE=0` opts out; a
    one-line deprecation notice on **stderr** (stdout stays clean JSON) when the legacy path is
    taken. **0.7.0:** legacy path removed.
- **New commands** (`capabilities`, `workspace`, `version`) and **all MCP tools** are
  **always-enveloped** from day one and ignore the legacy opt-out — they have no legacy shape to
  protect (resolves X7). A familiar therefore sees: new surfaces always enveloped; legacy surfaces
  bare-until-negotiated through 0.5.x.
- A multi-version `--api grain.engine/vN` negotiator is **not built now** — built only when a
  `v2` frame actually exists.

### 3.6 Versioning policy for `grain.engine/vN`

Reuse the contract's semver discipline (locked §7), but the **frame** version bumps only on
*frame* changes, not `data` changes.

**Additive (stays `grain.engine/v1`):** a new `kind`; a new optional top-level key (`meta`,
`links`); fields *inside* a `data` shape (governed by that shape's own embedded `apiVersion`); a new
`error.code` token *only if* it maps to a new `ForgeError`/exit code (governed by `cli_spec §5`).

**Breaking (`grain.engine/v2`):** removing/renaming a top-level key (`apiVersion`, `kind`,
`status`, `data`, `gate`, `error`, `grain_version`); changing a key's type/semantics; removing a
`kind` or repurposing one to carry a different `data` schema; changing the `error.code`↔`exit_code`
mapping or the `status` tri-state vocabulary.

`data`-internal breaking changes are out of scope for the frame — each shape owns its own contract.

---

## 4. Typed error model (the anchor — owns the one error object)

The error model is the strongest, most correct area and is the **anchor**: its `ErrorEnvelope` is
the single source of truth that the frame (§3) embeds verbatim and that MCP, capabilities, and
non-interactive all reference. No other area defines an error shape.

### 4.1 The canonical code registry

Each `ForgeError` subclass gains a stable string `code`, namespaced `grain.<token>` (familiars
operate across sibling tools — Diwa/Scry/Assay — so a bare `validation` is ambiguous on a shared
surface). Codes are **1:1 with the locked `cli_spec.md §5` exit table; the exit codes do not
change.**

| `ForgeError` class | `code` (stable) | `exit_code` |
|---|---|---|
| `GeneralError` | `grain.general` | 1 |
| `UsageError` | `grain.usage` | 2 |
| `ValidationError` | `grain.validation` | 3 |
| `MissingPathError` | `grain.missing_path` | 4 |
| `InvalidTransitionError` | `grain.invalid_transition` | 5 |
| `ConfigError` | `grain.config` | 6 |
| `AdapterError` | `grain.adapter` | 7 |

These 7 strings are a **contract surface** and must remain stable once shipped (same stability
promise as the exit codes). New classes are additive only.

### 4.2 Shapes (Grain idioms: `ClassVar` + `VALID_*` frozenset + frozen dataclass `__post_init__`)

In `domain/errors.py`: `code` and `exit_code` become `ClassVar`s on `ForgeError` (overridden per
subclass), making `EXIT_CODES` in `error_handler.py` a thin derived lookup kept as the single
audited table (a startup assert verifies every `VALID_ERROR_CODES` member resolves through it — no
drift). `VALID_ERROR_CODES` frozenset holds the 7 tokens.

The portable error object (the **only** error shape, lives in the shared `domain/envelope.py`):

```jsonc
{
  "apiVersion": "grain.error/v1",       // the only version anchor the error block carries
  "code": "grain.missing_path",         // ∈ VALID_ERROR_CODES (grain.-namespaced)
  "message": "unknown recipe",
  "detail": "no recipe 'foo' under docs/recipes/ or bundled",   // "" → omitted
  "exit_code": 4                         // the int the CLI process exits with; the portable class token
}
```

`to_envelope(exc: ForgeError) -> ErrorEnvelope` and `envelope_to_dict(env)` (stable key order) are
the single construct/serialize path every surface goes through. `__post_init__` asserts
`code ∈ VALID_ERROR_CODES` and that `code`↔`exit_code` match the registry.

`apiVersion: grain.error/v1` is decoupled from `grain.engine/v1` (the frame) and from
`grain_version` (the build) — the error contract can evolve independently. It is the one extra
field beyond the four contract fields `{code, message, detail, exit_code}`; `detail` defaults `""`.

### 4.3 How each surface emits it

- **CLI (`error_handler.handle_error(exc, fmt) -> int`):** `fmt == "text"` (default): unchanged —
  `Error: <message>` (+ indented detail) to **stderr**, return exit code (full human/script back-
  compat). `fmt == "json"`: emit a §3 envelope with `status: "error"` and `error =
  envelope_to_dict(...)` to **stdout** (a familiar capturing stdout gets structured output), process
  still exits with `exit_code`. CLI json errors are *new* (today they are text on stderr regardless
  of `--format`), so this is a pure improvement with no consumer to break. The catch-all wraps non-
  `ForgeError` exceptions as `GeneralError` → `grain.general`, so json mode never emits a bare
  traceback.
- **Recipe engine errors:** the `RecipeEngineError` family already funnels through
  `recipe.py::_drive` → `ForgeError`. **Extract** that inline mapping into a pure
  `recipe_service.engine_error_to_forge(exc) -> ForgeError` so `_drive` **and** the MCP recipe tools
  call the *same* function (resolves the errors↔mcp reconcile note — extract + both call it):

  | engine error | ForgeError | code / exit |
  |---|---|---|
  | `RecipeNotFoundError`, `RunNotFoundError` | `MissingPathError` | `grain.missing_path` / 4 |
  | `MissingParamError`, `GateStateError` | `UsageError` | `grain.usage` / 2 |
  | `RecipeSchemaError`, `RecipeEngineError` (catch-all) | `ValidationError` | `grain.validation` / 3 |

- **MCP (`services/mcp_service.py`):** two **distinct** error axes, never conflated. (1) JSON-RPC
  *transport* errors (`-32700/-32600/-32601/-32602`: malformed request / unknown method / bad
  params) stay protocol-level, unchanged. (2) *Tool-execution* errors replace the untyped
  `{"errors":[...]}` blob: `_err(tool, exc: ForgeError)` builds a §3 envelope with `status: error`,
  the §4.2 error object under `error`, mirrors it as JSON in `content[0].text`, and sets
  `isError: true`. The 5 existing tools' failure paths are retyped (`packet/artifact not found` →
  `MissingPathError`; empty/!str/!int args → `UsageError`; unknown tool → `UsageError`). The
  `exit_code` is carried on MCP too even though no process exits — it is the portable class token, so
  a familiar reading MCP `error.code`/`.exit_code` lands on the exact same taxonomy as a CLI exit
  code. That symmetry is the point.

---

## 5. MCP surface (full drive loop + recipe verbs)

### 5.1 Versioned MCP result = the §3 engine envelope (no separate frame)

Every `tools/call` result carries the **§3 `grain.engine/v1` envelope** inside `structuredContent`,
mirrored as pretty JSON in `content[0].text`, with `isError = (status == "error")`. The tool name
rides in the optional `command` field; `kind` is the discriminator (same as CLI). Helpers replace
today's `_tool_success`/`_tool_error`:

```python
def _ok(tool, kind, data) -> dict:        # status="ok"; isError False
def _gate(tool, kind, data, gate) -> dict: # status="gate"; isError False
def _err(tool, exc: ForgeError) -> dict:   # status="error"; error from exc; isError True
```

**Back-compat break (the one real MCP break):** the 5 existing tools currently put their payload at
`structuredContent` root; under the envelope it moves to `data`, and `ok` moves to `status`.
Acceptable in a 0.5.0 minor because (a) the headless contract is being *established* now, (b) only
5 tools exist, (c) the sole consumer (`apps/grain-mcp`) discards `structuredContent` today. Gated
behind `apiVersion: grain.engine/v1` so future changes are detectable. Call it out in the change
proposal as a one-time pre-1.0 contract break.

### 5.2 serverInfo.version + contract advertisement (resolves X8)

Factor the version resolver out of `cli/__init__.py` into a tiny **`grain/version.py`**
(`get_version()` — `importlib.metadata.version("grain-kit")` with the `pyproject.toml` fallback,
cached). It becomes the **only** version source for: envelope `grain_version`, MCP
`serverInfo.version`, the `grain_capabilities.yaml` `grain_version`, and `grain version`. No
hardcoded version strings anywhere (this retires the stale `"0.3.0-dev"` and forbids re-introducing
hardcoded `"0.5.0"` examples). `initialize` advertises the contract so familiars can negotiate:

```jsonc
"serverInfo": { "name": "grain", "version": "<get_version()>" },
"capabilities": { "tools": { "listChanged": false } },
"instructions": "Drive the loop file-backed: write artifacts to the output_path a tool returns, then call the next tool.",
"_meta": { "grainContractVersion": "1.1", "engineApiVersion": "grain.engine/v1" }
```

### 5.3 Tool registry references the ONE capability registry (resolves X4)

There is **one** capability registry: `domain/capabilities.py::CAPABILITIES` (§6), owned by the
capabilities area. The MCP `McpTool` dataclass does **not** carry its own `since`/registry — it
**references** a capability id and a `write` flag:

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

`tools/list` is a **derived view** of `CAPABILITIES` (filter `surfaces ∋ "mcp"`) joined with these
schemas — not a hand-maintained second source. There is **one** `capabilities_service.py` (§6),
owned by the capabilities area, writing the one `grain_capabilities.yaml`. The MCP area does not
create a competing service or registry.

### 5.4 Tool catalog

Naming: `noun_verb`, 1:1 with the CLI verb it wraps; each tool delegates to the **same service
function** the CLI uses (CLI stays canonical). Drive-loop + recipe tools share
`capability: "workflow_drive"` (the concrete realization of the locked doc's forward-declared
capability). `decision` enums validate against `VALID_DECISIONS = frozenset({"approve","reject"})`;
a bad value → `UsageError` → `grain.usage`.

**Read (no confirmation):** `workflow_next` *(exists)*, `workflow_explain`, `prompt_show`
*(exists)*, `task_list`, `task_show`, `review_summary` *(exists)*, `review_check`,
`office_review_show` *(exists)*, `recipe_list`, `recipe_show`, `recipe_status`,
**`capabilities_list`** (see §5.7), `version_check` (§7).

**Write (single-call, deterministic, non-interactive):** `task_create` (+ `create_task` hidden
alias for one minor cycle), `task_status`, `task_close`, `workflow_run` (see §5.5),
`workflow_reconcile`, `gate_decide`, `recipe_run` (operator mode), `recipe_next`, `recipe_resume`,
`recipe_gate`.

Payloads reuse existing dicts verbatim under `data`: `NextResult.to_dict()` (recipe verbs),
`run.json` `grain.recipe-run/v1` (`recipe_status`), `_definition_to_dict` `grain.recipe/v2`
(`recipe_show`).

### 5.5 The recipe drive loop is file-backed and local-FS-only (resolves C2)

`recipe_run`/`recipe_next` return a `NextResult`; on `prompt_ready` they carry `prompt` +
`output_path` + `inputs`. The familiar's loop: `recipe_run` → write the artifact **itself** to
`output_path` → `recipe_next` → on `awaiting_gate`, `recipe_gate {decision}`. Bytes move through
the filesystem (locked §2/§4.1). **This loop is declared local-FS-only** — the familiar must share
the workspace filesystem. This is consistent with stdio MCP (§5.6) and is why remote/auth MCP is
dropped.

**`workflow_run` agent-spawn check (resolves trace #3):** `workflow_run` is exposed **only if
`run_workflow_step` is a deterministic single call**. If it shells out to an external agent (like
recipe auto-mode), it is **deferred** for the same reason auto-mode is — this must be confirmed at
build time (open decision OD-4). Recipe **auto mode** (`--auto`, agent subprocess) is **CLI-only**,
not exposed over MCP.

### 5.6 HTTP wrapper: pass-through fix; HTTP+auth dropped from canonical (resolves C1)

- **Fix the flattening bug (in scope):** `apps/grain-mcp/main.py::call_tool` returns the MCP result
  verbatim so `structuredContent` + `content` + `isError` survive; `tools/list` and version come
  from the shared registry / `get_version()` (drop the hardcoded FastAPI `version`); JSON-RPC
  protocol errors map to the §4 error shape, not a bare string.
- **HTTP + bearer auth is OUT of canonical scope.** The locked contract §4.3 says "no HTTP or any
  network transport" and §2 says "no auth — same OS user," full stop; the draft's "control channel
  not data channel" distinction is not one the locked doc makes. Reversing a core "never" is a
  **major** bump, not the additive 1.1 this phase makes. Therefore: **stdio MCP is the contract-
  conformant surface**; the FastAPI wrapper remains a **deployment-only, out-of-contract**
  convenience and is **not** promoted to canonical and gets **no** auth feature in Phase 35. The
  drive loop's local-FS requirement (§5.5) also makes remote auth pointless (a remote agent cannot
  write the artifact file). Remote MCP, if ever wanted, is a separate major contract revision.

### 5.7 MCP-only discovery (resolves trace #1)

So an MCP-only familiar can discover capabilities without shelling out, expose a read tool
**`capabilities_list`** that returns the live `CAPABILITIES` registry under `data` (same payload as
the CLI `capabilities` command, §6). This is the only capability-discovery surface needed for MCP
in Phase 35; the `reconcile` verdict verb stays CLI-only/deferred (§6).

### 5.8 The MCP↔CLI boundary for autonomous familiars (resolves trace #2, write-tool consent)

Stated explicitly so a familiar knows the edges:
- **Suggestion acceptance over MCP is deferred.** The SDLC loop's frequent "next action" is "accept
  a suggestion → create a task," fixed for headless **CLI** (§7 `--yes`) but **not** wrapped as an
  MCP write tool in Phase 35. A pure-MCP familiar cannot accept a suggested task; it must drop to
  CLI for `suggest accept`. The autonomous loop therefore works over **MCP + CLI**, not MCP alone.
  Document this boundary; lift it in a later phase once `suggest_accept` carries the §7 gate over MCP.
- **MCP write tools act immediately (no confirmation gate).** Unlike the CLI gate model (§7), MCP
  write tools are deterministic single-call mutations and do **not** emit a `status: gate`. This
  asymmetry is **intended**: the familiar *is* the agent and the gate exists to protect a *human* at
  a terminal; an MCP caller has already decided. (When `suggest_accept` lands over MCP it will be
  the exception that carries the gate, because its whole purpose is "show before creating.")

---

## 6. Capability registry + discovery (reconciled with toolkit_contract.md)

### 6.1 One generated registry, source-of-truth in code

The registry is **generated from code, never hand-maintained**. Source of truth: a frozen tuple in
a new `domain/capabilities.py` (mirroring `mcp_service.TOOLS` and the `VALID_*` + `__post_init__`
idiom). This is the **single** registry (resolves X4) — MCP references into it (§5.3); the YAML file
and `tools/list` are derived views.

```python
CAPABILITY_REGISTRY_API_VERSION = "grain.capabilities/v1"   # the FILE's apiVersion
GRAIN_CONTRACT_VERSION = "1.1"                              # bilateral schema (was 1.0)

VALID_CAP_KINDS:     frozenset = {"read", "write", "discovery"}
VALID_CAP_DRIVE:     frozenset = {"headless", "confirm", "interactive"}
VALID_CAP_STABILITY: frozenset = {"stable", "experimental", "planned"}

@dataclass(frozen=True)
class Capability:
    id: str                      # stable snake_case id, e.g. "workflow_state"
    since: str | None            # semver introduced; None ⇔ stability == "planned"
    kind: str                    # ∈ VALID_CAP_KINDS
    drive: str = "headless"      # ∈ VALID_CAP_DRIVE — the mechanical "is it headless-safe" answer
    stability: str = "stable"    # ∈ VALID_CAP_STABILITY
    command: str | None = None   # canonical CLI invocation; None for planned/file-only
    description: str = ""
    surfaces: tuple[str, ...] = ("cli",)   # ⊆ {"cli","mcp","file"}
    def __post_init__(self): ...  # validate each field against its VALID_* set
```

Adding a capability is a reviewed code change to `CAPABILITIES`; the **file is never edited**. A
familiar filters `drive == "headless"` to get the safe-to-automate set (`suggest_approve` is
`confirm`; `tui` excluded; `workflow_drive` `planned`).

### 6.2 Initial seed (MVP)

`workflow_state` (0.2.0), `workflow_explain` (0.4.0), `task_create` (0.1.0), `task_results_write`
(0.1.0), `verify_submit`/`verify_ingest` (0.3.0), `review_summary` (0.3.0), `context_link` (0.4.0),
`suggest_approve` (0.4.0, **drive: confirm**), `recipe_run`/`recipe_state` (0.5.0, experimental),
`version_check` (0.5.0), `capabilities_list` (0.5.0, discovery), `workspace_list` (0.5.0,
discovery), `workflow_drive` (**planned**, no `since`/`command`). Superset of the locked doc's
example — a v1.0 reader keying on `id/command/since` is unaffected (new keys ignored).

### 6.3 On-disk file (additive over locked §3.2)

`grain init` / `grain upgrade` call `write_capabilities_file(root)` in **one**
`services/capabilities_service.py` (owned here) serializing `CAPABILITIES` + `get_version()` to
`docs/runtime/grain_capabilities.yaml` (exact locked path). New top-level keys `apiVersion:
grain.capabilities/v1` and `grain_contract_version: "1.1"`, plus per-capability
`kind/drive/stability/surfaces` — all additive; v1.0 consumers ignore unknown keys. A `doctor` check
+ `grain capabilities --check` compares the file's `(id, since)` + `grain_version` against the live
registry; drift → `ConfigError` (exit 6) in `--check`, doctor warning otherwise. The file is a
**verifiable cache**, not a rottable source.

### 6.4 CLI surface

```
grain --format json capabilities            # list (kind=CapabilityList) — LIVE from CAPABILITIES
grain capabilities show <id>                # one (kind=Capability)
grain capabilities --check                  # drift check; 0 ok / 6 ConfigError on drift
grain workspace list                        # discovery (kind=WorkspaceList)
grain workspace resolve                     # echo the single resolved workspace + why
```

`capabilities` reads **live from `CAPABILITIES`** (not the file) so a familiar negotiates against
the installed binary, never a stale cache. `workspace list`/`resolve` are a **new group** in
`cli/__init__.py` implementing locked §8 resolution (env → walk-up). **Marker (decision #5):**
the walk-up resolves the workspace via the canonical-marker resolver decided in the
`grain.toml`-as-marker migration (the `grain.toml` vs `docs/runtime/PROJECT_RULES.md` split-brain) —
`workspace list` MUST call that resolver, **not** hardwire `PROJECT_RULES.md`; if that migration
has not landed, `workspace list` ships behind it rather than on the fragile marker. **Resolves C3:** MVP does
env + walk-up only (single active workspace); to avoid silently under-delivering vs locked §8 step 3
("enumerate all linked workspaces"), the payload carries an explicit
`"link_enumeration": "unsupported"` field so a familiar is not misled into thinking one workspace is
all there are. Multi-workspace/link enumeration is deferred (§9).

### 6.5 Reconcile verb — deferred (scoping cut)

`grain capabilities reconcile --contract <path>` (diff a sibling's bilateral `requires:` against the
live registry, return a drivable verdict) is **deferred** — there is no Phase-35 consumer (Assay's
contract is static), and the critique flagged it as over-scoped. When built, its negative verdict
("not drivable") is `status: gate` exit 0 (§3.3), **not** an error — per the ratified philosophy.
Reserve the verb name now.

---

## 7. Non-interactive completeness + version check

### 7.1 One confirmation policy, one gate (uses the §3.3 `gate` status)

Three interactive blockers today: `suggest accept` (`click.confirm` always, even with
`--no-confirm`; JSON refuses), `docs audit --fix` (`--format json` `return`s **before** the fix
block — a silent no-op), `upgrade` (`click.prompt` per file). Flag naming is split-brain
(`--no-confirm` vs `--interactive`).

- **One flag:** add `--yes / -y` ("assume yes to all confirmations") to `suggest accept`, `docs
  audit`, `upgrade`. Keep `--no-confirm` as a **hidden, deprecated alias** of `--yes`. `upgrade
  --interactive` stays for humans, never required headlessly.
- **Invariant:** **JSON mode NEVER calls `click.confirm`/`click.prompt`.** Decision matrix:

  | fmt | `--yes`? | confirm needed? | behaviour |
  |---|---|---|---|
  | text | no | yes | `click.confirm` (today) |
  | text | yes | yes | proceed, no prompt |
  | json | — | no | act, `status: ok` envelope |
  | json | no | yes | emit **`status: gate`** envelope, take NO action, **exit 0** |
  | json | yes | yes | act, `status: ok` envelope |

- **The gate rides the frame's `gate` slot (resolves X3).** A command needing consent it cannot
  prompt for returns its existing dict under `data` and a `ConfirmationGate` under `gate`:

  ```jsonc
  "status": "gate",
  "data": { /* existing command fields: proposal_id, proposed_task_md, ... */ },
  "gate": {
    "action": "suggest.accept",
    "reason": "new_task_packet_create",   // ∈ VALID_CONFIRM_REASONS frozenset
    "prompt": "Create this packet?",
    "preview": { "proposed_task_md": "..." },   // exactly what the human would have seen
    "retry_with": ["--yes"]                       // literal flags to re-invoke headlessly (stateless)
  }
  ```

  `reason ∈ VALID_CONFIRM_REASONS = {new_task_packet_create, active_task_switch, docs_fix_apply,
  upgrade_overwrite_customized}`. `ConfirmationGate` is a frozen dataclass in `domain/confirm.py`
  (`__post_init__` validates `reason`); a CLI helper `gate()` in `cli/confirm.py` centralizes the
  decision so no command hand-rolls `click.confirm` anymore.

- **Per-command:** `suggest accept` (new-task + pick-up) routes through `gate()`; `docs audit --fix`
  moves the fix logic **above** the json early-return, builds the fixable set, gates, and on proceed
  adds `"fixes_applied": [...]` (closes the silent no-op). `upgrade --yes` is **deferred** (§9,
  scoping cut — `upgrade` non-interactive already applies all non-customized updates headlessly;
  consenting to overwrite *customized* files is marginal).

- **Back-compat behaviour changes to ratify in the change proposal:** (1) `suggest accept` pick-up
  JSON exit code **1 → 0** (now a gate, not an error); (2) `suggest accept` new-task can now be
  auto-confirmed via `--yes` (D4 relaxed from "always prompt" to "always *show* + explicit
  consent"). Both are the deliberate headless-completeness fix. (Per §5.8, MCP write tools do not
  carry this gate; it protects humans at a terminal.)

### 7.2 `grain version` + `--check` (v0.5.0 #11) — single command, single shape (resolves X5)

**Ownership resolved:** the non-interactive area **owns the command**; the frame (§3) **wraps it**.
The command is **always-enveloped** (it is new, §3.5). The payload's own
`apiVersion: grain.version/v1` lives **inside `data`** (exactly like `grain.recipe-run/v1` lives
inside `data`) — so the two draft shapes reconcile cleanly: one frame, one payload version.

```jsonc
// grain --format json version --check  →  kind: "VersionInfo"
"data": {
  "apiVersion": "grain.version/v1",
  "installed": "0.5.0",              // from get_version() — never hardcoded
  "install_mode": "uv-tool",
  "python": "3.12.3",
  "latest": "0.5.1",                 // only with --check; null + check_error on network failure
  "update_available": true,
  "upgrade_command": "uv tool upgrade grain-kit",   // derived from install_mode
  "checked_at": "2026-06-28T00:00:00Z",
  "source": "pypi",                  // "pypi" | "cache" | "unavailable"
  "workspace": { "required": "0.4.0", "satisfied": true }   // from upgrade_policy.min_version
}
```

- Three axes deliberately separated: installed-vs-latest (this command, `--check`), installed-vs-
  workspace-required (read-only here, reuses `_enforce_version_gate`), installed-vs-repo-source (that
  is `doctor`/#8, out of scope — link, don't duplicate).
- **Network/cache/escape hatch (resolves C5, stays additive):** new `adapters/pypi.py`
  `fetch_latest(timeout=2.0)` via stdlib `urllib` (no new deps), raising `AdapterError` on failure;
  the caller **catches it** and degrades to `check_error` — **fail-silent, still exit 0**. Cache
  `.grain/version_check.json` daily TTL; `--refresh` forces a hit; `GRAIN_NO_UPDATE_CHECK=1` short-
  circuits all network/cache. `--check` is the only thing that touches the network, only when
  invoked. This is **not** inter-tool transport, so it does not violate locked §4.3 — a package-
  manager freshness check is an explicit, opt-in, flag-gated exception (the critique agreed C5
  stands, unlike C1).
- **Human surface (#11a):** `_maybe_notice_new_release(root)` in the `main()` preamble — **cache-
  read-only** (no network in the hot path), text-mode only (never in `--format json`), non-blocking,
  honours `GRAIN_NO_UPDATE_CHECK`, prints one line. The cache is populated by explicit `grain version
  --check` (a keeper/cron/DAEMON schedules it). No background network refresh from the preamble.
- `version_check` is in the capability registry (§6.2, `since: 0.5.0`); `version_check` MCP tool
  (§5.4) returns the same payload.

---

## 8. MVP slice vs deferred

**Foundational first (build order — resolves the "no area owns the one frame" gap):**

1. **`domain/envelope.py`** (NEW, shared, landed FIRST) — `EngineEnvelope` (tri-state `status`,
   `VALID_ENGINE_KINDS`, `__post_init__`) **+** `ErrorEnvelope` + `to_envelope`/`envelope_to_dict`.
   Owned by the merged errors+envelope area. Everything else imports it.
2. **`grain/version.py`** (NEW) — `get_version()`; the single version resolver, imported everywhere
   (`cli/__init__.py`, MCP, capabilities, version command).
3. **`domain/capabilities.py`** (NEW) — the one `Capability` dataclass + `CAPABILITIES` tuple.

**Then MVP (Phase 35 / 0.5.0):**

- **Envelope:** the dataclass + the one emit helper consumed by all `workflow` and `recipe` JSON
  sites (proves verbatim-`data` wrap end to end); `--envelope` flag + `GRAIN_ENGINE_ENVELOPE` env on
  `ctx.obj`, default bare for legacy sites; new commands always-enveloped.
- **Errors:** `code`/`exit_code` ClassVars on all 7 classes + `VALID_ERROR_CODES` + the
  `EXIT_CODES` consistency assert; format-aware `handle_error`; `engine_error_to_forge` extracted and
  reused by `_drive` + MCP. Round-trip parity tests: every taxonomy class → identical error dict over
  CLI json and MCP; plus **top-level frame parity** tests (CLI↔MCP same `apiVersion`/`kind`/`status`
  shape — the critique noted nothing tested this).
- **MCP:** `grain.engine/v1` envelope helpers (`_ok`/`_gate`/`_err`); typed errors; live
  `serverInfo.version` + `_meta`; read tools (`workflow_next, workflow_explain, prompt_show,
  task_list, task_show, review_summary, review_check, office_review_show, recipe_list, recipe_show,
  recipe_status, capabilities_list, version_check`); write tools (`task_create` + `create_task`
  alias, `task_status, task_close, workflow_run` [if non-spawning, §5.5], `workflow_reconcile,
  gate_decide, recipe_run` [operator], `recipe_next, recipe_resume, recipe_gate`); `McpTool` carries
  `write`+`capability`; `tools/list` derived from `CAPABILITIES`.
- **HTTP wrapper:** pass-through fix + version from registry. **No auth.**
- **Capabilities:** `capabilities_service.py` (`write_capabilities_file`, `load`, `check_drift`);
  `grain init`/`upgrade` write the file; `grain capabilities` (list/show/`--check`); `grain
  workspace list/resolve` (env + walk-up, `link_enumeration: "unsupported"`); `doctor` drift check.
- **Non-interactive:** `domain/confirm.py` + `cli/confirm.py::gate()`; uniform `--yes` (+ hidden
  `--no-confirm`) on `suggest accept`/`docs audit`/`upgrade`; route the blockers through `gate()`;
  fix `docs audit --fix --format json` silent no-op; `status: gate` exit 0.
- **Version check:** `grain version` (+ `--check`/`--refresh`), `adapters/pypi.py`, daily cache,
  `GRAIN_NO_UPDATE_CHECK`, fail-silent; `_maybe_notice_new_release` human one-liner.
- **Spec + change proposal:** this doc; the proposal edits **`toolkit_contract.md`** (1.0→1.1: built
  registry/workspace, `workflow_drive` concrete, new fields), **`cli_spec.md`** (§10 `errors`→`error`
  + envelope; §5 ratify the two exit-code behaviour changes; register `capabilities`/`workspace`/
  `version` groups), and **`recipe_engine_spec.md` §6** (un-defer recipe verbs over MCP).

**Deferred:**

- Migrating the remaining legacy JSON sites (`task *`, `review *`, `suggest *`, `docs audit`,
  `status`, `guard`, `reconcile`) to the helper (mechanical follow-ons); the **0.6.0 default flip**
  and **0.7.0 legacy removal**; `grain.engine/v2` + multi-version `--api` negotiation.
- Pinning each `data` shape's own internal `apiVersion` (workflow/task/review shapes have none).
- `suggest_accept` write tool over MCP (carries the §7 gate) — lifts the §5.8 boundary.
- Recipe **auto mode** over MCP; `workflow_loop` over MCP (multi-step agent orchestration).
- `capabilities reconcile --contract` (no Phase-35 consumer); multi-workspace/link enumeration in
  `workspace list`.
- `upgrade --yes` overwrite-of-customized-files headless path.
- Background/opportunistic network refresh from the preamble; familiar **self-execution** of upgrade
  (Grain only *reports* `update_available`).
- HTTP + bearer auth / remote MCP (a separate **major** contract revision, not this phase).

**Explicitly out of scope:** changing exit codes, changing on-disk artifact versions
(`run.json`/`recipe.yaml` keep their `apiVersion`), and turning the HTTP wrapper into a canonical
network surface.

---

## 9. Design decisions — RESOLVED (2026-06-28)

**All confirmed by the founder ("do recommended"); OD-4 resolved by a code check; decision #5 (marker) baked into §6.4.**

- ✅ **OD-1** confirmed — `grain.`-namespaced error codes.
- ✅ **OD-2** confirmed — tri-state `status: ok | gate | error` (replaces the boolean/XOR).
- ✅ **OD-3** confirmed — stdio MCP only; HTTP wrapper stays deployment-only with no auth; remote MCP is a future major revision.
- ✅ **OD-4 resolved (code check)** — `run_workflow_step` does NOT shell out (no `subprocess`; the agent spawn is only in `workflow loop`), so `workflow_run` is a deterministic single call and **is** exposed over MCP; `workflow loop` stays CLI-only.
- ✅ **OD-5** confirmed — the autonomous loop is MCP+CLI (not MCP-alone) until `suggest_accept`-over-MCP lands in a later phase.
- ✅ **OD-6** confirmed — 0.5.0 opt-in / 0.6.0 default-flip / 0.7.0 legacy removal for legacy JSON sites.
- ➕ **Decision #5 (discovery marker)** — `grain workspace list` consumes the canonical-marker resolver per the `grain.toml` migration, not the fragile `PROJECT_RULES.md` walk-up (see §6.4).

_Original options + rationale retained below for the record._

- **OD-1 — `grain.`-namespaced error codes.** Ratify `grain.validation` (namespaced) over bare
  `validation`. Argument for: familiars operate across sibling tools (Diwa/Scry/Assay) on a shared
  surface, so a bare token is ambiguous. Cost: 7 strings become a locked contract surface. *(Spec
  assumes yes.)*
- **OD-2 — Tri-state `status` over a boolean `ok`.** Confirm replacing `ok` with `status: ok | gate
  | error` (so consent gates and valid-negative answers are exit-0 first-class, not errors). This is
  the central integration fix; it changes `suggest accept` pick-up exit 1→0. *(Spec assumes yes.)*
- **OD-3 — Drop HTTP + auth from canonical; stdio MCP only.** Confirm the HTTP wrapper stays a
  deployment-only, out-of-contract convenience with no auth in Phase 35, and remote MCP is a future
  major revision. The alternative (promote HTTP+auth) is a major contract break and conflicts with
  the local-FS drive loop. *(Spec assumes drop.)*
- **OD-4 — Is `workflow_run` (`run_workflow_step`) a deterministic single call?** If it shells to an
  external agent, defer it from MCP (like recipe auto-mode). Needs a code confirmation before the MCP
  catalog is final.
- **OD-5 — MCP↔CLI autonomy boundary.** Accept that a *pure-MCP* familiar cannot accept suggestions
  in 0.5.0 (must drop to CLI `suggest accept`), i.e. the autonomous loop is MCP+CLI, not MCP-alone,
  until `suggest_accept`-over-MCP lands. Confirm this is acceptable for the first hosted-Apex
  routing.
- **OD-6 — Envelope opt-in vs flip timing.** Confirm 0.5.0 opt-in / 0.6.0 default-flip / 0.7.0
  removal for legacy JSON sites (vs a harder/softer cadence).

---

## 10. Implementation notes (fit Grain's idioms)

- **One shared frame module, landed first:** `src/grain/domain/envelope.py` holds `EngineEnvelope`
  **and** `ErrorEnvelope` + serializers — frozen dataclasses, `VALID_*` frozensets, `__post_init__`
  validation (mirrors `recipe_run.py`/`workflow_loop.py`). MCP, capabilities, non-interactive, and
  the CLI emit sites **import** it; none re-defines a frame or error shape.
- **One version resolver:** `src/grain/version.py::get_version()` (extracted from
  `cli/__init__.py`); the only source for envelope `grain_version`, MCP `serverInfo.version`,
  `grain_capabilities.yaml`, and `grain version`. No hardcoded version strings.
- **One capability registry + service:** `src/grain/domain/capabilities.py::CAPABILITIES` (source of
  truth) + `src/grain/services/capabilities_service.py` (the only writer of
  `docs/runtime/grain_capabilities.yaml`); `McpTool.capability` references ids; `tools/list` is a
  derived view (`surfaces ∋ "mcp"`).
- **One error path:** `error_handler.handle_error(exc, fmt)` is format-aware and the central emit;
  `recipe_service.engine_error_to_forge` is the single engine-error→`ForgeError` map called by both
  `recipe.py::_drive` and the MCP recipe tools.
- **New files:** `domain/envelope.py`, `domain/capabilities.py`, `domain/confirm.py`, `version.py`,
  `services/capabilities_service.py`, `cli/capabilities.py`, `cli/workspace.py`, `cli/confirm.py`,
  `cli/version.py`, `adapters/pypi.py`. **Touched:** `cli/__init__.py` (register `capabilities`/
  `workspace`/`version`; `ctx.obj["envelope"]`/`["kind"]`; import `get_version`), `cli/workflow.py`
  + `cli/recipe.py` (emit via the helper), `cli/error_handler.py` (format-aware + consistency
  assert), `domain/errors.py` (ClassVar codes), `services/mcp_service.py` (envelope helpers,
  registry expansion, typed errors, live version), `services/recipe_service.py`
  (`engine_error_to_forge`), `cli/suggest.py`/`cli/docs.py`/`cli/upgrade.py` (route through
  `gate()`), `apps/grain-mcp/main.py` (pass-through + registry version).
- **Tests:** taxonomy round-trip (every `ForgeError` → identical error dict over CLI json + MCP);
  **frame parity** (CLI↔MCP identical `apiVersion`/`kind`/`status` framing); tri-state
  `__post_init__` (gate/error/ok legality); `docs audit --fix --format json` actually applies and
  reports `fixes_applied`; `grain version --check` fail-silent exit 0 on network failure.
