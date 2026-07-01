"""README renderer for dynamic repository documentation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def render_readme(root: Path, state: dict[str, Any], site_base_url: str = "") -> None:
    """Generate README.md from current state and summary files."""

    summary_path = root / "output" / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
    rows = []
    adult_rows = []
    for url, source, last in _online_sources(state, adult=False):
        rows.append(
            "| {name} | {label} | {score} | {latency} | `{url}` |".format(
                name=_md(source.get("name", url)),
                label=_md(last.get("label", "稳定")),
                score=last.get("score", "-"),
                latency=f"{last.get('elapsed_ms')}ms" if last.get("elapsed_ms") is not None else "-",
                url=url,
            )
        )
    for url, source, last in _online_sources(state, adult=True):
        adult_rows.append(
            "| {name} | {label} | {score} | {latency} | `{url}` |".format(
                name=_md(source.get("name", url)),
                label=_md(last.get("label", "稳定")),
                score=last.get("score", "-"),
                latency=f"{last.get('elapsed_ms')}ms" if last.get("elapsed_ms") is not None else "-",
                url=url,
            )
        )

    trend = _trend_line(state.get("runs", []))
    total = summary.get("total", 0)
    online_rate = summary.get("online_rate", 0.0)
    last_update = summary.get("generated_at", "-")
    selected = summary.get("artifacts", {}).get("selected", "0")
    adult_selected = summary.get("artifacts", {}).get("adult_selected", "0")
    base = site_base_url.rstrip("/")
    tvbox_link = f"{base}/output/tvbox.json" if base else "output/tvbox.json"
    warehouse_link = f"{base}/output/warehouse.json" if base else "output/warehouse.json"
    adult_warehouse_link = f"{base}/output/adult-warehouse.json" if base else "output/adult-warehouse.json"
    all_lines_link = f"{base}/output/all-lines.json" if base else "output/all-lines.json"
    m3u_link = f"{base}/output/live.m3u" if base else "output/live.m3u"
    adult_m3u_link = f"{base}/output/adult-live.m3u" if base else "output/adult-live.m3u"
    pages_link = base or "public/index.html"

    content = f"""# TV-Matrix-Core

全自动影视仓线路聚合与健康度验证系统。系统默认以自动发现为主、手动配置为辅：会从 GitHub 公共代码搜索和用户配置的公开聚合页中搜集候选线路，验证后只发布评分较优的一小批结果，避免 GitHub Actions 运行时间过长。

![线路总数](https://img.shields.io/badge/total-{total}-blue)
![在线率](https://img.shields.io/badge/online_rate-{online_rate:.2%}-brightgreen)
![最后更新](https://img.shields.io/badge/updated-{str(last_update).replace('-', '--')}-lightgrey)

## 快速引用

- GitHub Pages: `{pages_link}`
- 普通影视仓聚合入口: `{warehouse_link}`
- 18+ 独立聚合入口: `{adult_warehouse_link}`
- TVBox JSON: `{tvbox_link}`
- M3U: `{m3u_link}`
- 18+ M3U: `{adult_m3u_link}`
- 全部可用清单: `{all_lines_link}`
- 本次精选发布数量: `{selected}`
- 本次18+精选发布数量: `{adult_selected}`

## 当前状态

- 已验证候选数: {total}
- 在线候选数: {summary.get('online', 0)}
- 离线候选数: {summary.get('offline', 0)}
- 平均健康分: {summary.get('average_score', 0)}

## 近期在线率趋势

```text
{trend}
```

## 本次普通可用线路

| 名称 | 标签 | 健康分 | 延迟 | 线路链接 |
| --- | --- | ---: | ---: | --- |
{chr(10).join(rows) if rows else '| 暂无可用线路 | - | - | - | - |'}

## 本次18+可用线路

| 名称 | 标签 | 健康分 | 延迟 | 线路链接 |
| --- | --- | ---: | ---: | --- |
{chr(10).join(adult_rows) if adult_rows else '| 暂无18+线路 | - | - | - | - |'}

## 自动与手动来源

- 自动发现默认开启，配置位于 `config/sources.yml` 的 `discovery.github_code_search`。
- 手动来源仍保留在 `fixed_sources`，适合放入你确认稳定、允许抓取和发布的线路。
- 最终产物会按健康分排序，并受 `output.max_valid_outputs` 限制。
- 普通内容和 18+ 内容会分别聚合，避免混在同一个入口中。

## 本地命令

```powershell
python -m pip install -r requirements.txt
python -m tv_matrix.cli run --config config/sources.yml
python -m tv_matrix.cli validate --url https://example.com/tvbox.json
python -m tv_matrix.cli rollback
```

## AI 维护指南

面向 Codex 和其他 AI 编码助手的系统架构、数据流和扩展点说明见 `AI_ARCHITECTURE.md`。
"""
    (root / "README.md").write_text(content, encoding="utf-8")


def _online_sources(state: dict[str, Any], adult: bool) -> list[tuple[str, dict[str, Any], dict[str, Any]]]:
    sources = []
    for url, source in state.get("sources", {}).items():
        last = (source.get("records") or [{}])[-1]
        if last.get("ok") and bool(last.get("adult")) is adult:
            sources.append((url, source, last))
    return sorted(
        sources,
        key=lambda item: (float(item[2].get("score", 0)), -(item[2].get("elapsed_ms") or 999999)),
        reverse=True,
    )[:50]


def _trend_line(runs: list[dict[str, Any]]) -> str:
    points = runs[-20:]
    if not points:
        return "no data"
    blocks = "▁▂▃▄▅▆▇█"
    line = []
    for run in points:
        rate = float(run.get("online_rate", 0))
        line.append(blocks[min(7, int(rate * 8))])
    labels = " ".join(f"{float(run.get('online_rate', 0)):.0%}" for run in points[-8:])
    return "".join(line) + "\n" + labels


def _md(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")
