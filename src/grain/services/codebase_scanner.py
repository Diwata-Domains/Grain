"""Codebase scanner for existing-project onboarding."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from grain.domain.scan_result import ScanResult

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
        )

        custom_adapter_hints = self._detect_custom_adapter_hints(
            primary_languages=primary_languages,
            has_notebook_signal=has_notebook_signal,
            has_data_signal=has_data_signal,
            has_devops_signal=has_devops_signal,
        )

        return ScanResult(
            root=str(self.root.resolve()),
            primary_languages=primary_languages,
            language_counts=dict(sorted(language_counts.items())),
            applicable_adapters=applicable_adapters,
            key_files=sorted(set(key_files)),
            ci_configs=sorted(set(ci_configs)),
            documentation_files=sorted(set(documentation_files)),
            custom_adapter_hints=custom_adapter_hints,
        )

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

        if has_notebook_signal or has_data_signal:
            hints.append(
                "Data science signals detected (notebooks or data files). "
                "Consider defining a custom `data_adapter` in docs/runtime/adapter_profiles.md "
                "with file patterns for notebooks, datasets, and model artifacts."
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

        return adapters

