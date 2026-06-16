# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

from pathlib import Path


def get_template(name: str, repo_root: Path) -> str:
    """Read and return the content of a template file.

    `name` is a relative path within the repo's `templates/` directory,
    e.g. "tasks/task_packet.md" or "docs/canonical_doc.md".

    Raises FileNotFoundError if the template does not exist.
    """
    template_path = repo_root / "templates" / name
    if not template_path.exists():
        raise FileNotFoundError(
            f"Template '{name}' not found at '{template_path}'. "
            f"Ensure the templates directory is initialized."
        )
    return template_path.read_text(encoding="utf-8")
