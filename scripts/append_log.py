#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / ".private" / "knowledge_cycle_log.md"
EVAL_RUNS = ROOT / ".private" / "eval_runs"
SOURCE_ID_RE = re.compile(r"^src_[A-Za-z0-9][A-Za-z0-9_-]*$")
WIKI_OUTPUT_RE = re.compile(r"^wiki/(topics|decisions|anti-patterns)/[^\n]+\.md$")
CYCLE_ID_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-\d{4}-knowledge-cycle$")
COMPILE_FIDELITY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-\d{4}-compile-fidelity\.md$")
GOLDEN_ANSWERABILITY_WIKI_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-\d{4}-golden-answerability-wiki\.md$")
VALID_INDEX_STATUSES = {"updated", "unchanged"}


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def has_duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def existing_report(path_text: str, pattern: re.Pattern[str], label: str) -> tuple[Path | None, list[str]]:
    path = Path(path_text)
    if not path.is_absolute():
        path = ROOT / path

    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        return None, [f"{label} does not exist: {path_text} ({exc})"]

    errors: list[str] = []
    try:
        eval_root = EVAL_RUNS.resolve(strict=True)
        resolved.relative_to(eval_root)
    except OSError as exc:
        errors.append(f"{rel(EVAL_RUNS)} is not available: {exc}")
    except ValueError:
        errors.append(f"{label} must be under {rel(EVAL_RUNS)}: {path_text}")

    if not pattern.fullmatch(resolved.name):
        errors.append(f"{label} filename does not match required contract: {resolved.name}")
    if not resolved.is_file():
        errors.append(f"{label} is not a file: {path_text}")

    return resolved, errors


def existing_wiki_output(path_text: str) -> tuple[Path | None, list[str]]:
    errors: list[str] = []
    if not WIKI_OUTPUT_RE.fullmatch(path_text):
        errors.append(f"wiki output must be under wiki/topics, wiki/decisions, or wiki/anti-patterns and end in .md: {path_text}")
    path = ROOT / path_text
    if not path.is_file():
        errors.append(f"wiki output does not exist: {path_text}")
    return path, errors


def validate_args(args: argparse.Namespace) -> tuple[Path | None, Path | None, list[Path], list[str]]:
    errors: list[str] = []

    if not CYCLE_ID_RE.fullmatch(args.cycle_id):
        errors.append("cycle ID must match YYYY-MM-DD-HHMM-knowledge-cycle")
    if args.index_status not in VALID_INDEX_STATUSES:
        errors.append("index status must be updated or unchanged")

    for duplicate in has_duplicates(args.source_id):
        errors.append(f"duplicate source ID argument: {duplicate}")
    for duplicate in has_duplicates(args.wiki_output):
        errors.append(f"duplicate wiki output argument: {duplicate}")

    for source_id in args.source_id:
        if not SOURCE_ID_RE.fullmatch(source_id):
            errors.append(f"source ID must match src_[A-Za-z0-9][A-Za-z0-9_-]*: {source_id}")

    wiki_outputs: list[Path] = []
    for output in args.wiki_output:
        path, output_errors = existing_wiki_output(output)
        if path is not None:
            wiki_outputs.append(path)
        errors.extend(output_errors)

    compile_report, compile_errors = existing_report(
        args.compile_fidelity_report,
        COMPILE_FIDELITY_RE,
        "compile-fidelity report",
    )
    golden_report, golden_errors = existing_report(
        args.golden_answerability_report,
        GOLDEN_ANSWERABILITY_WIKI_RE,
        "golden-answerability report",
    )
    errors.extend(compile_errors)
    errors.extend(golden_errors)

    return compile_report, golden_report, wiki_outputs, errors


