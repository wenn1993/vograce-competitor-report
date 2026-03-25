#!/usr/bin/env python3
"""
Vograce 竞品数据自动抓取与更新脚本 v2.0
自动从竞品网站抓取最新数据并更新报告
"""

import json
import os
import re
import time
from datetime import datetime
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_DEPENDENCIES = True
except ImportError:
    HAS_DEPENDENCIES = False

# 配置
WORKSPACE = "/Users/admin/WorkBuddy/20260324141124"
DATA_DIR = os.path.join(WORKSPACE, "competitor_data")
os.makedirs(DATA_DIR, exist_ok=True)

# 竞品网站配置 - 使用正确的URL
COMPETITORS = {
    "vograce": {
        "name": "Vograce",
        "name_cn": "🇨🇳 中国",
        "url": "https://vograce.com",
        "price_check_pages": [
            "https://vograce.com/collections/custom-keychains",
            "https://vograce.com/collections/custom-stickers",
            "https://vograce.com/collections/custom-standees",
            "https://vograce.com/collections/vograce-hot-sale-promotion",
            "https://vograce.com/collections/monthly-discount-activity"
        ]
    },
    "wooacry": {
        "name": "WooAcry",
        "name_cn": "🇨🇳 中国",
        "url": "https://wooacry.com",
        "price_check_pages": [
            "https://wooacry.com/product-category/keychains",
            "https://wooacry.com/product-category/keychains/acrylic-keychains",
            "https://wooacry.com/product-category/standees",
            "https://wooacry.com/product-category/special"
        ]
    },
    "zap": {
        "name": "Zap! Creatives",
        "name_cn": "🇬🇧 英国",
        "url": "https://zapcreatives.com",
        "price_check_pages": [
            "https://zapcreatives.com/en-us/collections/all-charms",
            "https://zapcreatives.com/en-us/collections/custom-stickers",
            "https://zapcreatives.com/en-us/collections/custom-keychains",
            "https://zapcreatives.com/en-us/collections/standees"
        ]
    }
}

def get_headers():
    """获取请求头"""
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

def scrape_page(url, timeout=15):
    """抓取单个页面"""
    if not HAS_DEPENDENCIES:
        print("⚠️ 需要安装依赖: pip3 install requests beautifulsoup4")
        return None

    try:
        response = requests.get(url, headers=get_headers(), timeout=timeout)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"  ❌ {url}: {str(e)[:50]}")
        return None

def extract_prices(html_content, site_name):
    """从页面提取价格"""
    if not html_content:
        return [], []

    soup = BeautifulSoup(html_content, 'html.parser')
    prices = []
    promotions = []

    # 移除script和style元素
    for tag in soup(['script', 'style']):
        tag.decompose()

    text = soup.get_text()

    # 多种价格模式
    price_patterns = [
        r'\$[\d,]+\.?\d*',           # $12.99
        r'USD\s*[\d,]+\.?\d*',       # USD 12.99
        r'[\d,]+\.?\d*\s*USD',       # 12.99 USD
    ]

    for pattern in price_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            price_str = re.sub(r'[^\d.]', '', match)
            try:
                price = float(price_str)
                if 0.05 <= price <= 200:  # 合理价格范围
                    prices.append(price)
            except ValueError:
                continue

    # 检测促销信息
    promo_keywords = ['sale', 'discount', 'off', 'deal', 'promo', '%', 'save']
    promo_pattern = r'(?:sale|discount|off|promo|save)[\s:]*[\d%]+'
    promo_matches = re.findall(promo_pattern, text, re.IGNORECASE)
    promotions = list(set(promo_matches))[:5]

    # 去重
    prices = sorted(list(set(prices)))[:30]

    return prices, promotions

