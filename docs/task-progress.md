# 任务进度索引

日期：2026-05-08

这个文件用于跨会话交接。后续 AI 或人工进入仓库时，先读本文件，再读 `docs/README.md` 和 `agent.md`。

## 当前会话约束

- 按用户要求：先计划再执行。
- 不启动多 agent。
- 使用并行命令做多任务文件读取和验证。
- 每个阶段完成后更新本索引。
- `external/` 仅作为被忽略的上游参考区，不参与提交和构建。

## 本轮执行计划与状态

### 2026-05-08 服务重启与九阶段可视化执行

| 阶段 | 状态 | 本轮动作 | 验收方式 |
|---|---|---|---|
| 1. 现状复核 | 已完成 | 复核 git、Docker 服务、Film Core API、前端九步工作台和九阶段 Starter Kit 固定开发顺序 | `git status --short --branch`、读取 `ProjectClient`、`/film/pipeline/run` |
| 2. 服务重启 | 已完成 | 电脑重启后重新构建并启动 `aidrama-backend`、`aidrama-frontend` | `docker compose up -d --build --remove-orphans`、`docker compose ps`、`curl` |
| 3. 缺口确认 | 已完成 | 确认九阶段内核已在后端实现，但页面没有九阶段可视化入口，`9. Export` 仍是 Beta 观感 | 前端侧栏与 `ExportStudio` 代码复核 |
| 4. 页面实现 | 已完成 | 新增 `9. QA & Export` Film Engine 控制台，自动 dry-run 当前项目并展示九阶段状态、QA、Retry、Ledger、Final Edit、导出动作 | `frontend/src/components/modules/FilmEngineControlRoom.tsx` |
| 5. API 契约增强 | 已完成 | `/film/pipeline/run` 响应补充 `film_run.shot_graph`，让 Shot Graph 阶段在页面和测试中可见 | `tests/test_film_pipeline_api.py` |
| 6. 测试补齐 | 已完成 | 新增前端 Film Engine payload/九阶段评估单测，补充测试用例文档；Docker 重建后容器内核心和全量后端测试通过 | `npm run test`、`npm run test:ui`、`npx tsc --noEmit`、`pytest` |
| 7. 清理提交推送 | 已完成 | 已完成最终验证、冲突检查和本轮提交；等待 push 结果回填 | `git diff --check`、`git ls-files -u`、本轮提交 |

## 九阶段完成体现

Starter Kit 固定九阶段为：Runtime、Director DSL、Shot Graph、Prompt Compiler、Character Registry、Scene Registry、QA Engine、Retry Engine、Film State Engine。

当前状态：九阶段内核已完成可测试闭环；本轮把它们从“后端和文档里完成”推进到“页面可见”。进入项目工作台后，左侧点击 `9. QA & Export`，页面会自动调用 `/film/pipeline/run` dry-run，并显示九阶段逐项状态、镜头数、QA 分、重试次数、生成台账和 Final Edit clips。

本轮页面映射：

| 九阶段 | 页面体现 | 后端/测试体现 |
|---|---|---|
| Runtime | Runtime 状态行、backend 与 attempt 数 | `RuntimeRouter`、`DryRunRuntimeAdapter` |
| Director DSL | Director Program shot 数 | `DirectorPlanner`、`DirectorDSLParser` |
| Shot Graph | Shot Graph 节点和 transition 数 | `film_run.shot_graph`、`ShotGraphBuilder` |
| Prompt Compiler | Ledger 中 prompt fingerprint | `PromptCompiler`、`GenerationLedger` |
| Character Registry | tracked characters 与 continuity locks | `CharacterRegistry`、角色锁定测试 |
| Scene Registry | tracked scenes 与场景连续性 | `SceneRegistry`、场景锁定测试 |
| QA Engine | QA Reports 与 average score | `QAEngine`、QA report 测试 |
| Retry Engine | retry attempt 数与 policy | `RetryEngine`、失败重试测试 |
| Film State Engine | continuity timeline events | `FilmStateEngine`、final_state 测试 |

