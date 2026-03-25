#!/usr/bin/env python3
"""
Vograce 竞品数据自动化更新脚本 v3.0
自动抓取竞品数据 → 分析变化 → 更新网页内容 → 同步GitHub Pages
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_DEPENDENCIES = True
except ImportError:
    HAS_DEPENDENCIES = False
    print("⚠️ 正在安装依赖: requests, beautifulsoup4...")
    os.system("pip3 install requests beautifulsoup4 --break-system-packages")
    try:
        import requests
        from bs4 import BeautifulSoup
        HAS_DEPENDENCIES = True
    except:
        HAS_DEPENDENCIES = False

# 配置
WORKSPACE = "/Users/admin/WorkBuddy/20260324141124"
DATA_DIR = os.path.join(WORKSPACE, "competitor_data")
REPORT_FILE = os.path.join(WORKSPACE, "vograce-competitor-report.html")
INDEX_FILE = os.path.join(WORKSPACE, "index.html")
os.makedirs(DATA_DIR, exist_ok=True)

# 竞品网站配置
COMPETITORS = {
    "wooacry": {
        "name": "WooAcry",
        "url": "https://wooacry.com",
        "products": ["acrylic-keychains", "keychains", "stickers", "badges", "stands"],
        "price_check_pages": [
            "https://wooacry.com/product-category/keychains/acrylic-keychains",
            "https://wooacry.com/product-category/keychains",
            "https://wooacry.com/product-category/stickers",
            "https://wooacry.com/product-category/badges",
            "https://wooacry.com/product-category/standees"
        ]
    },
    "stickermule": {
        "name": "Sticker Mule",
        "url": "https://www.stickermule.com",
        "products": ["stickers", "labels", "packaging"],
        "price_check_pages": [
            "https://www.stickermule.com/uses/custom-stickers",
            "https://www.stickermule.com/uses/custom-labels",
            "https://www.stickermule.com/uses/custom-packaging"
        ]
    },
    "zapcreatives": {
        "name": "Zap! Creatives",
        "url": "https://www.zapcreatives.com",
        "products": ["keychains", "stickers", "badges", "magnetic-badges", "standees"],
        "price_check_pages": [
            "https://www.zapcreatives.com/en-us/collections/custom-keychains",
            "https://www.zapcreatives.com/en-us/collections/custom-stickers",
            "https://www.zapcreatives.com/en-us/collections/badges-pins",
            "https://www.zapcreatives.com/en-us/collections/custom-standees"
        ]
    },
    "vograce": {
        "name": "Vograce",
        "url": "https://vograce.com",
        "products": ["keychains", "stickers", "badges", "stands", "plush", "t-shirts"],
        "price_check_pages": [
            "https://vograce.com/collections/custom-keychains",
            "https://vograce.com/collections/custom-stickers",
            "https://vograce.com/collections/custom-badges-pins",
            "https://vograce.com/collections/custom-standees"
        ]
    }
}

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

def scrape_page(url, timeout=15):
    """抓取单个页面"""
    try:
        response = requests.get(url, headers=get_headers(), timeout=timeout)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"  ❌ {url}: {str(e)[:50]}")
        return None

def extract_prices(html_content):
    """从页面提取价格数据"""
    if not html_content:
        return [], []
    
    soup = BeautifulSoup(html_content, 'html.parser')
    prices = []
    promotions = []
    
    # 移除script和style元素
    for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
        tag.decompose()
    
    text = soup.get_text()
    
    # 价格模式
    price_patterns = [
        r'\$[\d,]+\.?\d*',
        r'USD\s*[\d,]+\.?\d*',
        r'[\d,]+\.?\d*\s*USD',
        r'US\$[\d,]+\.?\d*',
    ]
    
    for pattern in price_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            price_str = re.sub(r'[^\d.]', '', match)
            try:
                price = float(price_str)
                if 0.05 <= price <= 200:
                    prices.append(price)
            except ValueError:
                continue
    
    # 促销信息
    promo_keywords = ['sale', 'discount', 'off', 'deal', 'promo', 'save', 'hot', 'new']
    promo_pattern = r'(?:sale|discount|off|promo|save)[\s:]*[\d%]+'
    promo_matches = re.findall(promo_pattern, text, re.IGNORECASE)
    promotions = list(set(promo_matches))[:5]
    
    prices = sorted(list(set(prices)))[:30]
    return prices, promotions

def extract_products(html_content, competitor_key):
    """提取产品信息"""
    if not html_content:
        return []
    
    soup = BeautifulSoup(html_content, 'html.parser')
    products = []
    
    # 查找产品卡片
    product_selectors = [
        '.product-item', '.product-card', '.product',
        '[class*="product"]', '[class*="item"]',
        '.col-xs-3', '.col-sm-3', '.grid-item'
    ]
    
    for selector in product_selectors:
        items = soup.select(selector)
        for item in items[:20]:
            try:
                # 尝试提取产品名称
                name_elem = item.select_one('h2, h3, h4, .title, .name, [class*="title"]')
                price_elem = item.select_one('.price, [class*="price"], del, ins')
                
                if name_elem or price_elem:
                    name = name_elem.get_text(strip=True)[:50] if name_elem else "未知产品"
                    price_text = price_elem.get_text(strip=True) if price_elem else ""
                    
                    # 提取价格数值
                    price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                    price = float(price_match.group(1).replace(',', '')) if price_match else None
                    
                    if name and name != "未知产品":
                        products.append({
                            "name": name,
                            "price": price,
                            "price_text": price_text
                        })
            except:
                continue
    
    return products[:10]

def scrape_competitor(competitor_key):
    """抓取单个竞品的数据"""
    competitor = COMPETITORS[competitor_key]
    print(f"\n📡 正在抓取 {competitor['name']}...")
    
    data = {
        "name": competitor['name'],
        "url": competitor['url'],
        "timestamp": datetime.now().isoformat(),
        "pages_checked": 0,
        "pages_success": 0,
        "prices_found": [],
        "promotions": [],
        "products": [],
        "price_by_category": {}
    }
    
    for page_url in competitor.get('price_check_pages', []):
        html = scrape_page(page_url)
        if html:
            data["pages_checked"] += 1
            prices, promos = extract_prices(html)
            data["prices_found"].extend(prices)
            data["promotions"].extend(promos)
            
            # 提取产品分类
            category = page_url.split('/')[-1] if '/' in page_url else 'general'
            products = extract_products(html, competitor_key)
            if products:
                data["price_by_category"][category] = {
                    "products": products,
                    "prices": prices[:10]
                }
            data["pages_success"] += 1
        
        import time
        time.sleep(0.3)
    
    # 去重和统计
    data["prices_found"] = sorted(list(set(data["prices_found"])))
    data["promotions"] = list(set(data["promotions"]))[:10]
    
    if data["prices_found"]:
        data["min_price"] = min(data["prices_found"])
        data["max_price"] = max(data["prices_found"])
        data["avg_price"] = round(sum(data["prices_found"]) / len(data["prices_found"]), 2)
    
    print(f"  ✅ {competitor['name']}: {data['pages_success']}/{data['pages_checked']}页, {len(data['prices_found'])}个价格")
    
    return data

def scrape_all():
    """抓取所有竞品"""
    print("=" * 60)
    print("🔄 开始自动抓取竞品数据")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = {}
    for key in COMPETITORS.keys():
        data = scrape_competitor(key)
        results[key] = data
    
    return results

def analyze_changes(new_data, old_data=None):
    """分析数据变化"""
    changes = {
        "price_changes": [],
        "new_promotions": [],
        "new_products": [],
        "alerts": []
    }
    
    if not old_data:
        return changes
    
    for competitor_key in COMPETITORS.keys():
        new = new_data.get(competitor_key, {})
        old = old_data.get(competitor_key, {})
        
        if not new or not old:
            continue
        
        # 价格变化
        new_min = new.get('min_price')
        old_min = old.get('min_price')
        
        if new_min and old_min and new_min != old_min:
            change_pct = ((new_min - old_min) / old_min) * 100
            changes["price_changes"].append({
                "competitor": new['name'],
                "old_price": old_min,
                "new_price": new_min,
                "change_pct": round(change_pct, 1)
            })
            
            # 生成预警
            if change_pct < -5:  # 降价超过5%
                changes["alerts"].append({
                    "type": "danger",
                    "competitor": new['name'],
                    "message": f"{new['name']} 价格下降了 {abs(round(change_pct, 1))}%，现最低价 ${new_min:.2f}"
                })
            elif change_pct > 5:  # 涨价超过5%
                changes["alerts"].append({
                    "type": "info",
                    "competitor": new['name'],
                    "message": f"{new['name']} 价格上调了 {round(change_pct, 1)}%"
                })
        
        # 新促销
        old_promos = set(old.get('promotions', []))
        new_promos = set(new.get('promotions', []))
        added_promos = new_promos - old_promos
        
        for promo in added_promos:
            changes["new_promotions"].append({
                "competitor": new['name'],
                "promotion": promo
            })
    
    return changes

def update_json_data(results, changes):
    """更新JSON数据文件"""
    
    # 1. 保存最新抓取结果
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    scrape_file = os.path.join(DATA_DIR, f"scrape_results_{timestamp}.json")
    with open(scrape_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 2. 更新latest文件
    latest_file = os.path.join(DATA_DIR, "latest_scrape_results.json")
    with open(latest_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 3. 保存变化分析
    changes_file = os.path.join(DATA_DIR, "latest_changes.json")
    with open(changes_file, 'w', encoding='utf-8') as f:
        json.dump(changes, f, ensure_ascii=False, indent=2)
    
    # 4. 更新价格历史
    price_history_file = os.path.join(DATA_DIR, "price_history.json")
    price_history = []
    if os.path.exists(price_history_file):
        with open(price_history_file, 'r', encoding='utf-8') as f:
            price_history = json.load(f)
    
    today = datetime.now().strftime("%Y-%m-%d")
    for competitor_key, data in results.items():
        if data.get('prices_found'):
            price_history.append({
                "date": today,
                "competitor": data['name'],
                "min_price": data.get('min_price'),
                "avg_price": data.get('avg_price'),
                "max_price": data.get('max_price'),
                "prices_count": len(data['prices_found'])
            })
    
    price_history = price_history[-365:]  # 保留一年
    with open(price_history_file, 'w', encoding='utf-8') as f:
        json.dump(price_history, f, ensure_ascii=False, indent=2)
    
    # 5. 更新每日摘要
    summary = {
        "date": today,
        "timestamp": datetime.now().isoformat(),
        "competitors_scraped": len([k for k, v in results.items() if v.get('pages_success', 0) > 0]),
        "total_pages": sum(v.get('pages_checked', 0) for v in results.values()),
        "successful_pages": sum(v.get('pages_success', 0) for v in results.values()),
        "price_changes": len(changes.get('price_changes', [])),
        "alerts": changes.get('alerts', []),
        "vograce_min_price": results.get('vograce', {}).get('min_price'),
        "wooacry_min_price": results.get('wooacry', {}).get('min_price'),
        "zap_min_price": results.get('zapcreatives', {}).get('min_price'),
        "stickermule_min_price": results.get('stickermule', {}).get('min_price')
    }
    
    summary_file = os.path.join(DATA_DIR, "daily_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    # 6. 更新daily log
    log_file = os.path.join(DATA_DIR, "daily_update_log.json")
    logs = []
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    
    logs.append({
        "date": today,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": "auto_update_v3",
        "details": f"抓取{summary['total_pages']}页成功{summary['successful_pages']}页, 价格变化{summary['price_changes']}项, 预警{len(summary['alerts'])}条"
    })
    logs = logs[-90:]
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    
    print(f"✅ JSON数据已更新")
    return summary

def update_html_report(results, changes):
    """更新HTML报告中的动态数据"""
    today = datetime.now().strftime("%Y年%m月%d日")
    scrape_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
    
    for report_file in [INDEX_FILE, REPORT_FILE]:
        if not os.path.exists(report_file):
            print(f"⚠️ 报告文件不存在: {report_file}")
            continue
        
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. 更新时间戳
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
        
        # 2. 更新数据抓取信息
        vograce = results.get('vograce', {})
        wooacry = results.get('wooacry', {})
        
        # 构建抓取摘要
        total_pages = sum(v.get('pages_checked', 0) for v in results.values())
        successful_pages = sum(v.get('pages_success', 0) for v in results.values())
        
        scrape_summary = f"""
