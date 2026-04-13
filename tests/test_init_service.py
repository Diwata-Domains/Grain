import yaml

from grain.services.init_service import init_repo

EXPECTED_DIRS = {
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

EXPECTED_SEED_FILES = {
    "docs/runtime/PROJECT_RULES.md",
    "docs/runtime/docs_manifest.yaml",
    "docs/runtime/docs_index.md",
    "docs/runtime/context_loading.md",
    "docs/runtime/agent_profiles.md",
    "docs/runtime/adapter_profiles.md",
    "docs/runtime/workflow_loop.yaml",
    "templates/tasks/task.md",
    "templates/tasks/context.md",
    "templates/tasks/plan.md",
    "templates/tasks/deliverable_spec.md",
    "templates/tasks/results.md",
    "templates/tasks/handoff.md",
    "templates/tasks/task_packet.md",
    "prompts/workflow.onboard.new.md",
    "prompts/workflow.onboard.existing.md",
    "prompts/workflow.init.md",
    "prompts/task.plan.next.md",
    "prompts/task.execute.md",
    "prompts/task.review.md",
    "prompts/task.close.md",
    "prompts/phase.plan.next.md",
    "prompts/phase.review.md",
    "prompts/phase.review_and_close.md",
    "prompts/tasks.plan.next.md",
}


def test_fresh_init_creates_all_dirs(tmp_path):
    result = init_repo(tmp_path)
    assert set(result.created) == EXPECTED_DIRS | EXPECTED_SEED_FILES
    assert result.skipped == []
    assert result.blocked == []
    assert result.updated == []
    for rel in EXPECTED_DIRS:
        assert (tmp_path / rel).is_dir()
    for rel in EXPECTED_SEED_FILES:
        assert (tmp_path / rel).is_file()


def test_existing_dirs_are_skipped(tmp_path):
    (tmp_path / "docs" / "canonical").mkdir(parents=True)
    result = init_repo(tmp_path)
    assert "docs/canonical" in result.skipped
    assert "docs/canonical" not in result.created


def test_dry_run_does_not_write(tmp_path):
    result = init_repo(tmp_path, dry_run=True)
    assert set(result.created) == EXPECTED_DIRS | EXPECTED_SEED_FILES
    assert result.updated == []
    for rel in result.created:
        assert not (tmp_path / rel).exists()


def test_all_dirs_present_means_all_skipped(tmp_path):
    init_repo(tmp_path)
    result = init_repo(tmp_path)
    assert result.created == []
    assert result.updated == []
    assert result.blocked == []
    assert set(result.skipped) == EXPECTED_DIRS | EXPECTED_SEED_FILES


def test_gitkeep_created_in_new_dirs(tmp_path):
    result = init_repo(tmp_path)
    for rel in EXPECTED_DIRS:
        assert (tmp_path / rel / ".gitkeep").exists()


def test_seed_files_are_skipped_when_present(tmp_path):
    init_repo(tmp_path)

    result = init_repo(tmp_path)
    assert "templates/tasks/task.md" in result.skipped
    assert "docs/runtime/PROJECT_RULES.md" in result.skipped


def test_force_overwrites_existing_seed_file(tmp_path):
    init_repo(tmp_path)
    target = tmp_path / "templates" / "tasks" / "task.md"
    original = target.read_text(encoding="utf-8")
    target.write_text("modified", encoding="utf-8")

    result = init_repo(tmp_path, force=True)
    assert "templates/tasks/task.md" in result.updated
    assert target.read_text(encoding="utf-8") == original


def test_dry_run_with_force_reports_update_without_writing(tmp_path):
    init_repo(tmp_path)
    target = tmp_path / "templates" / "tasks" / "task.md"
    target.write_text("modified", encoding="utf-8")

    result = init_repo(tmp_path, force=True, dry_run=True)
    assert "templates/tasks/task.md" in result.updated
    assert target.read_text(encoding="utf-8") == "modified"


# --- adapter selection tests ---


def test_no_adapter_leaves_fields_empty(tmp_path):
    result = init_repo(tmp_path)
    assert result.primary_adapter == ""
    assert result.secondary_adapters == []
    assert result.adapter_warnings == []


def test_valid_primary_adapter_is_accepted(tmp_path):
    result = init_repo(tmp_path, primary_adapter="code_adapter")
    assert result.primary_adapter == "code_adapter"
    assert result.adapter_warnings == []


def test_valid_secondary_adapter_is_accepted(tmp_path):
    result = init_repo(tmp_path, secondary_adapters=["frontend_adapter"])
    assert "frontend_adapter" in result.secondary_adapters
    assert result.adapter_warnings == []


def test_unknown_primary_adapter_generates_warning(tmp_path):
    result = init_repo(tmp_path, primary_adapter="nonexistent_adapter")
    assert result.primary_adapter == ""
    assert any("nonexistent_adapter" in w for w in result.adapter_warnings)


def test_unknown_secondary_adapter_generates_warning(tmp_path):
    result = init_repo(tmp_path, secondary_adapters=["ghost_adapter"])
    assert "ghost_adapter" not in result.secondary_adapters
    assert any("ghost_adapter" in w for w in result.adapter_warnings)


def test_mixed_valid_and_invalid_secondary_adapters(tmp_path):
    result = init_repo(tmp_path, secondary_adapters=["frontend_adapter", "ghost_adapter"])
    assert "frontend_adapter" in result.secondary_adapters
    assert "ghost_adapter" not in result.secondary_adapters
    assert any("ghost_adapter" in w for w in result.adapter_warnings)


def test_adapter_selection_dry_run_does_not_write(tmp_path):
    result = init_repo(tmp_path, dry_run=True, primary_adapter="code_adapter")
    assert result.primary_adapter == "code_adapter"
    assert result.adapter_warnings == []
    # no files written in dry-run
    assert not (tmp_path / "docs" / "runtime" / "PROJECT_RULES.md").exists()


# --- bootstrap tests ---


def test_bootstrap_creates_task_packet(tmp_path):
    result = init_repo(tmp_path, bootstrap=True)
    assert result.bootstrapped_task_id == "TASK-0001"
    assert (tmp_path / "tasks" / "P1-T01-TASK-0001").is_dir()
    assert (tmp_path / "tasks" / "P1-T01-TASK-0001" / "task.md").exists()


def test_bootstrap_creates_current_task_md(tmp_path):
    init_repo(tmp_path, bootstrap=True)
    current_task = tmp_path / "docs" / "working" / "current_task.md"
    assert current_task.exists()
    content = current_task.read_text(encoding="utf-8")
    assert "TASK-0001" in content
    assert "Status: ready" in content


def test_bootstrap_with_primary_adapter_sets_adapter_in_task_md(tmp_path):
    init_repo(tmp_path, bootstrap=True, primary_adapter="code_adapter")
    task_md = tmp_path / "tasks" / "P1-T01-TASK-0001" / "task.md"
    content = task_md.read_text(encoding="utf-8")
    assert "code_adapter" in content
    assert "**Primary Adapter:** code_adapter" in content


def test_bootstrap_without_adapter_leaves_task_md_neutral(tmp_path):
    init_repo(tmp_path, bootstrap=True)
    task_md = tmp_path / "tasks" / "P1-T01-TASK-0001" / "task.md"
    content = task_md.read_text(encoding="utf-8")
    assert "**Primary Adapter:** none" in content


def test_bootstrap_dry_run_reports_without_writing(tmp_path):
    result = init_repo(tmp_path, dry_run=True, bootstrap=True)
    assert result.bootstrapped_task_id == "TASK-0001"
    assert "tasks/P1-T01-TASK-0001" in result.created
    assert not (tmp_path / "tasks" / "P1-T01-TASK-0001").exists()


def test_bootstrap_result_id_reported_in_created(tmp_path):
    result = init_repo(tmp_path, bootstrap=True)
    all_created = " ".join(result.created)
    assert "P1-T01-TASK-0001" in all_created


def test_init_seeds_project_shaped_manifest_without_forcing_cli_docs(tmp_path):
    init_repo(tmp_path)

    manifest_path = tmp_path / "docs" / "runtime" / "docs_manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    canonical_ids = {entry["id"] for entry in manifest["canonical"]}

    assert canonical_ids == {"product_scope", "architecture"}
    assert "cli_spec" not in canonical_ids
    assert "workflow_spec" not in canonical_ids
    assert "data_contracts" not in canonical_ids


def test_init_stamps_minimum_grain_version_into_manifest(tmp_path):
    init_repo(tmp_path)

    manifest_path = tmp_path / "docs" / "runtime" / "docs_manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

    assert manifest["project"]["minimum_grain_version"] != "__GRAIN_VERSION__"
