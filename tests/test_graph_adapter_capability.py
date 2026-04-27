"""Tests for graph-backed adapter capability behavior."""

from pathlib import Path

from grain.adapters.adapter_config import load_adapter_profiles


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_adapter_profiles(root: Path) -> None:
    _write(
        root / "docs" / "runtime" / "adapter_profiles.md",
        """# Adapter Profiles

## 5. Adapter Profiles

### code_adapter
- `adapter_id`: `code_adapter`
- `domain_type`: `code`
- `applies_to`:
  - python
  - backend
- `relevant_file_patterns`:
  - `src/**`
- `test_or_validation_hints`:
  - run focused tests
""",
    )


def test_load_profiles_registers_graph_aware_capabilities(tmp_path: Path):
    _write_adapter_profiles(tmp_path)
    profiles = load_adapter_profiles(tmp_path)
    assert len(profiles) == 1
    cap = profiles[0].get_capabilities()
    signal = cap.detect_scope("add python backend api")
    assert signal.relevant_areas


def test_graph_capability_detect_scope_uses_file_paths_when_available(tmp_path: Path):
    _write_adapter_profiles(tmp_path)
    _write(tmp_path / "src" / "service.py", "def run():\n    return 1\n")
    profiles = load_adapter_profiles(tmp_path)
    cap = profiles[0].get_capabilities()

    signal = cap.detect_scope("update service")
    assert "src/service.py" in signal.file_patterns


def test_graph_capability_analyze_impact_returns_related_files(tmp_path: Path):
    _write_adapter_profiles(tmp_path)
    _write(tmp_path / "src" / "a.py", "def a():\n    return 1\n")
    _write(tmp_path / "src" / "b.py", "def b():\n    return 2\n")
    profiles = load_adapter_profiles(tmp_path)
    cap = profiles[0].get_capabilities()

    impact = cap.analyze_impact(["src/a.py"])
    assert "src/a.py" in impact.affected_files
    assert "src/b.py" in impact.affected_files
    assert "code" in impact.downstream_areas