def format_entry(args: argparse.Namespace, compile_report: Path, golden_report: Path) -> str:
    timestamp = args.cycle_id.removesuffix("-knowledge-cycle")
    lines = [
        f"## Knowledge Cycle {timestamp}",
        "",
        f"- cycle_id: `{args.cycle_id}`",
        "- status: completed",
        "- validation_status: passed",
        f"- index_status: {args.index_status}",
        "- source_ids:",
    ]
    for source_id in sorted(args.source_id):
        lines.append(f"  - `{source_id}`")
    lines.append("- wiki_outputs:")
    for output in sorted(args.wiki_output):
        lines.append(f"  - `{output}`")
    lines.extend(
        [
            "- reports:",
            f"  - compile_fidelity: `{rel(compile_report)}`",
            f"  - golden_answerability: `{rel(golden_report)}`",
        ]
    )
    return "\n".join(lines) + "\n"


def duplicate_reasons(text: str, cycle_id: str, compile_report: Path, golden_report: Path) -> list[str]:
    reasons: list[str] = []
    if re.search(rf"(?m)^- cycle_id: `{re.escape(cycle_id)}`$", text) or re.search(
        rf"(?m)^## Knowledge Cycle {re.escape(cycle_id.removesuffix('-knowledge-cycle'))}$", text
    ):
        reasons.append(f"cycle ID already present in {rel(LOG)}: {cycle_id}")

    compile_line = f"  - compile_fidelity: `{rel(compile_report)}`"
    golden_line = f"  - golden_answerability: `{rel(golden_report)}`"
    if compile_line in text and golden_line in text:
        reasons.append(f"evaluation-report pair already present in {rel(LOG)}")

    return reasons


def append_entry(entry: str, existing_text: str) -> None:
    prefix = ""
    if existing_text and not existing_text.endswith("\n"):
        prefix += "\n"
    if existing_text.strip():
        prefix += "\n"
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(prefix + entry)


def main() -> int:
    parser = argparse.ArgumentParser(description=f"Append one completed knowledge-cycle entry to {rel(LOG)}.")
    parser.add_argument("--cycle-id", required=True, help="YYYY-MM-DD-HHMM-knowledge-cycle")
    parser.add_argument("--source-id", action="append", required=True, help="compiled source ID; repeat for multiple sources")
    parser.add_argument("--wiki-output", action="append", required=True, help="existing wiki output path; repeat for multiple outputs")
    parser.add_argument("--index-status", choices=sorted(VALID_INDEX_STATUSES), required=True, help="whether update_index.py changed wiki/index.md")
    parser.add_argument("--compile-fidelity-report", required=True, help=".private/eval_runs/YYYY-MM-DD-HHMM-compile-fidelity.md")
    parser.add_argument("--golden-answerability-report", required=True, help=".private/eval_runs/YYYY-MM-DD-HHMM-golden-answerability-wiki.md")
    parser.add_argument("--write", action="store_true", help=f"append to {rel(LOG)}; without this flag, print a preview only")
    args = parser.parse_args()

    compile_report, golden_report, _wiki_outputs, errors = validate_args(args)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    assert compile_report is not None
    assert golden_report is not None

    try:
        current_log = LOG.read_text(encoding="utf-8")
    except FileNotFoundError:
        current_log = ""
    except OSError as exc:
        print(f"error: could not read {rel(LOG)}: {exc}", file=sys.stderr)
        return 1

    duplicates = duplicate_reasons(current_log, args.cycle_id, compile_report, golden_report)
    if duplicates:
        for reason in duplicates:
            prefix = "error" if args.write else "warning"
            suffix = "" if args.write else "; --write would be rejected"
            print(f"{prefix}: {reason}{suffix}", file=sys.stderr)
        if args.write:
            return 1

    entry = format_entry(args, compile_report, golden_report)
    if not args.write:
        print(entry, end="")
        return 0

    try:
        append_entry(entry, current_log)
    except OSError as exc:
        print(f"error: could not append to {rel(LOG)}: {exc}", file=sys.stderr)
        return 1

    print(f"Appended completed knowledge-cycle entry to {rel(LOG)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
