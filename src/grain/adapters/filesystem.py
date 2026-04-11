from pathlib import Path

# The presence of this file identifies a valid Forge repository root.
_REPO_MARKER = "docs/runtime/PROJECT_RULES.md"


def find_repo_root(start: Path) -> Path:
    """Walk upward from `start` until the repository root marker is found.

    Raises FileNotFoundError if no marker is found before reaching the filesystem root.
    """
    current = start.resolve()
    while True:
        if (current / _REPO_MARKER).exists():
            return current
        parent = current.parent
        if parent == current:
            raise FileNotFoundError(
                f"Could not find repository root. "
                f"No '{_REPO_MARKER}' found in '{start}' or any parent directory."
            )
        current = parent


def resolve_repo_root(repo_option: str | None = None) -> Path:
    """Return the repository root path.

    Uses `repo_option` directly if provided, otherwise auto-detects from cwd.
    """
    if repo_option is not None:
        return Path(repo_option).resolve()
    return find_repo_root(Path.cwd())
