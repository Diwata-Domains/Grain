from pathlib import Path

from scripts.bump_version import bump_pyproject_version, bump_version_tuple


def test_bump_version_tuple() -> None:
    assert bump_version_tuple((1, 2, 3), "patch") == (1, 2, 4)
    assert bump_version_tuple((1, 2, 3), "minor") == (1, 3, 0)
    assert bump_version_tuple((1, 2, 3), "major") == (2, 0, 0)


def test_bump_pyproject_version_updates_version_once(tmp_path: Path) -> None:
    path = tmp_path / "pyproject.toml"
    path.write_text(
        """[project]
name = "grain"
version = "0.1.0"
requires-python = ">=3.11"
""",
        encoding="utf-8",
    )

    old, new = bump_pyproject_version(path, "minor")

    assert old == "0.1.0"
    assert new == "0.2.0"
    content = path.read_text(encoding="utf-8")
    assert 'version = "0.2.0"' in content

