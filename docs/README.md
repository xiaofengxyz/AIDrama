# AIDrama 文档中心

日期：2026-05-07

本项目是一个基于 LumenX Studio 的 AI 漫剧试制与生产工作台。目标不是先做一个重平台，而是让 2-3 人团队尽快跑通“小说/梗概 -> 剧本 -> 角色/场景/道具资产 -> 分镜图 -> 分镜视频 -> 配音与合成 -> 发布复盘”的可重复流程。

## 阅读顺序

1. [项目说明](project-overview.md)：本项目做什么、能做什么、暂时不做什么。
2. [本地环境与项目配置](local-setup.md)：WSL Ubuntu 22.04 + Docker 下如何启动。
3. [AI 漫剧开源项目对比](open-source-comparison.md)：为什么推荐 LumenX，以及为什么不是只选 star 多、更新频率高的项目。
4. [AI 漫剧开源研究报告对比分析](ai-manjv-report-comparison-2026.md)：对比 ChatGPT 研究报告、当前基座和本轮落地决策。
5. [AI 漫剧产品分析与改进建议](ai-drama-product-review.md)：产品经理视角的项目取舍和改进优先级。
6. [AI 漫剧测试用例分析与问题清单](ai-drama-test-analysis.md)：测试工程师视角的用例矩阵和问题记录。
7. [架构分析与本轮工程动作](ai-drama-architecture-actions.md)：架构/工程视角的修复与后续优化。
8. [AI 漫剧赚钱方式与落地路线](ai-drama-business-plan.md)：内容试制、B2B、账号矩阵与 90 天路线。
9. [任务进度索引](task-progress.md)：跨会话交接时先看这里。
10. [AI 协作指南](../agent.md)：给后续 AI 会话使用的仓库工作规则。

## 当前推荐

主基座：`LumenX Studio`

`external/` 只允许作为临时、忽略提交的上游参考区。本轮清理后，主工程以根目录为唯一可运行配置源；需要对比上游时再临时 clone，用完不让它参与构建或提交。

## 常用入口

```bash
make up
make ps
make logs
make down
```

启动后访问：

- 前端：`http://localhost:3014`
- 后端 API：`http://localhost:17177/docs`
