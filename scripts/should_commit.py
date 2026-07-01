"""Decide whether generated changes are meaningful enough to commit in CI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Exit 0 when CI should commit, 1 when it should skip."""

    changed = subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True).splitlines()
    if not changed:
        print("skip: no staged changes")
        return 1

    material_prefixes = ("output/tvbox.json", "output/live.m3u", "state/history.json")
    if any(path.startswith(material_prefixes) for path in changed):
        print("commit: material artifact or history changed")
        return 0

    old_summary = _read_json(Path(".old-summary.json"))
    new_summary = _read_json(Path("output/summary.json"))
    threshold = _read_threshold(Path("config/sources.yml"))
    delta = abs(float(new_summary.get("online_rate", 0)) - float(old_summary.get("online_rate", 0)))
    if delta >= threshold:
        print(f"commit: online rate changed by {delta:.4f}")
        return 0
    print(f"skip: only non-material changes and online-rate delta {delta:.4f} < {threshold:.4f}")
    return 1


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _read_threshold(path: Path) -> float:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    for line in text.splitlines():
        if "change_threshold_online_rate:" in line:
            return float(line.split(":", 1)[1].strip())
    return 0.02


if __name__ == "__main__":
    sys.exit(main())
