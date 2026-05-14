# 任务进度索引

日期：2026-05-15

这个文件用于跨会话交接。后续 AI 或人工进入仓库时，先读本文件，再读 `docs/README.md` 和 `agent.md`。

## 当前会话约束

- 按用户要求：先计划再执行。
- 不启动多 agent。
- 使用并行命令做多任务文件读取和验证。
- 每个阶段完成后更新本索引。
- `external/` 仅作为被忽略的上游参考区，不参与提交和构建。

## 本轮执行计划与状态

### 2026-05-15 多集视频真实产出、PRD 同步与批量制片闭环

| 阶段 | 状态 | 本轮动作 | 验收方式 |
|---|---|---|---|
| 1. 计划与现状复核 | 已完成 | 复核 git 状态、AGENTS 指令、现有 Auto Drama、分集生产包、视频任务、FFmpeg 合并、PRD 和测试文档 | `git status --short --branch`、读取关键模块和文档 |
| 2. 产品 PRD | 已完成 | 将“直接产出若干集视频”的制作人需求补充进 PRD，明确离线样片产出与工业链路关系 | 文档复核 |
| 3. 工程实现 | 已完成 | 新增可重复、可测试的分集视频制片 runtime/API/CLI，用真实 mp4 交付多集样片 | pytest、API 冒烟、文件探测 |
| 4. 真实产出 | 已完成 | 直接运行项目生产多集视频，落盘 episode manifests 和 series manifest | `ffprobe`、manifest 复核 |
| 5. 测试工程 | 已完成 | 补充后端测试和测试用例文档，覆盖生产包到 mp4 的批量链路 | pytest、文档复核 |
| 6. 运行清理提交推送 | 已完成 | 启动服务、接口冒烟、检查冲突和工作区，提交并按需要 push | `make up`、curl、`git diff --check`、`git ls-files -u`、`git push` |

当前决策：

- 不启动多 agent，保持单一执行上下文。
- “真实产出”采用本地 deterministic production runtime：使用 Novel/Auto Drama 结构化生产包生成可播放 mp4 样片，避免默认 dry-run 只产生 JSON 或 dummy 文件。
- 该 runtime 是本地可验证兜底，不替代 DashScope/Wan/Kling/Vidu 等正式视频模型；正式模型仍作为可接入 runtime。
- 产出文件仍落在被忽略的 `output/`，代码、测试和文档提交入库，生成视频不提交。

当前实现记录：

- 新增 `src/film_engine/episode_video.py`，提供 `EpisodeVideoProducer` 本地 deterministic 视频 runtime。
- 新增 `POST /film/auto-drama/produce-videos` 和 `GET /film/auto-drama/produce-videos`。
- 新增 `scripts/produce_auto_drama_videos.py`，可直接从命令行生成多集 mp4。
- 新增 `tests/test_episode_video_producer.py`，并在 API 测试中补 direct production contract。
- `requirements.txt` / `requirements-docker.txt` 固化 `pillow`，用于 frame slate 渲染。

真实产出记录：

- 已运行 `python3 scripts/produce_auto_drama_videos.py --title "Night Signal Direct Production" --episodes 3 --frame-seconds 1.2 --width 720 --height 1280 --fps 24`。
- 系列 manifest：`output/productions/night_signal_direct_production_1778781770_d122d417/series_manifest.json`。
- 第 1 集：`output/productions/night_signal_direct_production_1778781770_d122d417/episodes/ep01_ep01_hook/ep01_ep01_hook.mp4`，`ffprobe` 返回 `h264,720,1280`，时长 `3.625000`。
- 第 2 集：`output/productions/night_signal_direct_production_1778781770_d122d417/episodes/ep02_ep02_escalation/ep02_ep02_escalation.mp4`，`ffprobe` 返回 `h264,720,1280`，时长 `3.625000`。
- 第 3 集：`output/productions/night_signal_direct_production_1778781770_d122d417/episodes/ep03_ep03_reversal/ep03_ep03_reversal.mp4`，`ffprobe` 返回 `h264,720,1280`，时长 `3.625000`。

阶段性验证记录：

- `python3 -m compileall -q src/film_engine src/apps/comic_gen/api.py scripts/produce_auto_drama_videos.py`：通过。
- `python3 -m pytest tests/test_episode_video_producer.py -q -s`：通过，2 passed。
- `python3 -m pytest tests/test_episode_video_producer.py tests/test_episode_production_extraction.py tests/test_auto_drama_pipeline.py -q -s`：通过，7 passed。
- `python3 -m pytest tests/test_film_pipeline_api.py -q -s`：宿主缺 DashScope SDK，16 skipped，保留 Docker 后端容器补跑。
- `cd frontend && npm run test`：通过，12 个测试文件，126 个测试。
- `cd frontend && npx tsc --noEmit --pretty false`：通过。
- `make up`：通过，Docker 前后端重建并启动；前端 `39211`、后端 `48217` 均 Up。
- `curl --noproxy '*' -sSI http://127.0.0.1:39211/`：HTTP 200。
- `GET http://127.0.0.1:48217/film/auto-drama/produce-videos`：HTTP 200，返回 `episode_video_producer.v1`。
- `docker compose exec -T backend python -m pytest -q -s tests/test_episode_video_producer.py tests/test_film_pipeline_api.py`：通过，18 passed。
- `POST http://127.0.0.1:48217/film/auto-drama/produce-videos`：HTTP 200，生成 `output/productions/api_video_smoke_1778782363_be4b3d92/.../ep01_ep01_hook.mp4`。
- API 冒烟产物 `ffprobe`：`h264,360,640`，时长 `1.750000`。
- 格式整理后再次执行 `make up`：通过，Docker 前后端使用缓存重建并启动。
- 最终容器冒烟：`curl http://127.0.0.1:39211/` HTTP 200，`GET /film/auto-drama/produce-videos` HTTP 200。
- 最终容器补测：`docker compose exec -T backend python -m pytest -q -s tests/test_episode_video_producer.py tests/test_film_pipeline_api.py` 通过，18 passed。
- `git diff --check`：通过。
- `git ls-files -u`：无输出，无未解决冲突。
- `git commit -m "Add direct Auto Drama video production"`：已创建提交 `b7e719d5`。
- 首次 `git push origin main` 在 SSH 交互/网络层挂起，已安全结束进程，保留本地提交。
- `GIT_SSH_COMMAND='ssh -o BatchMode=yes -o ConnectTimeout=15' git push origin main`：已成功推送 `b7e719d5` 到 `origin/main`。

