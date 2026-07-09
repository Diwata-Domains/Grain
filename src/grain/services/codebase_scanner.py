# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: MIT

"""Codebase scanner for existing-project onboarding."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from grain.domain.scan_result import ScanResult

# Maximum characters to read from any single doc to keep drafts manageable.
_CONTENT_CAP = 2000

# Well-known doc paths scanned for content, in priority order.
# All compared case-insensitively against the relative path.
_README_NAMES: frozenset[str] = frozenset(
    {"readme.md", "readme.rst", "readme.txt", "readme"}
)
_ARCHITECTURE_NAMES: frozenset[str] = frozenset(
    {
        "architecture.md",
        "architecture.rst",
        "docs/architecture.md",
        "docs/architecture.rst",
        "docs/design.md",
        "docs/design.rst",
        "design.md",
    }
)
_SCOPE_NAMES: frozenset[str] = frozenset(
    {
        "product_scope.md",
        "scope.md",
        "docs/product_scope.md",
        "docs/scope.md",
        "vision.md",
        "docs/vision.md",
    }
)
_CONTRIBUTING_NAMES: frozenset[str] = frozenset(
    {"contributing.md", "contributing.rst", ".github/contributing.md"}
)

_IGNORED_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".venv",
        "venv",
        "node_modules",
        "dist",
        "build",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
    }
)

_LANGUAGE_BY_EXTENSION: dict[str, str] = {
    ".c": "C",
    ".cc": "C++",
    ".cpp": "C++",
    ".cxx": "C++",
    ".cs": "C#",
    ".go": "Go",
    ".java": "Java",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".php": "PHP",
    ".py": "Python",
    ".rb": "Ruby",
    ".rs": "Rust",
    ".sh": "Shell",
    ".swift": "Swift",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
}

_FRONTEND_EXTENSIONS: frozenset[str] = frozenset(
    {".css", ".htm", ".html", ".jsx", ".less", ".sass", ".scss", ".tsx", ".vue", ".svelte"}
)
_DOC_EXTENSIONS: frozenset[str] = frozenset({".md", ".mdx", ".rst", ".txt"})
_SPREADSHEET_EXTENSIONS: frozenset[str] = frozenset({".csv", ".ods", ".xls", ".xlsx"})

_NOTEBOOK_EXTENSION: str = ".ipynb"
_DATA_EXTENSIONS: frozenset[str] = frozenset({".parquet", ".feather", ".arrow", ".h5", ".hdf5"})
_DEVOPS_FILE_NAMES: frozenset[str] = frozenset(
    {
        "dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        "docker-compose.override.yml",
        "docker-compose.override.yaml",
        "vagrantfile",
        "ansible.cfg",
    }
)
_DEVOPS_EXTENSIONS: frozenset[str] = frozenset({".tf", ".hcl"})
_MOBILE_LANGUAGE_MAP: dict[str, str] = {
    "Swift": "ios_adapter",
    "Kotlin": "android_adapter",
}

_KEY_FILE_NAMES: frozenset[str] = frozenset(
    {
        "makefile",
        "package.json",
        "pyproject.toml",
        "readme",
        "readme.md",
        "readme.rst",
    }
)

_CI_FILE_NAMES: frozenset[str] = frozenset(
    {
        ".gitlab-ci.yml",
        ".gitlab-ci.yaml",
        "azure-pipelines.yml",
        "azure-pipelines.yaml",
    }
)


class CodebaseScanner:
    """Read-only scanner that extracts onboarding signals from a repo."""

    def __init__(self, root: Path):
        self.root = root

    def scan(self) -> ScanResult:
        language_counts: Counter[str] = Counter()
        key_files: list[str] = []
        ci_configs: list[str] = []
        documentation_files: list[str] = []

        has_frontend_signal = False
        has_spreadsheet_signal = False
        has_notebook_signal = False
        has_data_signal = False
        has_devops_signal = False

        for rel in self._iter_files():
            rel_path = Path(rel)
            ext = rel_path.suffix.lower()
            name = rel_path.name.lower()

            language = _LANGUAGE_BY_EXTENSION.get(ext)
            if language is not None:
                language_counts[language] += 1

            if name in _KEY_FILE_NAMES:
                key_files.append(rel)

            if self._is_ci_config(rel_path):
                ci_configs.append(rel)

            if ext in _DOC_EXTENSIONS or rel_path.name.lower().startswith("readme"):
                documentation_files.append(rel)

            if ext in _FRONTEND_EXTENSIONS or rel_path.name.lower().startswith(
                ("vite.config.", "next.config.", "tailwind.config.")
            ):
                has_frontend_signal = True

            if ext in _SPREADSHEET_EXTENSIONS:
                has_spreadsheet_signal = True

            if ext == _NOTEBOOK_EXTENSION:
                has_notebook_signal = True

            if ext in _DATA_EXTENSIONS:
                has_data_signal = True

            if ext in _DEVOPS_EXTENSIONS or name in _DEVOPS_FILE_NAMES:
                has_devops_signal = True

        primary_languages = [
            language
            for language, _count in sorted(
                language_counts.items(),
                key=lambda item: (-item[1], item[0]),
            )
        ]

        applicable_adapters = self._detect_adapters(
            primary_languages=primary_languages,
            documentation_files=documentation_files,
            has_frontend_signal=has_frontend_signal,
            has_spreadsheet_signal=has_spreadsheet_signal,
            has_notebook_signal=has_notebook_signal,
            has_data_signal=has_data_signal,
        )

        custom_adapter_hints = self._detect_custom_adapter_hints(
            primary_languages=primary_languages,
            has_notebook_signal=has_notebook_signal,
            has_data_signal=has_data_signal,
            has_devops_signal=has_devops_signal,
        )

        existing_doc_content = self._read_existing_doc_content(all_files=key_files + documentation_files)
        detected_modules = self._detect_modules()

        return ScanResult(
            root=str(self.root.resolve()),
            primary_languages=primary_languages,
            language_counts=dict(sorted(language_counts.items())),
            applicable_adapters=applicable_adapters,
            key_files=sorted(set(key_files)),
            ci_configs=sorted(set(ci_configs)),
            documentation_files=sorted(set(documentation_files)),
            custom_adapter_hints=custom_adapter_hints,
            existing_doc_content=existing_doc_content,
            detected_modules=detected_modules,
        )

    def _read_existing_doc_content(self, all_files: list[str]) -> dict[str, str]:
        """Read content from well-known existing docs and structured config files."""
        content: dict[str, str] = {}
        seen_lower: set[str] = set()

        def _add(rel: str) -> None:
            lower = rel.lower()
            if lower in seen_lower:
                return
            seen_lower.add(lower)
            text = self._read_text_file(rel)
            if text:
                content[rel] = text

        # Priority 1: README
        for rel in sorted(all_files):
            if rel.lower() in _README_NAMES or Path(rel).name.lower() in _README_NAMES:
                _add(rel)
                break  # first README only

        # Priority 2: Architecture docs
        for rel in sorted(all_files):
            if rel.lower() in _ARCHITECTURE_NAMES or Path(rel).name.lower() in _ARCHITECTURE_NAMES:
                _add(rel)
                break

        # Priority 3: Scope/vision docs
        for rel in sorted(all_files):
            if rel.lower() in _SCOPE_NAMES or Path(rel).name.lower() in _SCOPE_NAMES:
                _add(rel)
                break

        # Priority 4: Contributing docs
        for rel in sorted(all_files):
            if rel.lower() in _CONTRIBUTING_NAMES or Path(rel).name.lower() in _CONTRIBUTING_NAMES:
                _add(rel)
                break

        # Priority 5: package.json — extract name, description, dependencies
        pkg_json = self.root / "package.json"
        if pkg_json.exists():
            text = self._read_package_json(pkg_json)
            if text:
                content["package.json"] = text

        # Priority 6: pyproject.toml — extract name, description, dependencies
        pyproject = self.root / "pyproject.toml"
        if pyproject.exists():
            text = self._read_pyproject_toml(pyproject)
            if text:
                content["pyproject.toml"] = text

        return content

    def _read_text_file(self, rel: str) -> str:
        """Read a text file, cap at _CONTENT_CAP chars, return empty string on error."""
        path = self.root / rel
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            if len(text) > _CONTENT_CAP:
                text = text[:_CONTENT_CAP] + "\n… (truncated)"
            return text.strip()
        except Exception:
            return ""

    def _read_package_json(self, path: Path) -> str:
        """Extract name, description, and top-level dependency names from package.json."""
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return ""

        lines: list[str] = []
        if name := data.get("name"):
            lines.append(f"name: {name}")
        if description := data.get("description"):
            lines.append(f"description: {description}")
        if version := data.get("version"):
            lines.append(f"version: {version}")

        all_deps = {
            **data.get("dependencies", {}),
            **data.get("devDependencies", {}),
        }
        if all_deps:
            top = sorted(all_deps.keys())[:20]
            lines.append(f"dependencies: {', '.join(top)}")

        return "\n".join(lines)

    def _read_pyproject_toml(self, path: Path) -> str:
        """Extract name, description, and dependencies from pyproject.toml."""
        try:
            import tomllib  # Python 3.11+
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return ""

        project = data.get("project", {})
        lines: list[str] = []
        if name := project.get("name"):
            lines.append(f"name: {name}")
        if description := project.get("description"):
            lines.append(f"description: {description}")
        if version := project.get("version"):
            lines.append(f"version: {version}")
        if deps := project.get("dependencies", []):
            top = sorted(str(d).split(">")[0].split("<")[0].split("=")[0].strip() for d in deps)[:20]
            lines.append(f"dependencies: {', '.join(top)}")

        return "\n".join(lines)

    def _iter_files(self) -> list[str]:
        if not self.root.exists() or not self.root.is_dir():
            return []

        results: list[str] = []
        for path in self.root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in _IGNORED_DIRS for part in path.relative_to(self.root).parts):
                continue
            results.append(path.relative_to(self.root).as_posix())
        return sorted(results)

    def _is_ci_config(self, rel_path: Path) -> bool:
        if rel_path.name.lower() in _CI_FILE_NAMES:
            return True

        parts = rel_path.parts
        if len(parts) >= 3 and parts[0] == ".github" and parts[1] == "workflows":
            return rel_path.suffix.lower() in {".yml", ".yaml"}

        if len(parts) >= 2 and parts[0] == ".circleci":
            return rel_path.name.lower() == "config.yml"

        return False

    def _detect_modules(self) -> list[str]:
        """Detect top-level code modules/packages to surface code-ahead-of-backlog warnings.

        Checks common source roots (src/, lib/, app/, and repo root) for Python
        packages (__init__.py), JS/TS packages (package.json or index.*), and
        generic named directories containing code files.
        """
        modules: list[str] = []
        seen: set[str] = set()

        # Source roots to check, in priority order
        source_roots = [
            self.root / "src",
            self.root / "lib",
            self.root / "app",
            self.root,
        ]

        code_extensions = frozenset(_LANGUAGE_BY_EXTENSION.keys())

        for source_root in source_roots:
            if not source_root.is_dir():
                continue
            for candidate in sorted(source_root.iterdir()):
                if not candidate.is_dir():
                    continue
                if candidate.name.startswith(".") or candidate.name in _IGNORED_DIRS:
                    continue
                # Skip the source root itself when checking repo root
                if source_root == self.root and candidate.name in {"src", "lib", "app", "tests", "test", "docs", "tasks"}:
                    continue
                rel = candidate.relative_to(self.root).as_posix()
                if rel in seen:
                    continue
                # Check if this looks like a code module
                has_init = (candidate / "__init__.py").exists()
                has_pkg_json = (candidate / "package.json").exists()
                has_index = any(
                    (candidate / f"index{ext}").exists()
                    for ext in (".js", ".ts", ".jsx", ".tsx", ".mjs")
                )
                has_code = any(
                    f.suffix.lower() in code_extensions
                    for f in candidate.iterdir()
                    if f.is_file()
                ) if not (has_init or has_pkg_json or has_index) else True

                if has_init or has_pkg_json or has_index or has_code:
                    seen.add(rel)
                    modules.append(rel)

        return modules

    def _detect_custom_adapter_hints(
        self,
        *,
        primary_languages: list[str],
        has_notebook_signal: bool,
        has_data_signal: bool,
        has_devops_signal: bool,
    ) -> list[str]:
        hints: list[str] = []

        if has_devops_signal:
            hints.append(
                "DevOps/infrastructure files detected (Dockerfile, Terraform, or similar). "
                "Consider defining a custom `devops_adapter` in docs/runtime/adapter_profiles.md "
                "with file patterns for your infrastructure artifacts."
            )

        for language, suggested_adapter in _MOBILE_LANGUAGE_MAP.items():
            if language in primary_languages:
                hints.append(
                    f"{language} detected as a primary language. "
                    f"Consider defining a custom `{suggested_adapter}` in docs/runtime/adapter_profiles.md "
                    f"with file patterns suited to {language} project structure."
                )

        return hints

    def _detect_adapters(
        self,
        *,
        primary_languages: list[str],
        documentation_files: list[str],
        has_frontend_signal: bool,
        has_spreadsheet_signal: bool,
        has_notebook_signal: bool,
        has_data_signal: bool,
    ) -> list[str]:
        adapters: list[str] = []

        if primary_languages:
            adapters.append("code_adapter")

        if has_frontend_signal or "TypeScript" in primary_languages or "JavaScript" in primary_languages:
            adapters.append("frontend_adapter")

        if documentation_files:
            adapters.append("docs_adapter")

        if has_spreadsheet_signal:
            adapters.append("spreadsheet_adapter")

        if has_notebook_signal or has_data_signal:
            adapters.append("data_adapter")

        return adapters
