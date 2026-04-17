# Plan: TASK-0089

## Approach

Add a repo-local Homebrew formula that can build Grain from source tarball plus pinned Python resources, then update installation docs to surface Homebrew as a first-class macOS path with validation/troubleshooting continuity.

---

## Step 1 — Add Homebrew Formula

Create `contrib/homebrew/Formula/grain.rb` with project metadata, source URL, checksum, Python dependency, resource blocks, install step, and a functional CLI test.

---

## Step 2 — Update Installation Docs

Update README installation and troubleshooting sections to include Homebrew install/build-from-source usage and failure diagnostics.

---

## Step 3 — Validate and Finalize

Run Homebrew build/install validation and standard Grain docs/task/test validations. Finalize packet and working docs in `review` state.

---

## Verification

- `brew --version`
- `.venv/bin/python -m build --sdist --no-isolation`
- `brew install --build-from-source ./contrib/homebrew/Formula/grain.rb`
- `grain --version`
- `.venv/bin/grain docs validate`
- `.venv/bin/grain task validate --id TASK-0089`
- `.venv/bin/pytest -q`
