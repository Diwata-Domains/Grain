# Results — P37-T13

## Delivered

`src/grain/contracts/workflow.py` (was an 82-byte license header): the five-term workflow vocabulary
as types. Enums `Gate`, `RunStatus`, `StepStatus`, `Mode`, `Supervision`, `StopReason`; frozen
dataclasses `Artifact`, `StepSpec`, `Protocol`, `StepRecord`, `Run` with `to_dict`/`from_dict`.
Stdlib only. Not wired into `grain/__init__.py`.

`tests/test_contracts_workflow.py` — 19 tests, all written before the module existed and watched to
fail with `ModuleNotFoundError`.

## What the tests found that the plan had wrong

**The `stop_reason` roster was mis-described.** The design brief said "~20 hardcoded string literals
compared inline". They are not literals — `services/workflow_service.py:22-41` declares twenty named
`STOP_*` constants. The test derives the roster from those declarations, so a new stop reason in the
service fails this test rather than silently escaping the contract.

**Loop reasons are a different vocabulary.** `steps_limit_reached`, `supervision_required`,
`invocation_failed`, `no_state_change` never reach `WorkflowEvaluation.stop_reason`
(`domain/workflow.py:25`); `workflow_loop_service.py:73` puts them into the `workflow loop` command's
JSON `_payload`. They are deliberately excluded from `StopReason`.

**The byte-identical acceptance clause was in the wrong task.** `RecipeRun.to_dict` emits `recipe` /
`recipe_apiVersion` under `grain.recipe-run/v1`; the contract speaks of a `protocol` under
`grain.workflow-run/v1`. A generic `Run` cannot round-trip a recipe `run.json` byte-identically —
that mapping is P37-T17's job, and the obligation was moved there in the backlog.

## Acceptance

- `python -c "import grain.contracts.workflow"` succeeds.
- `import grain.cli` does **not** pull `grain.contracts.workflow` (subprocess-asserted). The demo's
  first command, `grain status`, exits 0.
- `Gate`/`RunStatus`/`StepStatus`/`Mode`/`Supervision` values equal the `VALID_*` frozensets in
  `domain/recipe_run.py:28-42` (parametrized test).
- `StopReason` values equal the twenty `STOP_*` constants, derived from source.
- The module imports only `__future__`, `dataclasses`, `enum`, `typing` (AST-asserted).
- Every `__post_init__` validator has a test; `Run.from_dict(run.to_dict())` is identity.

## Verification

`uv run pytest -q` → **1926 passed, 1 xfailed** (was 1907 + 1). `uv run grain status` → exit 0.
`uv run grain task validate` → ok.

## User Review

- **State:** pending
- **Notes:** awaiting `grain review approve P37-T13` then `grain task close`.
