"""Deterministic structural entity extraction service (Phase 10 Layer 1)."""

from __future__ import annotations

import ast
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class StructuralEntity:
    """Normalized structural entity record extracted from one source file."""

    entity_type: str
    name: str
    language: str
    line: int
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class StructuralExtraction:
    """Extraction result for one file."""

    file_path: str
    language: str
    entities: list[StructuralEntity]
    parser: str

    def to_dict(self) -> dict[str, object]:
        return {
            "file_path": self.file_path,
            "language": self.language,
            "entities": [asdict(entity) for entity in self.entities],
            "parser": self.parser,
        }


_LANG_BY_SUFFIX: dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".css": "frontend_style",
    ".scss": "frontend_style",
    ".md": "markdown",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".hcl": "hcl",
    ".tf": "hcl",
    ".sh": "shell",
}

_IMPORT_RE = re.compile(r"^\s*import\s+([A-Za-z0-9_./{}* ,]+)\s+from\s+['\"]([^'\"]+)['\"]")
_REQUIRE_RE = re.compile(r"^\s*(?:const|let|var)\s+[A-Za-z0-9_$]+\s*=\s*require\(\s*['\"]([^'\"]+)['\"]\s*\)")
_FUNC_RE = re.compile(r"^\s*function\s+([A-Za-z0-9_$]+)\s*\(")
_CLASS_RE = re.compile(r"^\s*class\s+([A-Za-z0-9_$]+)\b")
_CALL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_MD_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_DOCKER_FROM_RE = re.compile(r"^\s*FROM\s+([^\s]+)", re.IGNORECASE)
_HCL_BLOCK_RE = re.compile(
    r'^\s*(resource|module|variable|output)\s+"?([^"\s]+)"?(?:\s+"([^"\s]+)")?\s*{'
)
_SHELL_FUNC_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(\)\s*\{")
_YAML_DEP_SECTION_RE = re.compile(r"^\s*(depends_on|dependencies|requires)\s*:\s*$")
_YAML_KEY_RE = re.compile(r"^\s*([A-Za-z0-9_.-]+)\s*:\s*(.+)?$")
_TOML_SECTION_RE = re.compile(r"^\s*\[([^\]]+)\]\s*$")
_TOML_DEP_RE = re.compile(r"^\s*([A-Za-z0-9_.-]+)\s*=\s*['\"]?([^'\"]+)['\"]?\s*$")


def extract_structural_entities(file_path: Path, content: str | None = None) -> StructuralExtraction:
    """Extract normalized structural entities from a source artifact.

    Layer 1 is deterministic and local-only. No LLMs or remote calls.
    """
    text = content if content is not None else file_path.read_text(encoding="utf-8")
    language = _detect_language(file_path)

    if language == "python":
        entities = _extract_python_entities(text)
        parser = "python-ast"
    elif language in {"javascript", "typescript", "frontend_style"}:
        entities = _extract_frontend_entities(text, language)
        parser = "regex"
    elif language == "markdown":
        entities = _extract_markdown_entities(text)
        parser = "regex"
    elif language in {"yaml", "toml", "hcl", "shell", "dockerfile"}:
        entities = _extract_devops_entities(text, language)
        parser = "regex"
    else:
        entities = []
        parser = "none"

    return StructuralExtraction(
        file_path=str(file_path),
        language=language,
        entities=entities,
        parser=parser,
    )


def extract_structural_entities_for_files(root: Path, paths: list[str]) -> list[StructuralExtraction]:
    """Extract entities for many repository-relative files."""
    extractions: list[StructuralExtraction] = []
    for rel_path in paths:
        path = root / rel_path
        if not path.exists() or not path.is_file():
            continue
        extractions.append(extract_structural_entities(path))
    return extractions


def _detect_language(file_path: Path) -> str:
    if file_path.name.lower() == "dockerfile":
        return "dockerfile"
    return _LANG_BY_SUFFIX.get(file_path.suffix.lower(), "unknown")


def _extract_python_entities(text: str) -> list[StructuralEntity]:
    entities: list[StructuralEntity] = []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return entities

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            entities.append(
                StructuralEntity(
                    entity_type="function",
                    name=node.name,
                    language="python",
                    line=getattr(node, "lineno", 0),
                )
            )
        elif isinstance(node, ast.ClassDef):
            entities.append(
                StructuralEntity(
                    entity_type="class",
                    name=node.name,
                    language="python",
                    line=getattr(node, "lineno", 0),
                )
            )
        elif isinstance(node, ast.Import):
            for alias in node.names:
                entities.append(
                    StructuralEntity(
                        entity_type="import",
                        name=alias.name,
                        language="python",
                        line=getattr(node, "lineno", 0),
                    )
                )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imported = f"{module}.{alias.name}".strip(".")
                entities.append(
                    StructuralEntity(
                        entity_type="import",
                        name=imported,
                        language="python",
                        line=getattr(node, "lineno", 0),
                    )
                )
        elif isinstance(node, ast.Call):
            call_name = _python_call_name(node.func)
            if call_name:
                entities.append(
                    StructuralEntity(
                        entity_type="call_site",
                        name=call_name,
                        language="python",
                        line=getattr(node, "lineno", 0),
                    )
                )

    return sorted(entities, key=lambda item: (item.line, item.entity_type, item.name))


def _python_call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _python_call_name(node.value)
        if base:
            return f"{base}.{node.attr}"
        return node.attr
    return ""


def _extract_frontend_entities(text: str, language: str) -> list[StructuralEntity]:
    entities: list[StructuralEntity] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        import_match = _IMPORT_RE.match(line)
        if import_match:
            entities.append(
                StructuralEntity(
                    entity_type="import",
                    name=import_match.group(2),
                    language=language,
                    line=idx,
                )
            )
        require_match = _REQUIRE_RE.match(line)
        if require_match:
            entities.append(
                StructuralEntity(
                    entity_type="import",
                    name=require_match.group(1),
                    language=language,
                    line=idx,
                )
            )
        func_match = _FUNC_RE.match(line)
        if func_match:
            entities.append(
                StructuralEntity(
                    entity_type="function",
                    name=func_match.group(1),
                    language=language,
                    line=idx,
                )
            )
        class_match = _CLASS_RE.match(line)
        if class_match:
            entities.append(
                StructuralEntity(
                    entity_type="class",
                    name=class_match.group(1),
                    language=language,
                    line=idx,
                )
            )
        for call in _CALL_RE.finditer(line):
            entities.append(
                StructuralEntity(
                    entity_type="call_site",
                    name=call.group(1),
                    language=language,
                    line=idx,
                )
            )
    return entities


def _extract_markdown_entities(text: str) -> list[StructuralEntity]:
    entities: list[StructuralEntity] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        heading = _MD_HEADING_RE.match(line)
        if heading:
            entities.append(
                StructuralEntity(
                    entity_type="heading",
                    name=heading.group(2).strip(),
                    language="markdown",
                    line=idx,
                    metadata={"level": len(heading.group(1))},
                )
            )
        for link in _MD_LINK_RE.finditer(line):
            entities.append(
                StructuralEntity(
                    entity_type="link",
                    name=link.group(2),
                    language="markdown",
                    line=idx,
                    metadata={"label": link.group(1)},
                )
            )
    return entities


def _extract_devops_entities(text: str, language: str) -> list[StructuralEntity]:
    if language == "dockerfile":
        return _extract_dockerfile_entities(text)
    if language == "hcl":
        return _extract_hcl_entities(text)
    if language == "shell":
        return _extract_shell_entities(text)
    if language == "toml":
        return _extract_toml_entities(text)
    if language == "yaml":
        return _extract_yaml_entities(text)
    return []


def _extract_dockerfile_entities(text: str) -> list[StructuralEntity]:
    entities: list[StructuralEntity] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        from_match = _DOCKER_FROM_RE.match(line)
        if from_match:
            entities.append(
                StructuralEntity(
                    entity_type="dependency",
                    name=from_match.group(1),
                    language="dockerfile",
                    line=idx,
                    metadata={"source": "FROM"},
                )
            )
    return entities


def _extract_hcl_entities(text: str) -> list[StructuralEntity]:
    entities: list[StructuralEntity] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        match = _HCL_BLOCK_RE.match(line)
        if not match:
            continue
        block_type = match.group(1)
        left = match.group(2)
        right = match.group(3)
        name = f"{left}.{right}" if right else left
        entity_type = "dependency" if block_type == "module" else "block"
        entities.append(
            StructuralEntity(
                entity_type=entity_type,
                name=name,
                language="hcl",
                line=idx,
                metadata={"block_type": block_type},
            )
        )
    return entities


def _extract_shell_entities(text: str) -> list[StructuralEntity]:
    entities: list[StructuralEntity] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        func_match = _SHELL_FUNC_RE.match(line)
        if func_match:
            entities.append(
                StructuralEntity(
                    entity_type="function",
                    name=func_match.group(1),
                    language="shell",
                    line=idx,
                )
            )
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        command = stripped.split()[0]
        entities.append(
            StructuralEntity(
                entity_type="call_site",
                name=command,
                language="shell",
                line=idx,
            )
        )
    return entities


def _extract_toml_entities(text: str) -> list[StructuralEntity]:
    entities: list[StructuralEntity] = []
    current_section = ""
    for idx, line in enumerate(text.splitlines(), start=1):
        section_match = _TOML_SECTION_RE.match(line)
        if section_match:
            current_section = section_match.group(1)
            continue
        dep_match = _TOML_DEP_RE.match(line)
        if not dep_match:
            continue
        if "depend" not in current_section and current_section != "project":
            continue
        entities.append(
            StructuralEntity(
                entity_type="dependency",
                name=dep_match.group(1),
                language="toml",
                line=idx,
                metadata={"constraint": dep_match.group(2), "section": current_section},
            )
        )
    return entities


def _extract_yaml_entities(text: str) -> list[StructuralEntity]:
    entities: list[StructuralEntity] = []
    dependency_section_indent: int | None = None
    for idx, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if dependency_section_indent is not None and indent <= dependency_section_indent:
            dependency_section_indent = None

        if _YAML_DEP_SECTION_RE.match(line):
            dependency_section_indent = indent
            continue

        if dependency_section_indent is not None and line.lstrip().startswith("- "):
            dep_name = line.lstrip()[2:].strip()
            if dep_name:
                entities.append(
                    StructuralEntity(
                        entity_type="dependency",
                        name=dep_name,
                        language="yaml",
                        line=idx,
                    )
                )
            continue

        key_match = _YAML_KEY_RE.match(line)
        if key_match:
            entities.append(
                StructuralEntity(
                    entity_type="key",
                    name=key_match.group(1),
                    language="yaml",
                    line=idx,
                )
            )
    return entities