### 2026-05-15 重启恢复：独立端口、百炼默认与服务验证

| 阶段 | 状态 | 本轮动作 | 验收方式 |
|---|---|---|---|
| 1. 安全审计与计划 | 已完成 | 复核 git 状态、AGENTS 指令、启动脚本、端口监听、模型运行时和测试入口 | `git status --short --branch`、`ss -ltnp`、读取关键文件 |
| 2. 产品 PRD | 已完成 | 明确重启恢复、独立端口、百炼默认、AI 漫剧生产流和 UI 模块验收 | 文档复核 |
| 3. 架构实现计划 | 已完成 | 拆分启动配置、后端端口、前端端口、Docker 代理、百炼运行时、测试验证 | 文档复核 |
| 4. 工程实现 | 已完成 | 修改脚本、Docker、前端 API URL 解析、`.env.example` 和本地 `.env` 非敏感运行键 | 代码检查 |
| 5. 测试验证 | 已完成 | 跑后端 Film API、前端 API/配置测试、启动服务并 curl 冒烟 | pytest、vitest、curl |
| 6. 清理提交推送 | 进行中 | 检查冲突和工作区，提交必要修改并 push | `git diff --check`、`git ls-files -u`、`git push` |

当前决策：

- 前端端口改为 `39211`，后端端口改为 `48217`，避开本机已监听的 `17177/3014/3015`。
- 大模型默认策略保持阿里百炼 DashScope：`LLM_PROVIDER=dashscope`，文本兼容模型默认 `qwen-plus`。
- `.env` 与 `.env.local` 保持本地密钥文件，不提交；本轮只写入端口和百炼默认这类运行配置。

当前实现记录：

- 新增 `scripts/runtime-config.js`，统一解析 `.env` / `.env.local` 中的端口、API URL 和百炼默认值。
- 新增 `scripts/start-frontend.js`，`npm run dev` 会注入 `PORT=39211` 和 `NEXT_PUBLIC_API_URL=http://localhost:48217`。
- 后端脚本、Docker、nginx、桌面入口和前端 API URL 解析已切换到 `48217`。
- `scripts/bootstrap_env.sh` 支持缺少 `Doc/accounts` 时从本地 `.env` 生成 `.env.local`，匹配本轮“密钥已经在 .env”场景。
- `Dockerfile.backend` 复制 `tests/`，让容器内 pytest 回归与文档保持一致。

验证记录：

- `python3 -m compileall -q src/apps/comic_gen/api.py src/apps/comic_gen/llm_adapter.py main.py`：通过。
- 宿主 `python3 -m pytest -q -s tests/test_film_pipeline_api.py`：宿主缺 DashScope SDK，15 个用例按项目 skip 规则跳过。
- `npm run test -- api-response.test.ts endpoint-config.test.ts`：2 个文件、27 个前端测试通过。
- `make up`：从 `.env` 生成 `.env.local`，Docker 前端与后端镜像构建成功。
- `docker compose ps`：前端 `39211->80`、后端 `48217->48217` 均 Up。
- `docker compose exec -T backend python -m pytest -q -s tests/test_film_pipeline_api.py`：15 个后端 API 测试通过。
- `curl http://127.0.0.1:39211/`：HTTP 200。
- `curl http://127.0.0.1:48217/config/info`：HTTP 200，返回 `llm_provider=dashscope`、`api_port=48217`、`frontend_port=39211`。
- `curl http://127.0.0.1:39211/film/runtime/recommendations`：HTTP 200，返回 `Bailian-first` 模型策略。

### 2026-05-14 重启恢复：PRD、最终验证与推送

| 阶段 | 状态 | 本轮动作 | 验收方式 |
|---|---|---|---|
| 1. 重启后审计 | 已完成 | 复核 git dirty 工作树、`docs/task-progress.md`、Auto Drama、生产包、Web Media、主题、首页流程和测试文件 | `git status`、`rg`、读取关键文件 |
| 2. 产品 PRD 与架构同步 | 已完成 | 新增产品需求说明书，更新文档中心、架构动作和本进度索引 | 文档复核 |
| 3. 实现缺口补齐 | 已完成 | 对审计中发现的注释、类型、测试或运行问题做小范围补齐 | `compileall`、`tsc`、单测 |
| 4. 运行验证 | 已完成 | 重启/重建服务，跑后端、前端和 Docker 冒烟 | pytest、vitest、curl、docker |
| 5. 清理提交推送 | 已完成 | 检查冲突、diff check、提交并 push 必要修改 | `git diff --check`、`git ls-files -u`、`git push` |

当前重启后审计结论：

