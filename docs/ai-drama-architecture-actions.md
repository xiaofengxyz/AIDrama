# 架构分析与本轮工程动作

日期：2026-05-14

## 当前架构判断

最终主平台基座采用 Starter Kit 指定的 Jellyfish。当前仓库运行 AIDrama Studio（FastAPI + Next.js），适合小团队先做内容生产闭环和迁移期回归。前端负责工作台交互，后端负责项目数据、模型调用、媒体文件、视频合成；模型供应商通过 provider registry 分流，天然适合以后替换或新增模型。

架构口径：Jellyfish 承载 Studio OS、Workflow Core、Project System、Asset Management、Async Task System、Shot Management 和 Studio UI；`src/film_engine/` 承载可迁移 Film Core；AIDrama Studio 是当前可运行入口和实现参考。

## 本轮修复

- Docker nginx 增加 `/series` 代理，解决 3014 首页把前端 HTML 当系列数组读取的问题。
- Docker nginx 增加 `/system/`、`/debug/` 代理，避免诊断接口在同源部署下落回前端页面。
- 前端 `selectProject` 统一使用 `API_URL`，不再硬编码 `localhost:8000`。
- 集合接口增加 `ensureArrayResponse`，把代理错误从压缩后的 `Q.map` 变成可读的 API routing 错误。
- 增加单测覆盖集合响应保护和 nginx API 前缀配置。
- 本轮已取消 `external/` 常驻上游 clone，避免根目录和 external 双工程配置混乱；后续只临时 clone 参考源。

## 当前会话新增固化

- `src/film_engine/models.py` 增加 `StoryBeat`、`StoryGraph`、`StoryGraphEdge`、`FinalEditClip`、`FinalEditTimeline`、`FilmProductionRun`，让 Script -> Story Graph -> Final Editing 有稳定数据契约。
- `src/film_engine/story_graph.py` 增加 deterministic Story Graph Builder，把剧本文本拆成有序 beat、边和 adjacency。
- `src/film_engine/director_planner.py` 增加 Director Planner，把 Story Graph 映射为镜头类型、构图、运镜、焦段、时长和转场。
- `src/film_engine/pipeline.py` 增加 Film Production Pipeline，串联 Script、Story Graph、Director Planner、Film Core 和 Final Editing。
- `src/film_engine/final_editing.py` 增加 Final Editing Assembler，从 Generation Ledger 输出 EDL/timeline、clip timing、QA summary 和 unresolved shots。
- `src/film_engine/models.py` 增加 `GenerationAttempt`、`ShotRun`、`GenerationLedger` 数据契约，把镜头级抽卡、QA、重试、prompt 指纹、输出、成本和耗时记录为可序列化台账。
- `src/film_engine/ledger.py` 增加 `GenerationLedgerRecorder`，作为独立 recorder 接入 Film Core，不绑定 DashScope、Kling、Vidu 或任何具体视频 runtime。
- `src/film_engine/orchestrator.py` 在每次 runtime attempt 后写入台账，并把台账 summary 放进 `FilmEngineRun.metadata["generation_ledger"]`，方便后续 UI、队列和成本看板读取。
- `tests/test_film_engine_core.py` 增加台账回归，覆盖正常成功、失败后重试、人工评分/标签/备注三类关键路径。
- `tests/test_film_production_pipeline.py` 覆盖从脚本文本到 Story Graph、Director Planner、Film Core dry-run 和 Final Editing 的端到端闭环。

## 本次复核新增固化

- `ProductionBible`、`PropAsset`、`CostumeAsset` 和 `AssetRegistry` 已进入 `src/film_engine/`，道具与服装不再只停留在应用层。
- Director DSL、Story Graph、Director Planner、Prompt Compiler、Film State、Generation Ledger、Final Editing 全部保留 `prop_ids` 与 `costume_ids`，支持镜头级道具/服装连续性追踪。
- Story Graph 支持脚本内 `[prop=...]`、`[costume=...]` 标签，且修复了 `INT.` / `EXT.` 场景头被错误拆句的问题。
- `src/apps/comic_gen/api.py` 新增 `POST /film/pipeline/run`，用于 Jellyfish-style 工作台以 dry-run 方式调用 Script -> Story Graph -> Director Planner -> Film Core -> Final Editing。
- `docker/nginx.conf` 增加 `/film/` 代理，避免 Docker 前端同源调用 Film Core API 时落回静态页面。
- `samples/production_bible/suspense_assets.yaml` 提供道具、服装与 continuity locks 样例。
- `tests/test_film_pipeline_api.py` 覆盖 Film Core API 的 dry-run 成功与未知资产拒绝路径；宿主缺 `dashscope` 时跳过，容器环境执行。

