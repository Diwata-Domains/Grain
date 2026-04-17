# Plan: TASK-0087

## Approach

Install `uv` in the project environment, run `uv tool install` against the local package using isolated tool/home/cache paths, and verify the installed binary works without project-venv activation. Update README install section to reflect verified command paths.

---

## Step 1 — Verify uv Tool Install Compatibility

Run `uv tool install --from . grain` in an isolated environment and validate binary startup via `grain --help` from the installed tool path.

---

## Step 2 — Update Installation Documentation

Update README installation section to make `uv tool install` the recommended path and include fallback editable install steps.

---

## Step 3 — Validate and Finalize Artifacts

Run docs/task/full test validation and update packet/working docs for review handoff.

---

## Verification

- `.venv/bin/uv --version`
- `UV_TOOL_DIR=<local> HOME=<local> .venv/bin/uv tool install --from . grain --force`
- `<local>/grain --help`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0087`
- `.venv/bin/pytest -q`