- 上次会话已把核心代码写入工作树，但尚未完成最终运行验证、提交和推送。
- 需求 1 的五个缺口均已有对应实现：一句话制片 UI、资产级网络图片/视频采集、首页流程地图、主题切换、每集生产包。
- 需求 2 缺少独立 PRD 文件，本轮新增 `docs/ai-drama-product-requirements.md`。
- 需求 3 的实现需要通过本轮测试确认，不在未验证状态下提交。
- 需求 4 的测试用例文档已有 TC-058 至 TC-063，本轮继续补充验证记录。
- 需求 5 需要在本次会话完成服务运行、测试、工作区清理、提交和 push。

当前补齐记录：

- 新增 `docs/ai-drama-product-requirements.md`，覆盖产品定位、端到端流程、功能需求、信息架构、接口、非功能需求和验收矩阵。
- 更新 `docs/README.md`，把 PRD 纳入文档中心阅读顺序。
- 更新 `docs/ai-drama-architecture-actions.md`，记录生产包提取、资产级 Web Media、首页制片入口和主题切换的架构决策。
- 补充新前端入口与主题模块的 JSDoc/字段注释，减少重启恢复后的接手成本。

本轮重启恢复验证记录：

- `python3 -m compileall -q src/film_engine src/apps/comic_gen`：通过。
- `cd frontend && npx tsc --noEmit --pretty false`：通过。
- `python3 -m pytest tests/test_episode_production_extraction.py tests/test_auto_drama_pipeline.py tests/test_web_media_collector.py -q -s`：通过，7 passed，1 skipped。
- `cd frontend && npm run test -- workflow-api theme-presets OneSentenceDramaPanel`：通过已匹配 API/主题测试，2 个测试文件，8 个测试。
- `cd frontend && npm run test`：通过，12 个测试文件，123 个测试。
- `cd frontend && npm run test:ui`：通过，4 个测试文件，50 个测试；错误态用例保留预期 stderr。
- 宿主 `python3 -m pytest -q -s tests`：collection 阶段被宿主缺 `dashscope` SDK 挡住；已进入 Docker 后端容器补跑完整测试。
- `docker compose up -d --build --remove-orphans`：通过，`aidrama-backend`、`aidrama-frontend` 已重建并启动。
- `curl --noproxy '*' -sSI http://127.0.0.1:3014/`：HTTP 200。
- `GET http://127.0.0.1:17177/film/auto-drama/run`：HTTP 200，返回 `persist_mode=series` 示例。
- `GET http://127.0.0.1:17177/film/templates`：HTTP 200，返回 3 个样片与系列蓝图目录。
- `POST http://127.0.0.1:17177/film/auto-drama/run` dry-run 冒烟：HTTP 200，返回 `novel_plan` 和 `episode_packages`。
- `docker cp tests aidrama-backend:/app/tests && docker compose exec -T backend python -m pytest -q -s /app/tests`：通过，174 passed。
- 小范围修正资产级 Web 采集返回 `upload_type=image` 后，已重新执行 `cd frontend && npx tsc --noEmit --pretty false`、`cd frontend && npm run test -- workflow-api`、`docker compose up -d --build --remove-orphans`、首页/Auto Drama 冒烟和容器内全量后端测试，均通过。
- `git diff --check`：通过。
- `git ls-files -u`：无输出，无未解决冲突。
- `git commit -m "Add producer Auto Drama workspace flow"`：已创建提交 `4e5a85c3`。
- `git push origin main`：已推送 `4e5a85c3` 到 `origin/main`。

### 2026-05-13 制作人一键漫剧、资产 Web 采集、主题与分集生产包

| 阶段 | 状态 | 本轮动作 | 验收方式 |
|---|---|---|---|
| 1. 计划与现状复核 | 已完成 | 复核 AGENTS、进度索引、Auto Drama、Web Media、模板中心、工作区、主题、分集/分镜/资产提取缺口 | `rg`、读取前后端关键模块 |
| 2. 产品链路实现 | 已完成 | 补可见的一句话生成多集漫剧入口、每集生产包、资产级 Web 图片/视频采集、工作区/模板流程地图、主题切换 | 后端/前端单测 |
| 3. 测试工程 | 已完成 | 补后端 API、Pipeline、前端 API/主题/面板测试 | pytest、vitest、tsc |
| 4. 文档与手册 | 已完成 | 更新测试用例文档、用户操作手册、任务进度索引 | 文档复核 |
| 5. 运行验证、清理、提交推送 | 待执行 | 重建运行、冒烟测试、冲突检查、提交并 push 必要修改 | docker、curl、git |

本轮初步结论：

- “一句话生成小说/多集漫剧”已有 `/film/auto-drama/run` API，但首页缺少制作人可见入口，且默认只持久化为单项目，不利于多集连续生产。
- Web 素材采集已有项目级 `/projects/{id}/web_media/collect`，但资产卡片没有角色/场景/道具级“采集参考图/参考视频”入口。
- 模板中心和工作区都已存在，但首页缺少清晰的流程地图：模板中心用于从验证样片/系列蓝图开始，工作区用于管理正在制作的项目和系列。
- 每集脚本、分镜、角色、道具、服装、特效需要成为可返回、可测试、可落盘的生产包，而不是只隐藏在 dry-run metadata 里。
- 页面主题目前是硬编码暗色科技风，需要通过 CSS 变量和可持久化主题开关扩展。

本轮阶段性验证记录：

- `python3 -m compileall -q src/film_engine src/apps/comic_gen`：通过。
- `cd frontend && npx tsc --noEmit --pretty false`：通过。
- `python3 -m pytest tests/test_episode_production_extraction.py tests/test_auto_drama_pipeline.py tests/test_web_media_collector.py -q -s`：通过，7 passed，1 skipped（宿主缺 DashScope 时 Pipeline 挂图测试跳过）。
- `python3 -m pytest tests/test_film_pipeline_api.py -q -s`：宿主 14 skipped（宿主缺 DashScope，保留容器复测）。
- `cd frontend && npm run test -- workflow-api theme-presets OneSentenceDramaPanel`：通过已匹配 API/主题测试，2 个测试文件，8 个测试。
- `cd frontend && npm run test:ui -- OneSentenceDramaPanel`：通过，1 个测试文件，1 个测试。

