# Deliverable Spec: P35-T09 — Non-interactive completeness

## Required Output

### New Files
- `tasks/P35-T09/task.md` — packet metadata/scope ✓
- `tasks/P35-T09/deliverable_spec.md` — this file ✓
- `src/grain/domain/confirm.py` — `ConfirmationGate` frozen dataclass + `VALID_CONFIRM_REASONS`
- `src/grain/cli/confirm.py` — the `gate()` consent centralizer
- `tests/test_noninteractive.py` — tests (≥ 8)

### Modified Files
- `src/grain/cli/suggest.py` — `--yes`/hidden `--no-confirm`; route accept (new-task +
  pick-up) through `gate()`; ratify pick-up json exit **1 → 0**.
- `src/grain/cli/docs.py` — `--yes`/hidden `--no-confirm`; route `docs audit --fix` through
  `gate()`.
- `src/grain/services/docs_audit_service.py` — move fix logic **above** the json early-return;
  add `fixes_applied`.
- `src/grain/cli/upgrade.py` — `--yes`/hidden `--no-confirm` (uniform flag surface only;
  overwrite-customized deferred).

All new `.py` files start with the SPDX header (Grain was relicensed Apache-2.0):
```python
# SPDX-License-Identifier: MIT
```

## Module contract: `src/grain/domain/confirm.py` (§7.1)

### Constants
```python
VALID_CONFIRM_REASONS: frozenset[str] = frozenset({
    "new_task_packet_create",       # suggest accept — new task packet
    "active_task_switch",           # suggest accept — pick-up / switch active task
    "docs_fix_apply",               # docs audit --fix
    "upgrade_overwrite_customized", # upgrade overwrite of customized file (reserved; deferred)
})
```
`upgrade_overwrite_customized` is reserved in the frozenset per §7.1 but NOT wired this
packet (its consent path is deferred, §8).

### Dataclass (frozen; mirror `domain/recipe_run.py` idiom)
```python
@dataclass(frozen=True)
class ConfirmationGate:
    action: str                              # e.g. "suggest.accept", "docs.audit.fix"
    reason: str                              # ∈ VALID_CONFIRM_REASONS
    prompt: str                              # the human-facing question text
    preview: dict = field(default_factory=dict)        # exactly what the human would see
    retry_with: tuple[str, ...] = ()         # literal flags to re-invoke headlessly (stateless)

    def __post_init__(self) -> None:
        # reason ∈ VALID_CONFIRM_REASONS else raise (naming the value);
        # action and prompt non-empty else raise.

    def to_dict(self) -> dict:
        # stable key order: action, reason, prompt, preview, retry_with
        # retry_with serialized as a list.
```

### `gate` JSON shape (rides the §3.3 `EngineEnvelope.gate` slot)
```jsonc
"status": "gate",
"data":  { /* the command's existing dict, unchanged (e.g. proposal_id, proposed_task_md) */ },
"gate": {
  "action": "suggest.accept",
  "reason": "new_task_packet_create",
  "prompt": "Create this packet?",
  "preview": { "proposed_task_md": "..." },
  "retry_with": ["--yes"]
}
```

## Module contract: `src/grain/cli/confirm.py` (§7.1)

```python
def gate(
    *,
    fmt: str,                 # ctx.obj["fmt"] — "text" | "json"
    assume_yes: bool,         # resolved --yes / --no-confirm
    kind: str,                # the command's §3.2 envelope kind (for the gate envelope)
    data: dict,               # the command's existing result dict (rides envelope.data)
    spec: ConfirmationGate,   # the gate descriptor
) -> bool:
    """Single consent decision point (§7.1). Returns True if the caller should
    PROCEED with the mutation, False if it must STOP without acting.

    INVARIANT: when fmt == "json", NEVER calls click.confirm/click.prompt.

    Decision matrix (§7.1):
      text + assume_yes        -> return True (no prompt)
      text + not assume_yes    -> return click.confirm(spec.prompt)  # human path
      json + assume_yes        -> return True
      json + not assume_yes    -> emit a status:"gate" EngineEnvelope (data + spec.to_dict())
                                  to stdout via the T01 serializer, then return False (exit 0)
    """
```
- The json + not-assume_yes branch builds
  `EngineEnvelope(kind=kind, status="gate", grain_version=get_version(), data=data,
  gate=spec.to_dict(), command=<cmd>)` and prints it through the P35-T04 emit seam (same
  surface as the `status: ok` path). The process exits 0 (the caller returns without acting).
