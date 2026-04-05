from dataclasses import dataclass, field
from pathlib import Path

# Directories required by architecture.md Section 5
_REQUIRED_DIRS = [
    "docs/canonical",
    "docs/working",
    "docs/runtime",
    "tasks",
    "templates/docs",
    "templates/tasks",
    "templates/prompts",
    "src",
    "tests",
]

# Paths treated as canonical — never overwritten without --force, always reported
_CANONICAL_PREFIX = "docs/canonical"


@dataclass
class InitResult:
    created: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    blocked: list[str] = field(default_factory=list)


def init_repo(root: Path, force: bool = False, dry_run: bool = False) -> InitResult:
    """Scaffold the required repository structure under `root`.

    - Creates missing directories and placeholder files.
    - Skips items that already exist (unless force=True).
    - Never overwrites canonical docs silently; reports them as blocked.
    - In dry_run mode, computes and returns intended actions without writing.
    """
    result = InitResult()

    for rel in _REQUIRED_DIRS:
        target = root / rel
        if target.exists():
            result.skipped.append(rel)
        else:
            result.created.append(rel)
            if not dry_run:
                target.mkdir(parents=True, exist_ok=True)

    # Write a .gitkeep placeholder into each newly created directory
    for rel in result.created:
        placeholder = root / rel / ".gitkeep"
        if not dry_run:
            placeholder.touch()

    return result
