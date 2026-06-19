#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPILED_SOURCES = ROOT / ".private" / "compiled_sources.yml"
RAW_IMPORTED = ROOT / "raw" / "imported"


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def clean_yaml_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] in {"'", '"'} and value[-1] == value[0]:
        return value[1:-1]
    return value


def load_compiled_source_paths(path: Path) -> tuple[set[str], bool]:
    if not path.exists():
        return set(), False

    compiled: set[str] = set()
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        print(f"Could not read {rel(path)}: {exc}", file=sys.stderr)
        return compiled, True

    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("source_path:"):
            continue
        value = clean_yaml_value(stripped.split(":", 1)[1])
        if value:
            compiled.add(value)

    return compiled, True


def main() -> int:
    compiled, registry_exists = load_compiled_source_paths(COMPILED_SOURCES)

    if not RAW_IMPORTED.exists():
        print("No raw/imported directory found. Nothing to list.")
        return 0

    imported_notes = sorted(RAW_IMPORTED.rglob("*.md"), key=lambda item: rel(item))
    candidates = [rel(path) for path in imported_notes if rel(path) not in compiled]

    if registry_exists:
        print(f"Read {rel(COMPILED_SOURCES)}; {len(compiled)} compiled source path(s) recorded.")
    else:
        print(f"No {rel(COMPILED_SOURCES)} found; treating all imported markdown files as candidates.")

    if not candidates:
        print("No uncompiled imported markdown sources found.")
        return 0

    print("Uncompiled source candidates:")
    for index, candidate in enumerate(candidates, start=1):
        print(f"{index}. {candidate}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