- **ALWAYS-ENVELOPED (§3.5):** this `status: gate` emit and the caller's `status: ok`
  post-action emit are **NOT** governed by T04's `--envelope` opt-in. `gate()` builds and prints
  the frame **unconditionally** (it MUST NOT read `ctx.obj["envelope"]` to decide whether to
  envelope); the T04 flag / `GRAIN_ENGINE_ENVELOPE` env governs ONLY the **pre-existing bare**
  `--format json` output these two sites printed before this packet. A familiar must be able to
  parse the consent gate and its result without opting in. (Cross-cutting rule: NEW emits on
  suggest accept / docs audit are always-enveloped, like all new commands and all MCP results.)
- **Kind tokens (§3.2, T01 `VALID_ENGINE_KINDS`):** callers pass `kind="SuggestionList"` for
  `suggest accept` and `kind="DocsAuditReport"` for `docs audit` — to **both** `gate(kind=...)`
  (the `status: gate` emit) and the proceed-path result `emit(...)` (the `status: ok` emit), so
  the gate and its result share one registered kind per command. These are the two registered
  legacy-site kinds in T01 §3.2; do not invent a new one.
- Callers use the pattern: `if not gate(...): return` so a refused gate neither acts nor
  emits a second envelope.

## CLI signatures & behavior

### `suggest accept` (`cli/suggest.py`)
```
grain [--format text|json] suggest accept <proposal_id> [--yes/-y] [--no-confirm (hidden)]
```
- Both paths route through `gate()` with `kind="SuggestionList"` (§3.2, T01
  `VALID_ENGINE_KINDS`) on both the `status: gate` and `status: ok` emits; both emits are
  ALWAYS-enveloped (§3.5), independent of the `--envelope` opt-in:
  - **new-task** → `ConfirmationGate(action="suggest.accept", reason="new_task_packet_create",
    prompt="Create this packet?", preview={"proposed_task_md": ...}, retry_with=("--yes",))`.
  - **pick-up / active switch** → `reason="active_task_switch"`,
    `prompt="Switch active task to <id>?"`, `retry_with=("--yes",)`.
- Pick-up json exit code is **0** (ratified 1→0): un-consented → `status:"gate"` exit 0;
  `--yes` → `status:"ok"` exit 0.
- `--no-confirm` is a hidden, deprecated alias mapping to `--yes` (one minor cycle).

### `docs audit` (`cli/docs.py` + `services/docs_audit_service.py`)
```
grain [--format text|json] docs audit [--fix] [--yes/-y] [--no-confirm (hidden)]
```
- **Restructure (closes the silent no-op):** in the service/command, the `--fix` apply logic
  moves **above** the `--format json` early-return. New ordering:
  1. compute the audit result + the fixable set (always);
  2. if `--fix`: call `gate()` with `kind="DocsAuditReport"` (§3.2, T01 `VALID_ENGINE_KINDS`)
     and `ConfirmationGate(action="docs.audit.fix", reason="docs_fix_apply",
     prompt="Apply N fix(es)?", preview={"fixable": [...]}, retry_with=("--fix","--yes"))`;
     on proceed, apply the fixes and set `result["fixes_applied"] = [...]`;
  3. emit (text or json) the result with `kind="DocsAuditReport"`.
