#!/usr/bin/env python3
"""Adjust data source references in text-exported BarTender files.

BarTender ``.btw`` files are commonly binary. Export the label/document to a
text-based format such as XML first, then use this utility to rewrite database
paths, server names, or connection strings in bulk.
"""
from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Replacement:
    """A literal text replacement rule."""

    old: str
    new: str


def load_replacements(config_path: Path) -> list[Replacement]:
    """Load replacement rules from a JSON file.

    Supported shapes:
    - {"replacements": [{"old": "...", "new": "..."}]}
    - {"replacements": {"old text": "new text"}}
    - {"old text": "new text"}
    """

    data = json.loads(config_path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "replacements" in data:
        data = data["replacements"]

    rules: list[Replacement] = []
    if isinstance(data, dict):
        rules = [Replacement(str(old), str(new)) for old, new in data.items()]
    elif isinstance(data, list):
        for item in data:
            if not isinstance(item, dict) or "old" not in item or "new" not in item:
                raise ValueError("Each replacement list item must contain 'old' and 'new'.")
            rules.append(Replacement(str(item["old"]), str(item["new"])))
    else:
        raise ValueError("Replacement config must be a JSON object or list.")

    if not rules:
        raise ValueError("Replacement config does not contain any rules.")
    for rule in rules:
        if rule.old == "":
            raise ValueError("Replacement 'old' value cannot be empty.")
    return rules


def iter_targets(paths: Iterable[Path], recursive: bool) -> list[Path]:
    """Expand file and directory arguments into a stable list of files."""

    targets: list[Path] = []
    for path in paths:
        if path.is_dir():
            globber = path.rglob if recursive else path.glob
            targets.extend(p for p in globber("*") if p.is_file())
        elif path.is_file():
            targets.append(path)
        else:
            raise FileNotFoundError(f"Target not found: {path}")
    return sorted(dict.fromkeys(targets))


def apply_replacements(text: str, rules: Iterable[Replacement]) -> tuple[str, int]:
    """Apply literal replacement rules and return changed text plus hit count."""

    hits = 0
    updated = text
    for rule in rules:
        occurrences = updated.count(rule.old)
        if occurrences:
            hits += occurrences
            updated = updated.replace(rule.old, rule.new)
    return updated, hits


def update_file(path: Path, rules: list[Replacement], dry_run: bool, backup: bool) -> int:
    """Update a single file and return the number of replacements."""

    original = path.read_text(encoding="utf-8")
    updated, hits = apply_replacements(original, rules)
    if hits and not dry_run:
        if backup:
            shutil.copy2(path, path.with_suffix(path.suffix + ".bak"))
        path.write_text(updated, encoding="utf-8")
    return hits


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bulk-adjust data source strings in text-exported BarTender files."
    )
    parser.add_argument("targets", nargs="+", type=Path, help="Files or folders to update.")
    parser.add_argument("--config", required=True, type=Path, help="JSON replacement config.")
    parser.add_argument("--recursive", action="store_true", help="Scan folders recursively.")
    parser.add_argument("--dry-run", action="store_true", help="Report changes without writing files.")
    parser.add_argument("--no-backup", action="store_true", help="Do not create .bak backups.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    rules = load_replacements(args.config)
    targets = iter_targets(args.targets, args.recursive)

    total = 0
    for target in targets:
        hits = update_file(target, rules, args.dry_run, not args.no_backup)
        total += hits
        print(f"{target}: {hits} replacement(s)")
    print(f"Total: {total} replacement(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
