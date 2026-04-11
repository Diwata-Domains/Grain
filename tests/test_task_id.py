from pathlib import Path

import pytest

from grain.domain.packets import next_task_id


def test_next_id_missing_dir(tmp_path):
    tasks_root = tmp_path / "tasks"
    assert next_task_id(tasks_root) == "TASK-0001"


def test_next_id_empty_dir(tmp_path):
    tasks_root = tmp_path / "tasks"
    tasks_root.mkdir()
    assert next_task_id(tasks_root) == "TASK-0001"


def test_next_id_single_packet(tmp_path):
    tasks_root = tmp_path / "tasks"
    tasks_root.mkdir()
    (tasks_root / "TASK-0005").mkdir()
    assert next_task_id(tasks_root) == "TASK-0006"


def test_next_id_multiple_packets(tmp_path):
    tasks_root = tmp_path / "tasks"
    tasks_root.mkdir()
    for name in ["TASK-0001", "TASK-0010", "TASK-0018"]:
        (tasks_root / name).mkdir()
    assert next_task_id(tasks_root) == "TASK-0019"


def test_next_id_with_gap(tmp_path):
    tasks_root = tmp_path / "tasks"
    tasks_root.mkdir()
    (tasks_root / "TASK-0001").mkdir()
    (tasks_root / "TASK-0003").mkdir()
    assert next_task_id(tasks_root) == "TASK-0004"


def test_next_id_legacy_and_new_mixed(tmp_path):
    tasks_root = tmp_path / "tasks"
    tasks_root.mkdir()
    (tasks_root / "TASK-0001").mkdir()
    (tasks_root / "P2-T07-TASK-0016").mkdir()
    (tasks_root / "P3-T01-TASK-0019").mkdir()
    assert next_task_id(tasks_root) == "TASK-0020"


def test_next_id_ignores_non_packet_dirs(tmp_path):
    tasks_root = tmp_path / "tasks"
    tasks_root.mkdir()
    (tasks_root / "scratch").mkdir()
    (tasks_root / ".gitkeep").mkdir()
    (tasks_root / "readme").mkdir()
    assert next_task_id(tasks_root) == "TASK-0001"
