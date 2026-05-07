# 任务进度索引

日期：2026-05-08

这个文件用于跨会话交接。后续 AI 或人工进入仓库时，先读本文件，再读 `docs/README.md` 和 `agent.md`。

## 当前会话执行计划（2026-05-08，批量生产补齐）

本轮继续按单 agent 串行推进，不启动子 agent。先 review 指定 Starter Kit、2026 开源研究报告、现有进度索引、`src/film_engine/`、启动脚本与测试基线，再执行下面计划。

| 阶段 | 状态 | 计划动作 | 验收方式 |
|---|---|---|---|
| 1. 文档与代码复盘 | 已完成 | 复核九阶段 Film Core、Generation Ledger、Docker/Makefile 入口 | `python3 -m compileall -q src/film_engine` 与 `tests/test_film_engine_core.py` 已通过 |
| 2. 缺口选择 | 已完成 | 对照目标“industrial batch production”，确认缺独立批次计划/runner/汇总层 | 在本索引记录缺口和实施计划 |
| 3. 批量生产模型 | 已完成 | 增加 BatchProductionItem/Plan/Run 数据契约，不耦合具体 runtime | Pydantic 模型可序列化、可汇总 |
| 4. 批量 runner | 已完成 | 增加单 agent/单进程 deterministic runner，支持优先级、错误隔离、QA/Retry/ledger 汇总 | 新增核心测试覆盖成功批次、失败隔离、优先级/上限 |
| 5. 文档固化 | 已完成 | 更新项目概览、架构动作和本进度索引；补 Batch Production Skill/Test/Freeze/Sample/Benchmark | 文档说明新增能力和验证记录 |
| 6. 测试与运行 | 已完成 | 跑核心/后端/前端和容器可用验证，并启动项目 | 测试输出和服务 HTTP 检查已写回本索引 |
| 7. 清理提交推送 | 已完成 | 检查 diff、冲突、工作区，提交并 push | `git diff --check`、`git ls-files -u`、`git status`、`git push` |

本轮 review 结论：

- Starter Kit 固定九阶段已经落在 `src/film_engine/`，上一轮补齐了 Character/Scene Bible、continuity locks、Shot Graph cycle check 和 Generation Ledger。
- 研究报告强调小团队重点不是 Agent 数量，而是可复用内容流水线、角色资产系统、镜头 DSL、Reference workflow 和稳定批量生产。
- 当前最值得补的工程缺口是 Film Core 级别的批量生产编排：多个 Director Program 可以被计划化执行，单条失败不拖垮整批，并产出可用于成本/QA/人工复盘的汇总。

本轮新增验证记录：

- `python3 -m compileall -q src/film_engine`：通过。
- `python3 -m pytest tests/test_film_engine_core.py -q -s`：通过，7 个测试。
- `python3 -m pytest tests/test_film_engine_core.py tests/test_film_engine_batch.py -q -s`：通过，11 个测试。
- `python3 -m pytest tests -q -s`：宿主缺少 `dashscope`，8 个测试文件在 collection 阶段失败；继续用 Docker 验证。
- `docker compose up -d --build`：通过，已重建并启动 `lumenx-backend` 和 `lumenx-frontend`。
- 容器临时安装 `pytest` 后执行 `docker compose exec -T backend python -m pytest -q -s /app/tests`：通过，128 个测试，41 个 warning。
- `docker run --rm -v /mnt/d/workplace/AIDrama/docker:/docker:ro -e NODE_ENV=test aidrama-frontend-builder npm run test`：通过，6 个测试文件、101 个测试。
- `docker compose ps`：backend 与 frontend 均为 Up。
- `curl -I http://localhost:3014/`：HTTP 200。
- `curl -sS http://localhost:17177/config/info`：HTTP 200，返回 development config 状态。
- `curl -sS http://localhost:3014/projects/`：HTTP 200，返回 `[]`。
- `curl -sS http://localhost:3014/series`：HTTP 200，返回 `[]`。
- `curl -I http://localhost:17177/docs`：HTTP 200。
- `git diff --check` / `git diff --cached --check`：通过。
- `git ls-files -u`：无输出，无未解决冲突。
- `git commit -m "Add film engine batch production runner"`：已创建提交 `3b6ae24b`。
- `git push`：已推送 `main`，`49aff29f..3b6ae24b`。

