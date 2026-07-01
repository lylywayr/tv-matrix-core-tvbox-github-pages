# TV-Matrix-Core

全自动影视仓线路聚合与健康度验证系统。系统默认以自动发现为主、手动配置为辅：会从 GitHub 公共代码搜索和用户配置的公开聚合页中搜集候选线路，验证后只发布评分较优的一小批结果，避免 GitHub Actions 运行时间过长。

![线路总数](https://img.shields.io/badge/total-0-blue)
![在线率](https://img.shields.io/badge/online_rate-0.00%-brightgreen)
![最后更新](https://img.shields.io/badge/updated-2026--07--01T02:30:23.442718+00:00-lightgrey)

## 快速引用

- GitHub Pages: `https://lylywayr.github.io/tv-matrix-core-tvbox-github-pages`
- TVBox JSON: `https://lylywayr.github.io/tv-matrix-core-tvbox-github-pages/output/tvbox.json`
- M3U: `https://lylywayr.github.io/tv-matrix-core-tvbox-github-pages/output/live.m3u`
- 本次精选发布数量: `0`

## 当前状态

- 已验证候选数: 0
- 在线候选数: 0
- 离线候选数: 0
- 平均健康分: 0.0

## 近期在线率趋势

```text
▁▁
0% 0%
```

## 本次可用线路

| 名称 | 标签 | 健康分 | 延迟 | 线路链接 |
| --- | --- | ---: | ---: | --- |
| 暂无可用线路 | - | - | - | - |

## 自动与手动来源

- 自动发现默认开启，配置位于 `config/sources.yml` 的 `discovery.github_code_search`。
- 手动来源仍保留在 `fixed_sources`，适合放入你确认稳定、允许抓取和发布的线路。
- 最终产物会按健康分排序，并受 `output.max_valid_outputs` 限制。

## 本地命令

```powershell
python -m pip install -r requirements.txt
python -m tv_matrix.cli run --config config/sources.yml
python -m tv_matrix.cli validate --url https://example.com/tvbox.json
python -m tv_matrix.cli rollback
```

## AI 维护指南

面向 Codex 和其他 AI 编码助手的系统架构、数据流和扩展点说明见 `AI_ARCHITECTURE.md`。
