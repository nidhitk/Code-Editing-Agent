from __future__ import annotations

import ast
import json
import re
from collections import defaultdict
from pathlib import Path

from utils.helpers import read_file


STOPWORDS = {
    "add",
    "another",
    "api",
    "apply",
    "change",
    "code",
    "create",
    "edit",
    "endpoint",
    "file",
    "function",
    "implement",
    "logic",
    "make",
    "modify",
    "need",
    "please",
    "requirement",
    "update",
    "class",
    "model",
    "service",
    "controller",
    "route",
    "handler",
    "user",
    "users",
    "auth",
    "login",
    "token",
}


def _split_identifier(value):
    parts = re.split(r"[^a-zA-Z0-9]+", value)
    tokens = []

    for part in parts:
        if not part:
            continue

        camel = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", part)
        tokens.extend(token.lower() for token in camel.split() if token)

    return tokens


def tokenize_requirement(text):
    tokens = _split_identifier(text)
    return [token for token in tokens if token not in STOPWORDS and len(token) > 1]


def _cache_dir(root):
    return root / ".codex-cache"


def _cache_file(root):
    return _cache_dir(root) / "python_index.json"


def _file_signature(file_path):
    stat = Path(file_path).stat()
    return {
        "path": str(Path(file_path).resolve()),
        "mtime_ns": stat.st_mtime_ns,
        "size": stat.st_size,
    }


def _project_signature(files):
    return {
        signature["path"]: {
            "mtime_ns": signature["mtime_ns"],
            "size": signature["size"],
        }
        for signature in sorted((_file_signature(file_path) for file_path in files), key=lambda item: item["path"])
    }


def _load_cached_index(root, signature):
    cache_path = _cache_file(root)
    if not cache_path.exists():
        return None

    try:
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    if cached.get("project_signature") != signature:
        return None

    return cached.get("index")


def _save_cached_index(root, signature, index):
    cache_path = _cache_file(root)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "project_signature": signature,
        "index": index,
    }
    cache_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _module_name_for_path(root, file_path):
    relative = Path(file_path).resolve().relative_to(root)
    parts = list(relative.with_suffix("").parts)
    return ".".join(parts)


def _resolve_import_module(current_module, node_module, level):
    if not level:
        return node_module or ""

    current_parts = current_module.split(".") if current_module else []
    current_parts = current_parts[:-level] if level <= len(current_parts) else []

    if node_module:
        current_parts.extend(node_module.split("."))

    return ".".join(part for part in current_parts if part)


def _best_module_match(module_name, module_to_file):
    if module_name in module_to_file:
        return module_to_file[module_name]

    parts = module_name.split(".")
    while len(parts) > 1:
        parts = parts[:-1]
        candidate = ".".join(parts)
        if candidate in module_to_file:
            return module_to_file[candidate]

    return None


def _collect_file_metadata(root, file_path, module_to_file):
    source = read_file(file_path)
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return {
            "symbols": set(),
            "imports": set(),
            "content_tokens": set(),
            "definitions": [],
        }

    symbols = set()
    imports = set()
    definitions = []
    lines = source.splitlines()

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            symbols.add(node.name)
            end_line = getattr(node, "end_lineno", node.lineno)
            snippet = "\n".join(lines[node.lineno - 1 : end_line]).strip()
            definitions.append(
                {
                    "kind": type(node).__name__,
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": end_line,
                    "snippet": snippet,
                    "tokens": tokenize_requirement(f"{node.name} {snippet}"),
                }
            )
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    symbols.add(target.id)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name
                imports.add(module_name)
        elif isinstance(node, ast.ImportFrom):
            module_name = _resolve_import_module(
                _module_name_for_path(root, file_path),
                node.module or "",
                node.level or 0,
            )
            if module_name:
                imports.add(module_name)
            for alias in node.names:
                if alias.name != "*":
                    symbols.add(alias.asname or alias.name)

    content_tokens = set(tokenize_requirement(source))
    content_tokens.update(token.lower() for token in Path(file_path).stem.split("_") if token)

    return {
        "symbols": symbols,
        "imports": imports,
        "content_tokens": content_tokens,
        "definitions": definitions,
    }


def build_python_index(project_path, files):
    root = Path(project_path).resolve()
    python_files = [Path(file).resolve() for file in files if Path(file).suffix == ".py"]
    signature = _project_signature(python_files)
    cached_index = _load_cached_index(root, signature)
    if cached_index is not None:
        return cached_index

    module_to_file = {
        _module_name_for_path(root, file_path): str(file_path)
        for file_path in python_files
    }

    metadata = {}
    dependency_graph = defaultdict(set)
    reverse_dependency_graph = defaultdict(set)

    for file_path in python_files:
        file_key = str(file_path)
        info = _collect_file_metadata(root, file_path, module_to_file)
        metadata[file_key] = info

        for module_name in info["imports"]:
            resolved = _best_module_match(module_name, module_to_file)
            if resolved and resolved != file_key:
                dependency_graph[file_key].add(resolved)
                reverse_dependency_graph[resolved].add(file_key)

    index = {
        "module_to_file": module_to_file,
        "metadata": {
            key: {
                "symbols": sorted(value.get("symbols", set())),
                "imports": sorted(value.get("imports", set())),
                "content_tokens": sorted(value.get("content_tokens", set())),
                "definitions": value.get("definitions", []),
            }
            for key, value in metadata.items()
        },
        "dependency_graph": {key: sorted(value) for key, value in dependency_graph.items()},
        "reverse_dependency_graph": {key: sorted(value) for key, value in reverse_dependency_graph.items()},
        "project_signature": signature,
    }
    _save_cached_index(root, signature, index)
    return index