## 当前会话连续执行计划（2026-05-08）

| 阶段 | 状态 | 本轮动作 |
|---|---|---|
| 0. 连续执行约束固化 | 已完成 | 单 agent 推进，不启动子 agent；每个阶段完成后更新本索引 |
| 1. 镜头级生成台账设计 | 已完成 | 设计为独立 `GenerationLedger`/recorder，记录 attempt、QA、retry、prompt 指纹、成本和输出 |
| 2. Film Core 接入台账 | 已完成 | 新增 `src/film_engine/ledger.py`，并在 orchestrator 的 QA/retry 循环记录每次 runtime attempt |
| 3. 测试固化 | 已完成 | 核心/provider/media 相关测试和容器内全量后端测试已通过 |
| 4. 文档固化 | 已完成 | 已更新架构建议、项目概览、进度索引和验证记录 |
| 5. 清理、提交、推送 | 已完成 | 工作区检查、冲突检查、必要提交和 push 按本轮最终状态处理 |

连续执行策略：

- 平台上下文和单次工具运行存在客观限制，不能真正“打破”硬限制；本轮用进度索引、阶段状态和验证记录把工作变成可恢复流程。
- 每完成一个阶段立即更新本文件，避免因为上下文压缩而丢失计划。
- 本轮不启动多 agent；使用单 agent 按阶段串行完成计划、实现、测试、固化、清理、提交和推送。

当前验证记录：

- `python3 -m compileall -q src/film_engine`：通过。
- `python3 -m pytest tests/test_film_engine_core.py -q -s`：通过，7 个测试。
- `python3 -m compileall -q src/film_engine src/apps/comic_gen/api.py src/apps/comic_gen/pipeline.py src/config.py`：通过。
- `python3 -m pytest tests/test_film_engine_core.py tests/test_media_refs.py tests/test_provider_media.py tests/test_provider_registry.py -q -s`：通过，33 个测试。
- `git diff --check`：通过。
- `git ls-files -u`：无输出，无未解决冲突。
- `python3 -m pytest tests -q -s`：宿主缺少 `dashscope`，8 个测试文件 collection 失败；继续使用容器验证。
- `docker compose config --quiet`：通过。
- 容器同步本轮 `src/`、`tests/`、`samples/` 后执行 `docker compose exec -T backend python -m pytest -q -s /app/tests`：通过，124 个测试，41 个 warning。
- 补充台账人工复盘防御校验后，重新执行 `python3 -m pytest tests/test_film_engine_core.py -q -s`：通过，7 个测试。
- 再次同步 `src/`、`tests/` 到容器后执行 `docker compose exec -T backend python -m pytest -q -s /app/tests`：通过，124 个测试，41 个 warning。
- 前端本地 `frontend/node_modules` 不存在；本轮未改前端，未执行前端测试。

## 本轮任务状态（2026-05-08）

| 任务 | 状态 | 备注 |
|---|---|---|
| 先做计划再执行 | 已完成 | 本轮已建立计划，按单 agent 连续推进，不启动子 agent |
| 查看 AGENTS/agent 指南 | 已完成 | 已读取 `AGENTS.md`、`agent.md`、`docs/task-progress.md` 和文档中心 |
| 校准主基座口径 | 已完成 | 已把文档调整为：Jellyfish 是主平台基座；LumenX 只作当前可运行参考/兼容工作台 |
| 审计固定九阶段 | 已完成 | 九阶段已有最小闭环；缺口是 Character/Scene Bible、Film State continuity locks、Shot Graph 环形转场校验 |
| 补齐阶段缺口 | 已完成 | 新增 Character/Scene Bible 数据契约与加载、Film State continuity locks、Prompt continuity 编译、Shot Graph 环校验 |
| 验证、清理、冲突处理 | 已完成 | 核心/容器验证通过；宿主全量 pytest 因缺 `dashscope` SDK 无法收集，容器内全量后端测试通过 |
| 提交并 push | 已完成 | 本轮必要修改已整理为提交并推送当前 `main` 分支 |

