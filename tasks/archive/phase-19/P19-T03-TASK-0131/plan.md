# Plan: TASK-0131

## Approach

Add one install service behind the adapter CLI that resolves an explicit package source, validates it with `adapter_package_service`, checks for adapter ID collisions in the current repo, and appends the rendered adapter profile into `docs/runtime/adapter_profiles.md`. Keep handle support local by resolving it against a user-supplied reviewed-registry checkout instead of inventing remote fetch behavior.

---

## Step 1 — Define source resolution and install behavior

Resolve either a direct package directory or a local registry handle plus registry root into one validated package path, then define the exact repo mutation the install command performs.

---

## Step 2 — Implement service and CLI surface

Add the install service plus `grain adapter install` command, enforce explicit input combinations, and surface readable output for successful installs and deterministic failures.

---

## Step 3 — Add focused coverage

Cover local source installs, local registry-handle installs, duplicate adapter rejection, and handle-resolution failures so later registry scaffold work can build on a stable install contract.

---

## Verification

Run focused install service and adapter CLI tests. If the repo `pytest` entrypoint remains unavailable, run direct Python execution checks and note the limitation in `results.md`.