### 2026-05-08 本次复核执行

| 阶段 | 状态 | 本轮动作 | 验收方式 |
|---|---|---|---|
| A. 现状复核 | 已完成 | 复核 Jellyfish 上游参考、Docker 运行口径、Film Core 模块和测试覆盖 | `git status --short --branch`、读取 `src/film_engine/`、`external/jellyfish/README.md` |
| B. 缺口确认 | 已完成 | 确认核心链路已具备，但道具/服装/资产圣经尚未进入 Film Core；缺少可供工作台调用的 dry-run 管线 API | 补齐 `ProductionBible`、`AssetRegistry`、`/film/pipeline/run` |
| C. 工程实现 | 已完成 | 将资产管理、continuity locks、prompt compiler、state engine、API 接入模块化实现 | 新增/更新单元测试 |
| D. 测试与运行 | 已完成 | 跑后端核心测试、前端测试、Docker 配置与本地服务冒烟 | pytest、vitest、docker compose/curl |
| E. 清理提交推送 | 已完成 | 检查冲突和工作区，提交必要修改并 push | `git diff --check`、`git ls-files -u`、`git push` |

| 阶段 | 状态 | 本轮动作 | 验收方式 |
|---|---|---|---|
| 1. 仓库盘点 | 已完成 | 检查 git 状态、运行入口、前后端、旧品牌残留、Film Core 模块 | `git status --short --branch`、全仓关键词搜索 |
| 2. Jellyfish 基座核对 | 已完成 | clone `https://github.com/Forget-C/Jellyfish` 到 ignored `external/jellyfish`，读取 README/AGENTS/compose/后端服务/前端页面结构 | `git -C external/jellyfish log -1`，确认官方端口 `8000/7788` 与 Studio OS 能力 |
| 3. 产品与制作人 Review | 已完成 | 明确工业级真人真实效果漫剧的痛点：角色一致性、服装道具锁定、镜头连续性、QA、Retry、镜头台账、批量生产 | 更新 `docs/ai-drama-product-review.md`、`docs/ai-drama-business-plan.md` |
| 4. 架构实现 | 已完成 | 补齐 Script -> Story Graph -> Director Planner -> Film Core -> Final Editing 的可测试闭环 | 新增 `story_graph.py`、`director_planner.py`、`pipeline.py`、`final_editing.py` |
| 5. 移除旧运行面品牌 | 已完成 | 前端品牌、页面标题、面包屑、Docker 容器名、数据目录、OSS 默认路径、README/手册/贡献指南改为 AIDrama/Jellyfish-oriented | 全仓运行面关键词检查；删除旧前端图片资源 |
| 6. 测试补齐 | 已完成 | 新增端到端 Film Production Pipeline 测试，覆盖 Story Graph、Director Planner、Final Editing unresolved 输出 | `python3 -m pytest tests/test_film_engine_core.py tests/test_film_engine_batch.py tests/test_film_production_pipeline.py -q -s` |
| 7. 运行验证与提交推送 | 已完成 | 已完成前端/容器/Jellyfish 参考启动验证、清理工作区、冲突检查、提交并 push | `e7838981` 已推送，进度索引已补记 |

## Jellyfish 核对记录

- clone 路径：`external/jellyfish`，该目录被 `.gitignore` 忽略。
- 当前参考提交：`a967819 [docs] Update README files...`
- 官方定位：AI Short Drama Studio，覆盖 project/chapter、assets、shot preparation、generation workspace、task center、model/prompt infrastructure。
- 官方运行方式：
  - Docker Compose：`docker compose --env-file deploy/compose/.env -f deploy/compose/docker-compose.yml up --build`
  - Frontend：`http://localhost:7788`
  - Backend：`http://localhost:8000/docs`
  - 依赖：MySQL、Redis、RustFS、Celery worker。
- 本仓库不会直接提交 Jellyfish 源码；本轮把 Jellyfish 的 Studio OS 边界和状态语义迁移到 AIDrama 文档与 Film Core 设计。

