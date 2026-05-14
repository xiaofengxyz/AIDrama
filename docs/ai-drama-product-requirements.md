# AI 漫剧产品需求说明书

日期：2026-05-15

## 0. 本轮重启恢复目标

电脑重启后，本轮必须把 AIDrama Studio 恢复为可直接启动、可验证、可继续生产的 AI 漫剧工作台。产品侧新增三条硬性约束：

- 服务端口必须独立且避开常见端口，前端固定使用 `39211`，后端固定使用 `48217`。
- 文本大模型默认走阿里百炼 DashScope，使用 `.env` / `.env.local` 内已经配置的 `DASHSCOPE_API_KEY`，不在代码、文档或日志中暴露密钥。
- 启动链路必须能在本地脚本、`npm run dev`、Docker 和桌面打包入口之间保持一致，减少重启后的人工排障。

本轮验收口径：

- `npm run dev` 会用 `39211/48217` 启动前后端。
- `make up` / Docker 会用 `39211/48217` 映射服务。
- 前端 API 解析不会再绑定 `3000/3001/17177` 这组历史端口。
- `/config/info` 和 `/film/runtime/recommendations` 能证明开发配置存在且模型策略为百炼优先。

## 1. 产品定位

AIDrama Studio 是面向小团队的 AI 漫剧工业化生产工作台。它不以“一句话直接出商业成片”为承诺，而是把一句故事点子拆成可检查、可重试、可复用的生产包：小说计划、每集脚本、分镜、角色、场景、道具、服装、特效、镜头素材、QA 与导出。

最终平台口径仍以 Jellyfish-oriented Film Engine 为准；当前仓库承担可运行试制、功能验证和迁移期回归。

## 2. 用户与核心问题

目标用户：

- 制作人：负责题材选择、系列规划、成本控制和交付验收。
- 导演/分镜师：负责镜头节奏、画面调度、角色表演和连续性。
- 资产师/抽卡师：负责角色、场景、道具、服装、参考图、参考视频和候选筛选。
- 测试/交付人员：负责回归、问题定位、QA 报告和产物打包。

核心问题：

- 从一个点子到多集项目的入口不清楚，制作人需要先学 API 才能开始。
- 模板中心和工作区边界不清，新用户不知道“先套模板”还是“先建项目”。
- 角色参考图、道具图、参考视频需要人工去网络查找和上传，链路割裂。
- 每集脚本、分镜、角色描述、道具、服装、特效没有作为显式生产包交接。
- 单一暗色页面不适合长时间生产和不同团队品牌偏好。

## 3. 产品目标

本轮目标：

- 在首页提供“一句话生成多集 AI 漫剧”入口，默认创建可编辑系列。
- 给模板中心、制片入口、我的工作区增加清晰流程说明。
- 支持项目级和资产级网络图片/视频采集，并能直接挂到分镜或资产。
- Auto Drama 返回并落盘 `episode_packages`，包含每集生产所需的脚本、分镜、角色、场景、道具、服装、特效和连续性锁。
- 增加可切换页面主题，主题状态在浏览器本地持久化。
- 补充自动化测试和测试用例文档，保证重启后可验证。

非目标：

- 不承诺一次生成最终商业成片。
- 不引入新的重型依赖或外部平台锁定。
- 不把网络素材视为可直接商用素材；它们是参考素材，需要人工确认版权和适配性。

## 4. 端到端流程

推荐主流程：

1. 制作人在首页选择入口。
2. 如果已有成熟结构，使用“AI 漫剧模板中心”创建样片或 5 集系列。
3. 如果只有故事点子，使用“一句话生成多集 AI 漫剧”生成系列草稿。
4. 系统生成小说计划和每集生产包，并写入工作区。
5. 进入某一集，在 Assets 补角色、场景、道具、服装参考。
6. 需要参考素材时，点击资产卡片的网络采集入口，直接采集图片/视频。
7. 进入 Storyboard 检查和补分镜图。
8. 进入 Motion 生成或采集参考视频，再生成候选。
9. 进入 QA & Export 检查工作流状态，缺素材时导出 render package，素材齐全时合成视频。

## 5. 功能需求

### FR-001 一句话生成多集 AI 漫剧

入口：工作区首页顶部。

用户输入：

- 系列标题。
- 一句话故事梗概。
- 集数选项：3、5、8。

系统行为：

- 调用 `POST /film/auto-drama/run`。
- 默认 `backend=dry_run`，避免打开页面就消耗模型预算。
- 默认 `persist_project=true`、`persist_mode=series`。
- 成功后创建一个系列和 N 个单集草稿，并跳转到系列详情页。

验收：

- 首页可见入口。
- API payload 包含 `persist_mode=series`。
- 返回结果包含 `novel_plan`、`episode_packages`、`series`、`episodes`、`next_hash`。

### FR-002 每集生产包

数据契约：`episode_packages`。

每集必须包含：

- `script_text`：可继续编辑的单集脚本。
- `storyboard_frames`：默认三段式分镜，覆盖 hook、development、cliffhanger。
- `characters`：角色描述和连续性锁。
- `scenes`：场景描述和连续性锁。
- `props`：剧情道具。
- `costumes`：服装资产。
- `special_effects`：特效资产。
- `continuity_locks`：角色、场景、道具、服装、特效锁定信息。

