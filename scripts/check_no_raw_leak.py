#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGETS = (ROOT / "public", ROOT / "metadata")
TEXT_SUFFIXES = {
    ".css",
    ".csv",
    ".htm",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".rst",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}

PATTERNS = (
    ("raw imported path", re.compile(re.escape("raw" + "/imported/"))),
    ("raw inbox path", re.compile(re.escape("raw" + "/inbox/"))),
    ("raw markdown source path", re.compile(r"(?<![A-Za-z0-9_.-])raw/[^\n`\"']*?\.md")),
    ("private source id", re.compile(r"\bsrc_[A-Za-z0-9][A-Za-z0-9_-]*\b")),
    ("DATABASE_URL", re.compile(r"\bDATABASE_URL\b")),
    ("MONGODB_URI", re.compile(r"\bMONGODB_URI\b")),
    ("REDIS_URL", re.compile(r"\bREDIS_URL\b")),
    ("client_secret", re.compile(r"\bclient_secret\b", re.IGNORECASE)),
    ("ARM_CLIENT_SECRET", re.compile(r"\bARM_CLIENT_SECRET\b")),
    ("private key", re.compile(r"\bprivate\s+key\b", re.IGNORECASE)),
    ("BEGIN RSA", re.compile(r"BEGIN\s+RSA", re.IGNORECASE)),
    ("BEGIN OPENSSH", re.compile(r"BEGIN\s+OPENSSH", re.IGNORECASE)),
    ("password", re.compile(r"\bpassword\b", re.IGNORECASE)),
    ("passwd", re.compile(r"\bpasswd\b", re.IGNORECASE)),
    ("token", re.compile(r"\btoken\b", re.IGNORECASE)),
    ("api_key", re.compile(r"\bapi_key\b", re.IGNORECASE)),
    ("apikey", re.compile(r"\bapikey\b", re.IGNORECASE)),
    ("PFX", re.compile(r"\bPFX\b", re.IGNORECASE)),
)


@dataclass(frozen=True)
class Finding:
    path: Path
    line_number: int
    label: str


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def target_paths(args: list[str]) -> list[Path]:
    if not args:
        return list(DEFAULT_TARGETS)
    return [Path(arg) if Path(arg).is_absolute() else ROOT / arg for arg in args]


def is_text_candidate(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or not path.suffix


def iter_files(target: Path):
    if not target.exists():
        return
    if target.is_file():
        if is_text_candidate(target):
            yield target
        return
    for path in sorted(target.rglob("*")):
        if path.is_file() and is_text_candidate(path):
            yield path


def scan_file(path: Path) -> list[Finding]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return []
    except OSError:
        return []

    findings: list[Finding] = []
    for line_number, line in enumerate(lines, start=1):
        for label, pattern in PATTERNS:
            if pattern.search(line):
                findings.append(Finding(path, line_number, label))
    return findings


def scan_paths(paths: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    seen: set[Path] = set()
    for target in paths:
        for path in iter_files(target):
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            findings.extend(scan_file(path))
    return findings


def print_findings(findings: list[Finding], stream=sys.stdout) -> None:
    for finding in findings:
        print(f"{rel(finding.path)}:{finding.line_number}: {finding.label}", file=stream)


def main() -> int:
    findings = scan_paths(target_paths(sys.argv[1:]))
    if findings:
        print_findings(findings)
        return 1
    print("No raw path leaks or secret-like patterns found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
