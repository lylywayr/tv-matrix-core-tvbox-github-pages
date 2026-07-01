# TV-Matrix-Core

全自动影视仓线路聚合与健康度验证系统。系统默认以自动发现为主、手动配置为辅：会从 GitHub 公共代码搜索和用户配置的公开聚合页中搜集候选线路，验证后只发布评分较优的一小批结果，避免 GitHub Actions 运行时间过长。

![线路总数](https://img.shields.io/badge/total-133-blue)
![在线率](https://img.shields.io/badge/online_rate-7.52%-brightgreen)
![最后更新](https://img.shields.io/badge/updated-2026--07--01T03:09:13.760594+00:00-lightgrey)

## 快速引用

- GitHub Pages: `https://lylywayr.github.io/tv-matrix-core-tvbox-github-pages`
- 普通影视仓聚合入口: `https://lylywayr.github.io/tv-matrix-core-tvbox-github-pages/output/warehouse.json`
- 18+ 独立聚合入口: `https://lylywayr.github.io/tv-matrix-core-tvbox-github-pages/output/adult-warehouse.json`
- TVBox JSON: `https://lylywayr.github.io/tv-matrix-core-tvbox-github-pages/output/tvbox.json`
- M3U: `https://lylywayr.github.io/tv-matrix-core-tvbox-github-pages/output/live.m3u`
- 18+ M3U: `https://lylywayr.github.io/tv-matrix-core-tvbox-github-pages/output/adult-live.m3u`
- 全部可用清单: `https://lylywayr.github.io/tv-matrix-core-tvbox-github-pages/output/all-lines.json`
- 本次精选发布数量: `3`
- 本次18+精选发布数量: `7`

## 当前状态

- 已验证候选数: 133
- 在线候选数: 10
- 离线候选数: 123
- 平均健康分: 9.83

## 近期在线率趋势

```text
▁▁▁▂▂▁
0% 0% 0% 22% 18% 8%
```

## 本次普通可用线路

| 名称 | 标签 | 健康分 | 延迟 | 线路链接 |
| --- | --- | ---: | ---: | --- |
| GitHub box.json | 快 | 100.0 | 4ms | `https://raw.githubusercontent.com/FreeDTV/FreeD/2511407b95ec434cf5d9e65f36aac63141c4a7ba/box.json` |
| www.seedhub.cc | 快 | 99.99 | 14ms | `https://www.seedhub.cc` |
| dxawi.github.io | 快 | 99.99 | 14ms | `https://dxawi.github.io/0/0.json` |
| GitHub tvbox.json | 快 | 99.99 | 15ms | `https://raw.githubusercontent.com/phoenix7750/iptv/b5321a52539e837847f1e2c96578482dd3bf7915/tvbox.json` |
| m3u.ibert.me | 快 | 99.98 | 34ms | `https://m3u.ibert.me/txt/fmml_ipv6.txt` |
| www.xb6v.com | 快 | 99.95 | 96ms | `https://www.xb6v.com` |
| tvbox.catvod.com | 快 | 99.93 | 138ms | `https://tvbox.catvod.com/js/bili.js` |
| tvbox.catvod.com | 快 | 99.93 | 140ms | `https://tvbox.catvod.com/js/aqy.js` |
| www.xb6v.com | 快 | 99.93 | 142ms | `http://www.xb6v.com` |
| jx.xmflv.com | 快 | 99.92 | 152ms | `https://jx.xmflv.com/?url=` |
| www.yemu.xyz | 快 | 99.89 | 224ms | `https://www.yemu.xyz/?url=` |
| www.yingm.cc | 快 | 99.88 | 241ms | `https://www.yingm.cc/dm/dm.json` |
| v.aikanbot.com | 快 | 99.88 | 246ms | `https://v.aikanbot.com` |
| www.rebovod.com | 快 | 99.73 | 549ms | `https://www.rebovod.com` |
| huohu.yihn.cc | 快 | 99.55 | 899ms | `http://huohu.yihn.cc` |
| tvbox.catvod.com | 快 | 99.48 | 46ms | `https://tvbox.catvod.com/js/tx.js` |
| tvbox.catvod.com | 快 | 98.98 | 46ms | `https://tvbox.catvod.com/js/mgtv.js` |
| 12586.kstore.space | 快 | 98.94 | 115ms | `https://12586.kstore.space/123.txt` |
| tvbox.catvod.com | 快 | 98.47 | 51ms | `https://tvbox.catvod.com/js/yk.js` |
| tvbox.catvod.com | 快 | 96.98 | 50ms | `https://tvbox.catvod.com/js/ik.js` |
| tvbox.catvod.com | 快 | 96.48 | 47ms | `https://tvbox.catvod.com/js/sg.js` |
| tvbox.catvod.com | 快 | 96.45 | 92ms | `https://tvbox.catvod.com/js/drpy2.min.js` |
| jx.m3u8.tv | 快 | 95.98 | 50ms | `https://jx.m3u8.tv/jiexi/?url=` |
| jx.aidouer.net | 快 | 95.48 | 46ms | `https://jx.aidouer.net/?url=` |
| jx.xyflv.cc | 快 | 95.48 | 48ms | `https://jx.xyflv.cc/?url=` |
| bind.315999.xyz | 快 | 95.45 | 108ms | `https://bind.315999.xyz/89.txt` |
| www.gsjtlxy.top | 快 | 95.44 | 112ms | `https://www.gsjtlxy.top/xgapp.php/v3/` |
| lanyinghz.oss-cn-hangzhou.aliyuncs.com | 快 | 95.39 | 229ms | `https://lanyinghz.oss-cn-hangzhou.aliyuncs.com/lanyingxmy.txt` |
| staraugust123456.oss-cn-hangzhou.aliyuncs.com | 快 | 95.39 | 229ms | `https://staraugust123456.oss-cn-hangzhou.aliyuncs.com/2.txt` |
| muouapp.oss-cn-hangzhou.aliyuncs.com | 快 | 95.38 | 234ms | `https://muouapp.oss-cn-hangzhou.aliyuncs.com/MUOUAPP/godbbq.txt` |
| tiantangyoulu.oss-cn-beijing.aliyuncs.com | 快 | 95.38 | 240ms | `https://tiantangyoulu.oss-cn-beijing.aliyuncs.com/tengxunyun.txt` |
| aysappto.oss-cn-chengdu.aliyuncs.com | 快 | 95.38 | 250ms | `https://aysappto.oss-cn-chengdu.aliyuncs.com/qj2.txt` |
| app.789dd.cn | 快 | 95.22 | 551ms | `http://app.789dd.cn` |

## 本次18+可用线路

| 名称 | 标签 | 健康分 | 延迟 | 线路链接 |
| --- | --- | ---: | ---: | --- |
| home.jundie.top:81 | 快 | 99.87 | 266ms | `http://home.jundie.top:81/top98.json` |
| www.cnblogs.com | 快 | 99.35 | 1292ms | `https://www.cnblogs.com/johnjackson/p/17082254.html` |
| www.饭太硬.net | 快 | 98.99 | 26ms | `http://www.饭太硬.net/tv` |
| www.159e.cn | 快 | 98.81 | 2390ms | `https://www.159e.cn/1838.html` |
| 我不是.摸鱼儿.top | 快 | 97.74 | 528ms | `http://我不是.摸鱼儿.top` |
| chat2db-ai.com | 快 | 97.69 | 625ms | `https://chat2db-ai.com/` |
| cdn-www.cnblogs.com | 快 | 97.48 | 1045ms | `https://cdn-www.cnblogs.com/js/blog-common.min.js?v=RFetZGrSQTwmcW6anQWlU044F8CCvhZ7MkLSxIC9Yng` |

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
