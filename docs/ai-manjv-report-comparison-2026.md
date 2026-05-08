# AI 漫剧开源研究报告对比分析

日期：2026-05-07

对比对象：

- `docs/complete_ai_manjv_open_source_research_report_2026.md`
- `docs/open-source-comparison.md`
- `docs/AI_Film_Engine_Starter_Kit_Final_Stable_v1.md`
- 当前 AIDrama 工程代码（AIDrama Studio 可运行入口）

## 核心结论

报告对行业瓶颈的判断是正确的：角色一致性、镜头可控、长剧情记忆、自动 QA、自动重试，才是 AI 漫剧工业化的核心壁垒。

Starter Kit 的最终推荐架构明确把 `Jellyfish` 定为主平台基座。此前文档把旧脚手架写成主基座，是基于当前仓库已有可运行代码做出的阶段性工程分析；本轮修正后，旧脚手架不再覆盖最终架构口径。

报告给出的“直接切换 huobao-drama 为主框架”仍不适合当前仓库阶段。当前工程已经有 AIDrama Studio Docker 入口、DashScope-first 路由、系列资产和前后端工作台，直接推倒会中断试制；正确路径是把 Jellyfish 作为目标平台，把 Film Core 做成独立内核，再逐步迁移工作台能力。

本轮采用的落地策略：

- 最终主平台基座采用 Jellyfish。
- 当前主工程继续保留 AIDrama Studio 可运行工作台，作为迁移期验证入口。
- 不把 huobao-drama、Toonflow、Jellyfish 或其它项目 clone 到主工程参与构建。
- 吸收报告和 Starter Kit 中的工业化思想，在当前工程新增可运行的 `src/film_engine/` 最小核心闭环。
- 先实现结构化 Runtime、Director DSL、Shot Graph、Prompt Compiler、Registry、QA、Retry、Film State，再逐步接真实视觉 QA 和外部运行时。

## 报告判断与当前仓库差异

| 维度 | 报告观点 | 当前仓库事实 | 本轮决策 |
|---|---|---|---|
| 主基座 | 推荐 `huobao-drama` | Starter Kit 明确 `Jellyfish -> 主平台基座`；本仓库已有 AIDrama Studio 可运行工作台 | 不把 huobao 切成主基座，Jellyfish 做目标平台，吸收 huobao 的 runtime/后期思路 |
| 旧脚手架评价 | 偏企业平台，小团队适配较弱 | 外部历史项目覆盖资产、风格、分镜、视频和合成；本仓库已把可运行入口改为 AIDrama Studio | 只作历史参考，不再写作主基座 |
| Toonflow | Agent/无限画布/Skill 成熟 | Toonflow 更像重型桌面创作 IDE，适合参考 Agent 组织和画布生产 | 暂不迁移，吸收 Skill 文件化和记忆思路 |
| Jellyfish | Starter Kit 推荐为 Studio OS | Jellyfish 与“短剧生产工作区”方向贴近，当前仓库尚未接入 | 作为最终主平台基座，先以文档和 Film Core 边界锁定迁移方向 |
| 核心壁垒 | 角色资产、镜头模板 DSL、自动剪辑、Reference workflow | 当前有资产链路，但缺完整独立 Film Core、QA/Retry/State 抽象 | 本轮补 `src/film_engine/` 闭环 |
| Agent 数量 | 不应堆 Agent | `AGENTS.md` 明确要求模块化、图工作流、运行时抽象 | 本轮单 agent 执行，不引入多 agent 依赖 |

## 需要修正的报告假设

1. `huobao-drama` 的产品链路很强，但它更像完整平台栈。对 2-3 人试制团队，迁移成本和授权边界需要先确认。
2. `Toonflow-app` 的 Agent 与无限画布能力强，但桌面端、供应商脚本、三层 Agent、记忆系统会提高维护成本。
3. `Jellyfish` 很符合 Studio OS 方向，并且是 Starter Kit 最终主平台基座；当前仓库已有 AIDrama Studio 工作台，短期更适合把 Film Core 做成可移植内核，再逐步迁移平台层。
4. “最强项目”不能只按出片能力排序，还要看当前团队是否能维护、是否可商业试制、是否能按镜头复盘成本和失败率。

## 本项目吸收报告的落地点

### Runtime

运行时必须抽象为 adapter。当前 AIDrama 已有 DashScope/Wanx/Kling/Vidu provider 路由，本轮新增 Film Engine runtime 层，先用 dry-run adapter 保障测试闭环，后续再接真实模型。

### Director DSL

报告强调运镜不可控，Starter Kit 要求 Director DSL。本轮把 YAML/结构化 shot 定义解析为 AST，避免只靠自然语言 prompt。

### Shot Graph

镜头不再只是数组，而是有 transition、pacing、emotion、target 的有向关系。后续自动剪辑、QA 和 Retry 都基于图结构。

### Prompt Compiler

Prompt 不硬编码在页面或运行时里，而是由 Director DSL、角色状态、场景状态和镜头状态编译到目标 backend。

### Character/Scene Registry

角色和场景是实体，不是 prompt 字符串。后续 LoRA、embedding、服装、参考图、声音、灯光和天气都挂在 registry。

### QA/Retry

本轮先做结构化 QA 和重试策略接口；后续可接 InsightFace、MediaPipe、CLIP、OpenCV 做真实画面检测。

### Film State

长剧情连续性用状态引擎维护，包括角色出镜、服装、情绪、场景、时间线和 continuity lock。

## 资料核验记录

本轮核验了以下公开页面，用来校正报告中的项目定位：

- LumenX 历史参考: https://github.com/alibaba/lumenx
- huobao-drama: https://github.com/chatfire-AI/huobao-drama
- Toonflow-app: https://github.com/HBAI-Ltd/Toonflow-app
- Jellyfish: https://github.com/Forget-C/Jellyfish

## 最终取舍

当前最稳路线不是“重选一个最强开源仓库”，而是：

1. 以 Jellyfish 作为最终主平台基座。
2. 保留 AIDrama Studio 工作台作为当前可运行生产入口和迁移期验证层。
3. 删除/隔离 external 下的重复参考项目，避免双配置干扰。
4. 新增独立 Film Core，把工业化能力做成可测试、可替换、可迁移的内核。
5. 继续用镜头级台账、QA、Retry 和 Film State 降低抽卡随机性。
