# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

"""Validation service for installable community adapter packages."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from grain.adapters.adapter_config import parse_adapter_profiles_markdown
from grain.cli.output import CommandResult
from grain.domain.adapters import AdapterProfile
from grain.domain.errors import ConfigError

PACKAGE_METADATA_FILE = "adapter_package.yaml"
DEFAULT_PROFILE_FILE = "adapter_profile.md"
_REQUIRED_METADATA_FIELDS = ("package_id", "adapter_id", "version")


@dataclass
class AdapterPackageValidation:
    """Structured validation result for one adapter package directory."""

    package_dir: Path
    valid: bool
    package_id: str = ""
    adapter_id: str = ""
    version: str = ""
    profile_path: str = ""
    profiles: list[AdapterProfile] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_adapter_package(
    package_dir: Path,
) -> tuple[CommandResult, AdapterPackageValidation]:
    """Validate one registry-entry package on disk."""
    errors: list[str] = []
    warnings: list[str] = []
    metadata_path = package_dir / PACKAGE_METADATA_FILE

    if not package_dir.exists() or not package_dir.is_dir():
        errors.append(f"package directory not found: {package_dir}")
        validation = AdapterPackageValidation(package_dir=package_dir, valid=False, errors=errors)
        return _result(package_dir, validation), validation

    metadata = _load_metadata(metadata_path, errors)
    package_id = _read_text(metadata, "package_id")
    adapter_id = _read_text(metadata, "adapter_id")
    version = _read_text(metadata, "version")
    profile_rel = _read_text(metadata, "profile_path") or DEFAULT_PROFILE_FILE

    for field_name in _REQUIRED_METADATA_FIELDS:
        if not _read_text(metadata, field_name):
            errors.append(f"missing required metadata field: {field_name}")

    profile_path = package_dir / profile_rel
    profiles: list[AdapterProfile] = []
    if not profile_path.exists():
        errors.append(f"missing adapter profile file: {profile_rel}")
    else:
        try:
            profiles = parse_adapter_profiles_markdown(profile_path.read_text(encoding="utf-8"))
        except ConfigError as exc:
            errors.append(exc.message if not exc.detail else f"{exc.message}: {exc.detail}")
        except Exception as exc:  # noqa: BLE001 - validation must surface deterministic failure text
            errors.append(f"could not read adapter profile file '{profile_rel}': {exc}")

    if profiles:
        if len(profiles) != 1:
            errors.append(
                f"adapter package must contain exactly one adapter profile, found {len(profiles)}"
            )
        elif adapter_id and profiles[0].adapter_id != adapter_id:
            errors.append(
                "metadata adapter_id does not match adapter profile adapter_id: "
                f"{adapter_id} != {profiles[0].adapter_id}"
            )

    validation = AdapterPackageValidation(
        package_dir=package_dir,
        valid=not errors,
        package_id=package_id,
        adapter_id=adapter_id,
        version=version,
        profile_path=profile_rel,
        profiles=profiles,
        errors=errors,
        warnings=warnings,
    )
    return _result(package_dir, validation), validation


def _result(package_dir: Path, validation: AdapterPackageValidation) -> CommandResult:
    return CommandResult(
        ok=validation.valid,
        command="adapter package validate",
        repo=str(package_dir),
        warnings=list(validation.warnings),
        errors=list(validation.errors),
    )


def _load_metadata(path: Path, errors: list[str]) -> dict[str, object]:
    if not path.exists():
        errors.append(f"missing required file: {PACKAGE_METADATA_FILE}")
        return {}
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - validation must degrade to readable errors
        errors.append(f"could not read {PACKAGE_METADATA_FILE}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"{PACKAGE_METADATA_FILE} must contain a mapping")
        return {}
    return payload


def _read_text(payload: dict[str, object], key: str) -> str:
    value = payload.get(key)
    return str(value).strip() if value is not None else ""
