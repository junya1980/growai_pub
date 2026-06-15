#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from pathlib import Path


BLOCKED_PATTERNS = (
    re.compile(r"BEGIN (RSA|OPENSSH|PRIVATE) KEY"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"/Users/"),
    re.compile(r"\.env"),
)
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache"}


def iter_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if path.name == "check_public_packet.py":
            continue
        yield path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


def blocked_hits(root: Path) -> list[str]:
    hits: list[str] = []
    for path in iter_files(root):
        text = read_text(path)
        for pattern in BLOCKED_PATTERNS:
            if pattern.search(text):
                hits.append(str(path.relative_to(root)))
                break
    return sorted(hits)


def syntax_hits(root: Path) -> list[str]:
    hits: list[str] = []
    for path in iter_files(root):
        if path.suffix != ".py":
            continue
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError):
            hits.append(str(path.relative_to(root)))
    return sorted(hits)


def packet_manifest(root: Path) -> dict[str, object]:
    packet_root = root / "public_ci" / "packets"
    files: list[dict[str, object]] = []
    if packet_root.is_dir():
        for path in sorted(packet_root.rglob("*")):
            if not path.is_file():
                continue
            data = path.read_bytes()
            files.append(
                {
                    "path": str(path.relative_to(root)),
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "size": len(data),
                }
            )
    return {"files": files}


def write_packet_manifest(root: Path) -> Path:
    destination = root / "public_ci" / "packet_manifest.json"
    destination.write_text(json.dumps(packet_manifest(root), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return destination


def required_files_missing(root: Path) -> list[str]:
    required = (
        "public_ci/README.md",
        "public_ci/tests/README.md",
        "public_ci/fixtures/README.md",
        "public_ci/scripts/README.md",
    )
    return [path for path in required if not (root / path).is_file()]


def check_packet(root: Path) -> list[str]:
    errors: list[str] = []
    missing = required_files_missing(root)
    if missing:
        errors.append("missing required files: " + ", ".join(missing))
    hits = blocked_hits(root)
    if hits:
        errors.append("blocked sensitive markers: " + ", ".join(hits))
    syntax_errors = syntax_hits(root)
    if syntax_errors:
        errors.append("python syntax errors: " + ", ".join(syntax_errors))
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a public-safe packet.")
    parser.add_argument("--root", default=".", help="Packet root to validate.")
    parser.add_argument("--write-manifest", action="store_true", help="Write public_ci/packet_manifest.json.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    errors = check_packet(root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    if args.write_manifest:
        manifest_path = write_packet_manifest(root)
        print(f"packet_manifest={manifest_path.relative_to(root)}")
    print("public_packet_check=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
