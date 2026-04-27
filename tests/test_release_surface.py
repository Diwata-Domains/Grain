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


def test_packet_first_guardrails_exist_in_shipped_prompt_assets() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    prompt_pairs = [
        repo_root / "prompts" / "task.execute.md",
        repo_root / "src" / "grain" / "data" / "prompts" / "task.execute.md",
        repo_root / "prompts" / "tasks.next_and_implement.md",
        repo_root / "src" / "grain" / "data" / "prompts" / "tasks.next_and_implement.md",
    ]

    for path in prompt_pairs:
        content = path.read_text(encoding="utf-8")
        assert "active task packet on disk" in content or "packet on disk is the authority" in content


def test_packet_first_guardrails_exist_in_shipped_runtime_guidance() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    content = (repo_root / "src" / "grain" / "data" / "runtime" / "context_loading.md").read_text(encoding="utf-8")

    assert "if no active task packet exists yet, stop and create/select one through the workflow before implementation" in content
