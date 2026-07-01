# TV-Matrix-Core

全自动影视仓线路聚合与健康度验证系统。首次运行后，本文件会由程序自动更新为包含徽章、统计表格、趋势图和产物链接的动态 README。

## Quick Start

```powershell
python -m pip install -r requirements.txt
Copy-Item config/sources.example.yml config/sources.yml
python -m tv_matrix.cli run --config config/sources.yml
```

更多架构说明见 `AI_ARCHITECTURE.md`。
