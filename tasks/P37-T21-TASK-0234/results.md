# Results — P37-T21

## Why this exists

`P37-T13` published the vocabulary at `grain.contracts.workflow`, exactly where spec §5.1 says it
belongs. Then Diwa tried to import it and hit the wall the adversarial pass predicted:

> "Diwa's build-time dependency stays grain-kit — the exact coupling §9 gives as the reason NOT to
> embed grain-kit ('It is a CLI, not a library')."

`grain-kit`'s **mandatory** dependencies are `networkx`, `textual`, `pdfplumber`, `openpyxl`,
`python-docx` and `tree-sitter-language-pack` (hundreds of MB). Diwa is a FastAPI service that wants
six enums and five dataclasses.

## Delivered

`packages/grain-contracts` — a zero-dependency distribution holding the vocabulary, importable as
`grain_contracts.workflow`. `grain/contracts/workflow.py` is now a re-export, so §5.1's address still
resolves and `from grain.contracts.workflow import Run` is unchanged for every existing caller.

This is the first slice of the storage-agnostic `grain-core` that §9 names as the exit criterion for
Diwa's sanctioned temporary Missions runtime: `grain-kit` becomes *a consumer* of the contract rather
than its only shipping vehicle.

## Acceptance

- `importlib.metadata.requires("grain-contracts")` → `['pytest; extra == "dev"']`, no runtime deps.
- `grain.contracts.workflow.Run is grain_contracts.workflow.Run` — an address, not a copy.
- `import grain.cli` pulls neither `grain.contracts.workflow` nor `grain_contracts`.
- `uv run pytest -q` → **1928 passed, 1 xfailed**. `grain status` exits 0.
- The stdlib-only AST test now resolves the source via `grain_contracts.__file__` rather than a
  monorepo-relative path, because `products/grain` is subtree-mirrored to a public repo where
  `packages/` does not exist.

## Release blocker — read before cutting 0.6.0

`grain-kit` 0.6.0 now declares `grain-contracts>=0.1`, which is **not on PyPI**.
`release-python.yml` publishes grain-kit only, so a 0.6.0 release today would ship an uninstallable
package. `grain-contracts` must be published first and the release workflow needs a second target.
Filed as tooling note #10 (high).

Also filed: note #11 — `reconcile --fix` advertises "backlog status sync" but
`packet_backlog_mismatch` reports `fix_available: false`.

## User Review

- **State:** pending
- **Notes:** awaiting `grain review approve P37-T21` then `grain task close`.
