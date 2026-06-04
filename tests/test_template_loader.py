import pytest
from grain.templates.loader import get_template


def test_known_template_returns_content(tmp_path):
    template_dir = tmp_path / "templates" / "tasks"
    template_dir.mkdir(parents=True)
    (template_dir / "task_packet.md").write_text("# Task Template", encoding="utf-8")

    content = get_template("tasks/task_packet.md", tmp_path)
    assert content == "# Task Template"


def test_unknown_template_raises(tmp_path):
    (tmp_path / "templates").mkdir()
    with pytest.raises(FileNotFoundError, match="Template 'tasks/missing.md' not found"):
        get_template("tasks/missing.md", tmp_path)


def test_nested_template_path_resolves(tmp_path):
    template_dir = tmp_path / "templates" / "docs"
    template_dir.mkdir(parents=True)
    (template_dir / "canonical_doc.md").write_text("# Doc Template", encoding="utf-8")

    content = get_template("docs/canonical_doc.md", tmp_path)
    assert "Doc Template" in content
