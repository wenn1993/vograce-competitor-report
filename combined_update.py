#!/usr/bin/env python3
"""
Vograce竞品数据综合更新
同时更新: 网站价格抓取 + 社媒监控
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

def log(msg, emoji="📋"):
    """带时间戳的日志输出"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {emoji} {msg}")

def run_price_scraper():
    """运行价格抓取脚本"""
    try:
        import competitor_scraper
        log("开始竞品价格数据抓取...", "🕷️")
        results = competitor_scraper.scrape_all_competitors()

        if results:
            log(f"价格抓取完成: {len(results)} 个竞品", "✅")
            return True
        else:
            log("价格抓取无结果", "⚠️")
            return False
    except Exception as e:
        log(f"价格抓取出错: {str(e)}", "❌")
        return False

def run_social_monitor():
    """运行社媒监控脚本"""
    try:
        import social_media_monitor
        log("开始社媒竞品监控...", "📱")
        data = social_media_monitor.main()

        if data:
            log("社媒监控完成", "✅")
            return True
        else:
            log("社媒监控无结果", "⚠️")
            return False
    except Exception as e:
        log(f"社媒监控出错: {str(e)}", "❌")
        return False

def update_html_report():
    """更新HTML报告中的自动抓取摘要"""
    try:
        data_dir = Path(__file__).parent / "competitor_data"

        # 读取最新抓取结果
        scrape_file = data_dir / "latest_scrape_results.json"
        social_file = data_dir / "social_media" / "social_media_monitor.json"

        summary_parts = []

        # 价格抓取摘要
        if scrape_file.exists():
            with open(scrape_file, 'r') as f:
                data = json.load(f)
                if 'summary' in data:
                    s = data['summary']
                    parts = []
                    for comp_id, comp_data in s.get('competitors', {}).items():
                        if comp_data.get('price_range'):
                            parts.append(f"{comp_data['name']}: {comp_data['price_range']}")
                    if parts:
                        summary_parts.append("💰 " + " | ".join(parts))

        # 社媒摘要
        if social_file.exists():
            with open(social_file, 'r') as f:
                data = json.load(f)
                last_updated = data.get('last_updated', '')[:16]
                total = 0
                most_active = ''
                if 'competitors' in data:
                    for comp_id, comp_data in data['competitors'].items():
                        if 'brand_mentions' in comp_data:
                            mentions = comp_data['brand_mentions'].get('mentions_7d', 0)
                            total += mentions
                            if not most_active or mentions > total:
                                most_active = comp_data.get('name', '')

                if total > 0:
                    summary_parts.append(f"📱 社媒7日提及: {total} | 最活跃: {most_active}")

        return summary_parts

    except Exception as e:
        log(f"HTML更新出错: {str(e)}", "❌")
        return []

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 Vograce竞品数据综合更新")
    print("=" * 60)

    all_success = True

    # 1. 运行价格抓取
    if not run_price_scraper():
        all_success = False

    # 2. 运行社媒监控
    if not run_social_monitor():
        all_success = False

    # 3. 更新摘要
    summaries = update_html_report()

    print()
    print("=" * 60)
    print("📊 更新摘要:")
    for summary in summaries:
        print(f"   {summary}")

    print()
    if all_success:
        print("✅ 综合更新完成!")
    else:
        print("⚠️ 部分更新失败，请检查日志")

    print("=" * 60)

    return 0 if all_success else 1

if __name__ == "__main__":
    sys.exit(main())