### 2026-05-12 分镜/Motion 故障修复、Workflow Switch 可视化与 Web 素材采集

| 阶段 | 状态 | 本轮动作 | 验收方式 |
|---|---|---|---|
| 1. 计划与故障定位 | 已完成 | 复核 AGENTS、进度索引、分镜生成、Motion 润色/提交、workflow_switch API、素材入口 | `rg`、读取前后端模块 |
| 2. 分镜生成韧性 | 已完成 | 强化 LLM JSON 解析、失败回退、缺省场景/资产补齐，避免“生成分镜失败”阻断制作 | `tests/test_storyboard_resilience.py` |
| 3. Web 素材采集 | 已完成 | 新增图片/视频采集服务与 `/projects/{id}/web_media/collect`，支持挂到分镜或供 Motion 使用 | `tests/test_web_media_collector.py`、前端 API 测试 |
| 4. Motion 修复 | 已完成 | AI 润色失败兜底、上传等待、提交错误细化、无素材时一键采集图片/视频 | `workflow-api`、`tsc` |
| 5. workflow_switch 可见化 | 已完成 | 在 `9. QA & Export` 显示 00-09 模块自动/人工开关和刷新按钮 | `workflow-switches-api`、`tsc` |
| 6. 文档与测试工程 | 已完成 | 更新测试用例文档、用户操作手册、任务进度索引 | 文档复核 |
| 7. 运行验证、清理、提交推送 | 已完成 | 宿主测试、Docker 重建冒烟、冲突检查、提交并 push 必要修改 | pytest、vitest、tsc、docker、git |

本轮初步结论：

- 分镜生成失败的主要风险点在 LLM 返回非标准 JSON、空 frames、无实体上下文时缺少可继续制作的 deterministic fallback。
- Motion 页面失败的主要风险点在无首帧/无参考视频时没有替代素材入口、上传中 blob 会被跳过、错误提示过泛。
- `workflow_switch` 已存在于 `docs/Codex_Workflow_Prompts` 和 `/film/workflow/prompts`，但制作人页面没有可见入口；本轮会放到 `9. QA & Export`。

本轮阶段性验证记录：

- `python3 -m compileall -q src/apps/comic_gen src/film_engine src/models`：通过。
- 电脑重启恢复续跑：WSL 内 `docker` 初始不可用，已从 Windows 侧启动 Docker Desktop，daemon 恢复后继续执行 Docker 验证。
- `cd frontend && npx tsc --noEmit --pretty false`：通过。
- `python3 -m pytest tests/test_storyboard_resilience.py tests/test_web_media_collector.py tests/test_workflow_prompt_switches.py -q -s`：通过，5 passed，2 skipped（宿主缺 DashScope，完整 Pipeline 留到容器复测）。
- `cd frontend && npm run test -- workflow-api workflow-switches-api`：通过，2 个测试文件，5 个测试。
- `python3 -m pytest tests/test_storyboard_resilience.py tests/test_web_media_collector.py tests/test_workflow_prompt_switches.py tests/test_auto_drama_pipeline.py tests/test_film_workflow.py tests/test_film_production_pipeline.py tests/test_series_production_blueprint.py -q -s`：通过，24 passed，2 skipped。
- `cd frontend && npm run test`：通过，11 个测试文件，119 个测试。
- `cd frontend && npm run test:ui`：通过，3 个测试文件，49 个测试；错误态用例保留预期 stderr。
- `docker compose up -d --build --remove-orphans`：通过，`aidrama-backend`、`aidrama-frontend` 已重建并启动。
- `curl -I http://localhost:3014/`：HTTP 200。
- `curl http://localhost:17177/film/workflow/prompts`：HTTP 200，返回 10 个模块、`workflow_prompt_switch.v1`、`status=ready`。
- `POST /projects/{id}/web_media/collect`：HTTP 200，返回 `source=web_media_collector.v1`，图片挂载 `attached_count=1`；视频采集返回可用 video item。
- `docker compose exec -T backend python -m pytest -q -s /app/tests`：通过，170 passed，81 warnings。
- `git diff --check`：通过。
- `git ls-files -u`：无输出，无未解决冲突。

### 2026-05-12 模型适配隔离、Workflow 自动开关与文字到漫剧 Auto Drama

| 阶段 | 状态 | 本轮动作 | 验收方式 |
|---|---|---|---|
| 1. 规范与现状复核 | 已完成 | 读取 AGENTS、`docs/Codex_Workflow_Prompts`、现有 Film Core、模型适配器和配置接口；确认顶层 `standards/` 目录不存在 | `rg --files`、读取 `workflow.py`、`api.py`、`src/models/*` |
| 2. 模型适配配置层 | 已完成 | 新增 `src/models/runtime_config.py`，让 DashScope、Kling、Vidu、Ark/Seedance、LLM Adapter 通过统一层解析 `api_key` / `base_url` / `baseurl` | `tests/test_model_runtime_config.py`、`compileall` |
| 3. Workflow Prompt 开关 | 已完成 | 为 00-09 prompt 文件增加 `workflow_switch`，新增 parser、execution plan 和 `/film/workflow/prompts` API | `tests/test_workflow_prompt_switches.py` |
| 4. 文字到小说到漫剧 | 已完成 | 新增 `NovelEngine`、`AutoDramaPipeline` 和 `/film/auto-drama/run`，支持自动完整 dry-run 或在非自动阶段停下 | `tests/test_auto_drama_pipeline.py`、API 测试 |
| 5. 测试与文档 | 已完成 | 更新测试用例文档、用户操作手册、前端 API 类型和环境配置页面字段 | pytest、tsc、vitest、Docker 复测 |
| 6. 清理提交推送 | 已完成 | 最终冲突检查、全量验证、提交并 push 必要修改 | `git diff --check`、`git ls-files -u`、`git push` |

