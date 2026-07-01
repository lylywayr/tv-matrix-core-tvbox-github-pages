"""Static GitHub Pages dashboard generator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def render_site(root: Path, state: dict[str, Any]) -> None:
    """Render a mobile-friendly static dashboard."""

    public = root / "public"
    public.mkdir(parents=True, exist_ok=True)
    output_public = public / "output"
    output_public.mkdir(parents=True, exist_ok=True)
    for name in ("tvbox.json", "live.m3u", "summary.json"):
        src = root / "output" / name
        if src.exists():
            (output_public / name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    summary = _read_json(root / "output" / "summary.json")
    sources = []
    for url, source in state.get("sources", {}).items():
        last = (source.get("records") or [{}])[-1]
        if last.get("ok"):
            sources.append(
                {
                    "name": source.get("name", url),
                    "url": url,
                    "score": last.get("score", 0),
                    "label": last.get("label", "稳定"),
                    "elapsed_ms": last.get("elapsed_ms"),
                    "origin": source.get("origin", ""),
                }
            )
    sources = sorted(
        sources,
        key=lambda item: (float(item.get("score", 0)), -(item.get("elapsed_ms") or 999999)),
        reverse=True,
    )[:50]
    data = {"summary": summary, "sources": sources, "runs": state.get("runs", [])[-60:]}
    (public / "data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    (public / "index.html").write_text(_html(), encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _html() -> str:
    return """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TV-Matrix-Core</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
  <style>
    :root { color-scheme: light; --ink:#202124; --muted:#5f6368; --line:#dadce0; --bg:#f8fafd; --brand:#0b57d0; --ok:#137333; }
    * { box-sizing: border-box; }
    body { margin:0; font-family: Arial, "Microsoft YaHei", sans-serif; background:var(--bg); color:var(--ink); }
    header { background:#fff; border-bottom:1px solid var(--line); }
    .wrap { max-width:1120px; margin:0 auto; padding:18px; }
    h1 { margin:0 0 6px; font-size:28px; letter-spacing:0; }
    .meta { color:var(--muted); font-size:14px; }
    .stats { display:grid; grid-template-columns:repeat(4, minmax(0, 1fr)); gap:10px; margin-top:16px; }
    .stat, .panel { background:#fff; border:1px solid var(--line); border-radius:8px; padding:14px; }
    .stat b { display:block; font-size:24px; margin-top:4px; }
    .actions { display:flex; gap:8px; flex-wrap:wrap; margin:16px 0; }
    button, a.button { border:1px solid var(--brand); background:var(--brand); color:#fff; border-radius:6px; padding:9px 12px; cursor:pointer; text-decoration:none; font-size:14px; }
    .grid { display:grid; grid-template-columns:1fr 360px; gap:14px; align-items:start; }
    table { width:100%; border-collapse:collapse; background:#fff; border:1px solid var(--line); border-radius:8px; overflow:hidden; }
    th, td { padding:10px; border-bottom:1px solid var(--line); text-align:left; font-size:14px; word-break:break-word; }
    th { background:#f1f3f4; color:#3c4043; }
    .tag { color:var(--ok); font-weight:700; }
    canvas { width:100%; min-height:260px; }
    @media (max-width: 820px) { .stats, .grid { grid-template-columns:1fr; } h1 { font-size:24px; } th:nth-child(4), td:nth-child(4) { display:none; } }
  </style>
</head>
<body>
  <header><div class="wrap"><h1>TV-Matrix-Core</h1><div class="meta" id="updated">loading</div></div></header>
  <main class="wrap">
    <section class="stats">
      <div class="stat">总线路<b id="total">0</b></div>
      <div class="stat">在线<b id="online">0</b></div>
      <div class="stat">在线率<b id="rate">0%</b></div>
      <div class="stat">平均分<b id="score">0</b></div>
    </section>
    <div class="actions">
      <button onclick="copyText(location.origin + location.pathname.replace(/index\\.html$/, '') + 'output/tvbox.json')">复制 TVBox</button>
      <button onclick="copyText(location.origin + location.pathname.replace(/index\\.html$/, '') + 'output/live.m3u')">复制 M3U</button>
      <a class="button" href="output/tvbox.json">打开 JSON</a>
      <a class="button" href="output/live.m3u">打开 M3U</a>
    </div>
    <section class="grid">
      <table>
        <thead><tr><th>名称</th><th>健康</th><th>延迟</th><th>地址</th><th>操作</th></tr></thead>
        <tbody id="rows"></tbody>
      </table>
      <aside class="panel"><canvas id="trend"></canvas></aside>
    </section>
  </main>
  <script>
    async function copyText(text) { await navigator.clipboard.writeText(text); }
    fetch('data.json').then(r => r.json()).then(data => {
      const s = data.summary || {};
      total.textContent = s.total || 0;
      online.textContent = s.online || 0;
      rate.textContent = (((s.online_rate || 0) * 100).toFixed(1)) + '%';
      score.textContent = s.average_score || 0;
      updated.textContent = '最后更新: ' + (s.generated_at || '-');
      rows.innerHTML = (data.sources || []).map(item => `<tr><td>${escapeHtml(item.name)}</td><td class="tag">${item.label} ${item.score}</td><td>${item.elapsed_ms || '-'}ms</td><td>${escapeHtml(item.url)}</td><td><button data-url="${escapeHtml(item.url)}">复制</button></td></tr>`).join('') || '<tr><td colspan="5">暂无可用线路</td></tr>';
      rows.querySelectorAll('button[data-url]').forEach(button => button.addEventListener('click', () => copyText(button.dataset.url)));
      new Chart(document.getElementById('trend'), {
        type: 'line',
        data: { labels: (data.runs || []).map((_, i) => i + 1), datasets: [{ label: '在线率', data: (data.runs || []).map(r => (r.online_rate || 0) * 100), borderColor: '#0b57d0', backgroundColor: 'rgba(11,87,208,.12)', tension: .25, fill: true }] },
        options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { min: 0, max: 100 } } }
      });
    });
    function escapeHtml(v) { return String(v).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
  </script>
</body>
</html>
"""