def _score_file(requirement_tokens, file_path, metadata):
    info = metadata.get(file_path, {})
    file_tokens = set()
    file_tokens.update(token.lower() for token in Path(file_path).stem.split("_") if token)
    file_tokens.update(_split_identifier(Path(file_path).stem))
    file_tokens.update(info.get("content_tokens", []))

    symbols = set(info.get("symbols", []))
    imports = set(info.get("imports", []))

    score = len(requirement_tokens & file_tokens) * 3
    score += len(requirement_tokens & {symbol.lower() for symbol in symbols}) * 4
    score += len(requirement_tokens & {token.lower() for token in imports})
    return score


def select_relevant_files(requirement, project_summary, limit=3):
    files = project_summary.get("files", [])
    metadata = project_summary.get("ast_metadata", {})
    requirement_tokens = set(tokenize_requirement(requirement))

    if not files:
        return [], []

    scored = [
        (_score_file(requirement_tokens, file_path, metadata), file_path)
        for file_path in files
        if Path(file_path).suffix == ".py"
    ]

    scored.sort(key=lambda item: item[0], reverse=True)
    selected = [file_path for score, file_path in scored[:limit] if score > 0]

    if not selected:
        selected = [file_path for _, file_path in scored[:limit]]

    dependency_graph = project_summary.get("dependency_graph", {})
    reverse_dependency_graph = project_summary.get("reverse_dependency_graph", {})

    dependency_set = set(selected)
    queue = list(selected)

    while queue:
        file_path = queue.pop(0)
        for dep in dependency_graph.get(file_path, []):
            if dep not in dependency_set:
                dependency_set.add(dep)
                queue.append(dep)
        for dependent in reverse_dependency_graph.get(file_path, []):
            if dependent not in dependency_set:
                dependency_set.add(dependent)
                queue.append(dependent)

    return selected, sorted(dependency_set)


def _score_definition(requirement_tokens, definition):
    tokens = set(definition.get("tokens", []))
    name_tokens = set(_split_identifier(definition.get("name", "")))
    kind_tokens = set(_split_identifier(definition.get("kind", "")))
    score = len(requirement_tokens & tokens) * 3
    score += len(requirement_tokens & name_tokens) * 5
    score += len(requirement_tokens & kind_tokens)
    return score


def _fallback_snippet(source, limit_lines=40):
    lines = source.splitlines()
    return "\n".join(lines[:limit_lines]).strip()


def choose_best_definition(requirement, file_path, metadata=None, source=None):
    metadata = metadata or {}
    source = source if source is not None else read_file(file_path)
    requirement_tokens = set(tokenize_requirement(requirement))
    definitions = metadata.get(file_path, {}).get("definitions", [])

    if definitions:
        scored = sorted(
            ((_score_definition(requirement_tokens, definition), definition) for definition in definitions),
            key=lambda item: item[0],
            reverse=True,
        )
        best_score, best_definition = scored[0]
        if best_score > 0:
            return best_definition
        return best_definition

    return {
        "kind": "module",
        "name": Path(file_path).stem,
        "start_line": 1,
        "end_line": min(40, len(source.splitlines())),
        "snippet": _fallback_snippet(source),
        "tokens": tokenize_requirement(source[:2000]),
    }


def select_relevant_snippets(requirement, project_summary, limit=3, per_file_limit=2):
    relevant_files = project_summary.get("relevant_files") or project_summary.get("files", [])
    dependency_files = project_summary.get("dependency_files", [])
    metadata = project_summary.get("ast_metadata", {})
    file_contents = project_summary.get("file_contents", {})
    requirement_tokens = set(tokenize_requirement(requirement))

    files = []
    for file_path in relevant_files + dependency_files:
        if file_path not in files:
            files.append(file_path)

    snippets = {}
    for file_path in files[:limit]:
        info = metadata.get(file_path, {})
        definitions = info.get("definitions", [])
        chosen = []

        if definitions:
            scored = sorted(
                ((_score_definition(requirement_tokens, definition), definition) for definition in definitions),
                key=lambda item: item[0],
                reverse=True,
            )
            for score, definition in scored[:per_file_limit]:
                chosen.append(
                    {
                        "kind": definition.get("kind"),
                        "name": definition.get("name"),
                        "snippet": definition.get("snippet", ""),
                        "start_line": definition.get("start_line"),
                        "end_line": definition.get("end_line"),
                    }
                )

        if not chosen:
            source = file_contents.get(file_path, "")
            if source:
                chosen.append(
                    {
                        "kind": "module",
                        "name": Path(file_path).stem,
                        "snippet": _fallback_snippet(source),
                        "start_line": 1,
                        "end_line": min(40, len(source.splitlines())),
                    }
                )

        snippets[file_path] = chosen

    return snippets


def collect_impacted_files(changed_files, project_summary):
    reverse_dependency_graph = project_summary.get("reverse_dependency_graph", {})

    impacted = set()
    queue = list(changed_files)

    while queue:
        file_path = queue.pop(0)
        for dependent in reverse_dependency_graph.get(file_path, []):
            if dependent not in impacted and dependent not in changed_files:
                impacted.add(dependent)
                queue.append(dependent)

    return sorted(impacted)
