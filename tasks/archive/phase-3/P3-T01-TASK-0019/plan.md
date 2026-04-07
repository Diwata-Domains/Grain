# Plan: TASK-0019

## Approach

Single new file. Single public function. No service or adapter involvement.

---

## Step 1 — Create `domain/packets.py`

Create `src/ai_build_toolkit/domain/packets.py`.

Add at the top:
```python
import re
from pathlib import Path

TASK_ID_PATTERN = re.compile(r"TASK-(\d{4})")
```

---

## Step 2 — Implement `next_task_id`

```python
def next_task_id(tasks_root: Path) -> str:
    """Return the next available TASK-#### ID by scanning tasks_root directory names."""
    if not tasks_root.exists():
        return "TASK-0001"

    numbers = []
    for entry in tasks_root.iterdir():
        if entry.is_dir():
            match = TASK_ID_PATTERN.search(entry.name)
            if match:
                numbers.append(int(match.group(1)))

    if not numbers:
        return "TASK-0001"

    return f"TASK-{max(numbers) + 1:04d}"
```

---

## Step 3 — Write tests in `tests/test_task_id.py`

Use `tmp_path` pytest fixture for all filesystem cases.

Test cases:
1. Missing `tasks_root` → `TASK-0001`
2. Empty `tasks_root` → `TASK-0001`
3. Single dir `TASK-0005` → `TASK-0006`
4. Multiple dirs, max `TASK-0018` → `TASK-0019`
5. Dirs with gap (`TASK-0001`, `TASK-0003`) → `TASK-0004`
6. Mixed legacy (`TASK-0001`) and CP-001 (`P3-T01-TASK-0019`) → correct max
7. Non-matching dirs (e.g., `scratch`, `.gitkeep`) → ignored, returns `TASK-0001`

---

## Step 4 — Verify

Run `pytest tests/test_task_id.py -v` and confirm all pass.
Run full suite to confirm no regressions.
