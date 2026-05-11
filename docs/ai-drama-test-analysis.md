# AI 漫剧测试用例分析与问题清单

日期：2026-05-12

## 测试目标

验证当前 AIDrama Studio 是否能支持小团队从题材样片到单集成片的生产闭环，并优先发现会阻断“打开、创建、生成、选择、导出”的问题。最终主平台基座以 Jellyfish 为准，本测试文档覆盖当前可运行入口。

## 核心用例

| 编号 | 场景 | 用例 | 预期 |
|---|---|---|---|
| TC-001 | 启动 | Docker 启动后访问 `http://localhost:3014` | 首页可打开，无客户端异常 |
| TC-002 | 空数据 | 后端无项目、无系列 | 首页展示空状态，不崩溃 |
| TC-003 | API 代理 | 前端访问 `/projects/`、`/series`、`/config/env` | 均返回 JSON，不返回前端 HTML |
| TC-004 | 系列 | 创建系列、进入系列详情、创建单集 | 系列和单集列表实时刷新 |
| TC-005 | 独立项目 | 创建独立项目、进入项目工作台 | 项目可被选中，详情从后端刷新 |
| TC-006 | 剧本分析 | 粘贴短剧脚本并提取角色/场景/道具 | 生成结构化资产 |
| TC-007 | 风格定调 | 选择预设风格或 AI 推荐风格 | 后续资产与分镜复用统一风格提示 |
| TC-008 | 角色一致性 | 生成全身图、三视图、头像并锁定 | 后续分镜使用同一角色参考 |
| TC-009 | 分镜 | 从脚本生成分镜、编辑镜头角色和动作 | 分镜可增删改和重排 |
| TC-010 | 图生视频 | 对分镜图批量生成多个候选 | 候选可轮播、删除、选择 |
| TC-011 | 参考视频驱动 | 使用上一镜头末帧或角色参考视频生成下一镜头 | 连续镜头运动更平滑 |
| TC-012 | 配音 | 绑定角色声音并生成台词音频 | 音频可回放并用于合成 |
| TC-013 | 合成导出 | 全部分镜选择视频后合并 | 输出 mp4 可播放 |
| TC-014 | 密钥配置 | DashScope key 缺失或保存失败 | 前端给出明确提示 |
| TC-015 | 模型切换 | DashScope 模式和 vendor 模式切换 | 缺失对应 key 时不能误发请求 |
| TC-016 | 文件上传 | 上传角色参考图或分镜图 | 本地/OSS URL 可正常显示 |

## 边界用例

- 浏览器拿到 HTML、错误对象或空字符串时，集合接口不能直接 `.map`。
- localStorage 中存在旧版本项目结构时，首页不能崩溃。
- 后端 17177 可用但 nginx 少代理某个路径时，前端必须显示明确错误。
- 项目没有分镜时，视频生成入口应禁用或显示空状态。
- 分镜有视频任务但没有 `video_url` 时，候选选择器不能默认播放空地址。
- 文件名包含中文、空格、特殊字符时，上传和回显路径应稳定。
- OSS 未配置时，本地文件路径应仍可访问。
- 单镜头批量生成失败一部分时，成功候选不能被失败任务覆盖。
- 切换模型后，参数面板只能显示该模型支持的字段。
- 长剧本导入拆集时，单集标题、集数、角色继承关系不能丢失。

## 已发现问题

| 编号 | 严重级别 | 问题 | 影响 | 修复状态 |
|---|---|---|---|---|
| BUG-001 | P0 | Docker nginx 缺少 `/series` API 代理 | `3014` 首页请求 `/series` 返回前端 HTML，触发 `Q.map is not a function` 客户端异常 | 已修复 |
| BUG-002 | P1 | `projectStore.selectProject` 仍硬编码 `localhost:8000` | 选择项目时可能绕过当前 `API_URL`，Docker/自定义端口下刷新失败 | 已修复 |
| BUG-003 | P1 | `getProjects`、`listSeries` 等集合接口直接 `.map` 或直接返回 | API 代理异常时错误信息晦涩，页面容易白屏 | 已修复 |
| BUG-004 | P1 | 缺少 nginx API 前缀测试 | 后续新增端点容易再次漏代理 | 已补测试 |
| BUG-005 | P2 | 文档中的上游 clone 路径指向旧脚手架 | 后续多候选仓库管理不清晰 | 已更新 |
| BUG-006 | P1 | QA & Export 点击 `Start Render` 时，缺少已选择视频会显示泛化的 `failed to export project` | 制作人无法判断是 FFmpeg、素材缺失还是导出链路坏了 | 已修复：缺素材时返回 render package 与阻塞项 |

