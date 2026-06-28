# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

"""Git hooks service — writes, removes, and checks Grain-managed git hooks."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

_GRAIN_HOOK_HEADER = "# Written by grain hooks install."

_PRE_COMMIT_SCRIPT = """\
#!/bin/sh
# Written by grain hooks install. Do not edit manually.
# Grain workflow guard: blocks implementation commits without an open packet.

# Allow GRAIN_SKIP_GUARD=1 as an emergency escape hatch
if [ "$GRAIN_SKIP_GUARD" = "1" ]; then
  echo "[grain] GRAIN_SKIP_GUARD=1: skipping workflow guard. This bypass is logged." >&2
  # Write bypass note directly to tooling_notes.md (grain notes add not yet implemented)
  NOTE_FILE="docs/working/tooling_notes.md"
  if [ -f "$NOTE_FILE" ]; then
    TODAY=$(date +%Y-%m-%d)
    echo "| $TODAY | workflow_friction | git commit | GRAIN_SKIP_GUARD=1 used to bypass pre-commit workflow guard. Justified bypass should be documented. | medium | open |" >> "$NOTE_FILE"
  fi
  exit 0
fi

# Skip hook for metadata-only commits (docs/working/ and tasks/ only)
CHANGED_FILES=$(git diff --cached --name-only 2>/dev/null)
NON_META=$(echo "$CHANGED_FILES" | grep -v "^docs/working/" | grep -v "^tasks/" | grep -v "^$")
if [ -z "$NON_META" ]; then
  exit 0
fi

# Run the guard
GUARD_OUTPUT=$(grain --format json workflow guard --strict 2>/dev/null)
STATUS=$(echo "$GUARD_OUTPUT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'error'))" 2>/dev/null)

if [ "$STATUS" = "violation" ]; then
  echo "" >&2
  echo "✗ grain workflow guard: commit blocked" >&2
  grain workflow guard --strict >&2
  echo "" >&2
  echo "Fix the violations above, then commit again." >&2
  echo "Emergency bypass: GRAIN_SKIP_GUARD=1 git commit (logs to tooling_notes)" >&2
  exit 1
fi

exit 0
"""

_POST_CHECKOUT_SCRIPT = """\
#!/bin/sh
# Written by grain hooks install. Do not edit manually.
# Grain post-checkout: cache workflow state for fast agent session start.

# Only run on branch checkouts (not file checkouts)
CHECKOUT_TYPE=$3
if [ "$CHECKOUT_TYPE" != "1" ]; then
  exit 0
fi

# Write current workflow state for fast agent reads at session start
mkdir -p .grain
grain --format json workflow next > .grain/last_workflow_state.json 2>/dev/null

# Warn if current_task.md points to a done packet (stale pointer)
STOP_REASON=$(grain --format json workflow next 2>/dev/null | \\
  python3 -c "import sys, json; d=json.load(sys.stdin); e=d.get('evaluation',{}); print(e.get('stop_reason',''))" 2>/dev/null)

if [ "$STOP_REASON" = "stale_task_pointer" ]; then
  echo "[grain] ⚠ current_task.md points to a completed packet — update 'Task ID:' to 'none'" >&2
fi
"""


@dataclass
class HookStatus:
    hook_name: str
    installed: bool
    current: bool          # matches the version Grain would write now
    path: str
    grain_managed: bool    # has the grain header marker


@dataclass
class HooksResult:
    ok: bool
    installed: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    statuses: list[HookStatus] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    dry_run: bool = False


def _hooks_dir(root: Path) -> Path:
    return root / ".git" / "hooks"


def _hook_scripts() -> dict[str, str]:
    return {
        "pre-commit": _PRE_COMMIT_SCRIPT,
        "post-checkout": _POST_CHECKOUT_SCRIPT,
    }


def _script_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def install_hooks(root: Path, dry_run: bool = False) -> HooksResult:
    hooks_dir = _hooks_dir(root)
    if not hooks_dir.exists():
        return HooksResult(
            ok=False,
            errors=["no .git/hooks directory found — is this a git repository?"],
        )

    result = HooksResult(ok=True, dry_run=dry_run)
    scripts = _hook_scripts()

    for name, content in scripts.items():
        hook_path = hooks_dir / name
        if hook_path.exists():
            existing = hook_path.read_text(encoding="utf-8")
            if _GRAIN_HOOK_HEADER not in existing:
                result.skipped.append(name)
                result.errors.append(
                    f"{name}: existing hook is not grain-managed — remove it manually first, "
                    f"then re-run `grain hooks install`"
                )
                continue
            if existing.strip() == content.strip():
                result.skipped.append(name)
                continue
        if not dry_run:
            hook_path.write_text(content, encoding="utf-8")
            hook_path.chmod(0o755)
        result.installed.append(name)

    return result


def uninstall_hooks(root: Path, dry_run: bool = False) -> HooksResult:
    hooks_dir = _hooks_dir(root)
    result = HooksResult(ok=True, dry_run=dry_run)
    scripts = _hook_scripts()

    for name in scripts:
        hook_path = hooks_dir / name
        if not hook_path.exists():
            result.skipped.append(name)
            continue
        existing = hook_path.read_text(encoding="utf-8")
        if _GRAIN_HOOK_HEADER not in existing:
            result.skipped.append(name)
            result.errors.append(f"{name}: not grain-managed — skipped")
            continue
        if not dry_run:
            hook_path.unlink()
        result.removed.append(name)

    return result


def status_hooks(root: Path) -> HooksResult:
    hooks_dir = _hooks_dir(root)
    result = HooksResult(ok=True)
    scripts = _hook_scripts()

    for name, expected_content in scripts.items():
        hook_path = hooks_dir / name
        if not hook_path.exists():
            result.statuses.append(HookStatus(
                hook_name=name,
                installed=False,
                current=False,
                path=str(hook_path),
                grain_managed=False,
            ))
            continue
        existing = hook_path.read_text(encoding="utf-8")
        grain_managed = _GRAIN_HOOK_HEADER in existing
        current = existing.strip() == expected_content.strip()
        result.statuses.append(HookStatus(
            hook_name=name,
            installed=True,
            current=current,
            path=str(hook_path),
            grain_managed=grain_managed,
        ))

    return result