## 本轮新增工程能力

- `src/film_engine/models.py`
  - 新增 `ProductionBible`、`PropAsset`、`CostumeAsset`。
  - `DirectorProgram` / `DirectorShot` / `PromptCompileRequest` / `ShotRun` / `FilmState` / `FinalEditClip` 保留道具和服装引用。
- `src/film_engine/registry.py`
  - 新增 `AssetRegistry`，可从 production bible 加载道具、服装与 continuity locks。
- `src/apps/comic_gen/api.py`
  - 新增 `POST /film/pipeline/run`，对 Jellyfish-style 工作台暴露 dry-run Film Core 管线。
- `docker/nginx.conf`
  - 新增 `/film/` 代理，保证 Docker 前端可同源调用 Film Core API。
- `src/film_engine/story_graph.py`
  - 从剧本文本构建 deterministic Story Graph。
  - 输出 StoryBeat、StoryGraphEdge、adjacency。
  - 支持人物对白、场景 hint、情绪和叙事功能的结构化抽取。
  - 支持 `[prop=...]`、`[costume=...]` 标签，并保护 `INT.` / `EXT.` 场景头不被错误拆分。
- `src/film_engine/director_planner.py`
  - 把 Story Graph 转成可拍摄 DirectorProgram。
  - 根据叙事功能映射镜头类型、构图、运镜、镜头焦段、时长。
  - 保留 `story_beat_id`，方便后续 UI 回跳和 QA 追踪。
- `src/film_engine/pipeline.py`
  - 串联 Script -> Story Graph -> Director Planner -> FilmEngine -> Final Editing。
  - 保持 runtime backend 可替换，默认 dry-run。
- `src/film_engine/final_editing.py`
  - 从 Generation Ledger 中读取 selected output。
  - 生成 FinalEditTimeline、clip timing、transition、QA summary。
  - 对缺失 selected output 的镜头输出 unresolved_shots。
- `src/film_engine/models.py`
  - 新增 StoryGraph、FinalEditTimeline、FilmProductionRun 等 Pydantic 契约。
- `tests/test_film_production_pipeline.py`
  - 覆盖剧本拆图、导演规划、全链路 dry-run、Final Editing 缺失输出。
- `tests/test_film_pipeline_api.py`
  - 覆盖 `/film/pipeline/run` dry-run API 成功与未知资产拒绝路径。

## 当前验证记录

- `docker compose up -d --build --remove-orphans`：通过，电脑重启后已重建并启动 `aidrama-backend`、`aidrama-frontend`。
- `docker compose ps`：`aidrama-backend`、`aidrama-frontend` 均 Up。
- `curl -I http://localhost:3014/`：HTTP 200。
- `curl -sS http://localhost:3014/projects/`：HTTP 200，返回 `[]`。
- `curl -sS http://localhost:3014/series`：HTTP 200，返回现有系列 JSON。
- `curl -sS http://localhost:17177/config/info`：HTTP 200。
- `curl -sS -X POST http://localhost:3014/film/pipeline/run ...`：HTTP 200，返回 `film_run.shot_graph`、`accepted_shots`、`final_edit`，验证九阶段控制台所需契约和 nginx `/film/` 代理。
- `python3 -m compileall -q src/film_engine src/apps/comic_gen/api.py`：通过。
- `python3 -m pytest tests/test_film_engine_core.py tests/test_film_engine_batch.py tests/test_film_production_pipeline.py tests/test_film_pipeline_api.py -q -s`：通过，17 passed，2 skipped（宿主缺 DashScope 时 API app 测试跳过）。
- `cd frontend && npm run test`：通过，7 个测试文件，106 个测试。
- `cd frontend && npm run test:ui`：通过，2 个测试文件，46 个测试。
- `cd frontend && npx tsc --noEmit --pretty false`：通过。
- `cd frontend && npm run build`：通过；仅保留 Next static export 下既有 rewrites warning。
- `docker compose exec -T backend python -m pytest --version`：`pytest 9.0.3`，已随 Docker requirements 固化。
- `docker compose exec -T backend python -m pytest -q -s /app/tests/test_film_engine_core.py /app/tests/test_film_engine_batch.py /app/tests/test_film_production_pipeline.py /app/tests/test_film_pipeline_api.py`：通过，19 passed。
- `docker compose exec -T backend python -m pytest -q -s /app/tests`：通过，136 passed，41 warnings。
- `git diff --check`：通过。
- `git ls-files -u`：无输出，无未解决冲突。

