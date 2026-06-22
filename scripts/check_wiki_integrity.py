#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from compiled_sources_registry import COMPILED_SOURCES, CompiledSourcesRegistry, SOURCE_ID_RE, load_registry


ROOT = Path(__file__).resolve().parents[1]
WIKI_DIRS = (
    ROOT / "wiki" / "topics",
    ROOT / "wiki" / "decisions",
    ROOT / "wiki" / "anti-patterns",
)
ALLOWED_KEYS = {"id", "type", "source", "valid_from"}
REQUIRED_KEYS = {"id", "type", "source", "valid_from"}
ALLOWED_TYPES = {"topic", "decision", "anti-pattern"}


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def clean_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] in {"'", '"'} and value[-1] == value[0]:
        return value[1:-1]
    return value


def split_frontmatter(text: str) -> tuple[list[str] | None, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[1:index], "\n".join(lines[index + 1 :])
    return None, text


def parse_frontmatter(path: Path, lines: list[str], errors: list[str]) -> dict[str, object]:
    data: dict[str, object] = {}
    current_key: str | None = None

    for offset, line in enumerate(lines, start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if line.startswith((" ", "\t")):
            if current_key == "source" and stripped.startswith("- "):
                source_value = clean_value(stripped[2:])
                source_list = data.setdefault("source", [])
                if isinstance(source_list, list):
                    source_list.append(source_value)
                else:
                    errors.append(f"{rel(path)}:{offset}: source must be a list")
                continue
            errors.append(f"{rel(path)}:{offset}: unsupported indented frontmatter")
            continue

        current_key = None
        if ":" not in line:
            errors.append(f"{rel(path)}:{offset}: malformed frontmatter line")
            continue

        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()

        if key in data:
            errors.append(f"{rel(path)}:{offset}: duplicate frontmatter key '{key}'")
            continue

        if value:
            data[key] = clean_value(value)
        elif key == "source":
            data[key] = []
            current_key = key
        else:
            data[key] = ""

    return data


def validate_sources(path: Path, sources: object, errors: list[str], registry_source_ids: set[str] | None = None) -> list[str]:
    if not isinstance(sources, list) or not sources:
        errors.append(f"{rel(path)}: source must be a non-empty list")
        return []

    normalized: list[str] = []
    for source in sources:
        if not isinstance(source, str) or not source.strip():
            errors.append(f"{rel(path)}: source entries must be non-empty strings")
            continue
        normalized.append(source)
        if source.startswith("raw/"):
            errors.append(f"{rel(path)}: source entries must use source IDs, not raw paths: {source}")
        elif not SOURCE_ID_RE.fullmatch(source):
            errors.append(f"{rel(path)}: source entry must match src_[A-Za-z0-9][A-Za-z0-9_-]*: {source}")
        elif registry_source_ids is not None and source not in registry_source_ids:
            errors.append(f"{rel(path)}: source ID absent from {rel(COMPILED_SOURCES)}: {source}")
    return normalized


def validate_file(
    path: Path,
    ids: dict[str, list[Path]],
    source_sets: dict[tuple[str, tuple[str, ...]], list[Path]],
    errors: list[str],
    registry_source_ids: set[str] | None = None,
) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{rel(path)}: could not read file: {exc}")
        return []

    frontmatter, _body = split_frontmatter(text)
    if frontmatter is None:
        errors.append(f"{rel(path)}: missing YAML frontmatter")
        return []

    data = parse_frontmatter(path, frontmatter, errors)
    keys = set(data)
    extra_keys = keys - ALLOWED_KEYS
    missing_keys = REQUIRED_KEYS - keys

    for key in sorted(extra_keys):
        errors.append(f"{rel(path)}: unsupported frontmatter key '{key}'")
    for key in sorted(missing_keys):
        errors.append(f"{rel(path)}: missing frontmatter key '{key}'")

    note_id = data.get("id")
    if isinstance(note_id, str) and note_id:
        ids.setdefault(note_id, []).append(path)
    else:
        errors.append(f"{rel(path)}: id must be a non-empty string")

    note_type = data.get("type")
    if note_type not in ALLOWED_TYPES:
        errors.append(f"{rel(path)}: type must be one of {', '.join(sorted(ALLOWED_TYPES))}")

    sources = validate_sources(path, data.get("source"), errors, registry_source_ids)
    if isinstance(note_type, str) and sources:
        signature = (note_type, tuple(sorted(sources)))
        source_sets.setdefault(signature, []).append(path)
    return sources


def wiki_paths() -> list[Path]:
    paths: list[Path] = []
    for directory in WIKI_DIRS:
        if directory.exists():
            paths.extend(directory.rglob("*.md"))
    return sorted(paths, key=rel)


def validate_registry_relationships(
    note_sources: dict[str, list[str]],
    registry: CompiledSourcesRegistry,
    errors: list[str],
) -> None:
    for note_path, sources in sorted(note_sources.items()):
        for source_id in sources:
            if not SOURCE_ID_RE.fullmatch(source_id):
                continue
            entry = registry.entries.get(source_id)
            if entry is None:
                continue
            if note_path not in entry.outputs:
                errors.append(f"{note_path}: source ID {source_id} does not list this note in {rel(COMPILED_SOURCES)} outputs")

    for entry in registry.entries.values():
        for output in entry.outputs:
            output_path = ROOT / output
            if not output_path.is_file():
                errors.append(f"{rel(COMPILED_SOURCES)}: output for {entry.source_id} does not exist: {output}")
                continue
            output_sources = note_sources.get(output, [])
            if entry.source_id not in output_sources:
                errors.append(f"{rel(COMPILED_SOURCES)}: output {output} does not reference source ID {entry.source_id}")


def validate_wiki() -> tuple[list[Path], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    ids: dict[str, list[Path]] = {}
    source_sets: dict[tuple[str, tuple[str, ...]], list[Path]] = {}
    note_sources: dict[str, list[str]] = {}
    registry, registry_errors = load_registry(COMPILED_SOURCES, ROOT)
    errors.extend(registry_errors)
    registry_source_ids = registry.source_ids if not registry_errors else None

    paths = wiki_paths()
    for path in paths:
        sources = validate_file(path, ids, source_sets, errors, registry_source_ids)
        if sources:
            note_sources[rel(path)] = sources

    for note_id, note_paths in sorted(ids.items()):
        if len(note_paths) > 1:
            joined = ", ".join(rel(path) for path in note_paths)
            errors.append(f"duplicate id '{note_id}': {joined}")

    for (_note_type, _sources), note_paths in sorted(source_sets.items()):
        if len(note_paths) > 1:
            joined = ", ".join(rel(path) for path in note_paths)
            warnings.append(f"possible duplicate wiki notes with same type and source set: {joined}")

    if not registry_errors:
        validate_registry_relationships(note_sources, registry, errors)

    return paths, errors, warnings


def main() -> int:
    _paths, errors, warnings = validate_wiki()

    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    for error in errors:
        print(f"error: {error}", file=sys.stderr)

    if errors:
        return 1
    print("Wiki integrity check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
