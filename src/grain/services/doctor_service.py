# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: AGPL-3.0-only

"""Doctor service — install/source alignment diagnostics."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class DoctorResult:
    grain_version: str = ""
    install_mode: str = ""        # "editable" | "installed" | "dev"
    install_path: str = ""
    source_path: str = ""
    pyproject_version: str = ""
    version_match: bool = True
    source_mtime: str = ""
    install_mtime: str = ""
    source_files_modified_since_install: list[str] = field(default_factory=list)
    workspace_root: str = ""
    python_version: str = ""
    checks: dict = field(default_factory=dict)
    overall: str = "ok"           # "ok" | "drift_detected"


def run_doctor(root: Path | None = None) -> DoctorResult:
    result = DoctorResult()

    result.grain_version = _installed_version()
    result.install_mode = detect_install_mode()
    result.install_path = _install_path()
    result.source_path = _source_path()
    result.python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    result.pyproject_version = _pyproject_version(root)

    result.version_match = (
        result.grain_version == result.pyproject_version
        or not result.pyproject_version
        or result.grain_version == "unknown"
    )

    install_mtime_dt, source_mtime_dt, modified = _mtime_check()
    result.install_mtime = install_mtime_dt.strftime("%Y-%m-%dT%H:%M:%S") if install_mtime_dt else ""
    result.source_mtime = source_mtime_dt.strftime("%Y-%m-%dT%H:%M:%S") if source_mtime_dt else ""
    result.source_files_modified_since_install = modified

    mtime_ok = len(modified) == 0

    if root:
        result.workspace_root = str(root.resolve())
    else:
        from grain.adapters.filesystem import resolve_repo_root
        try:
            resolved = resolve_repo_root(None)
            result.workspace_root = str(resolved.resolve())
        except Exception:
            result.workspace_root = ""

    result.checks = {
        "version_match": result.version_match,
        "mtime_ok": mtime_ok,
        "install_mode_ok": result.install_mode != "unknown",
        "workspace_resolved": bool(result.workspace_root),
    }

    all_ok = all(result.checks.values())
    result.overall = "ok" if all_ok else "drift_detected"
    return result


def detect_install_mode() -> str:
    """Return 'editable', 'installed', or 'dev'."""
    try:
        import importlib.metadata as meta
        dist = meta.distribution("grain-kit")
        direct_url_text = dist.read_text("direct_url.json")
        if direct_url_text:
            import json
            data = json.loads(direct_url_text)
            if data.get("dir_info", {}).get("editable"):
                return "editable"
            return "installed"
        # Check for __editable__ marker file
        for file in dist.files or []:
            if "__editable__" in str(file):
                return "editable"
        return "installed"
    except Exception:
        pass

    # Fallback: check if running from source tree
    try:
        import grain
        p = Path(grain.__file__).resolve()
        if "/src/grain/" in str(p) or str(p).endswith("/src/grain/__init__.py"):
            return "dev"
    except Exception:
        pass
    return "unknown"


def _installed_version() -> str:
    try:
        from importlib.metadata import version
        return version("grain-kit")
    except Exception:
        return "unknown"


def _install_path() -> str:
    try:
        import importlib.metadata as meta
        dist = meta.distribution("grain-kit")
        location = dist.locate_file("")
        return str(location)
    except Exception:
        return ""


def _source_path() -> str:
    try:
        import grain
        p = Path(grain.__file__).resolve().parent
        return str(p)
    except Exception:
        return ""


def _pyproject_version(root: Path | None) -> str:
    candidates = []
    if root:
        candidates.append(root / "pyproject.toml")
    try:
        import grain
        candidates.append(Path(grain.__file__).resolve().parents[3] / "pyproject.toml")
    except Exception:
        pass

    for path in candidates:
        if path.exists():
            try:
                import tomllib
                with path.open("rb") as f:
                    return tomllib.load(f)["project"]["version"]
            except Exception:
                pass
    return ""


def _mtime_check() -> tuple[datetime | None, datetime | None, list[str]]:
    """Return (install_mtime, source_mtime, files_modified_since_install)."""
    try:
        import importlib.metadata as meta
        dist = meta.distribution("grain-kit")
        record = dist.read_text("RECORD")
        if not record:
            return None, None, []

        # Find the oldest installed .py file mtime as proxy for install time
        install_root = Path(dist.locate_file(""))
        install_mtimes: list[float] = []
        for line in record.splitlines():
            rel = line.split(",")[0]
            if rel.endswith(".py") and "grain" in rel:
                candidate = install_root / rel
                if candidate.exists():
                    install_mtimes.append(candidate.stat().st_mtime)

        if not install_mtimes:
            return None, None, []

        install_mtime_ts = min(install_mtimes)  # earliest = install time proxy
        install_dt = datetime.fromtimestamp(install_mtime_ts, tz=timezone.utc)

        # Scan source .py files
        import grain
        src_root = Path(grain.__file__).resolve().parent
        modified: list[str] = []
        latest_src_mtime: float = 0.0

        for py_file in src_root.rglob("*.py"):
            mt = py_file.stat().st_mtime
            if mt > latest_src_mtime:
                latest_src_mtime = mt
            if mt > install_mtime_ts + 60:  # 60s grace period
                modified.append(str(py_file.relative_to(src_root.parent)))

        source_dt = datetime.fromtimestamp(latest_src_mtime, tz=timezone.utc) if latest_src_mtime else None
        return install_dt, source_dt, modified[:5]  # cap at 5 files in output

    except Exception:
        return None, None, []
