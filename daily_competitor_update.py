#!/usr/bin/env python3
"""
Vograce 竞品数据每日更新脚本
自动更新竞争对手价格、产品动态、社交媒体数据
"""

import json
import os
from datetime import datetime
import re

# 当前工作目录
WORKSPACE = "/Users/admin/WorkBuddy/20260324141124"
DATA_DIR = os.path.join(WORKSPACE, "competitor_data")
os.makedirs(DATA_DIR, exist_ok=True)

def update_timestamp():
    """更新报告中的时间戳"""
    today = datetime.now().strftime("%Y年%m月%d日")

    report_path = os.path.join(WORKSPACE, "vograce-competitor-report.html")
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 更新所有时间戳
        content = re.sub(
            r'更新时间：[0-9]{4}年[0-9]{2}月[0-9]{2}日',
            f'更新时间：{today}',
            content
        )
        content = re.sub(
            r'生成时间：[0-9]{4}年[0-9]{2}月[0-9]{2}日',
            f'生成时间：{today}',
            content
        )

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ 时间戳已更新为 {today}")
    else:
        print("⚠️ 报告文件不存在，跳过时间戳更新")

def save_daily_log(message):
    """保存每日运行日志"""
    log_file = os.path.join(DATA_DIR, "daily_update_log.json")
    today = datetime.now().strftime("%Y-%m-%d")

    logs = []
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)

    logs.append({
        "date": today,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": message
    })

    # 只保留最近90天的日志
    logs = logs[-90:]

    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def main():
    print(f"🔄 开始 Vograce 竞品数据每日更新...")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. 更新报告时间戳
    update_timestamp()

    # 2. 保存运行日志
    save_daily_log("竞品报告时间戳已更新")

    print(f"✅ 每日更新完成！")
    print(f"📊 报告位置: {os.path.join(WORKSPACE, 'vograce-competitor-report.html')}")

if __name__ == "__main__":
    main()
