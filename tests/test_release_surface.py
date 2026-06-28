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
    assert 'license "Apache-2.0"' in content


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
        assert "grain --format json workflow next" in content or "verification state on disk" in content


def test_packet_first_guardrails_exist_in_shipped_runtime_guidance() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    content = (repo_root / "src" / "grain" / "data" / "runtime" / "context_loading.md").read_text(encoding="utf-8")

    assert "if no active task packet exists yet, stop and create/select one through the workflow before implementation" in content


def test_readme_explains_codex_and_mcp_paths() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    content = (repo_root / "README.md").read_text(encoding="utf-8")

    assert "grain --format json workflow next" in content
    assert "grain --format json mcp manifest" in content
    assert "Codex/tool-execution path: direct CLI" in content
    assert "obsidian_adapter" in content
    assert "database_adapter" in content
    assert "crawler_adapter" in content
    assert "grain verify submit --id TASK-0001" in content
    assert "grain verify ingest --verification-id VERIFY-0001-001 --payload payload.json" in content


def test_runtime_agents_guidance_keeps_cli_canonical_for_desktop_paths() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    content = (repo_root / "docs" / "runtime" / "AGENTS.md").read_text(encoding="utf-8")

    assert "grain --format json workflow next" in content
    assert "grain mcp serve" in content
    assert "The CLI remains canonical even when the MCP wrapper is used." in content
    assert "obsidian_adapter" in content
    assert "database_adapter" in content
    assert "crawler_adapter" in content
    assert "do not continue from chat memory alone" in content
    assert "do not skip `grain verify submit` or `grain verify ingest`" in content
    assert "grain workflow explain" in content
    assert "grain workflow reconcile --dry-run" in content


def test_project_rules_document_packet_local_verification_loop() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    content = (repo_root / "src" / "grain" / "data" / "runtime" / "PROJECT_RULES.md").read_text(encoding="utf-8")

    assert "grain verify submit --id TASK-####" in content
    assert "grain verify status --verification-id VERIFY-####-NNN" in content
    assert "Do not close a task while verification is `pending`." in content
    assert "If the session drifts away from the active packet" in content
    assert "Do not “mentally complete” the verification step in chat." in content
    assert "grain workflow explain" in content
    assert "grain workflow reconcile --dry-run" in content


def test_readme_documents_workflow_explain_and_reconcile_loop() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    content = (repo_root / "README.md").read_text(encoding="utf-8")

    assert "grain workflow explain" in content
    assert "grain workflow reconcile --dry-run" in content


def test_cli_spec_describes_live_assay_verification_bridge() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    content = (repo_root / "docs" / "canonical" / "cli_spec.md").read_text(encoding="utf-8")

    assert "packet-local Assay verification integration" in content
    assert "grain verify ingest" in content
    assert "not manage remote verifier execution" in content


def test_runtime_claude_guidance_mentions_database_review_risks() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    content = (repo_root / "docs" / "runtime" / "CLAUDE.md").read_text(encoding="utf-8")

    assert "database_adapter" in content
    assert "destructive migrations" in content
    assert "schema/query drift" in content
    assert "grain verify submit" in content
    assert "stop and route the finding through the packet review bundle" in content


def test_runtime_claude_guidance_mentions_crawler_review_risks() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    content = (repo_root / "docs" / "runtime" / "CLAUDE.md").read_text(encoding="utf-8")

    assert "crawler_adapter" in content
    assert "robots constraints" in content
    assert "selector brittleness" in content
