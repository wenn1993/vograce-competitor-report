#!/bin/bash
# ============================================================
# 本地每日自动更新脚本 — 双重备份方案
# 时间: 每天 09:00（GitHub Actions 是 08:00 UTC+8）
# 逻辑: 如果 GitHub Actions 今天已成功运行，跳过；否则执行本地更新
# ============================================================
LOG_DIR="/Users/admin/WorkBuddy/20260324141124/logs"
LOG="$LOG_DIR/launchd_stdout.log"
mkdir -p "$LOG_DIR"

echo "=============================" >> "$LOG"
echo "$(date '+%Y-%m-%d %H:%M:%S') [本地备份] 开始检查..." >> "$LOG"

cd /Users/admin/WorkBuddy/20260324141124 || {
  echo "$(date '+%Y-%m-%d %H:%M:%S') ❌ 无法进入工作目录" >> "$LOG"
  exit 1
}

# 拉取最新 git 记录，判断今天 GitHub Actions 是否已运行
git fetch origin master --quiet 2>/dev/null
TODAY=$(date '+%Y-%m-%d')
LAST_AUTO=$(git log origin/master --oneline --since="${TODAY} 00:00" --grep="auto: 每日数据更新" 2>/dev/null | head -1)

if [ -n "$LAST_AUTO" ]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') ✅ GitHub Actions 今天已成功更新（${LAST_AUTO}），跳过本地备份" >> "$LOG"
  exit 0
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') ⚠️  GitHub Actions 今天未运行，启动本地备份更新..." >> "$LOG"

/opt/homebrew/bin/python3 auto_update.py >> "$LOG" 2>&1
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') ✅ 本地备份更新成功" >> "$LOG"
else
  echo "$(date '+%Y-%m-%d %H:%M:%S') ❌ 本地备份更新失败（exit code: $EXIT_CODE）" >> "$LOG"
fi

# 保留最近 30 天日志（防止日志文件过大）
if [ -f "$LOG" ] && [ $(wc -l < "$LOG") -gt 3000 ]; then
  tail -2000 "$LOG" > "${LOG}.tmp" && mv "${LOG}.tmp" "$LOG"
fi
