
import pytest

from grain.services.task_service import create_packet_directory


def test_create_packet_directory_returns_ok(packet_repo):
    result = create_packet_directory(packet_repo, phase=3, task_num=3)
    assert result.ok


def test_create_packet_directory_assigns_task_id(packet_repo):
    result = create_packet_directory(packet_repo, phase=3, task_num=3)
    assert result.task_id == "TASK-0001"


def test_create_packet_directory_name_format(packet_repo):
    result = create_packet_directory(packet_repo, phase=3, task_num=3)
    packet_dir = packet_repo / "tasks" / f"P3-T03-{result.task_id}"
    assert packet_dir.exists()


def test_create_packet_directory_increments_id(packet_repo):
    create_packet_directory(packet_repo, phase=3, task_num=1)
    result = create_packet_directory(packet_repo, phase=3, task_num=2)
    assert result.task_id == "TASK-0002"


def test_create_packet_directory_creates_required_files(packet_repo):
    result = create_packet_directory(packet_repo, phase=3, task_num=1)
    packet_dir = packet_repo / "tasks" / f"P3-T01-{result.task_id}"
    for filename in ("task.md", "context.md", "plan.md", "deliverable_spec.md"):
        assert (packet_dir / filename).exists(), f"{filename} not found"


def test_create_packet_directory_files_are_nonempty(packet_repo):
    result = create_packet_directory(packet_repo, phase=3, task_num=1)
    packet_dir = packet_repo / "tasks" / f"P3-T01-{result.task_id}"
    for filename in ("task.md", "context.md", "plan.md", "deliverable_spec.md"):
        assert (packet_dir / filename).read_text(), f"{filename} is empty"


def test_create_packet_directory_files_created_list(packet_repo):
    result = create_packet_directory(packet_repo, phase=3, task_num=1)
    # directory + 4 template files
    assert len(result.files_created) == 5


def test_create_packet_directory_respects_existing_packets(packet_repo):
    # Create a packet with a high ID to test that next_task_id picks up correctly
    (packet_repo / "tasks" / "P1-T01-TASK-0010").mkdir()
    result = create_packet_directory(packet_repo, phase=3, task_num=1)
    assert result.task_id == "TASK-0011"


def test_create_packet_directory_missing_template_raises(packet_repo):
    # Remove a required template to trigger FileNotFoundError
    (packet_repo / "templates" / "tasks" / "plan.md").unlink()
    with pytest.raises(FileNotFoundError):
        create_packet_directory(packet_repo, phase=3, task_num=1)


def test_create_packet_directory_phase_zero_padding(packet_repo):
    result = create_packet_directory(packet_repo, phase=1, task_num=9)
    packet_dir = packet_repo / "tasks" / f"P1-T09-{result.task_id}"
    assert packet_dir.exists()


def test_create_packet_directory_double_digit_task_num(packet_repo):
    result = create_packet_directory(packet_repo, phase=3, task_num=13)
    packet_dir = packet_repo / "tasks" / f"P3-T13-{result.task_id}"
    assert packet_dir.exists()
