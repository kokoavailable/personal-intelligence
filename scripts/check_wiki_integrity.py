#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WIKI_DIRS = (
    ROOT / "wiki" / "topics",
    ROOT / "wiki" / "decisions",
    ROOT / "wiki" / "anti-patterns",
)
ALLOWED_KEYS = {"id", "type", "source", "valid_from"}
REQUIRED_KEYS = {"id", "type", "source", "valid_from"}
ALLOWED_TYPES = {"topic", "decision", "anti-pattern"}
SOURCE_ID_RE = re.compile(r"^src_[A-Za-z0-9][A-Za-z0-9_-]*$")


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


def validate_sources(path: Path, sources: object, errors: list[str]) -> list[str]:
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
    return normalized


def validate_file(
    path: Path,
    ids: dict[str, list[Path]],
    source_sets: dict[tuple[str, tuple[str, ...]], list[Path]],
    errors: list[str],
) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{rel(path)}: could not read file: {exc}")
        return

    frontmatter, _body = split_frontmatter(text)
    if frontmatter is None:
        errors.append(f"{rel(path)}: missing YAML frontmatter")
        return

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

    sources = validate_sources(path, data.get("source"), errors)
    if isinstance(note_type, str) and sources:
        signature = (note_type, tuple(sorted(sources)))
        source_sets.setdefault(signature, []).append(path)


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    ids: dict[str, list[Path]] = {}
    source_sets: dict[tuple[str, tuple[str, ...]], list[Path]] = {}

    for directory in WIKI_DIRS:
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*.md")):
            validate_file(path, ids, source_sets, errors)

    for note_id, paths in sorted(ids.items()):
        if len(paths) > 1:
            joined = ", ".join(rel(path) for path in paths)
            errors.append(f"duplicate id '{note_id}': {joined}")

    for (_note_type, _sources), paths in sorted(source_sets.items()):
        if len(paths) > 1:
            joined = ", ".join(rel(path) for path in paths)
            warnings.append(f"possible duplicate wiki notes with same type and source set: {joined}")

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
