"""End-to-end pipeline orchestration."""

from __future__ import annotations

import asyncio
import os
from dataclasses import asdict
from pathlib import Path

from .config import load_config
from .discovery import discover_candidates
from .output import generate_artifacts, rollback_latest
from .readme import render_readme
from .robots import RobotsCache
from .scoring import label_for_score, score_result
from .site import render_site
from .state import HistoryStore
from .validator import SourceValidator


async def run_pipeline(root: Path, config_path: Path) -> None:
    """Run discovery, validation, scoring, output, docs, and site generation."""

    config = load_config(config_path)
    state = HistoryStore(root / "state" / "history.json")
    robots = RobotsCache()
    discovered = await discover_candidates(config.discovery, robots)
    candidates = _dedupe(config.fixed_sources + discovered)
    candidates = _apply_shard(candidates)
    revive_days = int(config.scoring.get("revive_every_days", 30))
    candidates = [candidate for candidate in candidates if state.should_validate(candidate.url, revive_days)]

    validator = SourceValidator(config.validation, robots)
    results = await validator.validate_many(candidates) if candidates else []
    for result in results:
        history = state.data.get("sources", {}).get(result.candidate.url, {})
        result.score = score_result(result, history, config.scoring)
        result.label = label_for_score(result.score, result.elapsed_ms)
        state.record_result(result)
    state.mark_sleeping_sources(int(config.scoring.get("sleep_after_failures", 5)))
    try:
        summary = generate_artifacts(results, root / "output", int(config.output.get("keep_backups", 3)))
    except Exception as exc:
        _write_alert(root, f"artifact_generation_failed: {exc}")
        try:
            rollback_latest(root / "output")
        except FileNotFoundError:
            pass
        raise
    state.add_run(asdict(summary))
    state.save()
    render_readme(root, state.data, str(config.output.get("site_base_url", "")))
    render_site(root, state.data)


def _dedupe(candidates: list) -> list:
    seen = set()
    output = []
    for candidate in candidates:
        if candidate.url in seen:
            continue
        seen.add(candidate.url)
        output.append(candidate)
    return output


def _apply_shard(candidates: list) -> list:
    """Filter candidates by TV_MATRIX_SHARD/TV_MATRIX_SHARDS in CI."""

    shard = os.getenv("TV_MATRIX_SHARD")
    shards = os.getenv("TV_MATRIX_SHARDS")
    if shard is None or shards is None:
        return candidates
    shard_index = int(shard)
    shard_count = max(1, int(shards))
    return [candidate for index, candidate in enumerate(candidates) if index % shard_count == shard_index]


def run(root: Path, config_path: Path) -> None:
    """Synchronous wrapper for CLI entry points."""

    asyncio.run(run_pipeline(root, config_path))


def _write_alert(root: Path, message: str) -> None:
    """Write a CI-visible alert file when rollback protection is triggered."""

    alert = root / "output" / "ALERT.md"
    alert.parent.mkdir(parents=True, exist_ok=True)
    alert.write_text(f"# TV-Matrix Alert\n\n{message}\n", encoding="utf-8")
