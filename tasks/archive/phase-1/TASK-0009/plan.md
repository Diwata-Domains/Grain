# Plan: TASK-0009

## Recommended Model
- **Primary:** `open_model`
- **Secondary:** `reviewer_model`
- **Reason:** Mechanical task — adding `--version` and subprocess-level smoke tests. No design decisions. `reviewer_model` should confirm all six command groups appear in `abt --help` output and that the version string matches `pyproject.toml`.

## Steps

1. Add `--version` option to `main` Click group in `src/ai_build_toolkit/cli/__init__.py`
   - Use `click.version_option()` with version read from package metadata (`importlib.metadata`)

2. Create `tests/test_smoke.py`:
   - Use `subprocess.run` to invoke `abt` via the `.venv` Python executable
   - `abt --help` exits 0 and output contains all six group names: `init`, `docs`, `task`, `context`, `model`, `review`
   - `abt --version` exits 0 and output contains the version string
   - `abt unknown-command` exits 2
   - `abt docs --help` exits 0
   - `abt task --help` exits 0

## Patch Strategy
- Update: `src/ai_build_toolkit/cli/__init__.py` — add `--version`
- New file: `tests/test_smoke.py`
- No other changes