- Both the `status: gate` and `status: ok` emits here are ALWAYS-enveloped (§3.5), independent
  of the `--envelope` opt-in (which governs only this site's pre-existing bare json output).
- json + `--fix` + not `--yes` → `status:"gate"` envelope, **no writes**, exit 0.
- json + `--fix` + `--yes` → fixes applied, `data["fixes_applied"]` populated, `status:"ok"`.
- `fixes_applied` is a list (e.g. of `{path, rule}` or fixed-file identifiers); empty list
  when `--fix` ran but nothing was fixable.

### `upgrade` (`cli/upgrade.py`) — flag surface only
```
grain upgrade [--interactive] [--yes/-y] [--no-confirm (hidden)]
```
- Add `--yes`/`-y` and hidden `--no-confirm` for uniform flag surface; keep `--interactive`
  for humans. **Do NOT** route the per-file overwrite-of-customized prompt through `gate()` —
  that headless path (`upgrade_overwrite_customized`) is **deferred** (§7.1, §8, §9). The flag
  must parse and not error; existing non-interactive apply-of-non-customized behavior is
  unchanged.

## §7.1 decision matrix (authoritative — every touched command obeys it)

| fmt | `--yes`? | confirm needed? | behaviour |
|---|---|---|---|
| text | no  | yes | `click.confirm` (human, unchanged) |
| text | yes | yes | proceed, no prompt |
| json | —   | no  | act, `status: ok` envelope |
| json | no  | yes | emit `status: gate` envelope, take NO action, **exit 0** |
| json | yes | yes | act, `status: ok` envelope |

## Out of scope for this packet (do NOT build here)
- `upgrade --yes` overwrite-of-customized-files headless consent path (§7.1/§8 Deferred).
- `suggest_accept` write tool over MCP / lifting the §5.8 MCP↔CLI boundary; MCP write tools
  carry NO gate (§5.8) — do not touch `mcp_service.py`.
- Any familiar self-execution of upgrade (Grain only reports / consents, never self-upgrades).
- Redefining `EngineEnvelope`, the `status` tri-state, or a second emit path (owned by
  P35-T01/T04 — import and reuse).
- The §7.2 `grain version --check` work (separate packet); `_maybe_notice_new_release`.
- Migrating other legacy JSON sites to the envelope (§8 Deferred).

## Acceptance Checklist
- [ ] `ConfirmationGate.__post_init__` rejects an invalid `reason` (naming it) and empty
      `action`/`prompt`; all 4 valid reasons construct; `to_dict()` keys are exactly
      `{action, reason, prompt, preview, retry_with}` in stable order.
- [ ] `gate()` json + not-`--yes` emits a `status:"gate"` `grain.engine/v1` envelope to
      stdout (`data` present, `gate` populated, `retry_with` includes `--yes`), returns False,
      exit 0; json + `--yes` returns True (no emit); text + not-`--yes` calls `click.confirm`;
      text + `--yes` returns True without prompting.
- [ ] No `click.confirm`/`click.prompt` is ever called when `fmt == "json"` (asserted via
      monkeypatch/spy in both `suggest accept` and `docs audit --fix`).
- [ ] `grain --format json suggest accept <id>` without `--yes` (new-task) → `status:"gate"`,
      no packet created, exit 0; with `--yes` → packet created, `status:"ok"`, exit 0.
- [ ] `suggest accept` pick-up in json exits **0** (not 1) — `status:"gate"` un-consented,
      `status:"ok"` with `--yes`.
- [ ] `grain --format json docs audit --fix --yes` writes fixes and `data["fixes_applied"]`
      is present/populated; without `--yes` → `status:"gate"`, **no files changed**, exit 0
      (proves the fix block runs above the json early-return — the old silent no-op is gone).
- [ ] `--no-confirm` behaves identically to `--yes` on `suggest accept` and `docs audit`;
      `upgrade --yes`/`--no-confirm` parse without error (overwrite-customized deferred).
- [ ] Text mode unchanged: `suggest accept` / `docs audit --fix` prompt via `click.confirm`
      without `--yes`, proceed without prompt with `--yes`.
- [ ] **Always-enveloped (§3.5):** with `--envelope` / `GRAIN_ENGINE_ENVELOPE` OFF (default-
      bare), the `status: gate` and `status: ok` emits on `suggest accept` and `docs audit
      --fix` are STILL `grain.engine/v1` frames (opt-in governs only the legacy bare output).
- [ ] **Kind tokens (§3.2):** `suggest accept` frames carry `kind == "SuggestionList"`;
      `docs audit` frames carry `kind == "DocsAuditReport"` (both ∈ T01 `VALID_ENGINE_KINDS`)
      on both the gate and ok emits.
- [ ] `uv run pytest tests/test_noninteractive.py` ≥ 8 tests pass; full suite no regressions.

## Test cases to include (`tests/test_noninteractive.py`)
1. `ConfirmationGate`: invalid reason rejected (message names value); empty action/prompt
   rejected; the 4 valid reasons construct; `to_dict()` key order/shape.
2. `gate()` matrix — json/not-yes emits gate envelope + returns False (exit-0 semantics);
   json/yes returns True; text/not-yes → `click.confirm` called; text/yes returns True.
3. json invariant spy: no `click.confirm`/`click.prompt` invoked in json paths.
4. `suggest accept` new-task json: gate (no packet) → exit 0; `--yes` → packet created.
5. `suggest accept` pick-up json: exit 0 (ratified from 1); gate vs `--yes` behavior.
6. `docs audit --fix --format json --yes`: fixes applied, `fixes_applied` populated.
7. `docs audit --fix --format json` (no `--yes`): gate envelope, no files written, exit 0.
8. `--no-confirm` alias parity with `--yes` on `suggest accept` and `docs audit`.
9. `upgrade --yes`/`--no-confirm` parse without error (overwrite-customized not exercised).
10. Text-mode `suggest accept`/`docs audit --fix` still prompt without `--yes`.
11. Always-enveloped (§3.5): with the `--envelope` opt-in OFF (default-bare), the `status:
    gate` and `status: ok` emits on `suggest accept` and `docs audit --fix` are still
    `grain.engine/v1` frames.
12. Kind tokens (§3.2): emitted frames carry `kind == "SuggestionList"` (suggest accept) and
    `kind == "DocsAuditReport"` (docs audit) on both gate and ok emits.