以下为此前会话验证记录，保留用于交接追溯：

- `python3 -m compileall -q src/film_engine src/apps/comic_gen/api.py`：通过。
- `python3 -m pytest tests/test_film_engine_core.py tests/test_film_engine_batch.py tests/test_film_production_pipeline.py -q -s`：通过，17 个测试。
- `python3 -m pytest tests/test_film_pipeline_api.py -q -s`：宿主缺 `dashscope`，2 个 API 测试按用例 skip，命令正常退出。
- `python3 -m pytest tests/test_media_refs.py tests/test_provider_media.py -q -s`：通过，17 个测试。
- `cd frontend && npm run test`：通过，6 个测试文件，101 个测试。
- `docker compose config --quiet`：通过。
- `docker compose up -d --build --remove-orphans`：通过，`aidrama-backend` 与 `aidrama-frontend` 已启动。
- `curl -I http://localhost:3014/`：HTTP 200。
- `curl -sS http://localhost:3014/projects/`：HTTP 200，返回 `[]`。
- `curl -sS http://localhost:3014/series`：HTTP 200，返回 `[]`。
- `curl -sS http://localhost:17177/config/info`：HTTP 200，返回 development config 状态。
- `curl -sS -X POST http://localhost:17177/film/pipeline/run ...`：HTTP 200，返回 Story Graph、Director Program、Generation Ledger、Final Edit。
- `curl -sS -X POST http://localhost:3014/film/pipeline/run ...`：HTTP 200，验证 nginx `/film/` 代理生效。
- `docker compose exec -T backend python -m pytest -q -s /app/tests/test_film_engine_core.py /app/tests/test_film_engine_batch.py /app/tests/test_film_production_pipeline.py /app/tests/test_film_pipeline_api.py`：通过，19 个测试。
- `docker compose exec -T backend python -m pytest -q -s /app/tests`：通过，136 个测试，41 个 warning。
- `git diff --check`：通过。
- `git ls-files -u`：无输出，无未解决冲突。
- `git fetch origin` + `git status --short --branch`：本地 `main` 未落后 `origin/main`。
- `git commit -m "Add film asset bible pipeline API"`：已创建本轮提交。
- `git push origin main`：已推送本轮提交至 `origin/main`。

