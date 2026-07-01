"""Persistent history and circuit-breaker state."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from .models import ValidationResult


class HistoryStore:
    """JSON-backed validation history store.

    The store is intentionally simple because GitHub Actions needs deterministic
    file artifacts that can be committed and diffed.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.data: dict[str, Any] = {"sources": {}, "runs": []}
        if path.exists():
            self.data = json.loads(path.read_text(encoding="utf-8"))

    def record_result(self, result: ValidationResult) -> None:
        """Append one validation record and update source-level counters."""

        source = self.data.setdefault("sources", {}).setdefault(
            result.candidate.url,
            {
                "name": result.candidate.name,
                "origin": result.candidate.origin,
                "priority": result.candidate.priority,
                "records": [],
                "consecutive_failures": 0,
                "sleeping": False,
                "last_checked_at": None,
            },
        )
        source["name"] = result.candidate.name
        source["origin"] = result.candidate.origin
        source["priority"] = result.candidate.priority
        source["last_checked_at"] = result.checked_at
        source["records"].append(
            {
                "checked_at": result.checked_at,
                "ok": result.ok,
                "elapsed_ms": result.elapsed_ms,
                "content_quality": result.content_quality,
                "score": result.score,
                "label": result.label,
                "http_status": result.http_status,
                "valid_item_count": result.valid_item_count,
                "adult": result.adult,
            }
        )
        source["records"] = source["records"][-120:]
        source["consecutive_failures"] = 0 if result.ok else source["consecutive_failures"] + 1

    def mark_sleeping_sources(self, threshold: int) -> None:
        """Move repeatedly failing sources to the low-frequency sleep pool."""

        for source in self.data.get("sources", {}).values():
            source["sleeping"] = source.get("consecutive_failures", 0) >= threshold

    def should_validate(self, url: str, revive_every_days: int) -> bool:
        """Return whether a source should be checked in this run.

        Sleeping sources are sampled after the configured revival interval.
        """

        source = self.data.get("sources", {}).get(url)
        if not source or not source.get("sleeping"):
            return True
        last_checked = source.get("last_checked_at")
        if not last_checked:
            return True
        checked_at = datetime.fromisoformat(last_checked.replace("Z", "+00:00"))
        return datetime.now(UTC) - checked_at >= timedelta(days=revive_every_days)

    def add_run(self, summary: dict[str, Any]) -> None:
        """Persist an aggregate run summary for README and dashboard trend charts."""

        self.data.setdefault("runs", []).append(summary)
        self.data["runs"] = self.data["runs"][-90:]

    def save(self) -> None:
        """Write state atomically."""

        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.path)
