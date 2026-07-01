"""Configuration loading for TV-Matrix-Core."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .models import SourceCandidate, SourceFormat


@dataclass(slots=True)
class MatrixConfig:
    """Runtime configuration with defaults suitable for local and CI execution."""

    fixed_sources: list[SourceCandidate]
    discovery: dict[str, Any]
    validation: dict[str, Any]
    scoring: dict[str, Any]
    output: dict[str, Any]


def load_config(path: Path) -> MatrixConfig:
    """Load YAML config and normalize source candidates.

    Args:
        path: YAML configuration path.

    Returns:
        MatrixConfig with all optional sections populated.
    """

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}
    raw = raw or {}
    fixed_sources = []
    for item in raw.get("fixed_sources", []):
        fixed_sources.append(
            SourceCandidate(
                name=str(item.get("name") or item.get("url")),
                url=str(item["url"]),
                origin="config",
                priority=int(item.get("priority", 1)),
                format_hint=SourceFormat(str(item.get("format", "unknown"))),
                tags=list(item.get("tags", [])),
            )
        )

    return MatrixConfig(
        fixed_sources=fixed_sources,
        discovery=raw.get("discovery", {}) or {},
        validation=raw.get("validation", {}) or {},
        scoring=raw.get("scoring", {}) or {},
        output=raw.get("output", {}) or {},
    )