def scrape_competitor_data(competitor_key):
    """抓取单个竞品的数据"""
    competitor = COMPETITORS[competitor_key]
    print(f"\n📡 正在抓取 {competitor['name']}...")

    data = {
        "name": competitor['name'],
        "name_cn": competitor['name_cn'],
        "url": competitor['url'],
        "timestamp": datetime.now().isoformat(),
        "pages_checked": 0,
        "pages_success": 0,
        "prices_found": [],
        "promotions": [],
        "new_products": [],
        "homepage_text": ""
    }

    for page_url in competitor.get('price_check_pages', []):
        html = scrape_page(page_url)
        if html:
            data["pages_checked"] += 1
            prices, promos = extract_prices(html, competitor['name'])
            data["prices_found"].extend(prices)
            data["promotions"].extend(promos)

            # 如果是首页或新品页，提取一些关键信息
            if 'new-arrivals' in page_url or page_url == competitor['url']:
                soup = BeautifulSoup(html, 'html.parser')
                data["homepage_text"] = soup.get_text()[:500]

            data["pages_success"] += 1
        time.sleep(0.5)  # 礼貌性延迟

    # 去重
    data["prices_found"] = sorted(list(set(data["prices_found"])))
    data["promotions"] = list(set(data["promotions"]))[:10]

    if data["prices_found"]:
        data["avg_price"] = round(sum(data["prices_found"]) / len(data["prices_found"]), 2)
        data["min_price"] = min(data["prices_found"])
        data["max_price"] = max(data["prices_found"])

    status = "✅" if data["pages_success"] > 0 else "⚠️"
    print(f"  {status} {competitor['name']}: {data['pages_success']}/{data['pages_checked']}页成功, 找到{len(data['prices_found'])}个价格")

    return data

def scrape_all_competitors():
    """抓取所有竞品数据"""
    print("=" * 60)
    print("🔄 开始自动抓取竞品数据")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    results = {}
    for key in COMPETITORS.keys():
        data = scrape_competitor_data(key)
        results[key] = data

    return results