## 本轮执行计划（2026-05-08）

1. 固化任务进度索引，确认每个节点都能跨会话恢复。
2. 修正主基座口径：最终主平台基座是 `Jellyfish`；`LumenX` 是当前仓库已有的可运行实现参考，不再作为架构主基座。
3. 审计 `src/film_engine/` 与测试，逐项核验固定九阶段是否真实可运行。
4. 补齐缺口：保持 graph-based workflow、ECS-inspired entities、runtime adapter、prompt compiler、QA/retry/state 的模块边界。
5. 运行必要测试和静态验证，清理工作区并确认无冲突。
6. 提交并 push 必要修改。

## 基座口径修正记录

- Starter Kit 明确写明 `Jellyfish -> 主平台基座`，并把 `huobao-drama`、`director_ai`、`BigBanana`、`waoowaoo`、`Toonflow-app`、`StoryDiffusion` 分别定位为运行时、导演 DSL、电影规则、编排、Storyboard UI、角色一致性参考层。
- 之前文档把 `LumenX Studio` 写成主基座，是基于当前仓库已可运行的 LumenX 代码和小团队启动成本做出的阶段性分析，不是 Starter Kit 的最终主基座结论。
- 本轮以后以 Starter Kit 为准：`Jellyfish` 是 AI Film Engine 的主平台基座；`LumenX` 只保留为当前仓库内可运行的兼容工作台/迁移参考，不能覆盖最终架构口径。

## 当前技术选择（2026-05-08）

主平台基座：Jellyfish

当前可运行兼容工作台：LumenX Studio

分层定位：

- `Jellyfish`：Studio OS、Workflow Core、Project System、Asset Management、Async Task System、Shot Management、Studio UI。
- `huobao-drama`：Runtime Layer 参考，包括 render pipeline、FFmpeg orchestration、subtitle/TTS/stitching。
- `director_ai`：Director DSL Layer 参考，包括 shot abstraction、camera grammar、scene timeline、transition metadata。
- `BigBanana`：Cinematic Rule Layer 参考，包括 emotion-camera mapping、pacing rules、composition heuristics。
- `waoowaoo`：Orchestration Layer 参考。
- `Toonflow-app`：Storyboard UI 与 Agent/skill 组织方式参考。
- `StoryDiffusion`：Character Consistency 参考。

必须自研：

- Film State Engine
- QA Engine
- Retry Engine
- Prompt Compiler
- Character Bible / Character Registry
- Scene Bible / Scene Registry

## 本轮九阶段落地索引（2026-05-08）

| 阶段 | 状态 | 落地位置 |
|---|---|---|
| Runtime | 已完成 | `src/film_engine/runtime.py`：runtime adapter/router + deterministic dry-run adapter |
| Director DSL | 已完成 | `src/film_engine/director_dsl.py`：YAML -> AST + schema validation |
| Shot Graph | 已完成 | `src/film_engine/shot_graph.py`：directed shot sequence、transition validation、cycle/self-loop rejection |
| Prompt Compiler | 已完成 | `src/film_engine/prompt_compiler.py`：Director DSL + character/scene/state/repair notes -> backend prompt |
| Character Registry/Bible | 已完成 | `src/film_engine/models.py`、`registry.py`、`samples/character_bible/` |
| Scene Registry/Bible | 已完成 | `src/film_engine/models.py`、`registry.py`、`samples/scene_bible/` |
| QA Engine | 已完成 | `src/film_engine/qa.py`：structural QA report and failure schema |
| Retry Engine | 已完成 | `src/film_engine/retry.py`：QA-driven repair/retry decision |
| Film State Engine | 已完成 | `src/film_engine/state.py`：character/scene state, timeline, continuity locks |

