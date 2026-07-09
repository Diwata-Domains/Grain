# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Install service for explicit local community adapter packages."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from grain.adapters.adapter_config import ADAPTER_PROFILES_PATH, load_adapter_profiles
from grain.cli.output import CommandResult
from grain.services.adapter_package_service import (
    AdapterPackageValidation,
    PACKAGE_METADATA_FILE,
    validate_adapter_package,
)


@dataclass
class AdapterInstallResult:
    """Structured install result for one adapter package install."""

    source_kind: str
    source_ref: str
    package_dir: Path | None = None
    package_id: str = ""
    adapter_id: str = ""
    installed_path: str = ""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def install_adapter(
    root: Path,
    *,
    source: Path | None = None,
    handle: str = "",
    registry_root: Path | None = None,
) -> tuple[CommandResult, AdapterInstallResult | None]:
    """Install one validated adapter package into the repo adapter profile file."""
    validation_error = _validate_selector(source=source, handle=handle, registry_root=registry_root)
    if validation_error:
        result = AdapterInstallResult(
            source_kind="",
            source_ref="",
            errors=[validation_error],
        )
        return _command_result(root, result), result

    if source is not None:
        source_kind = "package_dir"
        source_ref = str(source)
        package_dir = source
    else:
        assert registry_root is not None
        source_kind = "registry_handle"
        source_ref = handle
        package_dir, resolution_errors = _resolve_handle(registry_root, handle)
        if package_dir is None:
            result = AdapterInstallResult(
                source_kind=source_kind,
                source_ref=source_ref,
                errors=resolution_errors,
            )
            return _command_result(root, result), result

    validation_result, validation = validate_adapter_package(package_dir)
    if not validation_result.ok:
        result = AdapterInstallResult(
            source_kind=source_kind,
            source_ref=source_ref,
            package_dir=package_dir,
            package_id=validation.package_id,
            adapter_id=validation.adapter_id,
            errors=list(validation.errors),
            warnings=list(validation.warnings),
        )
        return _command_result(root, result), result

    target_path = root / ADAPTER_PROFILES_PATH
    if not target_path.exists():
        result = AdapterInstallResult(
            source_kind=source_kind,
            source_ref=source_ref,
            package_dir=package_dir,
            package_id=validation.package_id,
            adapter_id=validation.adapter_id,
            errors=[f"adapter profile target not found: {ADAPTER_PROFILES_PATH}"],
        )
        return _command_result(root, result), result

    existing_ids = {profile.adapter_id for profile in load_adapter_profiles(root)}
    if validation.adapter_id in existing_ids:
        result = AdapterInstallResult(
            source_kind=source_kind,
            source_ref=source_ref,
            package_dir=package_dir,
            package_id=validation.package_id,
            adapter_id=validation.adapter_id,
            errors=[f"adapter '{validation.adapter_id}' is already installed"],
        )
        return _command_result(root, result), result

    _append_profile(target_path, validation)
    result = AdapterInstallResult(
        source_kind=source_kind,
        source_ref=source_ref,
        package_dir=package_dir,
        package_id=validation.package_id,
        adapter_id=validation.adapter_id,
        installed_path=ADAPTER_PROFILES_PATH,
    )
    return _command_result(root, result), result


def _command_result(root: Path, result: AdapterInstallResult) -> CommandResult:
    return CommandResult(
        ok=not result.errors,
        command="adapter install",
        repo=str(root),
        files_updated=[result.installed_path] if result.installed_path else [],
        warnings=list(result.warnings),
        errors=list(result.errors),
    )


def _validate_selector(
    *,
    source: Path | None,
    handle: str,
    registry_root: Path | None,
) -> str:
    if source is not None and handle:
        return "specify either --source or --handle, not both"
    if source is None and not handle:
        return "either --source or --handle is required"
    if handle and registry_root is None:
        return "--registry-root is required when --handle is used"
    if source is not None and registry_root is not None:
        return "--registry-root may only be used with --handle"
    return ""


def _resolve_handle(registry_root: Path, handle: str) -> tuple[Path | None, list[str]]:
    if not registry_root.exists() or not registry_root.is_dir():
        return None, [f"registry root not found: {registry_root}"]

    matches: list[Path] = []
    for metadata_path in registry_root.rglob(PACKAGE_METADATA_FILE):
        package_dir = metadata_path.parent
        _, validation = validate_adapter_package(package_dir)
        if handle in {validation.package_id, validation.adapter_id}:
            matches.append(package_dir)

    if not matches:
        return None, [f"registry handle not found: {handle}"]
    if len(matches) > 1:
        names = ", ".join(sorted(str(path.relative_to(registry_root)) for path in matches))
        return None, [f"registry handle is ambiguous: {handle} ({names})"]
    return matches[0], []


def _append_profile(target_path: Path, validation: AdapterPackageValidation) -> None:
    profile_text = (validation.package_dir / validation.profile_path).read_text(encoding="utf-8")
    profile_block = _extract_profile_block(profile_text, validation.adapter_id)
    current = target_path.read_text(encoding="utf-8").rstrip()
    updated = current + "\n\n" + profile_block.strip() + "\n"
    target_path.write_text(updated, encoding="utf-8")


def _extract_profile_block(profile_text: str, adapter_id: str) -> str:
    lines = profile_text.splitlines()
    start = None
    end = len(lines)
    header = f"### {adapter_id}"
    for index, line in enumerate(lines):
        if line.strip() == header:
            start = index
            continue
        if start is not None and line.strip().startswith("### "):
            end = index
            break

    if start is None:
        raise ValueError(f"adapter profile section not found: {adapter_id}")
    return "\n".join(lines[start:end]).strip()
