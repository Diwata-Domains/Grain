# Plan: TASK-0094

## Approach

Implement the `grain onboard` CLI command modeled on `grain init`. The key difference from init: onboard targets an existing repo path (defaulting to cwd), is additive only, and produces a manifest of what was created vs skipped. Service layer handles all filesystem logic; CLI handles output formatting and flag parsing.

---

## Step 1 — Define Domain Types

In `src/grain/domain/onboard.py`:
- `ScaffoldManifest` dataclass with `created: list[str]`, `skipped: list[str]`, `root: str`

---

## Step 2 — Implement `OnboardService`

In `src/grain/services/onboard_service.py`:
- `OnboardService(root: Path)` class
- `scaffold(dry_run: bool = False) -> ScaffoldManifest` method
- Define the canonical directory list: `docs/canonical/`, `docs/working/`, `docs/runtime/`, `tasks/`, `prompts/`
- Define the stub file list with minimal template content (title + DRAFT marker)
- For each dir/file: create if missing, skip and record if exists
- Under `--dry-run`: compute what would be created without writing

---

## Step 3 — Implement `grain onboard` CLI Command

In `src/grain/cli/onboard.py`:
- `@cli.command("onboard")` with options: `path` (argument, default "."), `--dry-run / --no-dry-run`, `--format [text|json]`
- Call `OnboardService(root).scaffold(dry_run=dry_run)`
- Text output: two sections — "Created:" and "Skipped:" with file paths
- JSON output: `{"created": [...], "skipped": [...], "root": "..."}` via `--format json`

---

## Step 4 — Register Command

In `src/grain/cli/__init__.py`:
- Import and register `onboard` command (same pattern as `init`)

---

## Step 5 — Tests

In `tests/test_onboard_cmd.py`:
- Test scaffold on empty temp dir — all canonical dirs and stubs created
- Test scaffold on dir with some files already present — skips existing, creates missing
- Test `--dry-run` — no files written, manifest still correct
- Test `--format json` output structure
- Test `--format text` output shows Created/Skipped sections
- At least 8 tests

---

## Verification

- `.venv/bin/grain onboard --help`
- `.venv/bin/grain onboard /tmp/test-existing-project`
- `.venv/bin/grain onboard /tmp/test-existing-project --dry-run`
- `.venv/bin/grain onboard /tmp/test-existing-project --format json`
- `.venv/bin/pytest -q`
