#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

from check_no_raw_leak import print_findings, scan_paths


ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"
PUBLIC = ROOT / "public"
PUBLIC_SAFE_COMMENT = "<!-- public_safe: true -->"
SAFE_FRONTMATTER_KEYS = {"id", "type", "valid_from"}
PRIVATE_SOURCE_ID = re.compile(r"\bsrc_[A-Za-z0-9][A-Za-z0-9_-]*\b")


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def split_frontmatter(text: str) -> tuple[list[str] | None, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            body = "\n".join(lines[index + 1 :])
            if text.endswith("\n"):
                body += "\n"
            return lines[1:index], body
    return None, text


def frontmatter_public_safe(lines: list[str] | None) -> bool:
    if not lines:
        return False
    for line in lines:
        stripped = line.strip().lower()
        if stripped == "public_safe: true":
            return True
    return False


def filter_frontmatter(lines: list[str] | None) -> list[str]:
    if not lines:
        return []

    filtered: list[str] = []
    keep_current_block = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if line.startswith((" ", "\t")):
            if keep_current_block:
                filtered.append(line)
            continue

        if ":" not in line:
            keep_current_block = False
            continue

        key = line.split(":", 1)[0].strip()
        keep_current_block = key in SAFE_FRONTMATTER_KEYS
        if keep_current_block:
            filtered.append(line)

    return filtered


def has_public_safe_marker(text: str, frontmatter: list[str] | None, body: str) -> bool:
    return PUBLIC_SAFE_COMMENT in body or PUBLIC_SAFE_COMMENT in text or frontmatter_public_safe(frontmatter)


def sanitize_body(body: str) -> str:
    body = body.replace(PUBLIC_SAFE_COMMENT, "")
    body = PRIVATE_SOURCE_ID.sub("[private-source]", body)
    return body.lstrip("\n")


def public_markdown(text: str) -> str | None:
    frontmatter, body = split_frontmatter(text)
    if not has_public_safe_marker(text, frontmatter, body):
        return None

    filtered_frontmatter = filter_frontmatter(frontmatter)
    sanitized_body = sanitize_body(body)

    if not filtered_frontmatter:
        return sanitized_body

    return "---\n" + "\n".join(filtered_frontmatter) + "\n---\n\n" + sanitized_body


def iter_wiki_notes() -> list[Path]:
    if not WIKI.exists():
        return []
    return sorted(WIKI.rglob("*.md"))


def export_note(path: Path) -> Path | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"skipped unreadable file: {rel(path)}: {exc}", file=sys.stderr)
        return None

    output = public_markdown(text)
    if output is None:
        print(f"skipped: {rel(path)}")
        return None

    destination = PUBLIC / path.relative_to(WIKI)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(output, encoding="utf-8")
    print(f"exported: {rel(destination)}")
    return destination


def main() -> int:
    notes = iter_wiki_notes()
    if not notes:
        print("No wiki markdown files found.")
        return 0

    exported = [destination for note in notes if (destination := export_note(note))]
    if not exported:
        print("No public-safe wiki notes were exported.")

    findings = scan_paths([PUBLIC])
    if findings:
        print("Public export validation failed:", file=sys.stderr)
        print_findings(findings, stream=sys.stderr)
        return 1

    print("Public export validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