## 本轮验证记录（2026-05-08）

- `python3 -m compileall -q src/film_engine`：通过。
- `python3 -m compileall -q src/film_engine src/apps/comic_gen/api.py src/apps/comic_gen/pipeline.py src/config.py`：通过。
- `python3 -m pytest tests/test_film_engine_core.py -q -s`：通过，6 个测试。
- `python3 -m pytest tests/test_film_engine_core.py tests/test_media_refs.py tests/test_provider_media.py tests/test_provider_registry.py -q -s`：通过，32 个测试。
- `docker compose config --quiet`：通过。
- `python3 -m pytest tests -q -s`：宿主缺少 `dashscope`，8 个测试文件在 collection 阶段失败；改用容器验证。
- 容器同步本轮源码、samples、tests 后执行 `docker compose exec -T backend python -m pytest -q -s /app/tests`：通过，123 个测试，41 个 warning。
- 格式微调后重新执行 `docker compose exec -T backend python -m pytest -q -s /app/tests/test_film_engine_core.py`：通过，6 个测试。
- `git diff --check`：通过。
- `git ls-files -u`：无输出，无未解决冲突。

## 历史记录（2026-05-07，以下为上一轮记录，LumenX 主基座口径已被本轮修正）

## 本轮新增 Film Core

- `src/film_engine/models.py`：核心 Pydantic 模型与状态、QA、Retry 数据契约。
- `src/film_engine/director_dsl.py`：YAML Director DSL 解析与 AST 校验。
- `src/film_engine/shot_graph.py`：镜头有向图构建与 transition 校验。
- `src/film_engine/registry.py`：角色/场景实体注册表。
- `src/film_engine/prompt_compiler.py`：从结构化镜头、角色、场景和状态编译 backend prompt。
- `src/film_engine/runtime.py`：运行时 adapter/router 抽象和 deterministic dry-run adapter。
- `src/film_engine/qa.py`：结构化 QA 报告与失败 schema。
- `src/film_engine/retry.py`：基于 QA finding 的自动修复/重试决策。
- `src/film_engine/state.py`：Film State 连续性追踪。
- `src/film_engine/orchestrator.py`：按固定阶段串联最小闭环。
- `tests/test_film_engine_core.py`：覆盖 DSL、Graph、Registry、全链路 dry-run、失败后 retry。

## 本轮验证记录

- `python3 -m pytest tests/test_film_engine_core.py -q -s`：通过，4 个测试。
- `python3 -m pytest tests/test_film_engine_core.py tests/test_media_refs.py tests/test_provider_media.py tests/test_provider_registry.py -q -s`：通过，30 个测试。
- `python3 -m compileall -q src/film_engine`：通过。
- `python3 -m compileall -q src/film_engine src/config.py src/apps/comic_gen/api.py`：通过。
- `npm run test`：通过，6 个测试文件、101 个测试。
- `npm run build`：通过。Next export 模式提示 rewrites 不生效，属当前 Docker nginx 代理架构下的预期提醒。
- `docker compose config --quiet`：通过；Compose 现在使用可选 `.env.local`，无本地密钥时也能完成配置语法校验。
- `python3 -m pytest tests -q -s`：宿主缺少 `dashscope`，8 个既有测试文件在 collection 阶段失败；本轮新增核心测试不依赖 DashScope，已单独通过。

## 历史技术选择（已修正）

历史记录：上一轮曾把 LumenX Studio 写为主基座；该口径已被 2026-05-08 本轮修正为 Jellyfish 主平台基座、LumenX 兼容工作台。

推荐原因：