## 回归建议

- 每次改 Docker 或前端 API 前缀，都运行前端单测。
- 每次新增后端路由，都检查 nginx 是否需要同源代理。
- 每次升级上游参考或平台层，都先跑空数据首页、系列列表、项目列表这三个冒烟用例。

## 本轮新增自动化测试

| 文件 | 覆盖点 |
|---|---|
| `tests/test_film_production_pipeline.py` | Script -> Story Graph -> Director Planner -> Film Core -> Final Editing 全链路 dry-run |
| `tests/test_film_engine_core.py` | Director DSL、Shot Graph、Registry、Prompt Compiler、QA、Retry、Ledger |
| `tests/test_film_engine_batch.py` | 批量生产计划、优先级、失败隔离、批次汇总 |
| `tests/test_film_pipeline_api.py` | `/film/pipeline/run` dry-run API、道具/服装资产输入、未知资产错误 |

新增验收命令：

```bash
python3 -m pytest tests/test_film_engine_core.py tests/test_film_engine_batch.py tests/test_film_production_pipeline.py -q -s
python3 -m pytest tests/test_film_pipeline_api.py -q -s
python3 -m pytest tests/test_media_refs.py tests/test_provider_media.py -q -s
```

宿主环境如果缺少 DashScope SDK，provider 集成测试会在 collection 阶段失败；这种情况进入 Docker 后端容器补齐依赖再跑全量测试。

## 本次复核新增测试点