def save_scrape_results(results):
    """保存抓取结果"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(DATA_DIR, f"scrape_results_{timestamp}.json")

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 更新最新结果
    latest_file = os.path.join(DATA_DIR, "latest_scrape_results.json")
    with open(latest_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 抓取结果已保存")
    return filename

def update_report_with_scrape_data(results):
    """使用抓取的数据更新报告"""
    report_path = os.path.join(WORKSPACE, "vograce-competitor-report.html")
    if not os.path.exists(report_path):
        print("⚠️ 报告文件不存在")
        return False

    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()

    today = datetime.now().strftime("%Y年%m月%d日")
    scrape_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")

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

    # 生成抓取摘要
    vograce_data = results.get('vograce', {})
    wooacry_data = results.get('wooacry', {})

    summary_lines = []
    total_pages = 0
    total_success = 0

    for key, data in results.items():
        total_pages += data.get('pages_checked', 0)
        total_success += data.get('pages_success', 0)
        if data.get('prices_found'):
            price_range = f"${data['min_price']:.2f} - ${data['max_price']:.2f}"
            summary_lines.append(f"{data['name_cn']} {data['name']}: {price_range}")

    scrape_info = f"""
    <div style="background:linear-gradient(135deg,rgba(16,185,129,0.15),rgba(59,130,246,0.1));border:1px solid rgba(16,185,129,0.3);border-radius:12px;padding:16px;margin-bottom:20px;">
        <div style="font-size:14px;font-weight:700;color:#10B981;margin-bottom:8px;">🤖 自动数据抓取</div>
        <div style="font-size:12px;color:#94A3B8;margin-bottom:10px;">
            抓取时间: {scrape_time} | 检查了 {total_success}/{total_pages} 个页面
        </div>
        <div style="font-size:12px;color:#E2E8F0;">
            {chr(10).join(summary_lines) if summary_lines else '正在获取最新价格数据...'}
        </div>
    </div>
    """

    # 在hero区域插入抓取信息
    content = content.replace(
        '<div class="hero-meta">',
        scrape_info + '<div class="hero-meta">'
    )

    # 更新Vograce起售价
    if vograce_data.get('min_price'):
        min_price_str = f"${vograce_data['min_price']:.2f}"
        content = re.sub(
            r'<p><span class="price-tag">\$[\d.]+</span>',
            f'<p><span class="price-tag">{min_price_str}</span>',
            content
        )
        # 同时更新木质钥匙扣的价格（如果有找到更低的）
        wood_prices = [p for p in vograce_data.get('prices_found', []) if p < 2]
        if wood_prices:
            wood_min = min(wood_prices)
            content = re.sub(
                r'木质钥匙扣起</span></p>\s*<p><span class="price-tag">\$[\d.]+',
                f'木质钥匙扣起</span></p><p><span class="price-tag">${wood_min:.2f}',
                content
            )

    # 更新WooAcry价格对比
    if wooacry_data.get('min_price'):
        wooacry_min = wooacry_data['min_price']
        # 更新价格对比表格中的WooAcry价格
        content = re.sub(
            r'亚克力钥匙扣</div>\s*<div class="comp-row-value">\s*<span style="color:#10B981;font-weight:700;">[^<]+</span>',
            f'亚克力钥匙扣</div><div class="comp-row-value"><span style="color:#10B981;font-weight:700;">贴纸 ${wooacry_data["min_price"]:.2f}起 · 钥匙扣 ${wooacry_min:.2f}起</span>',
            content
        )

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ 报告已更新为最新数据")
    return True

def generate_summary(results):
    """生成抓取摘要"""
    summary = {
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "competitors": {}
    }

    for key, data in results.items():
        summary["competitors"][key] = {
            "name": data.get("name"),
            "name_cn": data.get("name_cn"),
            "pages_checked": data.get("pages_checked"),
            "pages_success": data.get("pages_success"),
            "prices_count": len(data.get("prices_found", [])),
            "min_price": data.get("min_price"),
            "max_price": data.get("max_price"),
            "avg_price": data.get("avg_price"),
            "promotions": data.get("promotions", [])[:3]
        }

    summary_file = os.path.join(DATA_DIR, "scrape_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # 保存到日志
    log_file = os.path.join(DATA_DIR, "daily_update_log.json")
    logs = []
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)

    total_pages = sum(c.get('pages_checked', 0) for c in results.values())
    total_success = sum(c.get('pages_success', 0) for c in results.values())

    logs.append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": "auto_scrape",
        "details": f"抓取{total_pages}页, {total_success}页成功"
    })
    logs = logs[-90:]

    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

    return summary

def main():
    print("=" * 60)
    print("🚀 Vograce 竞品数据自动抓取与报告更新")
    print("=" * 60)

    if not HAS_DEPENDENCIES:
        print("\n⚠️ 缺少必要依赖，正在安装...")
        os.system("pip3 install requests beautifulsoup4 --break-system-packages")

    # 1. 抓取所有竞品数据
    results = scrape_all_competitors()

    # 2. 保存抓取结果
    save_scrape_results(results)

    # 3. 生成摘要
    summary = generate_summary(results)

    # 4. 更新报告
    update_report_with_scrape_data(results)

    # 5. 打印摘要
    print("\n" + "=" * 60)
    print("📊 抓取摘要")
    print("=" * 60)
    for key, data in summary["competitors"].items():
        price_info = f"${data['min_price']:.2f}" if data.get('min_price') else "N/A"
        print(f"• {data['name_cn']} {data['name']}: "
              f"{data['pages_success']}/{data['pages_checked']}页, "
              f"{data['prices_count']}个价格, "
              f"最低 ${data['min_price']:.2f}" if data.get('min_price') else f"{data['pages_success']}/{data['pages_checked']}页")

    print("\n" + "=" * 60)
    print("✅ 全部完成！")
    print(f"📁 数据目录: {DATA_DIR}")
    print(f"📊 报告: http://localhost:8899/vograce-competitor-report.html")
    print("=" * 60)

if __name__ == "__main__":
    main()
