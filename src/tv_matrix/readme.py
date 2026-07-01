"""README renderer for dynamic repository documentation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def render_readme(root: Path, state: dict[str, Any], site_base_url: str = "") -> None:
    """Generate README.md from current state and summary files."""

    summary_path = root / "output" / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
    sources = state.get("sources", {})
    rows = []
    for url, source in sorted(sources.items(), key=lambda item: item[1].get("name", "")):
        last = (source.get("records") or [{}])[-1]
        rows.append(
            "| {name} | {status} | {score} | {latency} | {failures} |".format(
                name=source.get("name", url),
                status="在线" if last.get("ok") else "离线",
                score=last.get("score", "-"),
                latency=f"{last.get('elapsed_ms')}ms" if last.get("elapsed_ms") is not None else "-",
                failures=source.get("consecutive_failures", 0),
            )
        )

    trend = _trend_line(state.get("runs", []))
    total = summary.get("total", 0)
    online_rate = summary.get("online_rate", 0.0)
    last_update = summary.get("generated_at", "-")
    base = site_base_url.rstrip("/")
    tvbox_link = f"{base}/output/tvbox.json" if base else "output/tvbox.json"
    m3u_link = f"{base}/output/live.m3u" if base else "output/live.m3u"

    content = f"""# TV-Matrix-Core

全自动影视仓线路聚合与健康度验证系统。系统从配置源和公开发现页采集候选线路，执行网络层、内容层和可选 TCP 探测，基于历史表现评分，并发布 TVBox/M3U 产物与 GitHub Pages 面板。

![线路总数](https://img.shields.io/badge/total-{total}-blue)
![在线率](https://img.shields.io/badge/online_rate-{online_rate:.2%}-brightgreen)
![最后更新](https://img.shields.io/badge/updated-{last_update.replace('-', '--')}-lightgrey)

## 快速引用

- TVBox JSON: `{tvbox_link}`
- M3U: `{m3u_link}`
- 静态导航页: `{base or 'public/index.html'}`

## 当前状态

- 总线路数: {total}
- 在线线路数: {summary.get('online', 0)}
- 离线线路数: {summary.get('offline', 0)}
- 平均健康分: {summary.get('average_score', 0)}

## 近期在线率趋势

```text
{trend}
```

## 线路统计

| 名称 | 状态 | 健康分 | 延迟 | 连续失败 |
| --- | --- | ---: | ---: | ---: |
{chr(10).join(rows) if rows else '| 暂无配置源 | - | - | - | - |'}

## 本地命令

```powershell
python -m pip install -r requirements.txt
python -m tv_matrix.cli run --config config/sources.yml
python -m tv_matrix.cli validate --url https://example.com/tvbox.json
python -m tv_matrix.cli rollback
```

## 配置

复制 `config/sources.example.yml` 为 `config/sources.yml`，填入你有权抓取和发布的公开源。抓取逻辑会读取 robots.txt，并遵守 Crawl-delay。

## AI 维护指南

面向 Codex 和其他 AI 编码助手的系统架构、数据流和扩展点说明见 `AI_ARCHITECTURE.md`。
"""
    (root / "README.md").write_text(content, encoding="utf-8")


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
