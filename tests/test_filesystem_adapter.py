import pytest
from pathlib import Path
from forge.adapters.filesystem import find_repo_root, resolve_repo_root


def test_find_repo_root_detects_from_subdirectory(tmp_path):
    marker = tmp_path / "docs" / "runtime" / "PROJECT_RULES.md"
    marker.parent.mkdir(parents=True)
    marker.touch()

    subdir = tmp_path / "src" / "forge"
    subdir.mkdir(parents=True)

    result = find_repo_root(subdir)
    assert result == tmp_path


def test_find_repo_root_detects_from_root_itself(tmp_path):
    marker = tmp_path / "docs" / "runtime" / "PROJECT_RULES.md"
    marker.parent.mkdir(parents=True)
    marker.touch()

    result = find_repo_root(tmp_path)
    assert result == tmp_path


def test_find_repo_root_raises_when_no_marker(tmp_path):
    subdir = tmp_path / "some" / "deep" / "path"
    subdir.mkdir(parents=True)

    with pytest.raises(FileNotFoundError, match="Could not find repository root"):
        find_repo_root(subdir)


def test_resolve_repo_root_uses_explicit_path(tmp_path):
    result = resolve_repo_root(str(tmp_path))
    assert result == tmp_path.resolve()


def test_resolve_repo_root_auto_detects(tmp_path, monkeypatch):
    marker = tmp_path / "docs" / "runtime" / "PROJECT_RULES.md"
    marker.parent.mkdir(parents=True)
    marker.touch()

    monkeypatch.chdir(tmp_path)
    result = resolve_repo_root()
    assert result == tmp_path
