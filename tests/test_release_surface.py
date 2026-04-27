from pathlib import Path


def test_prompt_indexes_do_not_contain_local_absolute_paths() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    prompt_indexes = [
        repo_root / "prompts" / "README.md",
        repo_root / "src" / "grain" / "data" / "prompts" / "README.md",
    ]

    for path in prompt_indexes:
        content = path.read_text(encoding="utf-8")
        assert "/Users/" not in content
        assert "ai-build-toolkit" not in content


def test_formula_metadata_matches_public_project_identity() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    content = (repo_root / "Formula" / "grain.rb").read_text(encoding="utf-8")

    assert 'homepage "https://github.com/Diwata-Labs/Grain"' in content
    assert 'license "MIT"' in content
