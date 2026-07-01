"""Artifact generation, validation, backups, and rollback."""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import RunSummary, ValidationResult


def atomic_write(path: Path, content: str) -> None:
    """Atomically write text content."""

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def generate_artifacts(
    results: list[ValidationResult],
    output_dir: Path,
    keep_backups: int,
    max_valid_outputs: int | None = None,
) -> RunSummary:
    """Generate TVBox JSON, M3U, machine summary, and backups."""

    all_valid = sorted(
        [result for result in results if result.ok],
        key=lambda result: (result.score, -(result.elapsed_ms or 999999)),
        reverse=True,
    )
    normal_valid = [result for result in all_valid if not result.adult]
    adult_valid = [result for result in all_valid if result.adult]
    valid = normal_valid[:max_valid_outputs] if max_valid_outputs else normal_valid
    adult_selected = adult_valid[:max_valid_outputs] if max_valid_outputs else adult_valid
    generated_at = datetime.now(UTC).isoformat()
    tvbox = {
        "name": "TV-Matrix-Core",
        "generated_at": generated_at,
        "sites": [
            {
                "key": _safe_key(result.candidate.url),
                "name": f"{result.candidate.name} [{result.label}]",
                "type": 3,
                "api": result.candidate.url,
                "searchable": 1,
                "quickSearch": 1,
                "filterable": 1,
                "ext": {"health_score": result.score, "latency_ms": result.elapsed_ms},
            }
            for result in valid
        ],
    }
    warehouse = _warehouse("TV-Matrix-Core 优选普通仓", generated_at, valid)
    adult_warehouse = _warehouse("TV-Matrix-Core 18+ 独立仓", generated_at, adult_selected)
    all_lines = {
        "generated_at": generated_at,
        "normal": [_line_entry(result) for result in normal_valid],
        "adult": [_line_entry(result) for result in adult_valid],
    }
    m3u_lines = ["#EXTM3U"]
    for result in valid:
        m3u_lines.append(
            f'#EXTINF:-1 tvg-name="{result.candidate.name}",{result.candidate.name} [{result.label}]'
        )
        m3u_lines.append(result.candidate.url)
    adult_m3u_lines = ["#EXTM3U"]
    for result in adult_selected:
        adult_m3u_lines.append(
            f'#EXTINF:-1 tvg-name="{result.candidate.name}",{result.candidate.name} [{result.label}]'
        )
        adult_m3u_lines.append(result.candidate.url)

    summary = RunSummary(
        generated_at=generated_at,
        total=len(results),
        online=len(all_valid),
        offline=len(results) - len(all_valid),
        online_rate=round(len(all_valid) / len(results), 4) if results else 0.0,
        average_score=round(sum(r.score for r in results) / len(results), 2) if results else 0.0,
        artifacts={
            "tvbox": "output/tvbox.json",
            "warehouse": "output/warehouse.json",
            "adult_warehouse": "output/adult-warehouse.json",
            "all_lines": "output/all-lines.json",
            "m3u": "output/live.m3u",
            "adult_m3u": "output/adult-live.m3u",
            "summary": "output/summary.json",
            "selected": str(len(valid)),
            "adult_selected": str(len(adult_selected)),
        },
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    tvbox_text = json.dumps(tvbox, ensure_ascii=False, indent=2)
    warehouse_text = json.dumps(warehouse, ensure_ascii=False, indent=2)
    adult_warehouse_text = json.dumps(adult_warehouse, ensure_ascii=False, indent=2)
    all_lines_text = json.dumps(all_lines, ensure_ascii=False, indent=2)
    summary_text = json.dumps(asdict(summary), ensure_ascii=False, indent=2)
    has_backup = (output_dir / "backups").exists()
    _validate_tvbox(tvbox, allow_empty=not results or not has_backup)
    atomic_write(output_dir / "tvbox.json", tvbox_text)
    atomic_write(output_dir / "warehouse.json", warehouse_text)
    atomic_write(output_dir / "adult-warehouse.json", adult_warehouse_text)
    atomic_write(output_dir / "all-lines.json", all_lines_text)
    atomic_write(output_dir / "live.m3u", "\n".join(m3u_lines) + "\n")
    atomic_write(output_dir / "adult-live.m3u", "\n".join(adult_m3u_lines) + "\n")
    atomic_write(output_dir / "summary.json", summary_text)
    _write_backup(output_dir, keep_backups)
    return summary


def rollback_latest(output_dir: Path) -> Path:
    """Restore the newest complete backup into output_dir."""

    backups = sorted((output_dir / "backups").glob("*"), reverse=True)
    if not backups:
        raise FileNotFoundError("No backups found")
    latest = backups[0]
    for name in (
        "tvbox.json",
        "warehouse.json",
        "adult-warehouse.json",
        "all-lines.json",
        "live.m3u",
        "adult-live.m3u",
        "summary.json",
    ):
        src = latest / name
        if src.exists():
            shutil.copy2(src, output_dir / name)
    return latest


def _validate_tvbox(data: dict[str, Any], allow_empty: bool = False) -> None:
    if "sites" not in data or not isinstance(data["sites"], list):
        raise ValueError("tvbox.json missing sites array")
    if not allow_empty and not data["sites"]:
        raise ValueError("tvbox.json contains no valid sites")
    for site in data["sites"]:
        if not site.get("name") or not str(site.get("api", "")).startswith(("http://", "https://")):
            raise ValueError("tvbox.json contains invalid site entry")


def _write_backup(output_dir: Path, keep_backups: int) -> None:
    stamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    backup_dir = output_dir / "backups" / stamp
    backup_dir.mkdir(parents=True, exist_ok=True)
    for name in (
        "tvbox.json",
        "warehouse.json",
        "adult-warehouse.json",
        "all-lines.json",
        "live.m3u",
        "adult-live.m3u",
        "summary.json",
    ):
        shutil.copy2(output_dir / name, backup_dir / name)
    backups = sorted((output_dir / "backups").glob("*"), reverse=True)
    for old in backups[int(keep_backups) :]:
        shutil.rmtree(old)


def _safe_key(url: str) -> str:
    return str(abs(hash(url)))


def _warehouse(name: str, generated_at: str, results: list[ValidationResult]) -> dict[str, Any]:
    """Create a common multi-warehouse style entry list for 影视仓/FongMi-style apps."""

    return {
        "name": name,
        "generated_at": generated_at,
        "urls": [
            {
                "name": f"{index:02d}. {result.candidate.name} [{result.label}/{result.score}]",
                "url": result.candidate.url,
            }
            for index, result in enumerate(results, start=1)
        ],
    }


def _line_entry(result: ValidationResult) -> dict[str, Any]:
    return {
        "name": result.candidate.name,
        "url": result.candidate.url,
        "score": result.score,
        "label": result.label,
        "elapsed_ms": result.elapsed_ms,
        "origin": result.candidate.origin,
        "adult": result.adult,
        "format": result.content_format.value,
        "valid_item_count": result.valid_item_count,
    }