## 本轮批量生产补齐

- `src/film_engine/models.py` 增加 `BatchProductionItem`、`BatchProductionPlan`、`BatchProductionRun`，把多序列生产批次、优先级、重试策略覆盖、错误隔离和批次汇总变成稳定数据契约。
- `src/film_engine/batch.py` 增加 `BatchProductionRunner`，在 Film Core 内部以 deterministic 单进程方式执行多个 Director Program；后续接 Celery、Temporal、Argo 或自研队列时可以替换执行层，不改 DSL/QA/Retry/Ledger。
- `tests/test_film_engine_batch.py` 覆盖成功批次汇总、单条失败隔离、优先级排序和 `max_items` 上限，避免“批量生产”退化成临时脚本。

## 本次九阶段页面可视化

- `frontend/src/components/project/ProjectClient.tsx` 将第 9 步从 `Export` Beta 调整为 `QA & Export`，作为 Film Engine 控制台入口。
- `frontend/src/components/modules/FilmEngineControlRoom.tsx` 新增单项目 dry-run 控制台，把 Starter Kit 固定九阶段 Runtime、Director DSL、Shot Graph、Prompt Compiler、Character Registry、Scene Registry、QA Engine、Retry Engine、Film State Engine 显示到页面。
- `frontend/src/lib/filmEngine.ts` 新增前端 Film Core payload 编译器和九阶段状态评估器。它从当前项目剧本、分镜、角色、场景、道具生成 `/film/pipeline/run` payload，保持 dry-run 默认不消耗模型预算。
- `src/apps/comic_gen/api.py` 的 `/film/pipeline/run` 响应补充 `film_run.shot_graph`，让 Shot Graph 从内部对象变成 UI、测试和集成层都可观测的契约。
- `frontend/src/__tests__/film-engine.test.ts` 覆盖 payload 编译、分镜脚本回退、九阶段状态评估和指标汇总。
- `requirements.txt`、`requirements-docker.txt` 固化 `pytest`，保证 Docker 后端容器重建后仍可直接执行回归测试。

## 本次 QA & Export 入口加固

- `src/apps/comic_gen/api.py` 新增 `GET /film/pipeline/run` 契约说明，浏览器直接访问 `http://localhost:3014/film/pipeline/run` 时返回使用方式、sample payload 和固定九阶段，不再表现为 405。
- `frontend/src/lib/workspaceRouting.ts` 抽出工作台 hash 路由解析，支持独立项目 `#/project/{id}/step/export` 和系列单集 `#/series/{seriesId}/episode/{episodeId}/step/export`。
- `frontend/src/components/series/SeriesDetailPage.tsx` 在单集面板增加 `QA & Export` 直达按钮，明确“系列详情页”和“单集项目工作台”的边界。
- `frontend/src/__tests__/workspace-routing.test.ts` 覆盖项目/系列单集深链解析和构造，防止第 9 步入口再次只存在于文档里。

## 本次 CineForge 工作流与导出兜底

- `src/film_engine/workflow.py` 增加 workflow-first 状态层，固定 Novel Engine、Asset Pipeline、Storyboard、Image Runtime、Video Runtime、Voice Runtime、Composition、QA & Retry、Export 九个可恢复生产阶段。
- 工作流状态按项目持久化到 `output/workflow_state.json`，并保留 `WorkflowEditEvent`，支持后续把编辑/重生成意图接入队列、任务中心或 Jellyfish 工作流系统。
- `GET /projects/{projectId}/workflow` 返回当前项目的阶段状态、阻塞项、下一步动作、模型建议和导出模式。
- `POST /projects/{projectId}/workflow/stages/{stageId}/regenerate` 记录阶段级重生成意图，先保持 state-only，不把 UI 硬绑定到某个供应商任务。
- `GET /film/runtime/recommendations` 输出百炼优先模型目录：文本用 `qwen-plus`，当前图片链路用 `wan2.6-image`、后续优先 `wan2.7-image(-pro)`，当前视频链路用 `wan2.6-i2v/r2v`、后续优先 `wan2.7-i2v/r2v`，配音用 CosyVoice，合成用 FFmpeg。
- `/projects/{projectId}/export` 不再在缺少 selected video 时只返回泛化失败；现在 `Start Render` 有素材则合成 mp4，缺素材则导出 `mode=render_package` 的 JSON manifest，包含 workflow state、阻塞项、模型建议和 frame 级媒体引用。
- `frontend/src/components/modules/FilmEngineControlRoom.tsx` 新增 CineForge Workflow readiness 面板，并展示 render package warnings/action_required，让制作人能知道下一步该补资产、分镜、视频、配音还是合成。
- `tests/test_film_workflow.py` 和 `frontend/src/__tests__/workflow-api.test.ts` 覆盖工作流状态、render package、模型建议和前端错误 detail 透传。

