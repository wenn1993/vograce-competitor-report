#!/bin/bash
# Vograce 竞品数据每日更新
# 自动更新竞争对手分析报告中的数据

WORKSPACE="/Users/admin/WorkBuddy/20260324141124"
LOG_FILE="$WORKSPACE/competitor_data/update.log"

echo "$(date '+%Y-%m-%d %H:%M:%S') - 开始竞品数据更新..." >> "$LOG_FILE"

# 运行Python更新脚本
python3 "$WORKSPACE/daily_competitor_update.py" >> "$LOG_FILE" 2>&1

echo "$(date '+%Y-%m-%d %H:%M:%S') - 更新完成" >> "$LOG_FILE"