验收：

- Auto Drama dry-run 返回每集生产包。
- 系列落盘后，每个单集项目带 frames、characters、scenes、props。
- 服装和特效以可编辑资产形式进入 Studio props 列表，避免 UI 当前模型缺少专门 costume/fx 列表导致信息丢失。

### FR-003 网络素材采集

入口：

- Storyboard/Motion 项目级素材采集。
- Assets 资产卡片级素材采集。

系统行为：

- 项目级采集使用 `POST /projects/{id}/web_media/collect`。
- 资产级采集使用 `POST /projects/{id}/assets/{type}/{assetId}/web_media/collect`。
- 图片进入资产 image variants 或分镜图槽位。
- 视频进入角色 motion reference、场景/道具 video assets 或项目参考视频列表。

验收：

- 支持 `image`、`video`、`both`。
- 网络失败时返回可理解错误或 fallback，不破坏项目数据。
- 资产采集成功后刷新当前项目。

### FR-004 模板中心与工作区流程说明

首页必须说明：

- 模板中心：从验证过的样片或 5 集蓝图开始，适合复用结构。
- 一句话制片：从故事点生成小说计划、单集脚本、分镜和资产包。
- 我的工作区：管理正在制作的系列和项目，继续补资产、视频、配音和导出。

验收：

- 首页展示三条流程路径。
- 文档与用户手册解释三者关系。

### FR-005 页面主题切换

入口：首页右上角主题切换器。

主题：

- `Noir`：默认黑色制片室。
- `Dailies`：偏绿色审片台。
- `Ember`：偏暖色剪辑台。

系统行为：

- 通过 CSS variables 改变背景、主色、强调色。
- Three.js 背景画布读取主题色。
- 主题写入 `localStorage`，下次打开继续生效。

验收：

- 切换主题后按钮、背景和画布颜色改变。
- 非法持久化主题回退默认主题。

## 6. 信息架构

首页从上到下：

- 工作区流程地图。
- 一句话生成多集 AI 漫剧。
- AI 漫剧模板中心。
- 我的工作区列表。

项目工作台：

- Script：剧本与结构。
- Assets：角色、场景、道具、服装/特效占位资产与网络采集入口。
- Storyboard：分镜图与分镜素材。
- Motion：视频候选、参考视频和 R2V/I2V 链路。
- QA & Export：工作流状态、自动/人工开关、导出兜底。

## 7. 数据与接口

关键接口：

- `GET /film/auto-drama/run`：返回使用说明。
- `POST /film/auto-drama/run`：执行一句话到多集生产包。
- `GET /film/templates`：返回样片和系列模板目录。
- `POST /projects/{id}/web_media/collect`：项目级网络素材采集。
- `POST /projects/{id}/assets/{type}/{assetId}/web_media/collect`：资产级网络素材采集。
- `GET /projects/{id}/workflow`：项目工作流状态。
- `GET /film/workflow/prompts`：自动/人工 prompt 开关。

关键数据：

- `AutoDramaRun`：端到端 dry-run 结果。
- `EpisodeProductionPackage`：单集生产包。
- `ExtractedProductionAsset`：角色、场景、道具、服装、特效资产。
- `ExtractedStoryboardFrame`：可编辑分镜帧。

## 8. 非功能需求

- 稳定性：dry-run 默认不依赖外部模型，缺 Key 时仍可验证主流程。
- 可扩展：Film Core 与具体 UI/runtime 解耦，后续可接 Jellyfish、队列和多模型路由。
- 可恢复：任务进度索引和 workflow state 支持重启后继续。
- 可测试：后端 pytest、前端 vitest、TypeScript 检查和 Docker 冒烟都要可运行。
- 可读性：新增函数、类、复杂流程保留注释，数据模型保持显式字段。

## 9. 验收矩阵

| 需求 | 自动化验证 | 人工验证 |
|---|---|---|
| 一句话生成系列 | `OneSentenceDramaPanel.spec.tsx`、`test_auto_drama_pipeline.py`、`test_film_pipeline_api.py` | 首页点击生成系列并跳转 |
| 每集生产包 | `test_episode_production_extraction.py` | 打开系列单集，检查脚本、分镜和资产 |
| 网络素材采集 | `test_web_media_collector.py`、`workflow-api.test.ts` | 在 Assets 卡片点击采集参考素材 |
| 流程地图 | 前端组件回归 | 首页可读三条路径 |
| 主题切换 | `theme-presets.test.ts`、TypeScript | 切换 Noir/Dailies/Ember |
| 导出兜底 | `test_film_workflow.py`、`workflow-api.test.ts` | 缺视频时导出 render package |

## 10. 风险与后续

- 网络素材版权需要在 UI 增加更明确的商用风险提示。
- 服装和特效当前借用 props 列表承载，后续应升级为系列级专门资产类型。
- 一句话生成目前是 deterministic dry-run 和结构化草稿，商业化成片仍需要图片、视频、配音和人工 QA。
- 后续应增加镜头级成本、生成耗时、失败原因和人工评分看板。