本轮阶段性结论：

- 各模型调用已通过统一适配配置层隔离：适配器优先读取显式 config，其次读取 `{PROVIDER}_API_KEY` / `{PROVIDER}_BASE_URL`，最后使用内置默认 base url。
- `docs/Codex_Workflow_Prompts` 00-09 每个模块都已有 `workflow_switch`。默认全自动；当 `auto_advance=false` 或 `requires_human_review=true` 时，执行计划会在该模块完成后返回 `waiting_for_user`。
- 新增 Auto Drama dry-run：输入一段文字后生成 `novel_plan`、`screenplay_text`、Story Graph、Director Program、QA/Ledger/Final Edit，并可自动写入 Studio 草稿项目。
- 当前实现不新增强制页面 UI 流程；已有 Settings/环境配置页面补充了可选模型 Key 和 endpoint 字段，主要一键链路通过 API 暴露，避免引入新的 UI 风险。
- Docker 后端镜像已复制 `docs/Codex_Workflow_Prompts/`，容器内 `/film/workflow/prompts` 与 `/film/auto-drama/run` 可直接读取 prompt 开关，不再依赖宿主挂载。

本轮阶段性验证记录：

- `python3 -m compileall -q src/film_engine src/models src/apps/comic_gen`：通过。
- `python3 -m pytest tests/test_model_runtime_config.py tests/test_workflow_prompt_switches.py tests/test_auto_drama_pipeline.py tests/test_film_workflow.py tests/test_film_pipeline_api.py -q -s`：宿主通过 13 passed，12 skipped（宿主 API app 受 DashScope SDK 可用性影响，保留容器复测）。
- `python3 -m pytest tests/test_model_runtime_config.py tests/test_workflow_prompt_switches.py tests/test_auto_drama_pipeline.py tests/test_film_workflow.py tests/test_film_production_pipeline.py tests/test_series_production_blueprint.py -q -s`：通过，24 passed。
- `cd frontend && npx tsc --noEmit --pretty false`：通过。
- `cd frontend && npm run test`：通过，10 个测试文件，117 个测试。
- `cd frontend && npm run test:ui`：通过，3 个测试文件，49 个测试；错误态用例保留预期 stderr。
- `docker compose up -d --build --remove-orphans`：通过，`aidrama-backend`、`aidrama-frontend` 已重建并启动。
- `curl -I http://localhost:3014/`：HTTP 200。
- `curl http://localhost:17177/film/workflow/prompts`：HTTP 200，返回 10 个 prompt 模块、`workflow_prompt_switch.v1` 和全自动 execution plan。
- `curl -X POST http://localhost:17177/film/auto-drama/run ...`：HTTP 200，返回 `novel_plan`、`screenplay_text`、Film Core dry-run、`final_edit`。
- `curl http://localhost:17177/config/env`：HTTP 200，返回 DashScope/OpenAI/Ark/PixVerse/Vidu/Kling 配置字段和 endpoint overrides。
- `docker compose exec -T backend python -m pytest -q -s /app/tests/test_model_runtime_config.py /app/tests/test_workflow_prompt_switches.py /app/tests/test_auto_drama_pipeline.py /app/tests/test_film_workflow.py /app/tests/test_film_pipeline_api.py`：通过，25 passed。
- `docker compose exec -T backend python -m pytest -q -s /app/tests`：通过，165 passed，76 warnings。
- `git diff --check`：通过。
- `git ls-files -u`：无输出，无未解决冲突。
- `git commit -m "Add Auto Drama workflow controls"`：已创建提交 `4404ab10`。
- `git push origin main`：已推送 `4404ab10` 到 `origin/main`。

### 2026-05-12 CineForge 工作流、模型建议与 QA Export 导出兜底

| 阶段 | 状态 | 本轮动作 | 验收方式 |
|---|---|---|---|
| 1. 规范与故障复核 | 已完成 | 读取 `docs/Codex_Workflow_Prompts`、AGENTS 规则、QA & Export Start Render 链路 | `rg`、读取 `FilmEngineControlRoom`、`/projects/{id}/export`、`merge_videos` |
| 2. 工作流状态实现 | 已完成 | 新增 workflow-first 状态层、模型建议目录、项目 workflow API、阶段重生成事件 | `tests/test_film_workflow.py`、`GET /projects/{id}/workflow` |
| 3. 导出兜底实现 | 已完成 | `Start Render` 有 selected clips 时合成视频，缺 clips 时导出 render package，不再泛化失败 | `/projects/{id}/export`、前端 workflow API 测试 |
| 4. UI 与文档 | 已完成 | QA & Export 增加 CineForge Workflow 面板、更新手册/测试文档/架构文档 | `frontend/src/components/modules/FilmEngineControlRoom.tsx`、`USER_MANUAL.md` |
| 5. 验证清理提交推送 | 已完成 | 后端/前端/容器回归已通过，冲突检查已通过，提交并 push 必要修改 | pytest、vitest、tsc、docker、git |

本轮初步结论：

