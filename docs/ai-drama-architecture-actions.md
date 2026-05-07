# 架构分析与本轮工程动作

日期：2026-05-07

## 当前架构判断

最终主平台基座采用 Starter Kit 指定的 Jellyfish。当前仓库仍运行 LumenX-compatible FastAPI + Next.js 工作台，适合小团队先做内容生产闭环和迁移期回归。前端负责工作台交互，后端负责项目数据、模型调用、媒体文件、视频合成；模型供应商通过 provider registry 分流，天然适合以后替换或新增模型。

架构口径：Jellyfish 承载 Studio OS、Workflow Core、Project System、Asset Management、Async Task System、Shot Management 和 Studio UI；`src/film_engine/` 承载可迁移 Film Core；当前 LumenX-compatible 层只作为可运行入口和实现参考。

## 本轮修复

- Docker nginx 增加 `/series` 代理，解决 3014 首页把前端 HTML 当系列数组读取的问题。
- Docker nginx 增加 `/system/`、`/debug/` 代理，避免诊断接口在同源部署下落回前端页面。
- 前端 `selectProject` 统一使用 `API_URL`，不再硬编码 `localhost:8000`。
- 集合接口增加 `ensureArrayResponse`，把代理错误从压缩后的 `Q.map` 变成可读的 API routing 错误。
- 增加单测覆盖集合响应保护和 nginx API 前缀配置。
- 本轮已取消 `external/` 常驻上游 clone，避免根目录和 external 双工程配置混乱；后续只临时 clone 参考源。

## 当前会话新增固化

- `src/film_engine/models.py` 增加 `GenerationAttempt`、`ShotRun`、`GenerationLedger` 数据契约，把镜头级抽卡、QA、重试、prompt 指纹、输出、成本和耗时记录为可序列化台账。
- `src/film_engine/ledger.py` 增加 `GenerationLedgerRecorder`，作为独立 recorder 接入 Film Core，不绑定 DashScope、Kling、Vidu 或任何具体视频 runtime。
- `src/film_engine/orchestrator.py` 在每次 runtime attempt 后写入台账，并把台账 summary 放进 `FilmEngineRun.metadata["generation_ledger"]`，方便后续 UI、队列和成本看板读取。
- `tests/test_film_engine_core.py` 增加台账回归，覆盖正常成功、失败后重试、人工评分/标签/备注三类关键路径。

## 本轮批量生产补齐

- `src/film_engine/models.py` 增加 `BatchProductionItem`、`BatchProductionPlan`、`BatchProductionRun`，把多序列生产批次、优先级、重试策略覆盖、错误隔离和批次汇总变成稳定数据契约。
- `src/film_engine/batch.py` 增加 `BatchProductionRunner`，在 Film Core 内部以 deterministic 单进程方式执行多个 Director Program；后续接 Celery、Temporal、Argo 或自研队列时可以替换执行层，不改 DSL/QA/Retry/Ledger。
- `tests/test_film_engine_batch.py` 覆盖成功批次汇总、单条失败隔离、优先级排序和 `max_items` 上限，避免“批量生产”退化成临时脚本。

## 后续架构优化建议

### 模型接入

- 继续保持“任务类型 -> provider -> 模型”的三层路由，不让 UI 直接依赖供应商细节。
- 新模型接入必须同时补：参数 schema、费用估算、失败码归一化、媒体引用格式、最小回归测试。
- 对同一镜头允许多模型候选并存，最终选择只写入 `selected_video_id`。

### 数据结构

- 系列级资产库应成为主数据：角色、场景、道具、服装、世界观、禁用设定都先落在系列层。
- 单集只保存引用和必要覆盖，减少重复生成和角色漂移。
- 镜头级台账已在 Film Core 中独立为 `GenerationLedger`，后续接入应用层时继续避免塞进视频任务临时字段。

### 可靠性

- 前端所有集合接口都要对返回 schema 做保护。
- 后端错误响应保持 `{detail, code?, hint?}`，便于 UI 显示可操作提示。
- nginx API 前缀由测试守住，避免新功能在 Docker 下可用性回退。

### 成本与速度

- 引入低清预检：先生成低分辨率/短时长候选，通过人工评分后再高质量重跑。
- 对失败率高的 prompt、动作、模型组合自动打标，减少重复抽卡。
- 批量生成默认小批量，避免一次性烧完预算。