| 编号 | 场景 | 用例 | 预期 |
|---|---|---|---|
| TC-017 | Production Bible | 加载道具/服装资产圣经并运行 Film Core | prompt、film state、ledger、final edit 都保留道具/服装和锁定信息 |
| TC-018 | 剧本标签 | 剧本含 `[prop=...]`、`[costume=...]` | Story Graph 与 Director Program 继承资产引用，不丢失标签 |
| TC-019 | Film Core API | 调用 `/film/pipeline/run` dry-run | 返回 story graph、director program、shot graph、ledger summary、final edit |
| TC-020 | API 错误 | 剧本引用未注册道具 | 返回 400 与可读错误，不静默生成随机资产 |
| TC-021 | 九阶段可视化 | 进入项目工作台 `9. QA & Export` | 页面显示 Runtime、Director DSL、Shot Graph、Prompt Compiler、Character Registry、Scene Registry、QA、Retry、Film State 九阶段 |
| TC-022 | Film Engine payload | 当前项目含剧本、角色、场景、道具锁定 | 前端生成 dry-run payload，保留参考图、锁定 traits、continuity locks |
| TC-023 | Film Engine 空脚本 | 项目没有原始剧本但已有分镜 | 前端从分镜生成 deterministic script，并保留 `[prop=...]` 标签 |
| TC-024 | Film Engine 指标 | dry-run 成功返回 ledger、QA、final edit | 页面指标展示 beats、shots、accepted、failed、attempts、retries、QA、duration |
| TC-025 | Film Core API 浏览器访问 | GET `/film/pipeline/run` | 返回 endpoint 使用说明、固定九阶段和 sample payload，不再返回 405 |
| TC-026 | QA & Export 深链 | 访问 `#/project/{id}/step/export` 或 `#/series/{sid}/episode/{eid}/step/export` | 直接打开项目/单集工作台第 9 步 |
| TC-027 | 系列单集入口 | 在系列详情页选择某一集并点击 `QA & Export` | 跳转到该集工作台并展示 `Industrial QA & Export` 控制台 |
| TC-028 | 5 集系列蓝图 | 加载 `samples/series_production/vertical_suspense_5ep.yaml` | 解析出 5 集、角色、场景、道具、服装和 continuity locks |
| TC-029 | 系列蓝图批量编排 | 将 5 集蓝图编译为 `BatchProductionPlan` | 5 个 episode item 按优先级排序，保留每集 Story Graph、Director Program 和资产引用 |
| TC-030 | 系列蓝图 dry-run | 使用共享 Character/Scene/Production Registry 执行 5 集 dry-run | 5 集全部 accepted，15 个镜头都有 selected output，Film State 保留 continuity locks |
| TC-031 | 3 个样片模板 | 加载 `samples/pilot_samples/three_60_90s_pilots.yaml` | 每个样片目标时长在 60-90 秒，可构建 Story Graph |
| TC-032 | 模板目录 API | 调用 `GET /film/templates` | 返回 3 个样片、1 个 5 集蓝图和 summary 统计 |
| TC-033 | 首页模板中心 | 访问 `http://localhost:3014` | 首页展示“AI 漫剧模板中心”、样片卡片和“创建 5 集系列”按钮 |
| TC-034 | 样片模板实例化 | 调用 `POST /film/templates/pilots/{sample_id}/instantiate` | 创建独立草稿项目，并返回 `#/project/{id}/step/export` |
| TC-035 | 系列模板实例化 | 调用 `POST /film/templates/series/{blueprint_id}/instantiate` | 创建 1 个系列、5 个单集草稿和共享角色/场景/道具资产 |
| TC-036 | 工作流状态 API | 调用 `GET /projects/{projectId}/workflow` | 返回 Novel、Asset、Storyboard、Image、Video、Voice、Composition、QA/Retry、Export 9 个阶段状态 |
| TC-037 | 模型建议目录 | 调用 `GET /film/runtime/recommendations` | 返回百炼优先的图片、视频、语音模型建议和未来适配器说明 |
| TC-038 | 重生成意图持久化 | 调用 `POST /projects/{projectId}/workflow/stages/video_runtime/regenerate` | 返回 queued/accepted 事件并写入 workflow edit history |
| TC-039 | Start Render 缺视频兜底 | 项目没有 selected video 时点击 `Start Render` | 返回 `mode=render_package`、可下载 JSON、warnings 和 action_required，不再泛化失败 |
| TC-040 | Start Render 错误信息 | 后端返回 400 detail | 前端展示具体 detail，而不是固定 `Failed to export project` |
| TC-041 | 工作流 UI 可视化 | 进入第 9 步 QA & Export | 页面显示 CineForge Workflow 阶段、进度、阻塞项与模型建议 |

## 本次九阶段可视化新增自动化测试

| 文件 | 覆盖点 |
|---|---|
| `frontend/src/__tests__/film-engine.test.ts` | 前端 Film Core payload 构造、空脚本分镜回退、九阶段状态评估、控制台指标汇总 |
| `frontend/src/__tests__/film-templates.test.ts` | 模板目录统计、样片排序、5 集蓝图资产统计 |
| `frontend/src/components/modules/__tests__/TemplateLibraryPanel.spec.tsx` | 首页模板中心渲染、样片创建后跳转 QA 路由 |
| `frontend/src/__tests__/workspace-routing.test.ts` | 项目/系列单集工作台 hash 解析、QA & Export 深链构造 |
| `tests/test_film_pipeline_api.py` | `/film/pipeline/run` 响应包含 `film_run.shot_graph`；模板目录和样片/系列实例化 API |
| `tests/test_series_production_blueprint.py` | D7 样片和 5 集系列蓝图加载、编译、批量 dry-run、重复集号拒绝、首页模板 catalog loader |
| `tests/test_film_workflow.py` | 工作流状态评估、视频就绪判断、edit history 保留、render package manifest、百炼优先模型目录 |
| `frontend/src/__tests__/workflow-api.test.ts` | `exportProject` 支持 render package 响应、后端 detail 透传、workflow state 加载 |

新增验收命令：

```bash
cd frontend && npm run test
cd frontend && npm run test:ui
cd frontend && npx tsc --noEmit --pretty false
python3 -m pytest tests/test_film_pipeline_api.py tests/test_film_production_pipeline.py -q -s
python3 -m pytest tests/test_series_production_blueprint.py -q -s
python3 -m pytest tests/test_film_workflow.py -q -s
```
