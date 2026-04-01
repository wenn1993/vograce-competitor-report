# MEMORY.md - 长期记忆

## 项目经验
- Vograce动漫周边竞品分析报告(vograce-competitor-report.html)维护者
- 竞品数据存储在 competitor_data/ 目录，包含最新爬取结果和历史数据

## 竞品价格数据
基于2026年3月调研：
- **Vograce**: 亚克力钥匙扣 $1.51起，木质钥匙扣 $0.71起，批量折扣~20%
- **WooAcry**: 亚克力钥匙扣 $0.99起(最低价)，批量折扣最高72%
- **Sticker Mule**: 亚克力钥匙扣 $1.19/个(1000个起)，全球免费配送
- **Zap! Creatives**: 亚克力钥匙扣 $1.44起(SAVE20促销)，英国制造

## 报告结构
报告包含9个模块：市场概览、竞品对比、Vograce概览、流量与用户、**竞品动向追踪**、市场趋势、SWOT、监测清单、社媒监控

## 2026-03-24 第一模块重大升级
第一模块"行业动态"进行全面重构，增加管理层视角深度分析：
- 新增战略洞察摘要区（核心优势/关键风险/战略机会）
- 新增市场竞争格局（市场份额图、竞品定位矩阵、价格带分布）
- 竞品价格动态扩展为4个竞品对比（WooAcry/StickerMule/Zap!/Vograce）
- 新增行业趋势深度解读（带影响分析和行动建议）
- 新增客户行为洞察（客户画像、购买决策TOP 5因素）
- 新增供应链与成本动态
- 新增战略行动建议（紧急/重要/规划三级分类）
- 概览指标增加至5个：核心竞品监测、产品品类覆盖、待处理预警、数据时效、市场规模估算

## 每日自动化更新任务
- 本地自动化任务 ID: vograce_daily，每天 08:00 执行（需电脑开机）
- **核心脚本: auto_update.py v3.1**（整合抓取+分析+更新+Git同步）
- CI 模式：设置 CI=true 时跳过 git push，由 GitHub Actions workflow 统一 push

### GitHub Actions 云端定时更新（2026-03-27 配置完成）
- Workflow：`.github/workflows/daily-update.yml`，每天 UTC 00:00 = 北京时间 08:00
- 权限：`contents: write`（commit + push 数据）
- 并发组：`daily-update-${{ github.run_id }}`（独立，不与 deploy.yml 冲突）
- 流程：checkout → python auto_update.py (CI=true) → commit → push → deploy Pages
- 关键修复：原 schedule 被 cancelled 原因：permissions: contents: read + 并发冲突
- 测试验证：2026-03-27 手动触发 50 秒全部成功

功能流程（auto_update.py）：
  1. 从竞品网站（WooAcry, StickerMule, Zap! Creatives, Vograce）抓取最新数据
  2. 分析价格变化，生成预警
  3. 更新所有JSON数据文件
  4. 更新HTML报告时间戳
  5. CI模式跳过push；本地模式自动push

## 竞品数据抓取配置
追踪竞品（配置在 auto_update.py）：
- WooAcry: wooacry.com
- Sticker Mule: stickermule.com
- Zap! Creatives: zapcreatives.com
- Vograce: vograce.com

**Vograce官方社媒账号**（已添加到报告）：
- TikTok: https://www.tiktok.com/@vogracecharms
- YouTube: https://www.youtube.com/channel/UCMd2dQcKZHzYsIc8LhUf8jQ

数据输出目录: competitor_data/

## 2026-03-24 第五模块重大升级
第五模块"市场动向追踪"升级为"竞品动向追踪"，全面重构：
- 新增战略洞察摘要区（Vograce核心优势/关键风险/战略机会）
- 新增竞品动向追踪矩阵（价格动向/促销动作/产品更新/社媒活跃/威胁等级）
- 新增价格变动追踪模块（4大品类价格比较，含Vograce vs WooAcry vs Zap!）
- 新增促销活动监测模块（实时监控WooAcry/Vograce/Zap!促销动态）
- 新增竞品市场策略分析（WooAcry价格侵略型/Zap!品质品牌型/Makeship精品限量型）
- 新增竞争威胁评估（5家竞品威胁等级可视化进度条）
- 新增动态数据加载函数（loadCompetitorTrackerMatrix/loadPriceChangeTracker）

## 2026-03-25 市场份额数据同步
关键市场份额数据已统一（概览指标与市场竞争格局饼图一致）：
- **Vograce市场份额: 22%**
- **WooAcry市场份额: 18%**
- 其他中小定制厂商: 40%
- 其他专业化平台: 20%
- 标注为"(基于公开信息推算)"

