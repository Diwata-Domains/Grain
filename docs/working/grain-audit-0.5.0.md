# Grain 0.5.0 — Health Audit & Positioning

> **Date:** 2026-06-29 · **Branch:** `chore/grain-audit-and-workspace-sync` · **Subject:** grain-kit 0.5.0 (editable) + the 18-workspace Diwata-Labs fleet
> **Method:** 5 parallel dimension audits (core-health, release-readiness, upgrade-UX, workspace-fleet, tests/CI) → synthesis. Read-only; all findings evidence-backed with file paths.

> ### ⚠ Founder corrections (2026-06-29, post-audit)
> Two audit conclusions are **overridden** by founder knowledge — read these first:
> 1. **`grain-kit` is already published and owned on PyPI.** The §3 "CRITICAL: distribution name taken" finding is **void**. The *only* reason 0.5.0 isn't on PyPI is mechanical: the `grain-v0.5.0` tag was never pushed, and tagging/release runs on **GitHub Actions credits that are currently exhausted** (reset pending). No rename needed.
> 2. **`packages/{identity-kernel, vault-kit, grimoire}` are strictly familiar runtime substrate, not grain.** They should **not** be grain workspaces — the fix is to *remove* their stray `grain.toml`, not `grain init` them (corrects §4's "shell" bucket and the Positioning note about grimoire). They are out of grain's scope entirely.

---

## TL;DR (one-glance health)

- **Grain is functionally solid but not cleanly *publishable*.** ~30k LOC, 33-command Click CLI, clean `cli → services → domain/adapters` layering, 1633 tests collecting cleanly, Apache-2.0 relicense fully done. The software is good.
- **The release was never actually triggered.** `grain-v0.5.0` exists locally but was **never pushed**; the publish pipeline only fires on the tag push, so 0.5.0 has never run through CI→build→PyPI. The package name is fine (`grain-kit` is already published/owned — see Founder corrections); the blocker is purely the unpushed tag + exhausted Actions credits.
- **`grain doctor` is failing fleet-wide** because `products/grain/pyproject.toml` reads version **0.1.0** while installed/tagged is 0.5.0. Confirm and fix this before re-tagging.
- **The fleet is messier than "11 empty shells."** 10 of those 11 hold real product code never `grain init`-ed (they have *no* governance manifest); only `apps/eden` is a true stub. They need `init`, **not** `upgrade`. `products/ledger/grain.toml` uses a malformed legacy schema.
- **Your feature instinct is right and the gap is confirmed:** grain has no staleness check — `doctor`/`status` never compare installed-vs-recorded version, and the one existing hint is a **silent no-op nag loop** (it counts customized files that plain `grain upgrade` then skips). Spec for the fix is in §5.
- **Biggest code-health debt doubles as the most strategically important fix:** the `--format json` machine contract is only honored by 7 of 31 CLI modules (813 ad-hoc `click.echo`). For the familiars direction (below), that *is* the tool API — it matters more than any other refactor.

---

## Positioning: grain as the "builder" in the familiars architecture

The audit was framed "SDLC-first," but the real frame is: **grain is one tool a *familiar* wields — specifically the builder.** Conclave forges familiars; `daemon` is the primary familiar; tools (grain, and presumably scry/diwa/…) are first-class citizens a familiar invokes. That reframing changes what "good" means for grain.

**Strategic recommendation: keep grain a *tool*, not a platform.** The "beyond SDLC" pull is real, but the answer is **not** for grain to become a general agentic/workflow runtime — that is `conclave`/`daemon`'s layer, and duplicating it inside grain would blur the boundary that makes the whole system legible. Grain's identity is *the builder*: deep domain expertise in turning intent into structured, shippable software work. SDLC is grain's expertise; recipes generalize the *mechanism*, not the identity.

Three concrete consequences:

1. **The MCP + structured-JSON seam is the product, for this vision.** A familiar drives grain programmatically, not by reading terminal text. Grain already ships an MCP server (`cli/mcp.py`, `apps/grain-mcp/main.py`) — that's the right seam. But code-health finding #2 (only 7/31 commands use the `print_result/CommandResult` contract) means `--format json` is *not yet a real contract*. **Reframe that refactor from "tech debt" to "the tool API a familiar depends on."** It's the highest-leverage work for where you're going.

2. **Recipes are the delegation interface.** A familiar should not micro-drive grain's per-packet SDLC loop turn-by-turn; it should hand grain a **recipe** and receive structured, resumable results. The `grain.recipe/v2` engine (offline, deterministic, gated, resumable) is exactly the right primitive for agent→tool hand-off. Lean into it: recipes as the familiar↔grain API, and let other tools (scry, diwa) expose their own recipe packs the same way. This is how "tools are first-class citizens" becomes concrete rather than aspirational.

3. **A tool that isn't installable isn't first-class.** For a familiar to *depend on* grain, grain has to be a real, pinnable dependency — which loops straight back to the PyPI blockers in §3. Ship 0.5.0 first; the architecture vision rests on it.

**On the fleet, through this lens:** `daemon` is half-scaffolded and `conclave` isn't grain-managed at all (no `grain.toml`). If familiars are the apex of the system, their own builders should be exemplary grain workspaces — a good early proving ground for the `init`/governance work in §4. The `packages/{identity-kernel, vault-kit, grimoire}` names suggest familiar infrastructure (identity, secrets, capability-book); worth a deliberate decision about whether those are grain-managed products or runtime substrate.

> *Caveat:* this section is grounded in the architecture you described plus what grain's audit revealed — I have not deep-read `daemon`/`conclave` internals. Happy to audit those next to pressure-test the boundary.

---

# Grain 0.5.0 Audit — Lead Synthesis

## 1. Verdict

Grain at 0.5.0 is a substantial, genuinely-working toolkit — a ~30k-LOC, 33-command Click CLI with clean `cli → services → domain/adapters` layering, a real and well-written test suite (1633 tests collected cleanly in 0.45s, ruff passing), and a fully completed, internally-consistent Apache-2.0 relicense. It is *functionally* shippable but *not cleanly publishable*: the actual PyPI release has never been triggered (the `grain-v0.5.0` tag was never pushed), the distribution name `grain-kit` is almost certainly taken, and the install is needlessly heavy (six lazily-imported heavy libs declared as mandatory deps). Underneath, the code carries real-but-bounded rot — an abandoned output abstraction, a tangled triple version-check on the hot path, ~238 copies of context boilerplate, and a phantom `contracts/` layer. The 18-workspace fleet is in worse shape than the "11 empty shells" framing suggests: those shells are live products that were never `grain init`-ed, and the documented upgrade path silently no-ops on the customized-drift workspaces. Nothing is on fire, but there is a clear, finite punch-list standing between this and a trustworthy 0.5.0 release.

## 2. State of grain (0.5.0)

Version metadata is internally coherent: `products/grain/pyproject.toml`, the editable egg-info, the sdist/wheel METADATA, the local tag `grain-v0.5.0` (commit `ff8d06c`), and `CHANGELOG [0.5.0]` (dated 2026-06-28) all agree on 0.5.0. The Apache-2.0 relicense is verifiably complete — `LICENSE`, `LICENSES/Apache-2.0.txt`, `REUSE.toml`, `License-Expression: Apache-2.0` in metadata, SPDX headers on all 135 source files, zero residual AGPL/MIT references.

Two contradictions across dimensions, resolved:
- **The "missing" publish-pypi workflow is not lost.** It was deliberately deleted in `e9f79a7` and centralized into the monorepo-root `.github/workflows/release-python.yml` (triggers on `grain-v*` tag push). The `.github/workflows/` directory holds **23** workflows (incl. `release-python.yml`), not "only `community-adapter-registry-validate.yml`" — that pre-gathered note was about the *product subtree* `products/grain/.github/workflows/`, which is the one with a single file. The `CHANGELOG` 0.4.0 entry still advertises the now-deleted `publish-pypi.yml`; it is stale documentation.
- **`grain doctor` reports 3/4 fail fleet-wide** because `products/grain/pyproject.toml` declares version **0.1.0** while installed/tagged grain is 0.5.0 ("source version (0.1.0) differs from installed (0.5.0)"). Note this is in tension with finding 2.x which reads pyproject as 0.5.0 — the doctor check compares against a source pyproject reading 0.1.0, so **confirm the actual on-disk `version` field before tagging again**; whichever is true, every workspace's doctor output is currently degraded by it.

So: shippable as software, blocked as a release.

## 3. PyPI-publish blockers (checklist)

A clean publish is gated by a chain, roughly in dependency order:

- [x] ~~**(CRITICAL) Distribution name `grain-kit` is almost certainly taken.**~~ **VOID — see Founder corrections.** `grain-kit` is already published and owned on PyPI; no rename or name-claim is needed. (The 6 `importlib.metadata.version("grain-kit")` call sites are still worth consolidating into P35-T02's single resolver, but that's hygiene, not a release blocker.)
- [ ] **(HIGH) Tag never pushed.** `git ls-remote --tags origin` shows only `grain-v0.3.0/0.3.1/0.4.0` — **no `grain-v0.5.0`**. `release-python.yml` only fires on the tag push, so the test→build→publish→mirror pipeline has *never run* for 0.5.0. This is the literal mechanical answer to "why can't I push to PyPI."
- [ ] **(HIGH/install-bloat) Move six mandatory heavy deps to extras** before publishing: `textual`, `pdfplumber`, `python-docx`, `openpyxl`, `networkx`, `tree-sitter`+`tree-sitter-language-pack` (`pyproject.toml:30-40`). Every one is already lazy-imported (`pdf_extractor.py:17`, `graph_service.py:25` + `:103` fallback, `tui/app.py:592`), and `networkx` even ships a fallback engine — so the runtime cost of making them optional is near zero while the install footprint (tree-sitter-language-pack alone is hundreds of MB) drops dramatically. The extras pattern already exists at `pyproject.toml:45-57`.
- [ ] **(MEDIUM) Fix project URLs.** `pyproject [project.urls]` Homepage/Repository/Issues point at `Diwata-Labs/Grain`, but the public mirror is force-pushed to `Diwata-Domains/Grain`. These ship into immutable PyPI metadata → 404 sidebar links.
- [ ] **(MEDIUM) Clean `dist/`.** A stale `grain_kit-0.4.0-py3-none-any.whl` sits alongside the 0.5.0 artifacts. CI builds clean so it's harmless there, but any local `uv publish`/`twine upload dist/*` would upload 0.4.0, and `gh release create … dist/*` would attach it.
- [ ] **(LOW) Pre-flight validation is impossible locally.** `release` extra (`build`, `twine`) is declared but not installed (`python -m twine` → not found). CI never runs `twine check`, so README long-description rendering is never validated before upload. Run `uv sync --extra release && twine check dist/*`.
- [ ] **(LATER) Homebrew formula is a 0.1.0 placeholder.** `Formula/grain.rb:6-11` points at a non-existent `file://…grain-0.1.0.tar.gz` and its own comment says it's not publish-ready. Regenerate against the real 0.5.0 sdist *after* PyPI lands, or mark it explicitly not-an-active-path.

Confirm `PYPI_TOKEN_GRAIN` and `SYNC_TOKEN` secrets exist on `Diwata-Domains/Diwata-Labs` before relying on the tag push, and check the Actions run history to see whether prior tags failed at the publish step (consistent with the name being blocked).

## 4. Workspace fleet (the 18-workspace reality)

The fleet splits into four buckets, and **the suggested "bulk `grain upgrade --add-missing`" is wrong for the largest bucket.**

| Bucket | Workspaces | Reality | Correct tool |
|---|---|---|---|
| Fully current | `products/diwa`, `products/scry` | Clean, `diwa` even has the AGENTS grain block | none |
| "Empty shells" (11) | `apps/{diwa-web,eden,gateway,sanctum}`, `packages/{grimoire,identity-kernel,vault-kit}`, `products/{atlas,chronicle,key,ledger}` | **Not empty** — 10 hold real product code (15–44 src files); only `apps/eden` is a true 0-code stub. **None has `docs/runtime/` at all**, so no manifest/governance. | `grain init` (NOT upgrade) |
| Half-scaffolded (2) | `apps/apex`, `products/daemon` | Have manifest + 3 runtime docs, but missing 25 managed + 8 seed files AND have 2 drifted files AND no AGENTS block | `upgrade --add-missing` → `--interactive` → `init --update-agents` |
| Customized-drift (3) | `.` (root), `products/lore`, `products/grain` | Stale files are user-edited; plain upgrade is a **silent no-op** | `upgrade --diff` → `--interactive` |

Two root causes make the "obvious" bulk upgrade wrong:
1. `docs_manifest.yaml` is in the **PROTECTED** set (`upgrade_service.py:170`), so `grain upgrade --add-missing` will *never* create it; and `write_upgrade_policy_min_version()` returns False when the manifest is absent (`upgrade_service.py:184-185`), so the ratchet silently no-ops and the shell stays ungoverned. Only `grain init` creates `docs_manifest.yaml`/`adapter_profiles.md` (confirmed via `grain --repo apps/eden init --dry-run`).
2. Customized files land in `skipped_customized` in non-interactive mode (`upgrade_service.py:141-145`), so root/lore/grain report the files as `updated` but write nothing. Confirmed live: root `skipped_customized == updated == [results.md, PROJECT_RULES.md, context_loading.md]`.

Also: **`products/ledger/grain.toml` is a malformed legacy schema** (`[workspace]`/name/type/port instead of `[project]`+`[paths]`); init warns "project name not set" and will mis-substitute the `[Your Project Name]` placeholder.

**Ordered remediation sequence** (all dry-run first, never `--force` in a loop, never bulk non-interactive on drift workspaces):

```
# Phase 1 — verify clean baseline (expect [] [])
for ws in products/diwa products/scry; do
  .venv/bin/grain --repo $ws upgrade --dry-run --format json; done

# Phase 2 — empty shells: grain init WITH explicit name (NOT upgrade)
for ws in apps/diwa-web apps/eden apps/gateway apps/sanctum \
          packages/grimoire packages/identity-kernel packages/vault-kit \
          products/atlas products/chronicle products/key; do
  n=$(basename $ws)
  .venv/bin/grain --repo $ws init --name $n --type product --dry-run; done
# review, then re-run WITHOUT --dry-run, WITHOUT --force  (init skips existing files)
# ledger first: migrate grain.toml to [project]+[paths] (or pass --name ledger), then init

# Phase 3 — half-scaffolded apex/daemon (two-step + agents)
for ws in apps/apex products/daemon; do
  .venv/bin/grain --repo $ws upgrade --add-missing            # 25+8 files, 0 overwrite risk
  .venv/bin/grain --repo $ws upgrade --diff                   # review the 2 drifted
  .venv/bin/grain --repo $ws upgrade --interactive            # reconcile
  .venv/bin/grain --repo $ws init --update-agents; done       # AGENTS grain block

# Phase 4 — customized-drift: root, lore, grain (NEVER bulk non-interactive)
for ws in . products/lore products/grain; do
  .venv/bin/grain --repo $ws upgrade --diff; done             # review per workspace
# then per-workspace: .venv/bin/grain --repo $ws upgrade --interactive  (manual merge)
# root also: .venv/bin/grain --repo . upgrade --add-missing   (6 absent seed files)
```

## 5. The staleness / auto-update feature

**The user's literal question — "does grain make you update the workspace when there's an update?" — is answered NO.** All three existing version mechanisms in `cli/__init__.py` only guard the *opposite* direction (installed grain **<** workspace requirement, i.e. too-old-grain protection): `_maybe_warn_if_grain_outdated` (`:79-120`), `_enforce_version_gate` (`:126-205`, returns early at `:153` when `current >= required`), `_maybe_warn_if_upgrade_needed` (`:235-259`). Neither `doctor_service.run_doctor()` (checks dict at `:64-72` compares installed grain to the *source* pyproject, never to the workspace's recorded `upgrade_policy.min_version`) nor `status._gather_state()` (`status.py:62-88`) ever compares installed-vs-recorded. Live proof: root records `min_version 0.4.0`, lore records `0.3.1`, installed is 0.5.0, yet `grain --repo . doctor` prints "4/4 pass ✓".

Worse, the one hint that *does* exist is a **silent no-op nag loop**: `_maybe_warn_if_upgrade_needed` counts staleness as `len(updated)+len(added)` — which *includes* the customized files — and says "Run `grain upgrade`", but plain `grain upgrade` skips exactly those files, so the hint reprints next command, forever. And it's off by default (`GrainConfig.upgrade_check` defaults `silent` at `manifest.py:58,96`; only root opted into `warn`), so most workspaces get no signal at all.

**Spec — proposed staleness check:**

- **New primitive** `check_staleness(root, installed_version) -> StalenessReport` in `upgrade_service.py`, reusing tested code: `load_upgrade_policy(root)` for `min_version`/`min_version_set_at`, and `upgrade_repo(root, dry_run=True, include_diffs=True)` for file drift. Hoist `_parse_semver` out of `cli/__init__.py` into a shared util.
- **Report fields:** `installed_version`, `recorded_version`, `recorded_at`, `version_behind` (semver: installed > recorded), `stale_files` (count, **minus** `skipped` to avoid double-counting), `customized_skipped` (`len(skipped_customized)`), `skipped_paths`.
- **Critical design constraint:** pair the version comparison with the file-drift scan — never rely on `min_version` alone. The ratchet (`upgrade_service.py:174-245`) bumps `min_version` to installed on every upgrade *unconditionally*, independent of which files were actually written, so a pure version check goes quiet immediately after `grain upgrade` even while customized files on disk remain stale.
- **CTA fix (resolves the loop):** report stale-applyable vs customized-skipped **separately**; when all stale files are customized, route to `grain upgrade --interactive`/`--diff`, **never** plain `grain upgrade`.
- **Wiring:** add to `doctor_service.run_doctor` (`workspace_recorded_version`, `workspace_version_behind`, `managed_files_stale`, `managed_files_customized_skipped`, a new `checks['workspace_current']`) rendered under a new "Upgrade" section — doctor is the right home (it's in `_VERSION_GATE_BYPASS`, always runs). Add a one-line warn to `grain status` Install line (e.g. `grain 0.5.0 (editable)  ⚠ workspace last upgraded 0.4.0  → grain upgrade --interactive`).
- **Performance:** the existing hint already runs a full `upgrade_repo(dry_run=True)` tree scan on *every* command when enabled (`cli/__init__.py:249-250`). Short-circuit on the cheap version comparison first, and cache the drift result into `.grain/` (precedent: `status.py:91-146`).
- **Defaults & enforcement:** flip `GrainConfig.upgrade_check` default `silent → warn` (matches the bundled template `data/runtime/docs_manifest.yaml:16`). Add `grain upgrade --check` / `doctor --check` that exits non-zero when behind/stale, for CI. **Do NOT auto-write** — that would clobber user-customized content and violate the protected/additive model.

## 6. Top maintainability / code-health issues (ranked)

1. **(HIGH) Dependency surface** — six mandatory-but-lazy heavy libs; covered in §3, top shipping risk.
2. **(HIGH) Output abstraction abandoned mid-adoption** — `cli/output.py` `print_result/CommandResult` is the canonical text|json contract but only **7 of 31** CLI modules use it; the other 24 hand-roll **813** `click.echo` and **101** inline `json.dumps`/`fmt == "json"` branches. The documented `--format json` machine contract has no schema guarantee — fragile for downstream tooling. *(See Positioning: this is the familiar-facing tool API.)*
3. **(HIGH) ~238 copies of repo/fmt boilerplate, no decorator** — every subcommand repeats `repo = ctx.obj.get("repo")…` / `fmt = ctx.obj.get("fmt"…)`, and `resolve_repo_root` is called **108×** in `cli/`. No `@grain_command`/`@pass_repo` decorator. (Fix #2 and #3 together.)
4. **(HIGH) Triple version-check tangle on the hot path** — `cli/__init__.py:294-302` chains three checks using **two manifest keys for the same concept** (`project.minimum_grain_version` vs `upgrade_policy.min_version` — dual source of truth), one of which runs a **full filesystem dry-run scan on every invocation**, all wrapped in broad `except: return` so failures are silent. Consolidate into one function, one key, off the hot path. (Directly intersects §5.)
5. **(MEDIUM) Broad exception swallowing on startup** — 95 `except Exception`, ~32 silent; densest in the version machinery, so a malformed manifest/date silently disables version enforcement with no diagnostic.
6. **(MEDIUM) God-modules + service sprawl** — `docs_audit_service.py` 1419 LOC, `context_service` 1098, `suggest_service` 1071, `recipe_service` 1063; plus 5 `workflow_*` + 4 `task_*` services, with `workflow_service` imported by **14** modules (highest change-blast-radius).
7. **(MEDIUM) Service layer leaks into Click** — `docs_audit_service.py:193-194` imports `click` and calls `click.confirm()` mid-service; interactivity belongs in the cli layer via a passed-in callback.
8. **(LOW) Dead `contracts/` package** — `src/grain/contracts/__init__.py` is 3 license-only lines, imported nowhere; real contracts live in `domain/`. Misleads anyone navigating the advertised `cli/services/adapters/contracts/tui` structure.
9. **(LOW) Incomplete Forge→grain rename** — 36 refs across 9 files incl. the **public** base exception `ForgeError` (`domain/errors.py:11`, caught by name in cli). Rename to `GrainError` with a deprecation alias.
10. **(LOW) No `grain.__version__`; `version("grain-kit")` duplicated across 6 modules** — planned `src/grain/version.py` (P35-T02) doesn't exist yet. A rename (likely per §3) would otherwise touch all 6 sites.

## 7. Tests & CI gaps

The suite itself is a **strength** — 1633 tests / 157 files collect cleanly in 0.45s with zero errors; sampled tests are genuine behavior tests (DI fakes for OpenAI/Ollama, no live network; ~20 real state-machine cases in `test_workflow_state_service.py`; realistic tmp_path repos in `conftest.py`). The holes are in the *plumbing*:

- **(HIGH) Zero coverage visibility** — no `pytest-cov`, no `[tool.coverage]`, no `--cov` in any workflow. 1633 tests run with completely unknown coverage and no gate; a regression in an untested branch (TUI path, an `upgrade_service` error branch) passes CI silently. Biggest regression-escape hole for a to-be-published package.
- **(MEDIUM) Single-Python CI** — package advertises 3.11/3.12/3.13 (`requires-python >=3.11`) but `ci-grain.yml` has no matrix and `.python-version` pins 3.12. 3.11/3.13-specific breakage in the textual/tree-sitter/pdfplumber paths ships untested.
- **(MEDIUM) Stale orphaned release lockfile** — `products/grain/uv.lock` pins `grain-kit 0.1.7` (vs pyproject 0.5.0) and drives `release-python.yml`'s `cache-dependency-glob`, while CI (`ci-grain.yml`, run from root) correctly uses the root workspace lock. Release resolves differently from CI — a latent divergence. Delete/regenerate it and point the release cache key at the root lock.
- **(LOW) Shallow lint** — `uvx ruff check .` with **no `[tool.ruff]` config** = default F/E only (no import-sort I, bugbear B, pyupgrade UP); no `ruff format --check`. "All checks passed" overstates coverage.
- **(LOW) CHANGELOG points at deleted `publish-pypi.yml`** (see §2).
- **(LATER) No scheduled CI run** — `ci-grain` only triggers on `products/grain/**` changes, so an upstream transitive-dep regression (textual/pdfplumber/tree-sitter) goes undetected until the next code change.

## 8. Prioritized action list

| Action | Priority | Effort | Why |
|---|---|---|---|
| Resolve PyPI name `grain-kit` (claim or rename, e.g. `diwata-grain-kit`); propagate to pyproject, README, Formula, 6 `version()` sites | **now** | M | True gate; project-scoped token can't publish an owned name (org already renamed `pulse-kit`) |
| Split 6 heavy lazy deps into extras (`[tui]`/`[office]`/`[scan]`) with clear "pip install …[office]" errors | **now** | M | Already lazy-imported w/ fallbacks; massive install-footprint drop at ~zero runtime cost; pre-publish |
| Fix `pyproject [project.urls]` to `Diwata-Domains/Grain` | **now** | S | Wrong links ship into immutable PyPI metadata → 404s |
| Reconcile `pyproject` version vs installed (0.1.0 vs 0.5.0) so doctor stops failing fleet-wide; then push `grain-v0.5.0` tag | **now** | S | Tag never pushed = pipeline never ran; version mismatch degrades every workspace's doctor |
| Add `check_staleness()` primitive + wire into `doctor`/`status`; fix the customized-skip no-op nag CTA (→ `--interactive`) | **now** | M | Directly answers the user's question; kills the confirmed silent nag loop on root/lore |
| Fleet Phase 2: `grain init` (not upgrade) the 11 shells; migrate `ledger/grain.toml` schema | **now** | M | Only init creates the PROTECTED manifest; upgrade leaves them governance-less |
| Add `pytest-cov` + coverage gate (baseline, ratchet up) | **now** | S | 1633 tests with no coverage signal is the largest regression-escape hole pre-publish |
| Add Python 3.11/3.12/3.13 CI matrix (test + pre-publish steps) | **now** | S | Advertises 3 versions, exercises 1; version-specific breakage ships to users |
| Introduce `@grain_command` decorator + migrate all CLI to `print_result/CommandResult` | **now** | L | Kills ~238 boilerplate copies + 108 ad-hoc resolves; makes `--format json` a real contract (the familiar-facing tool API) |
| Clean `dist/` (drop 0.4.0 wheel) + `uv sync --extra release` + `twine check dist/*` pre-flight | **soon** | S | Manual publish would upload 0.4.0; long-description rendering never validated |
| Consolidate the 3 version checks → one function, one manifest key, off the hot path | **soon** | M | Removes dual source of truth + per-command filesystem diff; lets failures surface |
| Fleet Phases 3–4: apex/daemon two-step; root/lore/grain `--diff`→`--interactive` | **soon** | M | Non-interactive bulk is a silent no-op on drift workspaces |
| Delete orphaned `products/grain/uv.lock`; point release cache at root lock | **soon** | S | Release resolves differently from CI (0.1.7 vs 0.5.0) |
| Flip `GrainConfig.upgrade_check` default `silent → warn` | **soon** | S | Most workspaces get zero staleness signal; template already intends warn |
| Add `[tool.ruff]` (I/B/UP) + `ruff format --check`; delete dead `contracts/`; finish Forge→grain rename (`ForgeError`→`GrainError` alias) | **soon** | S | Broader lint coverage; removes phantom layer + stale public branding |
| Add `grain upgrade --check` exit-non-zero for CI; land `src/grain/version.py` single resolver (P35-T02) | **later** | M | CI enforcement hook without unsafe auto-write; one home for the (renamed) package name |
| Break up >1000-LOC god services; move `click.confirm` out of `docs_audit_service` via callback | **later** | L | Cuts change-blast-radius on the 14-importer workflow hub; restores cli→service direction |
| Fix Homebrew `Formula/grain.rb` (real 0.5.0 sdist url+sha) post-publish; correct CHANGELOG publish-path entry; add scheduled CI run | **later** | M | Advertised `brew install` fails; docs point at deleted workflow; catches upstream-dep regressions |
