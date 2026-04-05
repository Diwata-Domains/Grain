"""Task service — packet directory creation and lifecycle operations."""

from pathlib import Path

from forge.cli.output import CommandResult
from forge.domain.packets import (
    TASK_ID_PATTERN,
    PacketRecord,
    find_packet_dir,
    next_task_id,
    read_packet_record,
    write_packet_status,
)
from forge.templates.loader import get_template
from forge.validators.packet_validator import (
    validate_closure,
    validate_packet,
    validate_status_transition,
)

_REQUIRED_TEMPLATES = [
    "tasks/task.md",
    "tasks/context.md",
    "tasks/plan.md",
    "tasks/deliverable_spec.md",
]


def create_packet_directory(
    root: Path, phase: int, task_num: int, title: str = ""
) -> CommandResult:
    """Create a new packet directory under tasks/ with required template files.

    Allocates the next available TASK-#### ID, constructs a P<N>-T<NN>-TASK-####
    directory name, creates the directory, and populates it with the four required
    template files (task.md, context.md, plan.md, deliverable_spec.md).

    Returns:
        CommandResult with ok=True, task_id set, and files_created populated on
        success. ok=False with errors on failure.
    """
    tasks_root = root / "tasks"
    task_id = next_task_id(tasks_root)
    dir_name = f"P{phase}-T{task_num:02d}-{task_id}"
    packet_dir = tasks_root / dir_name

    if packet_dir.exists():
        return CommandResult(
            ok=False,
            command="task create",
            errors=[f"packet directory already exists: {packet_dir.relative_to(root)}"],
        )

    packet_dir.mkdir(parents=True)

    files_created = [str(packet_dir.relative_to(root))]

    for template_name in _REQUIRED_TEMPLATES:
        content = get_template(template_name, root)
        filename = Path(template_name).name
        if filename == "task.md":
            content = content.replace("TASK-####", task_id)
            if title:
                content = content.replace("[Title]", title)
        dest = packet_dir / filename
        dest.write_text(content, encoding="utf-8")
        files_created.append(str(dest.relative_to(root)))

    return CommandResult(
        ok=True,
        command="task create",
        repo=str(root),
        task_id=task_id,
        files_created=files_created,
    )


def list_packets(root: Path) -> tuple[CommandResult, list[PacketRecord]]:
    """Scan tasks/ and return a sorted list of PacketRecords.

    Directories without a valid TASK-#### segment are ignored.
    Directories missing task.md are skipped with a warning.

    Returns:
        (CommandResult, list[PacketRecord]) — result is ok=True even when
        tasks/ is empty or absent. Warnings are populated for unreadable packets.
    """
    tasks_root = root / "tasks"

    if not tasks_root.exists():
        return CommandResult(ok=True, command="task list", repo=str(root)), []

    packet_dirs = sorted(
        (d for d in tasks_root.iterdir() if d.is_dir() and TASK_ID_PATTERN.search(d.name)),
        key=lambda d: int(TASK_ID_PATTERN.search(d.name).group(1)),
    )

    records: list[PacketRecord] = []
    warnings: list[str] = []

    for packet_dir in packet_dirs:
        try:
            records.append(read_packet_record(packet_dir))
        except FileNotFoundError:
            warnings.append(f"{packet_dir.name}: task.md not found, skipped")

    return CommandResult(
        ok=True,
        command="task list",
        repo=str(root),
        warnings=warnings,
    ), records


_ALL_PACKET_FILES = (
    "task.md",
    "context.md",
    "plan.md",
    "deliverable_spec.md",
    "results.md",
    "handoff.md",
)


def validate_one_packet(root: Path, task_id: str) -> CommandResult:
    """Validate required files and metadata for one packet.

    Returns ok=False with errors when the packet is not found or fails validation.
    """
    packet_dir = find_packet_dir(root / "tasks", task_id)
    if packet_dir is None:
        return CommandResult(
            ok=False,
            command="task validate",
            errors=[f"packet '{task_id}' not found"],
        )
    errors = validate_packet(packet_dir)
    return CommandResult(
        ok=not errors,
        command="task validate",
        repo=str(root),
        task_id=task_id,
        errors=errors,
    )


