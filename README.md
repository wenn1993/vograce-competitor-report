# Vograce 竞品分析报告系统

## 📋 概述

本系统用于维护 Vograce 定制动漫周边产品的竞争对手分析报告，支持每日自动更新数据。

## 📁 文件结构

```
/Users/admin/WorkBuddy/20260324141124/
├── vograce-competitor-report.html     # 竞品分析报告主文件
├── competitor_data_update.py           # 每日更新脚本
├── competitor_data/                    # 数据存储目录
│   ├── daily_update_log.json         # 更新日志
│   ├── daily_summary.json            # 每日摘要
│   ├── price_history.json            # 价格历史
│   └── competitor_*.json            # 各竞品快照
├── serve_competitor_report.py        # 本地服务器脚本
└── run_competitor_update.sh          # Shell包装脚本
```

## 🚀 使用方法

### 1. 启动本地服务器

```bash
cd /Users/admin/WorkBuddy/20260324141124
python3 serve_competitor_report.py
```

访问地址: http://localhost:8899/vograce-competitor-report.html

### 2. 手动运行更新

```bash
python3 competitor_data_update.py
```

### 3. 查看数据

- 更新日志: `competitor_data/daily_update_log.json`
- 价格历史: `competitor_data/price_history.json`
- 每日摘要: `competitor_data/daily_summary.json`

## ⏰ 自动化任务

已配置每日自动更新任务：
- **任务名称**: Vograce竞品报告每日更新
- **执行时间**: 每天 08:00
- **执行内容**: 更新报告时间戳、记录日志、生成摘要

## 📊 报告内容

报告包含以下模块：

1. **Vograce 主体概况** - 核心品类、目标客户、起售价、核心优势
2. **主要竞品分析** - 5大核心竞品详细信息（WooAcry、Zap! Creatives、Sticker Mule、Makeship、Chilly Pig）
3. **WooAcry vs Vograce 深度对比** - 最大威胁的详细对比分析
4. **六维综合评分对比** - 价格竞争力、产品质量、品类广度等
5. **关键产品价格对比** - 各竞品热门产品价格对比
6. **市场重要动向** - 关税冲击、产品趋势、营销动态
7. **SWOT分析** - Vograce 竞争优势与核心风险
8. **竞品动态监测清单** - 监测方向、渠道、频率

## 🔧 维护说明

- 报告中的价格和动态信息需要手动更新
- 自动化任务只更新时间戳和记录日志
- 建议每周检查一次竞品网站以获取最新数据
