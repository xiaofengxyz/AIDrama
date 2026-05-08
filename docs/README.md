# AIDrama 文档中心

日期：2026-05-07

本项目是一个面向 Jellyfish 主平台基座的工业 AI Film Engine 工作区。当前仓库可运行入口已统一为 AIDrama Studio，用于本地试制、测试和迁移验证；最终架构口径以 Starter Kit 为准。

## 阅读顺序

1. [项目说明](project-overview.md)：本项目做什么、能做什么、暂时不做什么。
2. [本地环境与项目配置](local-setup.md)：WSL Ubuntu 22.04 + Docker 下如何启动。
3. [AI 漫剧开源项目对比](open-source-comparison.md)：Jellyfish 主平台和各参考层的取舍。
4. [AI 漫剧开源研究报告对比分析](ai-manjv-report-comparison-2026.md)：对比研究报告、Starter Kit、当前代码和本轮落地决策。
5. [AI 漫剧产品分析与改进建议](ai-drama-product-review.md)：产品经理视角的项目取舍和改进优先级。
6. [AI 漫剧测试用例分析与问题清单](ai-drama-test-analysis.md)：测试工程师视角的用例矩阵和问题记录。
7. [架构分析与本轮工程动作](ai-drama-architecture-actions.md)：架构/工程视角的修复与后续优化。
8. [AI 漫剧赚钱方式与落地路线](ai-drama-business-plan.md)：内容试制、B2B、账号矩阵与 90 天路线。
9. [任务进度索引](task-progress.md)：跨会话交接时先看这里。
10. [AI 协作指南](../agent.md)：给后续 AI 会话使用的仓库工作规则。

## 当前推荐

主平台基座：`Jellyfish`

当前可运行工作台：`AIDrama Studio`

`external/` 只允许作为临时、忽略提交的上游参考区。当前根目录是唯一可运行配置源；需要对比 Jellyfish 或其它上游时再临时 clone，用完不让它参与构建或提交。

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
