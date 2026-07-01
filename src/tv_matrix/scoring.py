"""Adaptive health scoring logic."""

from __future__ import annotations

from statistics import mean
from typing import Any

from .models import ValidationResult


def score_result(result: ValidationResult, history: dict[str, Any], config: dict[str, Any]) -> float:
    """Compute a 0-100 health score from current and historical observations.

    Args:
        result: Latest validation result.
        history: Source-level history dictionary.
        config: Scoring config containing weights and recent window.

    Returns:
        Health score where higher means faster and more reliable.

    Extension point:
        Adjust this function to add new dimensions such as geo reachability,
        stream startup latency, or CDN stability.
    """

    weights = config.get("weights", {})
    recent_window = int(config.get("recent_window", 3))
    records = list(history.get("records", []))
    recent = records[-recent_window:]

    recent_success = mean([1.0 if r.get("ok") else 0.0 for r in recent] or [1.0 if result.ok else 0.0])
    lifetime_success = mean([1.0 if r.get("ok") else 0.0 for r in records] or [1.0 if result.ok else 0.0])
    latency_ms = result.elapsed_ms if result.elapsed_ms is not None else 30000
    latency_score = max(0.0, min(1.0, 1.0 - (latency_ms / 30000)))
    content_quality = result.content_quality

    score = (
        weights.get("recent_success", 0.45) * recent_success
        + weights.get("lifetime_success", 0.35) * lifetime_success
        + weights.get("latency", 0.15) * latency_score
        + weights.get("content_quality", 0.05) * content_quality
    )
    if not result.ok:
        score *= 0.25
    return round(max(0.0, min(100.0, score * 100)), 2)


def label_for_score(score: float, elapsed_ms: int | None) -> str:
    """Convert numeric score into a TVBox-friendly health label."""

    if score >= 85 and (elapsed_ms or 99999) <= 2500:
        return "快"
    if score >= 75:
        return "稳定"
    if score >= 50:
        return "慢"
    return "离线"
