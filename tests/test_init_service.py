import pytest
from pathlib import Path
from forge.services.init_service import init_repo


def test_fresh_init_creates_all_dirs(tmp_path):
    result = init_repo(tmp_path)
    assert set(result.created) == {
        "docs/canonical",
        "docs/working",
        "docs/runtime",
        "tasks",
        "templates/docs",
        "templates/tasks",
        "templates/prompts",
        "src",
        "tests",
    }
    assert result.skipped == []
    assert result.blocked == []
    for rel in result.created:
        assert (tmp_path / rel).is_dir()


def test_existing_dirs_are_skipped(tmp_path):
    (tmp_path / "docs" / "canonical").mkdir(parents=True)
    result = init_repo(tmp_path)
    assert "docs/canonical" in result.skipped
    assert "docs/canonical" not in result.created


def test_dry_run_does_not_write(tmp_path):
    result = init_repo(tmp_path, dry_run=True)
    assert len(result.created) == 9
    for rel in result.created:
        assert not (tmp_path / rel).exists()


def test_all_dirs_present_means_all_skipped(tmp_path):
    init_repo(tmp_path)
    result = init_repo(tmp_path)
    assert result.created == []
    assert result.blocked == []
    assert len(result.skipped) == 9


def test_gitkeep_created_in_new_dirs(tmp_path):
    result = init_repo(tmp_path)
    for rel in result.created:
        assert (tmp_path / rel / ".gitkeep").exists()