def validate_all_packets(root: Path) -> CommandResult:
    """Validate all packets found under tasks/.

    Each error is prefixed with the packet directory name.
    Returns ok=True when tasks/ is empty or absent.
    """
    tasks_root = root / "tasks"
    if not tasks_root.exists():
        return CommandResult(ok=True, command="task validate", repo=str(root))

    packet_dirs = sorted(
        (d for d in tasks_root.iterdir() if d.is_dir() and TASK_ID_PATTERN.search(d.name)),
        key=lambda d: int(TASK_ID_PATTERN.search(d.name).group(1)),
    )

    all_errors: list[str] = []
    for packet_dir in packet_dirs:
        for err in validate_packet(packet_dir):
            all_errors.append(f"{packet_dir.name}: {err}")

    return CommandResult(
        ok=not all_errors,
        command="task validate",
        repo=str(root),
        errors=all_errors,
    )


def close_packet(root: Path, task_id: str) -> CommandResult:
    """Attempt closure of a packet after running all closure validation checks.

    Runs validate_closure(); if all checks pass, transitions status to 'done'.

    Returns:
        CommandResult with ok=True and status='done' on success.
        ok=False with errors when packet not found or closure validation fails.
    """
    packet_dir = find_packet_dir(root / "tasks", task_id)

    if packet_dir is None:
        return CommandResult(
            ok=False,
            command="task close",
            errors=[f"packet '{task_id}' not found"],
        )

    errors = validate_closure(packet_dir)
    if errors:
        return CommandResult(
            ok=False,
            command="task close",
            errors=errors,
        )

    write_packet_status(packet_dir, "done")

    return CommandResult(
        ok=True,
        command="task close",
        repo=str(root),
        task_id=task_id,
        status="done",
        files_updated=[str((packet_dir / "task.md").relative_to(root))],
    )


def update_packet_status(root: Path, task_id: str, new_status: str) -> CommandResult:
    """Validate and apply a status transition for one packet.

    Returns:
        CommandResult with ok=True and status set on success.
        ok=False with errors when packet not found, task.md missing,
        or the transition is not allowed.
    """
    packet_dir = find_packet_dir(root / "tasks", task_id)

    if packet_dir is None:
        return CommandResult(
            ok=False,
            command="task status",
            errors=[f"packet '{task_id}' not found"],
        )

    try:
        record = read_packet_record(packet_dir)
    except FileNotFoundError:
        return CommandResult(
            ok=False,
            command="task status",
            errors=[f"packet '{task_id}': task.md not found"],
        )

    errors = validate_status_transition(record.status, new_status)
    if errors:
        return CommandResult(
            ok=False,
            command="task status",
            errors=errors,
        )

    write_packet_status(packet_dir, new_status)

    return CommandResult(
        ok=True,
        command="task status",
        repo=str(root),
        task_id=task_id,
        status=new_status,
        files_updated=[str((packet_dir / "task.md").relative_to(root))],
    )


def show_packet(
    root: Path, task_id: str
) -> tuple[CommandResult, PacketRecord | None, dict[str, bool]]:
    """Return metadata and file inventory for one packet.

    Returns:
        (CommandResult, PacketRecord | None, file_inventory)
        file_inventory maps each packet filename to True (present) or False (absent).
        On failure, CommandResult.ok is False and record is None.
    """
    tasks_root = root / "tasks"
    packet_dir = find_packet_dir(tasks_root, task_id)

    if packet_dir is None:
        return (
            CommandResult(
                ok=False,
                command="task show",
                errors=[f"packet '{task_id}' not found"],
            ),
            None,
            {},
        )

    try:
        record = read_packet_record(packet_dir)
    except FileNotFoundError:
        return (
            CommandResult(
                ok=False,
                command="task show",
                errors=[f"packet '{task_id}': task.md not found"],
            ),
            None,
            {},
        )

    inventory = {name: (packet_dir / name).exists() for name in _ALL_PACKET_FILES}

    return (
        CommandResult(ok=True, command="task show", repo=str(root), task_id=task_id),
        record,
        inventory,
    )