## 2026-03-25 第七模块：竞品流量对比
新增Section 7: 竞品流量对比模块，包含：
- 流量核心指标概览（MAU、PV、趋势）
- 流量趋势对比图（SVG折线图，近30天）
- 流量来源分布对比（搜索引擎/社交媒体/直接访问）
- 关键指标对比表（跳出率/停留时间/页面访问量）
- 主要关键词排名对比（custom keychain/acrylic keychain等）
- 流量洞察与行动建议（短期/中期/长期）
- 数据来源说明（SimilarWeb估算，每日08:00更新）
- 导航栏同步更新"流量对比"入口

## 2026-03-25 数据源全面自动化
auto_update.py升级至v3.1，整合更多数据源：
1. **竞品价格数据** - WooAcry, StickerMule, Zap! Creatives, Vograce
2. **社媒动态** - social_summary.json (粉丝数、提及量)
3. **Reddit话题热度** - reddit_trends.json (r/ArtistAlley, r/merch等热门帖子)
4. **行业动态** - industry_news.json (搜索趋势、行业报告)

HTML报告新增动态加载模块：
- loadRedditTrends() - 加载Reddit热门话题
- loadIndustryNews() - 加载行业动态新闻
- Section 6末尾新增Reddit趋势网格和行业动态列表

所有数据源每日08:00自动抓取并同步到GitHub

## 2026-03-25 第六模块社媒数据更新
用户提供的真实社媒数据（2026年3月25日），更新所有竞品卡片：

**Twitter粉丝：**
- WooAcry: 8,466 | Vograce: 4.7万 | Zap! Creatives: 1.5万 | Sticker Mule: 21.3万 | Makeship: 44.3万

**YouTube粉丝：**
- WooAcry: 6,080 | Vograce: 1.37万 | Zap! Creatives: 413 | Sticker Mule: 1.43万 | Makeship: 2.86万

**TikTok粉丝：**
- WooAcry: 65.1K | Vograce: 249.2K | Zap! Creatives: 5,337 | Sticker Mule: 91.4K | Makeship: 131.8K

**Instagram粉丝：**
- WooAcry: 354 | Vograce: 175K | Zap! Creatives: 36.7K | Sticker Mule: 450K | Makeship: 310K

已同步更新：
1. vograce-competitor-report.html Section 6所有社媒卡片
2. auto_update.py中的social_accounts配置
3. 每个竞品卡片添加完整4平台徽章（TikTok/YouTube/Twitter/IG）

## 2026-03-25 第六模块社媒URL重构
用户提供的竞品社媒完整URL，重构第六模块所有卡片：

**各竞品社媒URL：**
- WooAcry: X=https://x.com/Wooacry_Charms, TikTok=@wooacryofficial, YouTube=搜索页, IG=wooacryofficial
- Vograce: X=https://x.com/VograceCharms, TikTok=@vogracecharms, YouTube=官方频道, IG=vograce_official
- Zap! Creatives: X=https://x.com/ZapCreatives, TikTok=@zapcreatives, YouTube=搜索页, IG=zapcreatives
- Sticker Mule: X=https://x.com/stickermule, TikTok=@stickermule, YouTube=搜索页, IG=stickermule
- Makeship: X=https://x.com/Makeship, TikTok=@makeship, YouTube=搜索页, IG=makeship

已更新：所有粉丝数据和标签改为可点击链接，指向对应社媒页面

## 2026-04-01 数据加载修复

### Reddit 热门话题数据修复
- reddit_trends.json 数据结构：
  - hot_posts: 热门帖子数组（title/subreddit/score/num_comments/url）
  - subreddits: 社区概览对象（active_posts/description/avg_engagement）
  - trending_topics: 热门话题数组（topic/sentiment/trend/mentions_7d）

### 行业动态数据修复
- industry_news.json 数据结构：
  - news: 新闻数组（headline/url/source/date）
  - market_trends: 市场趋势数组（name/impact/description）
  - industry_insights: 行业洞察对象（total_market_size/growth_rate/key_drivers）

### 加载函数修复
- loadRedditTrends(): 支持 trending_topics 热门话题标签显示
- loadRedditPlatformInfo(): 改进 subreddit 颜色匹配逻辑
- loadIndustryNews(): 支持 market_trends 对象格式和 industry_insights 概览

## 2026-04-01 JavaScript 语法错误全面修复

**vograce-competitor-report.html 语法错误修复**：
- **核心问题**：`updateSocialStats` 函数内的 try 语句缺少 catch 块，导致整个脚本解析失败
- **症状**：所有数据加载函数未定义（typeof 返回 undefined），页面一直显示"加载中"
- **修复**：添加缺失的 catch 块
- **验证**：Reddit趋势、行业动态、社媒统计等模块全部正常加载

**GitHub 已同步**：efd1e1e / 0f6ea5b / 9ba8b40
