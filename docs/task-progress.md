# 任务进度索引

日期：2026-05-07

这个文件用于跨会话交接。后续 AI 或人工进入仓库时，先读本文件，再读 `docs/README.md` 和 `agent.md`。

## 本轮任务状态

| 任务 | 状态 | 备注 |
|---|---|---|
| 先做计划再执行 | 已完成 | 本轮已建立计划，按单 agent 连续推进，不启动子 agent |
| 查看 AGENTS/agent 指南 | 已完成 | 已读取 `AGENTS.md`、`agent.md` 和文档中心，确认工业 AI Film Engine 原则 |
| 确认阶段边界 | 已完成 | 以 Starter Kit 固定顺序推进：Runtime、Director DSL、Shot Graph、Prompt Compiler、Character Registry、Scene Registry、QA Engine、Retry Engine、Film State Engine |
| 对比分析 2026 开源研究报告 | 已完成 | 新增 `docs/ai-manjv-report-comparison-2026.md`，结论是保留 LumenX，吸收 huobao/Toonflow/Jellyfish 的方法 |
| 清理根目录/external 配置混乱 | 已完成 | 已删除本地 ignored `external/` clone，文档改为根目录唯一可运行配置源 |
| 落地 Film Core 最小闭环 | 已完成 | 新增 `src/film_engine/`，覆盖 Runtime、Director DSL、Shot Graph、Prompt Compiler、Registry、QA、Retry、Film State |
| 验证、工作区清理、提交、push | 已完成 | 测试、构建、Compose 校验、换行归一化、工作区清理、提交和 push 已在本轮收束 |

## 本轮执行计划

1. 固化任务索引，确保每个节点都有状态记录。
2. 对比 ChatGPT 研究报告、现有 `open-source-comparison` 与 Starter Kit，明确继续用 LumenX 还是切换/吸收其它项目。
3. 清理配置混乱：根目录保留主工程运行配置，`external/` 仅保留忽略的只读参考源或直接移除陈旧 clone，不让外部项目配置参与构建。
4. 按固定开发顺序实现 Film Core 最小闭环：Runtime 抽象、Director DSL、Shot Graph、Prompt Compiler、Character/Scene Registry、QA、Retry、Film State。
5. 补 Python 测试和样例读取验证，确认核心阶段可以串起来。
6. 归一化换行与工作区状态，解决冲突，提交并 push 必要修改。

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

## 当前技术选择

主基座：LumenX Studio

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
