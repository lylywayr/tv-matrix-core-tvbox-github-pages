# TV-Matrix-Core

全自动影视仓线路聚合与健康度验证系统。系统从配置源和公开发现页采集候选线路，执行网络层、内容层和可选 TCP 探测，基于历史表现评分，并发布 TVBox/M3U 产物与 GitHub Pages 面板。

![线路总数](https://img.shields.io/badge/total-0-blue)
![在线率](https://img.shields.io/badge/online_rate-0.00%-brightgreen)
![最后更新](https://img.shields.io/badge/updated-2026--07--01T02:30:23.442718+00:00-lightgrey)

## 快速引用

- TVBox JSON: `output/tvbox.json`
- M3U: `output/live.m3u`
- 静态导航页: `public/index.html`

## 当前状态

- 总线路数: 0
- 在线线路数: 0
- 离线线路数: 0
- 平均健康分: 0.0

## 近期在线率趋势

```text
▁▁
0% 0%
```

## 线路统计

| 名称 | 状态 | 健康分 | 延迟 | 连续失败 |
| --- | --- | ---: | ---: | ---: |
| 暂无配置源 | - | - | - | - |

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