- `python3 -m compileall -q src/film_engine src/apps/comic_gen/api.py src/utils/oss_utils.py src/utils/media_refs.py`：通过。
- `python3 -m pytest tests/test_film_engine_core.py tests/test_film_engine_batch.py tests/test_film_production_pipeline.py -q -s`：通过，15 个测试。
- `python3 -m pytest tests/test_media_refs.py tests/test_provider_media.py -q -s`：通过，17 个测试。
- 宿主执行 provider 集成测试集合时，因本机 Python 缺少 `dashscope`，`test_image_provider_media.py`、`test_vidu_provider_routing.py`、`test_wanx_provider_media.py` collection 失败；改用后端容器全量验证。
- `docker compose config --quiet`：通过。
- `docker compose up -d --build --remove-orphans`：通过，已启动 `aidrama-backend` 和 `aidrama-frontend`。
- `docker compose ps`：`aidrama-backend`、`aidrama-frontend` 均 Up。
- `curl -I http://localhost:3014/`：HTTP 200。
- `curl -sS http://localhost:3014/projects/`：HTTP 200，返回 `[]`。
- `curl -sS http://localhost:3014/series`：HTTP 200，返回 `[]`。
- `curl -sS http://localhost:17177/config/info`：HTTP 200，返回 development config 状态。
- `docker run --rm aidrama-frontend:latest ... grep 'LumenX|lumenx|Lumen'`：通过，构建后的前端无旧品牌字符串。
- `docker build --target builder -t aidrama-frontend-builder -f Dockerfile.frontend .`：通过。
- `docker run --rm -v /mnt/d/workplace/AIDrama/docker:/docker:ro aidrama-frontend-builder npm run test`：通过，6 个测试文件，101 个测试。
- `docker cp tests aidrama-backend:/app/tests && docker cp samples aidrama-backend:/app/samples && docker compose exec -T backend python -m pytest -q -s /app/tests`：通过，132 个测试，41 个 warning。
- Jellyfish 外部参考：`docker compose --env-file external/jellyfish/deploy/compose/.env -f external/jellyfish/deploy/compose/docker-compose.yml config --quiet` 通过；完整 `up -d --build` 失败在 `deb.debian.org` apt 索引 502/404，未启动容器。
- `git diff --check`：通过。
- `git ls-files -u`：无输出，无未解决冲突。
- `git commit -m "Align AIDrama with Jellyfish film engine base"`：已创建提交 `e7838981`。
- `git push`：已推送 `main`，`25d2abcd..e7838981`。

## 当前技术选择

主平台基座：Jellyfish

当前可运行入口：AIDrama Studio

分层定位：

- `Jellyfish`：Studio OS、Workflow Core、Project System、Asset Management、Async Task System、Shot Management、Studio UI。
- `src/film_engine/`：可迁移 Film Core。
- `huobao-drama`：Runtime Layer 参考，包括 render pipeline、FFmpeg orchestration、subtitle/TTS/stitching。
- `director_ai`：Director DSL Layer 参考，包括 shot abstraction、camera grammar、scene timeline、transition metadata。
- `BigBanana`：Cinematic Rule Layer 参考，包括 emotion-camera mapping、pacing rules、composition heuristics。
- `waoowaoo`：Orchestration Layer 参考。
- `Toonflow-app`：Storyboard UI 与 Agent/skill 组织方式参考。
- `StoryDiffusion`：Character Consistency 参考。

必须自研并保持独立：

- Story Graph
- Director Planner
- Film State Engine
- QA Engine
- Retry Engine
- Prompt Compiler
- Character Bible / Character Registry
- Scene Bible / Scene Registry
- Production Bible / Asset Registry
- Generation Ledger
- Final Editing

## 一周落地计划

原 1-4 周压缩为 7 天：

| 天 | 目标 | 交付 |
|---|---|---|
| D1 | AIDrama/Jellyfish-oriented 工作台启动、品牌和路径清理 | 首页不再出现旧品牌，容器名和数据目录统一 |
| D2 | Script -> Story Graph -> Director Planner 核心链路 | 可测试 DirectorProgram 与镜头图 |
| D3 | 角色/服装/道具/场景资产锁定 | Character/Scene/Production Bible 与 continuity locks 用于 prompt compile |
| D4 | QA/Retry/Generation Ledger | 单镜头 attempt、QA finding、repair notes、成本和输出可复盘 |
| D5 | Batch Production | 多序列计划、优先级、失败隔离、汇总 |
| D6 | Final Editing | EDL/timeline、selected output、unresolved shot 报告 |
| D7 | 3 个 60-90 秒样片和 1 个 5 集题材验证模板 | 测试文档、发布复盘表、成本复盘表 |

## 已知注意事项

- `Doc/accounts`、`.env.local`、旧 `.env` 必须保持忽略。
- `external/` 是临时忽略区，不提交、不构建。
- 宿主直接跑全量 pytest 可能因缺 DashScope/OSS SDK 失败；需要时优先在容器内跑全量后端测试。
- 前端端口使用 `3014`，后端端口使用 `17177`。
