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
- 自动化任务 ID: vograce_daily，每天 08:00 执行
- **核心脚本: auto_update.py v3.0** （整合抓取+分析+更新+Git同步）
- 功能流程：
  1. 从所有竞品网站（WooAcry, StickerMule, Zap! Creatives, Vograce）抓取最新数据
  2. 分析价格变化，生成预警信息
  3. 更新所有JSON数据文件（latest_scrape_results.json, daily_summary.json, price_history.json等）
  4. 更新HTML报告中的时间戳
  5. 自动git add/commit/push到GitHub master
- GitHub Actions自动部署: push后自动触发GitHub Pages部署workflow
- 首次成功执行：2026-03-25 15:40

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