- MIT 许可，源码开放，适合二开。
- 工作流正好覆盖 AI 漫剧：资产提取、风格定调、资产生成、分镜图、分镜视频、合成。
- 与 DashScope/Qwen/Wanx 贴合，适合先用一个账号跑通低成本样片。
- 对 2-3 人团队而言，部署和维护负担低于 huobao、Toonflow、FastMovieAI 等更重平台。

上游参考：

- `external/` 本轮已清理，不再常驻上游 clone。
- 需要对比官方 LumenX 时，再临时 clone 到 ignored 目录，按需人工移植，不让外部项目配置参与主工程构建。

## 已知注意事项

- 当前主仓库只有初始提交，项目主体文件本轮会作为首次完整工程提交。
- `Doc/accounts`、`.env.local` 和旧 `.env` 必须保持忽略，任何输出都不要暴露密钥。
- `external/` 是临时忽略区，不提交、不构建；本轮已删除旧 clone 以避免双配置。
- 本轮将运行配置默认文件从 `.env` 调整为 `.env.local`，Docker Compose 使用可选 env_file；旧 `.env` 仍兼容读取。
- 当前启动建议使用 Docker：宿主是 WSL Ubuntu 22.04，已有 Docker，无需另装 Python 3.11 或 FFmpeg。
- 前端端口使用 `3014`，后端端口使用 `17177`，避免常用 `3000` 冲突。
- 前端 `package-lock.json` 与 `yarn.lock` 已把残留内部 registry 地址改为公开 npm registry，避免 Docker 构建拉包失败。

## 上一轮已完成验证记录

- `npm run test -- api-response nginx-proxy-config`：通过，2 个测试文件、4 个测试。
- `npm run test`：通过，6 个测试文件、101 个测试。
- `npm run build`：通过。Next export 模式提示 rewrites 不生效，属当前 Docker nginx 代理架构下的预期提醒。
- `docker compose up -d --build frontend`：通过，已重建并启动 `lumenx-backend` 和 `lumenx-frontend`。
- `curl http://localhost:3014/series`：HTTP 200，`Content-Type: application/json`，返回 `[]`。
- `curl http://localhost:3014/projects/`：HTTP 200，`Content-Type: application/json`，返回 `[]`。
- `curl http://localhost:3014/`：HTTP 200，页面包含 LumenX Studio 和空项目入口，无 `Application error` 标记。

上一轮验证记录：

- `docker compose config --quiet`：通过。
- `make up`：通过，已启动 `lumenx-backend` 和 `lumenx-frontend`。
- `curl http://localhost:17177/config/info`：HTTP 200。
- `curl http://localhost:3014/`：HTTP 200。
- 容器内完整后端测试：`117 passed, 41 warnings`。
- 宿主直接跑完整 pytest 会因未安装 `dashscope`/`oss2` 等运行依赖失败；以后优先在容器或虚拟环境中跑全量测试。

## 本轮新增文档

- `docs/ai-drama-product-review.md`：产品经理视角的开源库取舍、行业落地和改进建议。
- `docs/ai-drama-test-analysis.md`：测试工程师视角的用例矩阵、边界用例和发现问题。
- `docs/ai-drama-architecture-actions.md`：架构/工程视角的修复记录和后续优化方向。
- `docs/ai-manjv-report-comparison-2026.md`：对比 ChatGPT 研究报告与当前工程落地路线。

## 下一步建议

1. 执行 `make up`，确认容器能启动。
2. 创建 3 个 60-90 秒题材样片，优先验证角色一致性和镜头废片率。
3. 把抽卡结果记录成镜头级台账：prompt、模型、参考图、seed/参数、成本、人工评分、是否可用。
4. 若 LumenX 在非技术同事使用上阻力明显，再并行评估 LocalMiniDrama 作为桌面备选。
5. 后续如需同步 LumenX 上游 model catalog/onboarding，先临时 clone 到 ignored `external/`，再人工移植必要修改。