- “补资产、分镜、视频、配音和合成”确实需要不同 runtime：图片模型负责资产和分镜关键帧，视频模型负责 I2V/R2V/T2V，语音模型负责对白，合成优先用 FFmpeg 而不是生成模型。
- 当前工程继续采用百炼优先：现有可运行适配器以 `wan2.6-image`、`wan2.6-i2v/r2v`、CosyVoice 为主；文档和模型目录把 `wan2.7-image(-pro)`、`wan2.7-i2v/r2v` 标为后续优先升级目标，避免 UI 暴露尚未完全适配的新协议。
- `QA & Export` 的 `Start Render` 不再在缺视频时只显示 `failed to export project`；现在会返回 `mode=render_package`，下载 JSON manifest，包含 workflow state、阻塞项、模型建议和 frame 级媒体引用。
- 新增 `GET /film/runtime/recommendations`、`GET /projects/{projectId}/workflow`、`POST /projects/{projectId}/workflow/stages/{stageId}/regenerate`，为 workflow state、可编辑/可重生成和后续队列接入留出稳定契约。

本轮阶段性验证记录：

- `python3 -m compileall -q src/film_engine src/apps/comic_gen/api.py tests/test_film_workflow.py`：通过。
- `python3 -m pytest tests/test_film_workflow.py -q -s`：通过，5 passed。
- `cd frontend && npx tsc --noEmit --pretty false`：通过。
- `python3 -m pytest tests/test_film_pipeline_api.py -q -s`：宿主缺 DashScope，9 skipped（保留容器内复测）。
- `python3 -m pytest tests/test_film_workflow.py tests/test_film_engine_core.py tests/test_film_engine_batch.py tests/test_film_production_pipeline.py tests/test_series_production_blueprint.py -q -s`：通过，28 passed。
- `cd frontend && npm run test`：通过，10 个测试文件，116 个测试。
- `cd frontend && npm run test:ui`：通过，3 个测试文件，49 个测试；错误态用例保留预期 stderr。
- `docker compose up -d --build --remove-orphans`：通过，`aidrama-backend`、`aidrama-frontend` 已重建并启动。
- `curl -I http://localhost:3014/`：HTTP 200。
- `curl http://localhost:3014/film/runtime/recommendations`：HTTP 200，返回 `cineforge_workflow.v1` 和百炼优先模型目录。
- API 冒烟创建 `Workflow Export Smoke` 项目后调用 `/projects/{id}/workflow` 与 `/projects/{id}/export`：通过，workflow 9 阶段，导出返回 `mode=render_package` 与可下载 JSON。
- `docker compose exec -T backend python -m pytest -q -s /app/tests/test_film_workflow.py /app/tests/test_film_pipeline_api.py /app/tests/test_film_engine_core.py /app/tests/test_film_engine_batch.py /app/tests/test_film_production_pipeline.py /app/tests/test_series_production_blueprint.py`：通过，37 passed。
- `docker compose exec -T backend python -m pytest -q -s /app/tests`：通过，154 passed，74 warnings。
- `git diff --check`：通过。
- `git ls-files -u`：无输出，无未解决冲突。
- `git commit -m "Add CineForge workflow export fallback"`：已创建提交 `4e65fb41`。
- `git push origin main`：已推送 `4e65fb41` 到 `origin/main`。

### 2026-05-11 服务重启、模板可见入口与全链路使用手册复核

| 阶段 | 状态 | 本轮动作 | 验收方式 |
|---|---|---|---|
| 1. 服务与仓库复核 | 已完成 | 复核 git、Docker 服务、3014/17177 运行入口、现有模板和 UI 缺口 | `git status --short --branch`、`docker compose ps`、读取首页和模板样例 |
| 2. 模板入口实现 | 已完成 | 把 3 个 60-90 秒样片和 5 集验证蓝图从 `samples/` 暴露到后端 API 与首页可见模板中心 | 后端 API 测试、前端模板中心测试 |
| 3. 测试工程复核 | 已完成 | 补充模板目录、模板实例化、首页入口、手册路径的自动化与文档测试记录 | pytest、vitest、tsc、Docker/curl 冒烟 |
| 4. 用户操作手册 | 已完成 | 说明当前 UI 不是 LumenX、模板在哪里看、从配置到多集出片怎么操作 | `USER_MANUAL.md`、`docs/ai-drama-test-analysis.md` |
| 5. 清理提交推送 | 已完成 | 重建重启服务、冲突检查、清理工作区并按需提交推送 | `git diff --check`、`git ls-files -u`、`git push origin main` |

本轮初步结论：

- 当前可运行页面是 AIDrama Studio；前端运行面源码没有 LumenX 页面入口。
- `samples/pilot_samples/three_60_90s_pilots.yaml` 和 `samples/series_production/vertical_suspense_5ep.yaml` 现在会通过 `GET /film/templates` 暴露，并显示在 `http://localhost:3014` 首页“AI 漫剧模板中心”。
- 首页支持从 3 个样片创建独立项目，也支持从 `night_signal_s01` 创建 5 集系列草稿；样片脚本中的 `[character]`、`[prop]`、`[costume]` 标签会在前端 Film Core payload 中推导为轻量资产，避免模板刚创建就无法进入 QA dry-run。
- `Dockerfile.backend` 已复制 `samples/`，容器内 `/film/templates` 不再依赖宿主手动挂载样例文件。

本轮验证记录：

