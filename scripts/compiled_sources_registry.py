#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPILED_SOURCES = ROOT / ".private" / "compiled_sources.yml"
SOURCE_ID_RE = re.compile(r"^src_[A-Za-z0-9][A-Za-z0-9_-]*$")
RAW_SOURCE_PATH_RE = re.compile(r"^raw/(imported|inbox)/[^\n]+\.md$")
WIKI_OUTPUT_RE = re.compile(r"^wiki/(topics|decisions|anti-patterns)/[^\n]+\.md$")


@dataclass(frozen=True)
class CompiledSourceEntry:
    source_id: str
    source_path: str
    outputs: tuple[str, ...]


@dataclass(frozen=True)
class CompiledSourcesRegistry:
    entries: dict[str, CompiledSourceEntry]

    @property
    def source_ids(self) -> set[str]:
        return set(self.entries)


def rel(path: Path, root: Path = ROOT) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def ruby_yaml_json(path: Path, root: Path = ROOT) -> object:
    script = (
        "require 'date'; "
        "require 'json'; "
        "require 'yaml'; "
        "data = YAML.safe_load(File.read(ARGV.fetch(0)), permitted_classes: [Date], aliases: false); "
        "puts JSON.generate(data)"
    )
    result = subprocess.run(
        ["ruby", "-e", script, str(path)],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or f"ruby exited {result.returncode}"
        raise ValueError(message)
    return json.loads(result.stdout)


def load_compiled_sources_items(path: Path = COMPILED_SOURCES, root: Path = ROOT) -> tuple[list[object], list[str]]:
    try:
        data = ruby_yaml_json(path, root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [], [f"{rel(path, root)}: could not parse YAML: {exc}"]

    if not isinstance(data, dict):
        return [], [f"{rel(path, root)}: expected top-level mapping"]
    if "compiled_sources" not in data:
        return [], [f"{rel(path, root)}: missing compiled_sources key"]
    items = data["compiled_sources"]
    if not isinstance(items, list):
        return [], [f"{rel(path, root)}: compiled_sources must be a list"]
    return items, []


def load_registry(path: Path = COMPILED_SOURCES, root: Path = ROOT) -> tuple[CompiledSourcesRegistry, list[str]]:
    items, errors = load_compiled_sources_items(path, root)
    entries: dict[str, CompiledSourceEntry] = {}
    duplicate_source_ids: set[str] = set()
    source_paths: dict[str, str] = {}
    duplicate_source_paths: set[str] = set()

    for index, item in enumerate(items, start=1):
        label = f"{rel(path, root)}: compiled_sources[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label}: expected mapping")
            continue

        raw_source_id = item.get("source_id")
        source_id = raw_source_id if isinstance(raw_source_id, str) else ""
        valid_source_id = False
        if not source_id.strip():
            errors.append(f"{label}: source_id must be a non-empty string")
        elif not SOURCE_ID_RE.fullmatch(source_id):
            errors.append(f"{label}: source_id must match src_[A-Za-z0-9][A-Za-z0-9_-]*: {source_id}")
        elif source_id in entries:
            duplicate_source_ids.add(source_id)
        else:
            valid_source_id = True

        raw_source_path = item.get("source_path")
        source_path = raw_source_path if isinstance(raw_source_path, str) else ""
        if not source_path.strip():
            errors.append(f"{label}: source_path must be a non-empty string")
        elif not RAW_SOURCE_PATH_RE.fullmatch(source_path):
            errors.append(f"{label}: source_path must be under raw/imported or raw/inbox and end in .md: {source_path}")
        else:
            if not (root / source_path).is_file():
                errors.append(f"{label}: source_path does not exist: {source_path}")
            if source_path in source_paths:
                duplicate_source_paths.add(source_path)
            else:
                source_paths[source_path] = source_id

        raw_outputs = item.get("outputs")
        outputs: list[str] = []
        if not isinstance(raw_outputs, list) or not raw_outputs:
            errors.append(f"{label}: outputs must be a non-empty list")
        else:
            for output_index, output in enumerate(raw_outputs, start=1):
                output_label = f"{label}.outputs[{output_index}]"
                if not isinstance(output, str) or not output.strip():
                    errors.append(f"{output_label}: output must be a non-empty string")
                elif not WIKI_OUTPUT_RE.fullmatch(output):
                    errors.append(
                        f"{output_label}: output must be under wiki/topics, wiki/decisions, or wiki/anti-patterns and end in .md: {output}"
                    )
                else:
                    outputs.append(output)

        if valid_source_id:
            entries[source_id] = CompiledSourceEntry(source_id=source_id, source_path=source_path, outputs=tuple(outputs))

    for source_id in sorted(duplicate_source_ids):
        errors.append(f"{rel(path, root)}: duplicate source_id: {source_id}")
    for source_path in sorted(duplicate_source_paths):
        errors.append(f"{rel(path, root)}: duplicate source_path: {source_path}")

    return CompiledSourcesRegistry(entries=entries), errors
