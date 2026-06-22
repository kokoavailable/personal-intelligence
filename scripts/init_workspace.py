#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from compiled_sources_registry import load_compiled_sources_items


ROOT = Path(__file__).resolve().parents[1]
BEGIN_MARKER = "<!-- BEGIN GENERATED WIKI INDEX -->"
END_MARKER = "<!-- END GENERATED WIKI INDEX -->"

REQUIRED_DIRS = (
    ROOT / "raw" / "imported",
    ROOT / "raw" / "inbox",
    ROOT / ".private" / "eval_runs",
    ROOT / "wiki" / "topics",
    ROOT / "wiki" / "decisions",
    ROOT / "wiki" / "anti-patterns",
    ROOT / "public" / "drafts",
)
INITIAL_FILES = {
    ROOT / ".private" / "compiled_sources.yml": "compiled_sources: []\n",
    ROOT / ".private" / "knowledge_cycle_log.md": "# Knowledge Cycle Log\n\n",
    ROOT / "wiki" / "index.md": (
        "# Wiki Index\n"
        "\n"
        "Generated view of compiled durable wiki notes.\n"
        "\n"
        "<!-- BEGIN GENERATED WIKI INDEX -->\n"
        "_No compiled wiki notes found._\n"
        "<!-- END GENERATED WIKI INDEX -->\n"
    ),
}


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def path_exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def validate_compiled_sources(path: Path, errors: list[str]) -> None:
    _items, registry_errors = load_compiled_sources_items(path, ROOT)
    errors.extend(registry_errors)


def validate_index(path: Path, errors: list[str]) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{rel(path)}: could not read file: {exc}")
        return
    begin_count = text.count(BEGIN_MARKER)
    end_count = text.count(END_MARKER)
    if begin_count != 1:
        errors.append(f"{rel(path)}: expected exactly one begin marker")
    if end_count != 1:
        errors.append(f"{rel(path)}: expected exactly one end marker")
    if begin_count == 1 and end_count == 1 and text.find(END_MARKER) < text.find(BEGIN_MARKER):
        errors.append(f"{rel(path)}: generated wiki index markers are misordered")


def validate_log(path: Path, errors: list[str]) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{rel(path)}: could not read file: {exc}")
        return
    if not text.strip():
        errors.append(f"{rel(path)}: file must not be empty")


def validate_workspace() -> list[str]:
    errors: list[str] = []
    for directory in REQUIRED_DIRS:
        if path_exists(directory) and not directory.is_dir():
            errors.append(f"{rel(directory)}: expected directory, found file")
        elif not path_exists(directory):
            errors.append(f"{rel(directory)}: missing required directory")

    for path in INITIAL_FILES:
        if path_exists(path) and not path.is_file():
            errors.append(f"{rel(path)}: expected file, found directory")
        elif not path_exists(path):
            errors.append(f"{rel(path)}: missing required file")

    compiled_sources = ROOT / ".private" / "compiled_sources.yml"
    index = ROOT / "wiki" / "index.md"
    log = ROOT / ".private" / "knowledge_cycle_log.md"
    if compiled_sources.is_file():
        validate_compiled_sources(compiled_sources, errors)
    if index.is_file():
        validate_index(index, errors)
    if log.is_file():
        validate_log(log, errors)
    return errors


def check_workspace() -> int:
    errors = validate_workspace()
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    if errors:
        return 1
    print("Workspace initialization check passed.")
    return 0


def write_workspace() -> int:
    for directory in REQUIRED_DIRS:
        if path_exists(directory):
            continue
        try:
            directory.mkdir(parents=True)
        except OSError as exc:
            print(f"error: could not create {rel(directory)}/: {exc}", file=sys.stderr)
        else:
            print(f"Created {rel(directory)}/")

    for path, content in INITIAL_FILES.items():
        if path_exists(path):
            continue
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        except OSError as exc:
            print(f"error: could not create {rel(path)}: {exc}", file=sys.stderr)
        else:
            print(f"Created {rel(path)}")

    return check_workspace()


def main() -> int:
    parser = argparse.ArgumentParser(description="Check or create missing local workspace components.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="validate required local workspace paths without modifying files")
    mode.add_argument("--write", action="store_true", help="create only missing local workspace paths, then validate")
    args = parser.parse_args()

    if args.check:
        return check_workspace()
    return write_workspace()


if __name__ == "__main__":
    raise SystemExit(main())