- `python3 -m compileall -q src/film_engine src/apps/comic_gen/api.py`：通过。
- `python3 -m pytest -q -s tests/test_series_production_blueprint.py tests/test_film_engine_core.py tests/test_film_engine_batch.py tests/test_film_production_pipeline.py tests/test_film_pipeline_api.py`：通过，23 passed，6 skipped（宿主缺 DashScope 时 API app 测试按既有规则跳过）。
- `cd frontend && npm run test`：通过，9 个测试文件，113 个测试。
- `cd frontend && npm run test:ui`：通过，3 个测试文件，49 个测试；错误态用例保留预期 stderr。
- `cd frontend && npx tsc --noEmit --pretty false`：通过。
- `docker compose up -d --build --remove-orphans`：通过，`aidrama-backend`、`aidrama-frontend` 已重建并重启。
- `curl -I http://localhost:3014/`：HTTP 200。
- `curl -sS http://localhost:3014/film/templates`：HTTP 200，返回 3 个样片、1 个 5 集蓝图和 summary。
- `curl -sS http://localhost:17177/film/pipeline/run`：HTTP 200，返回 Film Core endpoint 说明和固定九阶段。
- `docker run --rm aidrama-frontend:latest ... grep 'AI 漫剧模板中心'`：通过，构建产物包含模板中心。
- `docker run --rm aidrama-frontend:latest ... grep 'LumenX|lumenx|Lumen'`：通过，构建后的前端无旧品牌字符串。
- `docker cp tests aidrama-backend:/app/tests && docker compose exec -T backend python -m pytest -q -s /app/tests`：通过，146 passed，72 warnings。
- `git diff --check`：通过。
- `git ls-files -u`：无输出，无未解决冲突。
- `git commit -m "Expose AI drama templates in Studio"`：已创建提交 `6dbd709f`。
- `git push origin main`：已推送本轮必要修改到 `origin/main`。

### 2026-05-09 D7 样片模板、使用手册与 LumenX 运行面清理复核

| 阶段 | 状态 | 本轮动作 | 验收方式 |
|---|---|---|---|
| 1. 现状复核 | 已完成 | 复核 git、文档、前端源码、Film Core、测试矩阵和 LumenX 关键词残留 | `git status --short --branch`、`rg 'LumenX|lumenx|Lumen'`、读取 `frontend/src/app/page.tsx` |
| 2. 工程补齐 | 已完成 | 补齐 D7 多题材样片/5 集验证模板与可复用系列生产编排能力 | `src/film_engine/series.py`、新增样例、后端单测 |
| 3. 测试文档 | 已完成 | 以测试工程师视角补充系列模板、操作路径和行业痛点验收用例 | `docs/ai-drama-test-analysis.md` |
| 4. 用户手册 | 已完成 | 从配置到多集 AI 漫剧出片补全详细操作手册，并说明页面是否涉及 UI 操作 | `USER_MANUAL.md` |
| 5. 清理提交推送 | 已完成 | 冲突检查、测试、提交并按需推送 | `git diff --check`、`git ls-files -u`、`git push origin main` |

本轮初步结论：

- 运行面 UI 源码没有使用 LumenX；`rg` 只在历史 PRD、开源对比报告和上一轮进度验证记录里发现 LumenX 文字。
- 当前 AIDrama Studio 是可运行入口，主平台口径是 Jellyfish-oriented，不再以 LumenX 作为 UI 基座。
- Film Core 九阶段、QA/Retry、Ledger、Batch Production、Final Editing 已有可测试闭环；本轮重点补 D7 样片/5 集验证模板和零基础操作手册。
- 已新增 `SeriesProductionBlueprint`、`SeriesProductionPlanner`、`samples/series_production/vertical_suspense_5ep.yaml` 和 `samples/pilot_samples/three_60_90s_pilots.yaml`，把 D7 样片/5 集验证纳入自动化测试。

本轮验证记录：

- `python3 -m compileall -q src/film_engine`：通过。
- `python3 -m pytest tests/test_series_production_blueprint.py -q -s`：通过，5 passed。
- `python3 -m pytest tests/test_series_production_blueprint.py tests/test_film_engine_core.py tests/test_film_engine_batch.py tests/test_film_production_pipeline.py tests/test_film_pipeline_api.py -q -s`：通过，22 passed，3 skipped（宿主缺 DashScope 时 API app 测试按既有规则跳过）。
- `cd frontend && npm run test`：通过，8 个测试文件，109 个测试。
- `cd frontend && npm run test:ui`：通过，2 个测试文件，47 个测试；错误态用例保留预期 stderr。
- `cd frontend && npx tsc --noEmit --pretty false`：通过。
- `docker compose up -d --build --remove-orphans`：通过，`aidrama-backend`、`aidrama-frontend` 已重建启动。
- `docker cp tests aidrama-backend:/app/tests && docker cp samples aidrama-backend:/app/samples && docker compose exec -T backend python -m pytest -q -s /app/tests`：通过，142 passed，41 warnings。
- `curl -I http://localhost:3014/`：HTTP 200。
- `curl http://localhost:17177/film/pipeline/run`：HTTP 200，返回 Film Core endpoint 说明和固定九阶段。
- `docker run --rm aidrama-frontend:latest ... grep 'LumenX|lumenx|Lumen'`：通过，构建后的前端无旧品牌字符串。
- `git diff --check`：通过。
- `git ls-files -u`：无输出，无未解决冲突。
- `git push origin main`：已推送本轮必要修改到 `origin/main`。

### 2026-05-08 QA & Export 入口复核与 D1-D6 收口

| 阶段 | 状态 | 本轮动作 | 验收方式 |
|---|---|---|---|
| 1. 现状复核 | 已完成 | 复核 `docs/task-progress.md`、`/film/pipeline/run`、项目/系列工作台路由和第 9 步页面 | `rg`、读取 `api.py`、`ProjectClient`、`SeriesDetailPage` |
| 2. API 兜底 | 已完成 | 新增 `GET /film/pipeline/run` 使用说明，避免浏览器直接访问返回 `Method Not Allowed` | `tests/test_film_pipeline_api.py`、`curl http://localhost:3014/film/pipeline/run` |
| 3. 工作台入口 | 已完成 | 支持 `#/project/{id}/step/export` 与 `#/series/{seriesId}/episode/{episodeId}/step/export` 深链；系列单集页新增 `QA & Export` 直达按钮 | `frontend/src/lib/workspaceRouting.ts`、前端单测 |
| 4. D1-D6 复核 | 已完成 | 按 D1-D6 验收矩阵复查核心实现和测试覆盖 | 后端核心 pytest、前端 vitest、tsc、容器全量 pytest |
| 5. 文档与清理 | 已完成 | 更新测试用例文档、最终验证、冲突检查、提交并 push 必要修改 | `git diff --check`、`git ls-files -u`、`git push` |