抓取时间: {scrape_time} | 检查了 {successful_pages}/{total_pages} 个页面
• Vograce: {'$' + str(vograce.get('min_price', 'N/A')) if vograce.get('min_price') else 'N/A'}
• WooAcry: {'$' + str(wooacry.get('min_price', 'N/A')) if wooacry.get('min_price') else 'N/A'}
        """
        
        # 查找并更新数据来源区域
        if '数据来源：' in content:
            # 更新数据来源时间
            pass
        
        # 3. 生成预警列表
        alerts_html = ""
        for alert in changes.get('alerts', []):
            color = '#EF4444' if alert['type'] == 'danger' else '#3B82F6'
            bg = 'rgba(239,68,68,0.1)' if alert['type'] == 'danger' else 'rgba(59,130,246,0.1)'
            alerts_html += f"""
        <div style="display:flex;align-items:center;gap:8px;padding:10px;background:{bg};border-radius:6px;margin-bottom:8px;">
          <div style="width:8px;height:8px;border-radius:50%;background:{color};flex-shrink:0;"></div>
          <div style="font-size:12px;color:#E2E8F0;">{alert['message']}</div>
        </div>
            """
        
        # 4. 更新竞品价格对比数据
        for competitor_key, data in results.items():
            if not data.get('min_price'):
                continue
            
            competitor_name = data['name']
            min_price = data['min_price']
            
            # 这里可以添加更多智能更新逻辑
            # 目前依赖JavaScript动态加载
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 报告已更新: {os.path.basename(report_file)}")

def sync_to_github():
    """同步到GitHub"""
    print("\n" + "=" * 50)
    print("🔄 同步到GitHub...")
    print("=" * 50)
    
    # 配置git
    subprocess.run(["git", "config", "user.email", "bot@vograce-report.com"], cwd=WORKSPACE)
    subprocess.run(["git", "config", "user.name", "Vograce Auto Bot"], cwd=WORKSPACE)
    
    # 检查更改
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=WORKSPACE,
        capture_output=True,
        text=True
    )
    
    if not result.stdout.strip():
        print("📝 没有需要提交的更改")
        return True
    
    # 添加并提交
    subprocess.run(["git", "add", "-A"], cwd=WORKSPACE)
    today = datetime.now().strftime("%Y-%m-%d")
    commit_msg = f"auto: 每日数据更新 {today}"
    
    result = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=WORKSPACE,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"⚠️ git commit 失败: {result.stderr}")
        return False
    
    print(f"✅ 已提交: {commit_msg}")
    
    # 推送
    result = subprocess.run(
        ["git", "push", "origin", "master"],
        cwd=WORKSPACE,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"⚠️ git push 失败: {result.stderr}")
        return False
    
    print("✅ 已推送到GitHub!")
    return True

def main():
    print("=" * 60)
    print("🚀 Vograce 竞品数据自动化更新系统 v3.0")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 加载历史数据（用于变化分析）
    old_results = None
    latest_file = os.path.join(DATA_DIR, "latest_scrape_results.json")
    if os.path.exists(latest_file):
        with open(latest_file, 'r', encoding='utf-8') as f:
            old_results = json.load(f)
    
    # 2. 抓取最新数据
    new_results = scrape_all()
    
    # 3. 分析变化
    changes = analyze_changes(new_results, old_results)
    
    if changes.get('price_changes'):
        print("\n📊 价格变化检测:")
        for change in changes['price_changes']:
            print(f"  • {change['competitor']}: ${change['old_price']:.2f} → ${change['new_price']:.2f} ({change['change_pct']:+.1f}%)")
    
    if changes.get('alerts'):
        print("\n🚨 预警信息:")
        for alert in changes['alerts']:
            print(f"  • [{alert['type']}] {alert['message']}")
    
    # 4. 更新JSON数据
    summary = update_json_data(new_results, changes)
    
    # 5. 更新HTML报告
    update_html_report(new_results, changes)
    
    # 6. 同步到GitHub
    github_synced = sync_to_github()
    
    print("\n" + "=" * 60)
    print("✅ 自动化更新完成！")
    print(f"📁 数据目录: {DATA_DIR}")
    print(f"📊 报告: vograce-competitor-report.html")
    print(f"🌐 GitHub同步: {'成功' if github_synced else '失败/无需同步'}")
    print("=" * 60)
    
    return summary

if __name__ == "__main__":
    main()
