"""Typed data objects used across the TV-Matrix pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class SourceFormat(str, Enum):
    """Supported candidate line formats."""

    UNKNOWN = "unknown"
    TXT = "txt"
    M3U = "m3u"
    TVBOX_JSON = "tvbox_json"


@dataclass(slots=True)
class SourceCandidate:
    """A URL discovered from config or crawling.

    Args:
        name: Human-readable label.
        url: Candidate endpoint URL.
        origin: Config, discovery page, or parser that produced the URL.
        priority: Higher values receive optional deeper checks such as TCP probing.
        format_hint: Known format, when configured or inferred.
    """

    name: str
    url: str
    origin: str = "config"
    priority: int = 1
    format_hint: SourceFormat = SourceFormat.UNKNOWN
    tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ParsedContent:
    """Normalized content extracted from a candidate response."""

    format: SourceFormat
    valid_items: list[dict[str, Any]]
    raw_title: str | None = None

    @property
    def quality_ratio(self) -> float:
        """Return a small content quality score based on useful extracted items."""

        if not self.valid_items:
            return 0.0
        return min(1.0, len(self.valid_items) / 10)


@dataclass(slots=True)
class ValidationResult:
    """Result for one validation attempt."""

    candidate: SourceCandidate
    checked_at: str
    ok: bool
    http_status: int | None
    elapsed_ms: int | None
    content_format: SourceFormat
    content_quality: float
    valid_item_count: int
    tcp_ok: bool | None
    error: str | None = None
    score: float = 0.0
    label: str = "离线"

    @classmethod
    def failure(cls, candidate: SourceCandidate, error: str) -> "ValidationResult":
        """Create a failed result with consistent timestamp fields."""

        return cls(
            candidate=candidate,
            checked_at=datetime.now(UTC).isoformat(),
            ok=False,
            http_status=None,
            elapsed_ms=None,
            content_format=SourceFormat.UNKNOWN,
            content_quality=0.0,
            valid_item_count=0,
            tcp_ok=None,
            error=error,
        )


@dataclass(slots=True)
class RunSummary:
    """Aggregate metrics emitted after a pipeline run."""

    generated_at: str
    total: int
    online: int
    offline: int
    online_rate: float
    average_score: float
    artifacts: dict[str, str]
