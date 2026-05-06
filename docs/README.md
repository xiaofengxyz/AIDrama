# AIDrama 文档中心

日期：2026-05-07

本项目是一个基于 LumenX Studio 的 AI 漫剧试制与生产工作台。目标不是先做一个重平台，而是让 2-3 人团队尽快跑通“小说/梗概 -> 剧本 -> 角色/场景/道具资产 -> 分镜图 -> 分镜视频 -> 配音与合成 -> 发布复盘”的可重复流程。

## 阅读顺序

1. [项目说明](project-overview.md)：本项目做什么、能做什么、暂时不做什么。
2. [本地环境与项目配置](local-setup.md)：WSL Ubuntu 22.04 + Docker 下如何启动。
3. [AI 漫剧开源项目对比](open-source-comparison.md)：为什么推荐 LumenX，以及为什么不是只选 star 多、更新频率高的项目。
4. [AI 漫剧产品分析与改进建议](ai-drama-product-review.md)：产品经理视角的项目取舍和改进优先级。
5. [AI 漫剧测试用例分析与问题清单](ai-drama-test-analysis.md)：测试工程师视角的用例矩阵和问题记录。
6. [架构分析与本轮工程动作](ai-drama-architecture-actions.md)：架构/工程视角的修复与后续优化。
7. [AI 漫剧赚钱方式与落地路线](ai-drama-business-plan.md)：内容试制、B2B、账号矩阵与 90 天路线。
8. [任务进度索引](task-progress.md)：跨会话交接时先看这里。
9. [AI 协作指南](../agent.md)：给后续 AI 会话使用的仓库工作规则。

## 当前推荐

主基座：`LumenX Studio`

官方上游本地参考克隆：`external/open-source-repos/lumenx`

该目录是本机参考源码，已在 `.gitignore` 和 `.dockerignore` 中忽略，不会提交到本仓库，也不会进入 Docker build context。

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