本轮 D1-D6 复核结论：

| 天 | 目标 | 当前结论 | 代码/测试锚点 |
|---|---|---|---|
| D1 | AIDrama/Jellyfish-oriented 工作台启动、品牌和路径清理 | 已实现，本轮继续验证入口可达性 | `frontend/src/app/page.tsx`、Docker nginx API 代理测试 |
| D2 | Script -> Story Graph -> Director Planner 核心链路 | 已实现 | `src/film_engine/story_graph.py`、`director_planner.py`、`tests/test_film_production_pipeline.py` |
| D3 | 角色/服装/道具/场景资产锁定 | 已实现 | `ProductionBible`、`AssetRegistry`、Film Core payload 测试 |
| D4 | QA/Retry/Generation Ledger | 已实现 | `src/film_engine/qa.py`、`retry.py`、`ledger.py`、核心测试 |
| D5 | Batch Production | 已实现 | `src/film_engine/batch.py`、`tests/test_film_engine_batch.py` |
| D6 | Final Editing | 已实现 | `src/film_engine/final_editing.py`、Final Edit pipeline 测试 |

如何进入项目工作台第 9 步：

- 独立项目：点击首页项目卡片进入工作台；也可直接访问 hash `#/project/{projectId}/step/export`。
- 系列项目（例如“星辰大海”）：先进入系列页，选择左侧某一集，在单集面板点击 `QA & Export`；也可直接访问 hash `#/series/{seriesId}/episode/{episodeId}/step/export`。
- 只有“系列详情页”本身不会显示九步工作台；九步工作台属于“独立项目”或“系列单集”。

本轮验证记录：

- `python3 -m compileall -q src/film_engine src/apps/comic_gen/api.py`：通过。
- `python3 -m pytest tests/test_film_engine_core.py tests/test_film_engine_batch.py tests/test_film_production_pipeline.py tests/test_film_pipeline_api.py -q -s`：宿主通过 17 passed，3 skipped（宿主缺 DashScope 时 API app 测试跳过）。
- `cd frontend && npm run test`：通过，8 个测试文件，109 个测试。
- `cd frontend && npm run test:ui`：通过，2 个测试文件，47 个测试。
- `cd frontend && npx tsc --noEmit --pretty false`：通过。
- `docker compose up -d --build --remove-orphans`：通过，`aidrama-backend`、`aidrama-frontend` 已重建启动。
- `curl -sS -i http://localhost:3014/film/pipeline/run`：HTTP 200，返回 GET 使用说明、固定九阶段和 sample payload。
- `curl -sS -X POST http://localhost:3014/film/pipeline/run ...`：HTTP 200，返回 story graph、shot graph、generation ledger、QA reports、final edit。
- `docker compose exec -T backend python -m pytest -q -s /app/tests/test_film_engine_core.py /app/tests/test_film_engine_batch.py /app/tests/test_film_production_pipeline.py /app/tests/test_film_pipeline_api.py`：通过，20 passed。
- `docker compose exec -T backend python -m pytest -q -s /app/tests`：通过，137 passed，41 warnings。
- `git diff --check`：通过。
- `git ls-files -u`：无输出，无未解决冲突。
- `git push origin main`：已推送本轮必要修改到 `origin/main`。

### 2026-05-08 服务重启与九阶段可视化执行

| 阶段 | 状态 | 本轮动作 | 验收方式 |
|---|---|---|---|
| 1. 现状复核 | 已完成 | 复核 git、Docker 服务、Film Core API、前端九步工作台和九阶段 Starter Kit 固定开发顺序 | `git status --short --branch`、读取 `ProjectClient`、`/film/pipeline/run` |
| 2. 服务重启 | 已完成 | 电脑重启后重新构建并启动 `aidrama-backend`、`aidrama-frontend` | `docker compose up -d --build --remove-orphans`、`docker compose ps`、`curl` |
| 3. 缺口确认 | 已完成 | 确认九阶段内核已在后端实现，但页面没有九阶段可视化入口，`9. Export` 仍是 Beta 观感 | 前端侧栏与 `ExportStudio` 代码复核 |
| 4. 页面实现 | 已完成 | 新增 `9. QA & Export` Film Engine 控制台，自动 dry-run 当前项目并展示九阶段状态、QA、Retry、Ledger、Final Edit、导出动作 | `frontend/src/components/modules/FilmEngineControlRoom.tsx` |
| 5. API 契约增强 | 已完成 | `/film/pipeline/run` 响应补充 `film_run.shot_graph`，让 Shot Graph 阶段在页面和测试中可见 | `tests/test_film_pipeline_api.py` |
| 6. 测试补齐 | 已完成 | 新增前端 Film Engine payload/九阶段评估单测，补充测试用例文档；Docker 重建后容器内核心和全量后端测试通过 | `npm run test`、`npm run test:ui`、`npx tsc --noEmit`、`pytest` |
| 7. 清理提交推送 | 已完成 | 已完成最终验证、冲突检查、提交并 push 到 `origin/main` | `git diff --check`、`git ls-files -u`、`git push origin main` |

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
- `git push origin main`：已推送 `1d316f49 Expose film engine QA control room` 到 `origin/main`。

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
