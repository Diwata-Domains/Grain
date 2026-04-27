#!/usr/bin/env python3
"""Bump semantic version in pyproject.toml for release workflow use."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

_VERSION_RE = re.compile(r'(?m)^(version\s*=\s*")(\d+)\.(\d+)\.(\d+)(")\s*$')


def bump_version_tuple(version: tuple[int, int, int], part: str) -> tuple[int, int, int]:
    major, minor, patch = version
    if part == "major":
        return major + 1, 0, 0
    if part == "minor":
        return major, minor + 1, 0
    if part == "patch":
        return major, minor, patch + 1
    raise ValueError(f"invalid bump part: {part}")


def bump_pyproject_version(path: Path, part: str) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    match = _VERSION_RE.search(text)
    if match is None:
        raise ValueError("could not locate project version in pyproject.toml")

    current = tuple(int(match.group(idx)) for idx in (2, 3, 4))
    next_version = bump_version_tuple(current, part)

    old = ".".join(str(item) for item in current)
    new = ".".join(str(item) for item in next_version)
    updated = _VERSION_RE.sub(rf'\g<1>{new}\g<5>', text, count=1)
    path.write_text(updated, encoding="utf-8")
    return old, new


def main() -> int:
    parser = argparse.ArgumentParser(description="Bump version in pyproject.toml")
    parser.add_argument(
        "--part",
        choices=("major", "minor", "patch"),
        default="patch",
        help="Semver component to increment (default: patch)",
    )
    parser.add_argument(
        "--path",
        default="pyproject.toml",
        help="Path to pyproject.toml (default: pyproject.toml)",
    )
    args = parser.parse_args()

    old, new = bump_pyproject_version(Path(args.path), args.part)
    print(f"version: {old} -> {new}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

