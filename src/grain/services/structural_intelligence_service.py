# SPDX-FileCopyrightText: 2024-2026 Shaznay Sison
# SPDX-License-Identifier: Apache-2.0

"""Deterministic structural entity extraction service (Phase 10 Layer 1)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
import re

try:
    from tree_sitter_language_pack import get_parser
except Exception:  # pragma: no cover - dependency may be unavailable
    get_parser = None


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
    ".tsx": "tsx",
    ".css": "css",
    ".scss": "scss",
    ".md": "markdown",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".hcl": "hcl",
    ".tf": "hcl",
    ".sh": "shell",
    ".bash": "shell",
    ".zsh": "shell",
    ".rs": "rust",
    ".go": "go",
    ".java": "java",
}

_PARSER_BY_LANGUAGE: dict[str, str] = {
    "python": "python",
    "javascript": "javascript",
    "typescript": "typescript",
    "tsx": "tsx",
    "css": "css",
    "scss": "scss",
    "markdown": "markdown",
    "yaml": "yaml",
    "toml": "toml",
    "hcl": "hcl",
    "shell": "bash",
    "rust": "rust",
    "go": "go",
    "java": "java",
    "dockerfile": "dockerfile",
}

_DEPENDENCY_KEYS = {"depends_on", "dependencies", "requires", "dependency", "deps"}


def extract_structural_entities(file_path: Path, content: str | None = None) -> StructuralExtraction:
    """Extract normalized structural entities from a source artifact.

    Layer 1 is deterministic and local-only. No LLMs or remote calls.
    Uses tree-sitter parsers where grammars are available.
    """
    text = content if content is not None else file_path.read_text(encoding="utf-8")
    language = _detect_language(file_path)
    parser_name = _PARSER_BY_LANGUAGE.get(language)

    if get_parser is None or not parser_name:
        return StructuralExtraction(
            file_path=str(file_path),
            language=language,
            entities=_extract_entities_without_parser(text, language),
            parser="tree-sitter" if parser_name else "none",
        )

    try:
        parser = get_parser(parser_name)
        tree = parser.parse(text.encode("utf-8"))
    except Exception:
        return StructuralExtraction(
            file_path=str(file_path),
            language=language,
            entities=_extract_entities_without_parser(text, language),
            parser="tree-sitter",
        )

    entities = _extract_entities_by_language(tree.root_node, text, language)
    entities = sorted(
        _dedupe_entities(entities),
        key=lambda item: (item.line, item.entity_type, item.name),
    )

    return StructuralExtraction(
        file_path=str(file_path),
        language=language,
        entities=entities,
        parser="tree-sitter",
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


def _extract_entities_by_language(root_node, text: str, language: str) -> list[StructuralEntity]:
    if language == "python":
        return _extract_python_entities(root_node, text)
    if language in {"javascript", "typescript", "tsx"}:
        return _extract_js_family_entities(root_node, text, language)
    if language == "markdown":
        return _extract_markdown_entities(root_node, text)
    if language in {"yaml", "dockerfile", "hcl", "toml", "shell"}:
        return _extract_devops_entities(root_node, text, language)
    return _extract_generic_code_entities(root_node, text, language)


def _extract_entities_without_parser(text: str, language: str) -> list[StructuralEntity]:
    if language == "python":
        return _extract_python_entities_fallback(text)
    if language in {"javascript", "typescript", "tsx"}:
        return _extract_js_family_entities_fallback(text, language)
    if language == "markdown":
        return _extract_markdown_entities_fallback(text)
    if language in {"yaml", "dockerfile", "hcl", "toml", "shell"}:
        return _extract_devops_entities_fallback(text, language)
    return []


def _extract_python_entities(root_node, text: str) -> list[StructuralEntity]:
    entities: list[StructuralEntity] = []
    for node in _walk(root_node):
        if node.type == "function_definition":
            name = _field_text(node, "name", text)
            if name:
                entities.append(_entity("function", name, "python", node.start_point[0] + 1))
        elif node.type == "class_definition":
            name = _field_text(node, "name", text)
            if name:
                entities.append(_entity("class", name, "python", node.start_point[0] + 1))
        elif node.type in {"import_statement", "import_from_statement"}:
            for import_name in _python_import_names(_node_text(node, text)):
                entities.append(_entity("import", import_name, "python", node.start_point[0] + 1))
        elif node.type == "call":
            func_node = node.child_by_field_name("function")
            call_name = _call_name(func_node, text)
            if call_name:
                entities.append(_entity("call_site", call_name, "python", node.start_point[0] + 1))
    return entities


def _extract_python_entities_fallback(text: str) -> list[StructuralEntity]:
    entities: list[StructuralEntity] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("import "):
            for name in _python_import_names(stripped):
                entities.append(_entity("import", name, "python", line_no))
        elif stripped.startswith("from "):
            for name in _python_import_names(stripped):
                entities.append(_entity("import", name, "python", line_no))
        match = re.match(r"class\s+([A-Za-z_][A-Za-z0-9_]*)", stripped)
        if match:
            entities.append(_entity("class", match.group(1), "python", line_no))
        match = re.match(r"def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", stripped)
        if match:
            entities.append(_entity("function", match.group(1), "python", line_no))
        for call in re.findall(r"([A-Za-z_][A-Za-z0-9_\.]*)\s*\(", stripped):
            if call not in {"def", "class", "if", "for", "while", "return"}:
                entities.append(_entity("call_site", call, "python", line_no))
    return entities


def _python_import_names(statement: str) -> list[str]:
    statement = " ".join(statement.split())
    if statement.startswith("import "):
        raw = statement[len("import ") :]
        names = []
        for part in raw.split(","):
            token = part.strip().split(" as ")[0].strip()
            if token:
                names.append(token)
        return names
    if statement.startswith("from ") and " import " in statement:
        left, right = statement[len("from ") :].split(" import ", 1)
        module = left.strip()
        names = []
        for part in right.split(","):
            token = part.strip().split(" as ")[0].strip()
            if not token:
                continue
            names.append(f"{module}.{token}".strip("."))
        return names
    return []


def _extract_js_family_entities(root_node, text: str, language: str) -> list[StructuralEntity]:
    entities: list[StructuralEntity] = []
    for node in _walk(root_node):
        if node.type == "import_statement":
            source = _field_text(node, "source", text)
            source = _strip_quotes(source)
            if source:
                entities.append(_entity("import", source, language, node.start_point[0] + 1))
        elif node.type in {"function_declaration", "method_definition"}:
            name = _field_text(node, "name", text)
            if name:
                entities.append(_entity("function", name, language, node.start_point[0] + 1))
        elif node.type == "class_declaration":
            name = _field_text(node, "name", text)
            if name:
                entities.append(_entity("class", name, language, node.start_point[0] + 1))
        elif node.type == "call_expression":
            function_node = node.child_by_field_name("function")
            call_name = _call_name(function_node, text)
            if call_name:
                entities.append(_entity("call_site", call_name, language, node.start_point[0] + 1))
    return entities


def _extract_js_family_entities_fallback(text: str, language: str) -> list[StructuralEntity]:
    entities: list[StructuralEntity] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        match = re.match(r'import\s+.+?\s+from\s+[\'"]([^\'"]+)[\'"]', stripped)
        if match:
            entities.append(_entity("import", match.group(1), language, line_no))
        match = re.match(r"function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", stripped)
        if match:
            entities.append(_entity("function", match.group(1), language, line_no))
        match = re.match(r"class\s+([A-Za-z_][A-Za-z0-9_]*)", stripped)
        if match:
            entities.append(_entity("class", match.group(1), language, line_no))
        for call in re.findall(r"([A-Za-z_][A-Za-z0-9_\.]*)\s*\(", stripped):
            if call not in {"function", "if", "for", "while", "return"}:
                entities.append(_entity("call_site", call, language, line_no))
    return entities


def _extract_markdown_entities(root_node, text: str) -> list[StructuralEntity]:
    entities: list[StructuralEntity] = []
    for node in _walk(root_node):
        if node.type in {"atx_heading", "setext_heading"}:
            heading = _field_text(node, "heading_content", text) or _node_text(node, text)
            heading = heading.lstrip("#").strip().strip("=").strip()
            if heading:
                entities.append(_entity("heading", heading, "markdown", node.start_point[0] + 1))

    for link_name, line in _scan_markdown_links(text):
        entities.append(_entity("link", link_name, "markdown", line, {"label": ""}))
    return entities


def _extract_markdown_entities_fallback(text: str) -> list[StructuralEntity]:
    entities: list[StructuralEntity] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
            if heading:
                entities.append(_entity("heading", heading, "markdown", line_no))
    for link_name, line in _scan_markdown_links(text):
        entities.append(_entity("link", link_name, "markdown", line, {"label": ""}))
    return entities


def _scan_markdown_links(text: str) -> list[tuple[str, int]]:
    results: list[tuple[str, int]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        cursor = 0
        while True:
            left = line.find("[", cursor)
            if left < 0:
                break
            mid = line.find("](", left + 1)
            if mid < 0:
                cursor = left + 1
                continue
            right = line.find(")", mid + 2)
            if right < 0:
                cursor = mid + 2
                continue
            link_target = line[mid + 2 : right].strip()
            if link_target:
                results.append((link_target, line_no))
            cursor = right + 1
    return results


def _extract_devops_entities(root_node, text: str, language: str) -> list[StructuralEntity]:
    if language == "dockerfile":
        return _extract_dockerfile_entities(root_node, text)
    if language == "yaml":
        return _extract_yaml_entities(root_node, text)
    if language == "hcl":
        return _extract_hcl_entities(root_node, text)
    if language == "toml":
        return _extract_toml_entities(root_node, text)
    if language == "shell":
        return _extract_shell_entities(root_node, text)
    return []


def _extract_devops_entities_fallback(text: str, language: str) -> list[StructuralEntity]:
    if language == "dockerfile":
        return _extract_dockerfile_entities_fallback(text)
    if language == "yaml":
        return _extract_yaml_entities_fallback(text)
    return []


def _extract_dockerfile_entities(root_node, text: str) -> list[StructuralEntity]:
    entities: list[StructuralEntity] = []
    for node in _walk(root_node):
        if node.type != "from_instruction":
            continue
        dep = ""
        for child in node.children:
            if child.type == "image_spec":
                dep = _node_text(child, text).strip()
                break
        if dep:
            entities.append(_entity("dependency", dep, "dockerfile", node.start_point[0] + 1, {"source": "FROM"}))
    return entities


def _extract_dockerfile_entities_fallback(text: str) -> list[StructuralEntity]:
    entities: list[StructuralEntity] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped.upper().startswith("FROM "):
            continue
        dep = stripped[5:].strip().split(" AS ", 1)[0].split(" as ", 1)[0].strip()
        if dep:
            entities.append(_entity("dependency", dep, "dockerfile", line_no, {"source": "FROM"}))
    return entities


def _extract_yaml_entities(root_node, text: str) -> list[StructuralEntity]:
    entities: list[StructuralEntity] = []
    for node in _walk(root_node):
        if node.type != "block_mapping_pair":
            continue
        key_node = node.child_by_field_name("key")
        value_node = node.child_by_field_name("value")
        key_name = _scalar_text(key_node, text).lower()
        if key_name not in _DEPENDENCY_KEYS or value_node is None:
            continue
        for value in _yaml_scalar_values(value_node, text):
            entities.append(_entity("dependency", value, "yaml", node.start_point[0] + 1))
    return entities


def _extract_yaml_entities_fallback(text: str) -> list[StructuralEntity]:
    entities: list[StructuralEntity] = []
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.rstrip(":").lower() not in _DEPENDENCY_KEYS and not any(
            stripped.lower().startswith(f"{key}:") for key in _DEPENDENCY_KEYS
        ):
            continue
        line_no = idx + 1
        base_indent = len(line) - len(line.lstrip())
        for child in lines[idx + 1 :]:
            if not child.strip():
                continue
            indent = len(child) - len(child.lstrip())
            if indent <= base_indent:
                break
            value = child.strip()
            if value.startswith("- "):
                dep = value[2:].strip().strip('"').strip("'")
                if dep:
                    entities.append(_entity("dependency", dep, "yaml", line_no))
    return entities


def _yaml_scalar_values(node, text: str) -> list[str]:
    values: list[str] = []
    for candidate in _walk(node):
        if candidate.type in {"string_scalar", "plain_scalar", "flow_scalar", "integer_scalar", "float_scalar"}:
            value = _node_text(candidate, text).strip().strip('"').strip("'")
            if value and value not in {"-"}:
                values.append(value)
    # block_mapping key names appear as scalars too; remove obvious key tokens.
    return [item for item in values if item.lower() not in _DEPENDENCY_KEYS]


def _extract_hcl_entities(root_node, text: str) -> list[StructuralEntity]:
    entities: list[StructuralEntity] = []
    for node in _walk(root_node):
        if node.type != "block":
            continue
        labels = [_node_text(child, text).strip().strip('"') for child in node.children if child.type in {"identifier", "string_lit"}]
        if not labels:
            continue
        block_type = labels[0]
        if block_type not in {"resource", "module", "variable", "output"}:
            continue
        name = ".".join(label for label in labels[1:] if label)
        dependency_name = f"{block_type}.{name}" if name else block_type
        entities.append(_entity("dependency", dependency_name, "hcl", node.start_point[0] + 1))
    return entities


def _extract_toml_entities(root_node, text: str) -> list[StructuralEntity]:
    entities: list[StructuralEntity] = []
    for node in _walk(root_node):
        if node.type != "pair":
            continue
        key_node = node.child_by_field_name("key")
        value_node = node.child_by_field_name("value")
        key = _node_text(key_node, text).strip().strip('"').strip("'") if key_node else ""
        value = _node_text(value_node, text).strip().strip('"').strip("'") if value_node else ""
        if not key or not value:
            continue
        if key in {"name", "version", "description", "license", "requires-python"}:
            continue
        entities.append(_entity("dependency", key, "toml", node.start_point[0] + 1, {"value": value}))
    return entities


def _extract_shell_entities(root_node, text: str) -> list[StructuralEntity]:
    entities: list[StructuralEntity] = []
    for node in _walk(root_node):
        if node.type == "function_definition":
            for child in node.children:
                if child.type == "word":
                    name = _node_text(child, text).strip()
                    if name:
                        entities.append(_entity("function", name, "shell", node.start_point[0] + 1))
                    break
        elif node.type == "command":
            for child in node.children:
                if child.type == "command_name":
                    name = _node_text(child, text).strip()
                    if name:
                        entities.append(_entity("call_site", name, "shell", node.start_point[0] + 1))
                    break
    return entities


def _extract_generic_code_entities(root_node, text: str, language: str) -> list[StructuralEntity]:
    entities: list[StructuralEntity] = []
    for node in _walk(root_node):
        if node.type in {"function_item", "function_declaration", "function_definition", "method_declaration", "method_definition"}:
            name = _field_text(node, "name", text)
            if name:
                entities.append(_entity("function", name, language, node.start_point[0] + 1))
        elif node.type in {"class_item", "class_declaration", "class_definition"}:
            name = _field_text(node, "name", text)
            if name:
                entities.append(_entity("class", name, language, node.start_point[0] + 1))
        elif node.type in {"import_declaration", "use_declaration", "include_directive"}:
            value = _node_text(node, text).strip()
            if value:
                entities.append(_entity("import", value, language, node.start_point[0] + 1))
        elif node.type in {"call_expression", "call"}:
            function_node = node.child_by_field_name("function")
            call_name = _call_name(function_node, text)
            if call_name:
                entities.append(_entity("call_site", call_name, language, node.start_point[0] + 1))
    return entities


def _walk(node):
    stack = [node]
    while stack:
        current = stack.pop()
        yield current
        for idx in range(current.child_count - 1, -1, -1):
            child = current.child(idx)
            if child is not None:
                stack.append(child)


def _entity(
    entity_type: str,
    name: str,
    language: str,
    line: int,
    metadata: dict[str, object] | None = None,
) -> StructuralEntity:
    return StructuralEntity(
        entity_type=entity_type,
        name=name,
        language=language,
        line=line,
        metadata=metadata or {},
    )


def _field_text(node, field_name: str, text: str) -> str:
    child = node.child_by_field_name(field_name)
    if child is None:
        return ""
    return _strip_quotes(_node_text(child, text).strip())


def _node_text(node, text: str) -> str:
    if node is None:
        return ""
    return text[node.start_byte : node.end_byte]


def _scalar_text(node, text: str) -> str:
    if node is None:
        return ""
    for candidate in _walk(node):
        if candidate.type in {"string_scalar", "plain_scalar", "string_fragment", "identifier", "bare_key"}:
            value = _node_text(candidate, text).strip().strip('"').strip("'")
            if value:
                return value
    return _node_text(node, text).strip().strip('"').strip("'")


def _call_name(node, text: str) -> str:
    if node is None:
        return ""
    if node.type in {
        "identifier",
        "property_identifier",
        "field_identifier",
        "type_identifier",
        "word",
    }:
        return _node_text(node, text).strip()
    if node.type in {"attribute", "member_expression"}:
        parts = []
        object_node = node.child_by_field_name("object")
        property_node = node.child_by_field_name("attribute") or node.child_by_field_name("property")
        if object_node is not None:
            left = _call_name(object_node, text)
            if left:
                parts.append(left)
        if property_node is not None:
            right = _call_name(property_node, text)
            if right:
                parts.append(right)
        if parts:
            return ".".join(parts)
    for child in node.children:
        value = _call_name(child, text)
        if value:
            return value
    return ""


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _dedupe_entities(entities: list[StructuralEntity]) -> list[StructuralEntity]:
    seen: set[tuple[str, str, str, int]] = set()
    deduped: list[StructuralEntity] = []
    for entity in entities:
        key = (entity.entity_type, entity.name, entity.language, entity.line)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(entity)
    return deduped