## 本次 D7 样片与系列模板补齐

- `src/film_engine/models.py` 增加 `SeriesEpisodeBlueprint`、`SeriesProductionBlueprint`，把多集题材验证模板变成稳定数据契约。
- `src/film_engine/series.py` 增加 `SeriesProductionPlanner`，负责加载 YAML/JSON 系列蓝图、构建共享 Character/Scene/Production Registry、编译每集 Story Graph 与 Director Program，并输出 `BatchProductionPlan`。
- `SeriesProductionPlanner.run_blueprint()` 复用 `BatchProductionRunner` 和 `FilmEngine` 执行多集 dry-run，验证跨集 continuity locks、QA、Retry、Ledger 和 selected outputs。
- `samples/series_production/vertical_suspense_5ep.yaml` 提供 5 集悬疑短漫剧模板，覆盖主角、场景、道具、服装、连续性锁和每集剧本。
- `samples/pilot_samples/three_60_90s_pilots.yaml` 提供 3 个 60-90 秒题材样片模板，用于先做题材验证再扩成 5 集。
- `tests/test_series_production_blueprint.py` 覆盖系列蓝图加载、批量编排、共享 registry dry-run、重复集号拒绝和 3 个样片 Story Graph 可用性。

## 本次制作人一键漫剧与分集生产包补齐

- `src/film_engine/production_extraction.py` 新增 `EpisodeProductionExtractor`、`EpisodeProductionPackage`、`ExtractedProductionAsset` 和 `ExtractedStoryboardFrame`，把小说计划拆成每集脚本、三段式分镜、角色、场景、道具、服装、特效和 continuity locks。
- `src/film_engine/auto_drama.py` 在 Auto Drama dry-run 中接入生产包提取，确保 `/film/auto-drama/run` 不只返回 Film Core 汇总，也返回可交付、可测试的分集制作资料。
- `src/apps/comic_gen/api.py` 支持 `persist_mode=series`，把一句话生成结果落盘为 Studio 系列和多个单集项目；单集项目继承对应 episode package 的 frames 和资产占位。
- `src/apps/comic_gen/api.py` 增加资产级 `POST /projects/{id}/assets/{type}/{assetId}/web_media/collect`，让角色、场景、道具可以直接采集网络参考图片和参考视频，不再只能项目级挂分镜。
- `frontend/src/components/modules/OneSentenceDramaPanel.tsx` 新增首页制作人入口，默认 dry-run、默认系列落盘、成功后跳转系列页。
- `frontend/src/app/page.tsx` 新增工作区流程地图和主题切换器，把“模板中心”“一句话制片”“我的工作区”的职责放到页面首屏。
- `frontend/src/lib/themePresets.ts`、`frontend/src/components/canvas/CreativeCanvas.tsx`、`frontend/src/app/globals.css` 通过主题预设和 CSS variables 支撑 `Noir`、`Dailies`、`Ember` 三套可持久化页面风格。
- `tests/test_episode_production_extraction.py`、`frontend/src/components/modules/__tests__/OneSentenceDramaPanel.spec.tsx`、`frontend/src/__tests__/theme-presets.test.ts` 覆盖分集生产包、一句话 UI 和主题预设。

架构决策：

- 生产包提取放在 Film Core，不放在页面组件中，避免后续迁移 Jellyfish 时丢失核心流程。
- 服装和特效先以 Studio prop records 进入当前 UI，保持落盘兼容；Film Core 层仍保留独立 `costumes` 与 `special_effects` 字段，后续可升级为专门资产表。
- 网络素材采集保持可选参考，不作为真实生成 runtime；这样离线测试、dry-run 和缺外部网络时仍能验证主流程。

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
