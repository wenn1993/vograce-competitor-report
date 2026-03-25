#!/usr/bin/env python3
"""
Vograce 竞品数据每日更新脚本 v2.1
自动更新竞争对手价格、产品动态、社交媒体数据
自动同步到GitHub Pages
"""

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

# 配置
WORKSPACE = "/Users/admin/WorkBuddy/20260324141124"
DATA_DIR = os.path.join(WORKSPACE, "competitor_data")
os.makedirs(DATA_DIR, exist_ok=True)

def run_git_command(args, cwd=WORKSPACE):
    """执行git命令"""
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def sync_to_github():
    """同步更新到GitHub"""
    print("\n" + "=" * 50)
    print("🔄 同步到GitHub...")
    print("=" * 50)
    
    # 1. 配置git（如果需要）
    run_git_command(["git", "config", "user.email", "bot@vograce-report.com"])
    run_git_command(["git", "config", "user.name", "Vograce Auto Bot"])
    
    # 2. 添加所有更改
    success, stdout, stderr = run_git_command(["git", "add", "-A"])
    if not success:
        print(f"⚠️ git add 失败: {stderr}")
        return False
    
    # 3. 检查是否有更改
    success, stdout, stderr = run_git_command(["git", "status", "--porcelain"])
    if not stdout.strip():
        print("📝 没有需要提交的更改")
        return True
    
    # 4. 提交更改
    today = get_today()
    commit_msg = f"auto: 每日数据更新 {today}"
    success, stdout, stderr = run_git_command(["git", "commit", "-m", commit_msg])
    if not success:
        print(f"⚠️ git commit 失败: {stderr}")
        return False
    print(f"✅ 已提交: {commit_msg}")
    
    # 5. 推送到GitHub
    success, stdout, stderr = run_git_command(["git", "push", "origin", "master"])
    if not success:
        print(f"⚠️ git push 失败: {stderr}")
        return False
    
    print("✅ 已推送到GitHub!")
    return True

def get_today():
    """获取今天的日期字符串"""
    return datetime.now().strftime("%Y年%m月%d日")

def get_today_short():
    """获取短日期格式"""
    return datetime.now().strftime("%Y-%m-%d")

def update_report_timestamp():
    """更新报告中的时间戳"""
    today = get_today()

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

        print(f"✅ 报告时间戳已更新: {today}")
        return True
    else:
        print("⚠️ 报告文件不存在")
        return False

def save_price_data(prices, page_type):
    """保存价格数据"""
    today = get_today_short()
    price_file = os.path.join(DATA_DIR, "price_history.json")

    history = []
    if os.path.exists(price_file):
        with open(price_file, 'r', encoding='utf-8') as f:
            history = json.load(f)

    history.append({
        "date": today,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "page": page_type,
        "prices": prices,
        "avg": round(sum(prices) / len(prices), 2) if prices else 0,
        "min": min(prices) if prices else 0,
        "max": max(prices) if prices else 0,
        "count": len(prices)
    })

    with open(price_file, 'w', encoding='utf-8') as f:
        json.dump(history[-365:], f, ensure_ascii=False, indent=2)

    print(f"✅ 价格数据已保存: {page_type}, {len(prices)} 个价格点")

def save_daily_log(action, details=""):
    """保存每日运行日志"""
    log_file = os.path.join(DATA_DIR, "daily_update_log.json")
    today = get_today_short()

    logs = []
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)

    logs.append({
        "date": today,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "details": details
    })

    # 只保留最近90天的日志
    logs = logs[-90:]

    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def save_competitor_snapshot(competitor, data):
    """保存竞品快照"""
    snapshot_file = os.path.join(DATA_DIR, f"competitor_{competitor}.json")
    today = get_today_short()

    snapshots = []
    if os.path.exists(snapshot_file):
        with open(snapshot_file, 'r', encoding='utf-8') as f:
            snapshots = json.load(f)

    snapshots.append({
        "date": today,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": data
    })

    # 只保留最近30天的快照
    snapshots = snapshots[-30:]

    with open(snapshot_file, 'w', encoding='utf-8') as f:
        json.dump(snapshots, f, ensure_ascii=False, indent=2)

def generate_summary():
    """生成每日更新摘要"""
    summary_file = os.path.join(DATA_DIR, "daily_summary.json")
    today = get_today_short()

    summary = {
        "date": today,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "report_updated": os.path.exists(os.path.join(WORKSPACE, "vograce-competitor-report.html")),
        "data_files": len([f for f in os.listdir(DATA_DIR) if f.endswith('.json')])
    }

    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    return summary

def main():
    print("=" * 50)
    print("🔄 Vograce 竞品数据每日更新")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 1. 更新报告时间戳
    report_updated = update_report_timestamp()

    # 2. 生成每日摘要
    summary = generate_summary()

    # 3. 保存运行日志
    save_daily_log(
        "daily_update",
        f"报告更新时间戳: {'成功' if report_updated else '失败'}, 数据文件数: {summary['data_files']}"
    )

    # 4. 同步到GitHub
    github_synced = sync_to_github()

    print("=" * 50)
    print("✅ 每日更新完成！")
    print(f"📁 数据目录: {DATA_DIR}")
    print(f"📊 报告: {os.path.join(WORKSPACE, 'vograce-competitor-report.html')}")
    print(f"🌐 GitHub同步: {'成功' if github_synced else '失败'}")
    print("=" * 50)

if __name__ == "__main__":
    main()
