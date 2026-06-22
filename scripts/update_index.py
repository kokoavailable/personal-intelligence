#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from check_wiki_integrity import ROOT, WIKI_DIRS, parse_frontmatter, rel, split_frontmatter, validate_wiki


INDEX = ROOT / "wiki" / "index.md"
BEGIN_MARKER = "<!-- BEGIN GENERATED WIKI INDEX -->"
END_MARKER = "<!-- END GENERATED WIKI INDEX -->"
BEGIN_MARKER_BYTES = BEGIN_MARKER.encode("utf-8")
END_MARKER_BYTES = END_MARKER.encode("utf-8")
TYPE_ORDER = (
    ("topic", "Topics"),
    ("decision", "Decisions"),
    ("anti-pattern", "Anti-patterns"),
)
WIKI_LINK_RE = re.compile(rb"\[\[(wiki/(?:topics|decisions|anti-patterns)/[^\]\n]+)\]\]")


@dataclass(frozen=True)
class WikiNote:
    path: Path
    note_id: str
    note_type: str

    @property
    def link(self) -> str:
        target = rel(self.path)
        if target.endswith(".md"):
            target = target[:-3]
        return f"[[{target}]]"


def parse_validated_frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    frontmatter, _body = split_frontmatter(text)
    if frontmatter is None:
        raise ValueError(f"{rel(path)}: missing YAML frontmatter")
    errors: list[str] = []
    data = parse_frontmatter(path, frontmatter, errors)
    if errors:
        raise ValueError("\n".join(errors))
    return data


def wiki_paths() -> list[Path]:
    paths: list[Path] = []
    for directory in WIKI_DIRS:
        if directory.exists():
            paths.extend(path for path in directory.rglob("*.md") if path.resolve() != INDEX.resolve())
    return sorted(paths, key=rel)


def load_wiki_notes() -> tuple[list[WikiNote], list[str]]:
    paths = wiki_paths()
    _validated_paths, errors, _warnings = validate_wiki()

    if errors:
        return [], errors

    notes: list[WikiNote] = []
    for path in paths:
        try:
            data = parse_validated_frontmatter(path)
        except (OSError, ValueError) as exc:
            return [], [str(exc)]
        notes.append(WikiNote(path=path, note_id=str(data["id"]), note_type=str(data["type"])))
    return notes, []


def notes_in_type_order(notes: list[WikiNote]) -> list[WikiNote]:
    ordered: list[WikiNote] = []
    for note_type, _heading in TYPE_ORDER:
        ordered.extend(sorted((note for note in notes if note.note_type == note_type), key=lambda note: rel(note.path)))
    return ordered


def render_generated_content(notes: list[WikiNote]) -> bytes:
    lines: list[str] = []
    for note_type, heading in TYPE_ORDER:
        typed_notes = sorted((note for note in notes if note.note_type == note_type), key=lambda note: rel(note.path))
        if not typed_notes:
            continue
        if lines:
            lines.append("")
        lines.append(f"### {heading}")
        lines.append("")
        for note in typed_notes:
            lines.append(f"- {note.link}")
    if not lines:
        lines.append("_No compiled wiki notes found._")
    return ("\n" + "\n".join(lines) + "\n").encode("utf-8")


def marker_region(data: bytes) -> tuple[int, int, list[str]]:
    errors: list[str] = []
    begin_count = data.count(BEGIN_MARKER_BYTES)
    end_count = data.count(END_MARKER_BYTES)
    if begin_count != 1:
        errors.append(f"{rel(INDEX)}: expected exactly one begin marker")
    if end_count != 1:
        errors.append(f"{rel(INDEX)}: expected exactly one end marker")
    if errors:
        return -1, -1, errors

    begin = data.find(BEGIN_MARKER_BYTES)
    end = data.find(END_MARKER_BYTES)
    if end < begin:
        errors.append(f"{rel(INDEX)}: generated wiki index markers are misordered")
        return -1, -1, errors
    return begin + len(BEGIN_MARKER_BYTES), end, []


def wiki_links(data: bytes) -> list[str]:
    return [f"[[{match.group(1).decode('utf-8')}]]" for match in WIKI_LINK_RE.finditer(data)]


def duplicate_items(items: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return sorted(duplicates)


def replace_marker_content(data: bytes, content: bytes) -> tuple[bytes, list[str]]:
    start, end, errors = marker_region(data)
    if errors:
        return data, errors
    return data[:start] + content + data[end:], []


def validate_generated_index(data: bytes, expected_links: list[str]) -> list[str]:
    start, end, errors = marker_region(data)
    if errors:
        return errors

    inside_links = wiki_links(data[start:end])
    outside_links = [link for link in wiki_links(data[:start] + data[end:]) if link in expected_links]

    if inside_links != expected_links:
        errors.append(f"{rel(INDEX)}: generated wiki index does not match current wiki files")

    for duplicate in duplicate_items(inside_links):
        errors.append(f"{rel(INDEX)}: duplicate generated wiki link {duplicate}")

    for link in sorted(set(outside_links)):
        errors.append(f"{rel(INDEX)}: compiled wiki link appears outside generated block: {link}")

    return errors


def unified_diff(before: bytes, after: bytes) -> str:
    before_text = before.decode("utf-8", errors="replace")
    after_text = after.decode("utf-8", errors="replace")
    return "".join(
        difflib.unified_diff(
            before_text.splitlines(keepends=True),
            after_text.splitlines(keepends=True),
            fromfile=rel(INDEX),
            tofile=rel(INDEX),
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=f"Update the generated wiki marker contents in {rel(INDEX)}.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="fail if generated marker contents are not up to date")
    mode.add_argument("--write", action="store_true", help="rewrite only the content between generated wiki index markers")
    args = parser.parse_args()

    notes, errors = load_wiki_notes()
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1

    expected_links = [note.link for note in notes_in_type_order(notes)]
    try:
        current = INDEX.read_bytes()
    except OSError as exc:
        print(f"error: could not read {rel(INDEX)}: {exc}", file=sys.stderr)
        return 1

    desired, marker_errors = replace_marker_content(current, render_generated_content(notes))
    if marker_errors:
        for error in marker_errors:
            print(f"error: {error}", file=sys.stderr)
        return 1

    generated_errors = validate_generated_index(desired, expected_links)
    if generated_errors:
        for error in generated_errors:
            print(f"error: {error}", file=sys.stderr)
        return 1

    if args.check:
        if current != desired:
            print(f"error: {rel(INDEX)} generated wiki index is not up to date", file=sys.stderr)
            print(unified_diff(current, desired), end="")
            return 1
        print(f"{rel(INDEX)} generated wiki index is up to date.")
        return 0

    if current == desired:
        print(f"{rel(INDEX)} already up to date.")
        return 0

    try:
        INDEX.write_bytes(desired)
    except OSError as exc:
        print(f"error: could not write {rel(INDEX)}: {exc}", file=sys.stderr)
        return 1

    print(f"Updated {rel(INDEX)} generated wiki index.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
