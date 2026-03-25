# Vograce 竞品监控报告

## 📊 在线访问

部署完成后，报告将可通过以下链接访问：
```
https://[你的用户名].github.io/[仓库名]/
```

## 🚀 部署到 GitHub Pages

### 方式一：使用 GitHub 网页（推荐）

1. 访问 https://github.com/new 创建新仓库，命名为 `vograce-competitor-report`

2. 推送代码到仓库：
   ```bash
   git remote add origin https://github.com/[你的用户名]/vograce-competitor-report.git
   git push -u origin master
   ```

3. 进入仓库 **Settings** → **Pages**

4. 在 "Source" 下选择：
   - Branch: `master` (或 `main`)
   - Folder: `/ (root)`
   - 点击 **Save**

5. 等待1-2分钟，页面将自动部署

6. 访问 `https://[你的用户名].github.io/vograce-competitor-report/`

### 方式二：使用 GitHub CLI

```bash
# 创建仓库
gh repo create vograce-competitor-report --public --push --source=.

# 启用GitHub Pages
gh repo edit vograce-competitor-report --enable-pages
```

## 📁 项目结构

```
├── vograce-competitor-report.html   # 主报告页面
├── competitor_data/                  # 竞品数据
│   ├── latest_scrape_results.json   # 最新爬取结果
│   └── social_media/                # 社媒监控数据
├── competitor_data_update.py        # 数据更新脚本
└── run_competitor_update.sh         # 自动化更新脚本
```

## ⏰ 自动更新

报告数据每日 08:00 UTC 自动更新。手动更新：
```bash
python competitor_data_update.py
```

## 📱 报告内容

- **Section 1**: 行业动态与市场份额
- **Section 2**: 竞品深度分析
- **Section 3**: 价格对比
- **Section 4**: WooAcry vs Vograce 深度对比
- **Section 5**: 竞品动向追踪
- **Section 6**: 社媒竞品监控
- **Section 7**: 竞品流量对比
