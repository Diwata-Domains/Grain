from click.testing import CliRunner
from grain.cli import main


def test_help_exits_zero():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Grain" in result.output


def test_unknown_group_exits_two():
    runner = CliRunner()
    result = runner.invoke(main, ["unknown-group"])
    assert result.exit_code == 2


def test_repo_version_warning_when_installed_grain_is_too_old(tmp_path):
    manifest = tmp_path / "docs" / "runtime" / "docs_manifest.yaml"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        """
version: 1
project:
  name: test
  type: library
  mode: single_user
  storage: filesystem
  authority_model: explicit_hierarchy
  minimum_grain_version: "99.0.0"
canonical:
  - id: architecture
    path: docs/canonical/architecture.md
    purpose: Defines system structure
    authority: highest
    editable_by_agents: false
    read_when: [always]
working: []
runtime:
  - id: project_rules
    path: docs/runtime/PROJECT_RULES.md
    purpose: rules
    authority: highest_runtime
    editable_by_agents: false
    read_when: [always]
tasks:
  root: tasks/
  packet_files: []
  patch_dir: patches/
  status_values: [draft]
  id_format: "TASK-####"
rules:
  authority_order: [docs/runtime/PROJECT_RULES.md]
  canonical_change_policy:
    direct_agent_edits_allowed: false
    require_human_approval: true
    proposal_location: docs/working/change_proposals.md
  context_policy:
    load_minimum_required_docs: true
    prefer_task_packet_context: true
    avoid_full_repo_context: true
  execution_policy:
    use_task_packets: true
    one_task_one_packet: true
    patch_over_rewrite: true
    preserve_doc_separation: true
  completion_policy:
    require_defined_deliverable: true
    require_results_recorded: true
    require_rule_check: true
""".strip()
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "runtime" / "PROJECT_RULES.md").write_text("", encoding="utf-8")
    (tmp_path / "docs" / "canonical" / "architecture.md").parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "canonical" / "architecture.md").write_text("", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["--repo", str(tmp_path), "docs", "show", "architecture"])
    assert result.exit_code == 0
    assert "requires Grain >=" in result.output
