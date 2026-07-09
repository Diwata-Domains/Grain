# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Document existence validator.

Checks that each path declared in a DocumentRegistry exists on the filesystem
relative to the repository root. Returns a list of error strings.
An empty list means all declared paths exist.
"""

from pathlib import Path

from grain.domain.documents import DocumentRegistry


def validate_doc_existence(registry: DocumentRegistry, root: Path) -> list[str]:
    """Validate that every registered document path exists on the filesystem.

    Args:
        registry: Populated DocumentRegistry from build_registry().
        root: Repository root path.

    Returns:
        List of error strings. Empty list means all paths present.
    """
    errors: list[str] = []
    for record in registry.all():
        if not record.path:
            errors.append(f"Doc '{record.id}': path is empty")
            continue
        if not (root / record.path).exists():
            errors.append(f"Doc '{record.id}': expected path not found: {record.path}")
    return errors
