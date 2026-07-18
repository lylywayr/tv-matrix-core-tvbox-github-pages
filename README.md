# TV-Matrix-Core

全自动影视仓线路聚合与健康度验证系统。系统默认以自动发现为主、手动配置为辅：会从 GitHub 公共代码搜索和用户配置的公开聚合页中搜集候选线路，验证后只发布评分较优的一小批结果，避免 GitHub Actions 运行时间过长。

![线路总数](https://img.shields.io/badge/total-29-blue)
![在线率](https://img.shields.io/badge/online_rate-82.76%-brightgreen)
![最后更新](https://img.shields.io/badge/updated-2026--07--18T05:05:57.878698+00:00-lightgrey)

## 快速引用

- GitHub Pages: `https://lylywayr.github.io/tv-matrix-core-tvbox-github-pages`
- 普通影视仓聚合入口: `https://lylywayr.github.io/tv-matrix-core-tvbox-github-pages/output/warehouse.json`
- 18+ 独立聚合入口: `https://lylywayr.github.io/tv-matrix-core-tvbox-github-pages/output/adult-warehouse.json`
- TVBox JSON: `https://lylywayr.github.io/tv-matrix-core-tvbox-github-pages/output/tvbox.json`
- M3U: `https://lylywayr.github.io/tv-matrix-core-tvbox-github-pages/output/live.m3u`
- 18+ M3U: `https://lylywayr.github.io/tv-matrix-core-tvbox-github-pages/output/adult-live.m3u`
- 全部可用清单: `https://lylywayr.github.io/tv-matrix-core-tvbox-github-pages/output/all-lines.json`
- 本次精选发布数量: `20`
- 本次18+精选发布数量: `4`

## 当前状态

- 已验证候选数: 29
- 在线候选数: 24
- 离线候选数: 5
- 平均健康分: 81.8

## 近期在线率趋势

```text
▂▁▁▁▁▁▁▁▁▁▁▁▂▁█▂▇▇▇▇
16% 12% 100% 20% 83% 83% 80% 83%
```

## 本次普通可用线路

| 名称 | 标签 | 健康分 | 延迟 | 线路链接 |
| --- | --- | ---: | ---: | --- |
| zhanghong1983 | 快 | 100.0 | 8ms | `https://raw.githubusercontent.com/zhanghong1983/tvboxzy/f8261b0d32e893aa9372fd385f5fb5c421fcdde2/XBPQ.json` |
| www.seedhub.cc | 快 | 99.99 | 14ms | `https://www.seedhub.cc` |
| GitHub tvbox.json | 快 | 99.99 | 15ms | `https://raw.githubusercontent.com/phoenix7750/iptv/b5321a52539e837847f1e2c96578482dd3bf7915/tvbox.json` |
| yw88075 | 快 | 99.99 | 16ms | `https://raw.githubusercontent.com/yw88075/tvbox/5df857abc263fda3c3e6cb1c285229f4d5e02230/yw.json` |
| wlcmc1972 | 快 | 99.99 | 18ms | `https://raw.githubusercontent.com/wlcmc1972/tvbox/15df8ab0379d8a2ee58c4b86a957e36e2f796337/t1.json` |
| freedtv-box | 快 | 99.99 | 23ms | `https://raw.githubusercontent.com/FreeDTV/FreeD/2511407b95ec434cf5d9e65f36aac63141c4a7ba/box.json` |
| aliluya1977 | 快 | 99.99 | 23ms | `https://raw.githubusercontent.com/aliluya1977/TVBox/35b1b50ee77ee4e422fc2b9cb83ac0668016305e/xm.json` |
| myhomebox | 快 | 99.99 | 23ms | `https://raw.githubusercontent.com/myhomebox/tv/c5142631f61c4e649bc615f5625066783ef38883/yt.json` |
| gaotianliuyun-js | 快 | 99.99 | 24ms | `https://raw.githubusercontent.com/gaotianliuyun/gao/8213bb046f4dce746b5f2ddcddb13a336d0b0d60/js.json` |
| m3u.ibert.me | 快 | 99.98 | 34ms | `https://m3u.ibert.me/txt/fmml_ipv6.txt` |
| guot55 | 快 | 99.98 | 37ms | `https://raw.githubusercontent.com/guot55/yg/d0879e44c351c7ede52709ae4194a0c1f692855f/jsm.json` |
| mcp2016 | 快 | 99.98 | 37ms | `https://raw.githubusercontent.com/mcp2016/TVBox/848272f1eaf98a3e10042681919c2ad2fa92daea/pj.json` |
| cnnbgo | 快 | 99.98 | 38ms | `https://raw.githubusercontent.com/cnnbgo/tvbox/f2afa9065deb1c2c2341df2776abdc6b02c5913f/x.json` |
| jak0099 | 快 | 99.98 | 39ms | `https://raw.githubusercontent.com/jak0099/dr/f2aa3691d11a6e198714fe14d445341576cba193/dr2.json` |
| dxawi.github.io | 快 | 99.96 | 78ms | `https://dxawi.github.io/0/0.json` |
| www.xb6v.com | 快 | 99.95 | 96ms | `https://www.xb6v.com` |
| catvod-mj | 快 | 99.95 | 101ms | `https://raw.githubusercontent.com/CatVodTV/CatTV.github.io/337cd299e699ca0d49b7bf35e29b8b38068572d5/mj.json` |
| tiantaiyx-0 | 快 | 99.94 | 115ms | `https://raw.githubusercontent.com/tiantaiyx/tvbox/d97a57c12bc0ac189cda5acfe530394e03d80371/0.json` |
| tvbox.catvod.com | 快 | 99.93 | 138ms | `https://tvbox.catvod.com/js/bili.js` |
| tvbox.catvod.com | 快 | 99.93 | 140ms | `https://tvbox.catvod.com/js/aqy.js` |
| www.xb6v.com | 快 | 99.93 | 142ms | `http://www.xb6v.com` |
| www.yingm.cc | 快 | 99.91 | 183ms | `https://www.yingm.cc/dm/dm.json` |
| tvbox.catvod.com | 快 | 99.48 | 46ms | `https://tvbox.catvod.com/js/tx.js` |
| 12586.kstore.space | 快 | 99.47 | 64ms | `https://12586.kstore.space/123.txt` |
| tvbox.catvod.com | 快 | 98.98 | 46ms | `https://tvbox.catvod.com/js/mgtv.js` |
| tvbox.catvod.com | 快 | 98.47 | 51ms | `https://tvbox.catvod.com/js/yk.js` |
| tvbox.catvod.com | 快 | 96.98 | 50ms | `https://tvbox.catvod.com/js/ik.js` |
| tvbox.catvod.com | 快 | 96.48 | 47ms | `https://tvbox.catvod.com/js/sg.js` |
| liu673cn-box | 快 | 96.47 | 69ms | `https://raw.githubusercontent.com/liu673cn/box/bac55898bcd4710a46245e37646b48c6a16ef0bd/m.json` |
| tvbox.catvod.com | 快 | 96.45 | 92ms | `https://tvbox.catvod.com/js/drpy2.min.js` |
| yueer59 | 快 | 94.95 | 93ms | `https://raw.githubusercontent.com/yueer59/Tvbox/74ee1483b67e73767fe67bf3a2d4d6502c4cafcd/api.json` |
| raw.liucn.cc | 快 | 87.23 | 83ms | `https://raw.liucn.cc/box/m.json` |
| home.jundie.top:81 | 稳定 | 79.89 | 213ms | `http://home.jundie.top:81/top98.json` |

## 本次18+可用线路

| 名称 | 标签 | 健康分 | 延迟 | 线路链接 |
| --- | --- | ---: | ---: | --- |
| gh.927223.xyz | 快 | 99.98 | 33ms | `https://gh.927223.xyz/https://raw.githubusercontent.com/develop202/migu_video/refs/heads/main/interface.txt` |
| tvbox18 | 快 | 99.95 | 99ms | `https://raw.githubusercontent.com/qirenzhidao/tvbox18/86e1e39338ae41fcbceb9d0d3896a7618ced6cd6/tv.json` |
| skyyaman18 | 快 | 99.95 | 99ms | `https://raw.githubusercontent.com/skyyaman/skyyaman.github.io/4ae60a8a2ccfe0444dea962d5ddb2f326fc640ed/s18.json` |
| davidlee6628 | 快 | 96.48 | 37ms | `https://raw.githubusercontent.com/davidlee6628/ssr/e510212c6f9ac2fa918679ea90ef04b29501c9b4/tt.json` |

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
