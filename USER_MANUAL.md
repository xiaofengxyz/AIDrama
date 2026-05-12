# AIDrama Studio 用户操作手册

日期：2026-05-12

本手册面向 2-3 人 AI 漫剧小团队，目标是从零配置环境，到做出一部多集 AI 漫剧的可复盘生产流程。

## 0. 先确认当前界面

当前可运行界面是 `AIDrama Studio`，不是 LumenX 页面。

- 前端入口：`frontend/`，Next.js 工作台。
- 后端入口：`src/apps/comic_gen/api.py`，FastAPI。
- Film Core：`src/film_engine/`，承载 Story Graph、Director Planner、Prompt Compiler、Runtime Adapter、QA、Retry、Ledger、Batch、Final Editing。
- LumenX 只作为历史开源项目对比材料出现在研究文档里，不是当前 UI 基座，也没有运行面源码引用。

## 1. 功能完成度

| 能力 | 状态 | 使用入口 |
|---|---|---|
| 剧本到 Story Graph | 已完成 | UI 剧本步骤、`FilmProductionPipeline` |
| Director Planner / Director DSL | 已完成 | Film Core、样例 YAML |
| Shot Graph | 已完成 | Film Core、第 9 步 QA & Export |
| Prompt Compiler | 已完成 | Film Core dry-run 与真实生成链路提示词 |
| Character / Scene / Production Bible | 已完成 | UI 资产步骤、样例 bible、系列蓝图 |
| QA Engine | 已完成 | 第 9 步 QA & Export、Film Core API |
| Retry Engine | 已完成 | Film Core retry policy |
| Generation Ledger | 已完成 | 第 9 步、Film Core run metadata |
| Batch Production | 已完成 | `BatchProductionRunner`、系列蓝图 |
| 5 集题材验证模板 | 已完成 | 首页“AI 漫剧模板中心”、`samples/series_production/vertical_suspense_5ep.yaml` |
| 3 个 60-90 秒样片模板 | 已完成 | 首页“AI 漫剧模板中心”、`samples/pilot_samples/three_60_90s_pilots.yaml` |
| 真实视频生成 | 已具备应用层入口 | UI 视频生成步骤，依赖供应商 Key 和额度 |
| Film Core 多供应商真实 Runtime | 抽象已完成，适配器按供应商继续扩展 | `RuntimeRouter` |
| CineForge 工作流状态 | 已完成 | `GET /projects/{id}/workflow`、第 9 步 QA & Export |
| Start Render 兜底导出 | 已完成 | 有选中视频时导出 mp4；缺视频时导出 render package |
| 统一模型适配配置层 | 已完成 | `/config/env`、Settings、`src/models/runtime_config.py` |
| Codex Workflow 自动/人工开关 | 已完成 | `docs/Codex_Workflow_Prompts/*.md`、`GET /film/workflow/prompts` |
| 一段文字到小说再到漫剧 dry-run | 已完成 | `POST /film/auto-drama/run`，可自动创建 Studio 草稿项目 |
| 分镜生成失败兜底 | 已完成 | `4. Storyboard` 的 `生成分镜`，LLM JSON 异常时自动生成可编辑分镜 |
| 无素材时自动采集图片/视频 | 已完成 | `4. Storyboard` 的 `采集图片`、`5. Motion` 的 `采集图片` / `采集视频` |
| workflow_switch 页面可见 | 已完成 | `9. QA & Export` 的 `Workflow Switches` 面板，按钮叫 `Refresh Switches` |

结论：文档要求的工业级“可测试闭环”已经完成，且工作流状态、可编辑/可重生成意图、QA/Retry、导出兜底、模型配置隔离、工作流自动/人工停顿和文字到漫剧 dry-run 已经具备。真实出片仍需要配置模型 Key，并在 UI 的图片、视频、配音、合成步骤里实际调用模型。

## 2. 本机准备

推荐环境：

- WSL Ubuntu 22.04 或 Linux/macOS。
- Docker Desktop / Docker Engine。
- Node.js 和 Python 可选；用 Docker 跑时不强依赖宿主完整环境。

先进入项目根目录：

```bash
cd /mnt/d/workplace/AIDrama
```

如果你已经把密钥写在 `Doc/accounts`，生成本地环境文件：

```bash
bash scripts/bootstrap_env.sh
```

不要提交这些文件：

- `Doc/accounts`
- `.env.local`
- `.env`
- `output/`
- `external/`

## 3. 配置模型和存储

先回答制作侧最关心的问题：补资产、分镜、视频、配音和合成都需要不同运行时。

| 环节 | 是否需要模型 | 当前建议 |
|---|---|---|
| 剧本/拆集/对白润色 | 需要文本模型 | 先用百炼 `qwen-plus` 或同级模型 |
| 角色/场景/道具/服装资产 | 需要图片模型 | 当前可用 `wan2.6-image`；后续优先补 `wan2.7-image-pro` / `wan2.7-image` 适配 |
| 分镜关键帧/图像编辑 | 需要图片或图像编辑模型 | 当前用 `wan2.6-image` / I2I 链路，先把关键帧锁住 |
| 图生视频/参考生视频 | 需要视频模型 | 当前可用 `wan2.6-i2v` / `wan2.6-r2v`；后续补 `wan2.7-i2v-2026-04-25`、`wan2.7-r2v` |
| 配音 | 需要 TTS 模型 | 当前用 CosyVoice，日常用 `cosyvoice-v3-flash`，终版可用 `cosyvoice-v3-plus` / `cosyvoice-v3.5-plus` |
| 合成导出 | 不需要生成模型 | 本地 FFmpeg 合成；缺素材时导出 render package |

最低成本建议：

- 编剧/分析：先用 `qwen-plus`，不要在大纲阶段消耗视频预算。
- 图片：先用百炼万相把角色、服装、场景、道具定稿，关键资产再升高质量。
- 视频：先用 `wan2.6-i2v` 或 `wan2.6-r2v` 跑通当前代码链路；后续把 `wan2.7` 作为优先升级目标。
- 配音：先用 `cosyvoice-v3-flash` 批量试音，最终角色再做精品音色或复刻。
- 存储：本地优先；多人协作或云端备份时再开 OSS。

常用环境变量：

| 环境变量 | 说明 | 示例 |
|---|---|---|
| `DASHSCOPE_API_KEY` | DashScope API Key | `sk-xxx` |
| `DASHSCOPE_BASE_URL` | DashScope provider base url，可选 | `https://dashscope.aliyuncs.com` |
| `DASHSCOPE_COMPATIBLE_BASE_URL` | DashScope OpenAI-compatible base url，可选 | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `LLM_PROVIDER` | 文本模型供应商 | `dashscope` 或 `openai` |
| `OPENAI_API_KEY` | OpenAI-compatible 文本模型 Key，可接 OpenAI、DeepSeek、Ollama 代理等 | `sk-xxx` |
| `OPENAI_BASE_URL` | OpenAI-compatible base url | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | OpenAI-compatible 模型名 | `gpt-4o` / `deepseek-chat` |
| `KLING_ACCESS_KEY` / `KLING_SECRET_KEY` | Kling vendor-direct 凭据 | `xxx` |
| `VIDU_API_KEY` | Vidu vendor-direct 凭据 | `xxx` |
| `ARK_API_KEY` / `ARK_BASE_URL` | Volcano Ark / Seedance 凭据与 base url | `https://ark.cn-beijing.volces.com/api/v3` |
| `PIXVERSE_API_KEY` / `PIXVERSE_BASE_URL` | PixVerse 预留适配器凭据与 base url | `https://api.pixverse.ai` |
| `OSS_BUCKET_NAME` | OSS Bucket，可选 | `my-aidrama-bucket` |
| `OSS_BASE_PATH` | OSS 路径前缀，可选 | `aidrama` |

模型调用现在统一经过适配配置层：

- 适配器优先读取单个模型 config 里的 `api_key`、`base_url` 或 `baseurl`。
- 如果模型 config 没写，再读取 `{PROVIDER}_API_KEY` 和 `{PROVIDER}_BASE_URL` 环境变量。
- 如果 base url 仍为空，再使用内置默认值。
- 诊断接口和日志只暴露“是否配置”和 base url，不应该打印真实 API Key。

在 UI 中配置：

1. 打开首页右上角环境配置弹窗，或进入 Settings。
2. 填 `DashScope API Key`。
3. 如需 OpenAI-compatible 文本模型，填 `LLM Provider=openai`、`OpenAI-compatible API Key`、模型名，并在 Advanced API Endpoints 填 `OpenAI-compatible Base URL`。
4. 如需 Kling/Vidu vendor-direct，先把 Provider Mode 切到 `Vendor Direct`，再填对应 Key。
5. 如需 Ark/Seedance 或 PixVerse，填对应 API Key 和 Advanced Base URL。

第 9 步还会读取模型建议目录：

```bash
curl -sS http://localhost:17177/film/runtime/recommendations
```

这个接口不会消耗模型额度，它只告诉你每个阶段推荐使用哪个模型、需要哪些环境变量，以及哪些适配器是“当前可用”还是“后续升级”。

工作流 prompt 开关目录：

```bash
curl -sS http://localhost:17177/film/workflow/prompts
```

每个 `docs/Codex_Workflow_Prompts/*.md` 文件顶部都有 `workflow_switch`：

- `auto_advance: true`：该阶段完成后自动进入下一阶段。
- `auto_advance: false`：该阶段完成后停止。
- `requires_human_review: true`：即使阶段完成，也等待人工确认。
- `stop_after_stage: true`：显式要求停在该阶段后。

默认 00-09 全部是自动模式，所以一键 dry-run 会完整走到 Final Integration。制作人要人工审某一阶段时，改对应 prompt 文件开关，或在 API 请求中传 `auto_overrides`。

页面上也能看到这个开关：进入项目工作台左侧 `9. QA & Export`，页面中部有 `Workflow Switches` 面板。右上角按钮叫 `Refresh Switches`，点击后重新读取 `/film/workflow/prompts`。面板里每个 00-09 模块会显示 `auto` 或 `manual`，并显示 `auto_advance=true/false`、manual gates 数量和 first waiting stage。

Web 素材采集可选环境变量：

| 环境变量 | 说明 |
|---|---|
| `AIDRAMA_WEB_IMAGE_URLS` | 逗号分隔的图片 URL 模板，支持 `{query}`、`{raw_query}`、`{index}`、`{seed}` |
| `AIDRAMA_WEB_VIDEO_URLS` | 逗号分隔的视频 URL 模板，支持同上占位符 |

不配置时，系统使用公开示例源采集少量图片/视频并下载到 `output/web_media/`。这些素材适合做试制、占位和连通性测试；正式商用发布前要替换为自有、授权或模型生成素材。

配置完成后启动：

```bash
make up
```

访问：

- Studio：`http://localhost:3014`
- Backend API：`http://localhost:17177/docs`
- Film Core dry-run API：`http://localhost:17177/film/pipeline/run`
- 模板目录 API：`http://localhost:17177/film/templates`

健康检查：

```bash
docker compose ps
curl -I http://localhost:3014/
curl -sS http://localhost:17177/config/info
```

## 4. UI 从零做一部多集 AI 漫剧

### 4.0A 一键从一句话生成 dry-run 漫剧包

如果你只有一个故事点子，还没有小说和分镜，可以先用 Auto Drama API 生成可编辑草稿：

```bash
curl -sS -X POST http://localhost:17177/film/auto-drama/run \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "夜半信号",
    "seed_text": "女调查员接到一通来自十年前死者的电话，电话里的人知道她下一步会去哪里。",
    "target_chapters": 5,
    "backend": "dry_run",
    "persist_project": true
  }'
```

返回内容包含：

- `novel_plan`：世界观、关系图、章节大纲、每集悬念。
- `screenplay_text`：由小说计划编译出的可拍摄剧本文本。
- `story_graph` / `director_program` / `film_run` / `final_edit`：Film Core dry-run 结果。
- `project`：写入 Studio 的草稿项目。
- `next_hash`：例如 `#/project/{projectId}/step/export`，可直接跳到第 9 步验收。

如果要在小说阶段停下来让制作人审大纲，可以传：

```json
{
  "auto_overrides": {
    "02_stage1_novel_engine": false
  }
}
```

这时接口会返回 `status=waiting_for_user`、`waiting_for_stage=stage1_novel_engine`，并保留已生成的 `novel_plan`，不会继续生成后面的 Film Core 产物。

### 4.0 先看首页模板中心

打开 `http://localhost:3014` 后，首页顶部会出现“AI 漫剧模板中心”。

这里能直接看到：

- 3 个 60-90 秒样片模板：Night Signal、Contract Bride Counterattack、Midnight Delivery。
- 1 个 5 集系列验证模板：Night Signal Season 1。
- 每个样片的题材、目标时长、钩子、生产风险和成功指标。
- 5 集蓝图的集数、角色数、场景数、道具数、服装数和单集目标时长。

按钮含义：

- “创建样片”：把单个 60-90 秒样片复制成独立项目，并跳到该项目第 9 步 `QA & Export`。
- “创建 5 集系列”：把 5 集蓝图复制成一个系列，自动创建 5 个单集草稿，并写入共享角色、场景、道具资产。
- “刷新模板”：重新读取后端 `/film/templates`，用于确认 `samples/` 文件和 UI 是否一致。

这一步不消耗真实模型额度。模板项目会以草稿形式进入工作台，后续是否分析剧本、生成图像、生成视频、配音和合成由你手动控制。

### 4.1 新建系列

打开 `http://localhost:3014`。

1. 点击“新建系列”。
2. 输入系列名，例如“夜半信号”。
3. 写一句描述，例如“女调查员接到死者手机来电，五集揭开身份谜案”。
4. 进入系列详情页。

系列层保存的是长期资产：角色、场景、道具、服装、世界观和禁用设定。单集应该尽量引用系列资产，减少每集重新生成导致的人设漂移。

### 4.2 创建 5 集结构

在系列详情页逐集创建：

| 集数 | 目标 | 建议时长 |
|---|---|---|
| EP01 | 3 秒钩子 + 核心悬念 | 60-90 秒 |
| EP02 | 第一个反转和关键道具 | 60-90 秒 |
| EP03 | 追逐/冲突升级 | 60-90 秒 |
| EP04 | 身份或规则揭示 | 60-90 秒 |
| EP05 | 小闭环结尾 + 下一季钩子 | 60-90 秒 |

每集先写 3-6 个短段落。一个段落会更容易转成一个 Story Beat 和一个镜头。复杂动作拆成多个 3-5 秒镜头。

### 4.3 导入或粘贴剧本

进入某一集工作台后：

1. 在剧本步骤粘贴文本。
2. 使用清晰的场景头，例如 `INT. NIGHT CORRIDOR` 或 `EXT. ROOFTOP DAWN`。
3. 用对白行稳定角色识别，例如 `Maya: ...`。
4. 关键资产用标签标记：

```text
Maya: The phone rang again. [character=maya] [prop=evidence_phone] [costume=blue_raincoat]
```

标签的作用：

- `[character=maya]`：强制镜头引用同一角色。
- `[prop=evidence_phone]`：锁定道具进入 Prompt、State、Ledger、Final Edit。
- `[costume=blue_raincoat]`：锁定服装，减少换衣漂移。

### 4.4 建立角色、场景、道具、服装资产

按这个顺序做：

1. 角色：全身图、头像、三视图、表情参考。
2. 服装：每个角色的可出镜服装包。
3. 场景：主场景参考图、灯光、时间、天气、色调。
4. 道具：特征细节必须固定，例如手机裂纹、徽章颜色。

每个资产都写“不可改变项”：

- 角色：脸型、发型、疤痕、瞳色、身高比例。
- 服装：颜色、材质、轮廓、标志性配件。
- 场景：灯光方向、天气、主色、空间结构。
- 道具：形状、颜色、破损位置、出现方式。

### 4.5 生成分镜

进入分镜步骤：

1. 点击 `生成分镜`，系统根据剧本生成分镜。
2. 人工检查每个镜头的角色、动作、情绪、构图和运镜。
3. 把大动作拆小：跑、转身、开门、回头、拔枪不要塞进一个长镜头。
4. 每个镜头控制在 3-5 秒，重要反应镜头可以 4-6 秒。

如果 `生成分镜` 遇到模型 JSON 格式异常、Key 临时不可用或剧本还没有实体抽取，系统会自动生成一组可编辑分镜，不再直接中断。你仍然要人工复核这些 fallback 分镜，把角色、场景、道具和动作补准。

如果分镜已经有了但缺图片，点击顶部 `采集图片`。它会从网上采集几张图片，下载到 `output/web_media/images/`，并自动填充没有图片的分镜。正式出片前建议把这些网络素材替换为自有参考图或真实模型生成图。

行业痛点“抽卡很辛苦”的根源是变量太多。这里的原则是每次只改变一个变量：模型、seed、参考图、运动提示或时长，不要全部一起改。

### 4.6 生成图片和视频候选

低成本策略：

1. 先生成低成本分镜图。
2. 图像稳定后再图生视频。
3. 每个镜头先抽 2-3 个候选。
4. 关键镜头再抽 4-6 个候选。
5. 每个候选记录模型、prompt、参考图、seed、成本、耗时和人工评分。

不要一开始就追求全片高规格。先把角色和镜头连续性跑顺，再把少数关键镜头升级模型。

进入 `5. Motion` 后：

1. `首帧驱动 (I2V)`：优先从 Storyboard 选择已有分镜图；没有图时点击 `采集图片`，系统会自动补几张网络首帧图片。
2. 输入提示词后点击 `AI 润色`。如果后端文本模型失败，页面会给出本地兜底的双语运动提示词，不会只显示失败。
3. 点击 `应用` 把英文提示词写回生成输入。
4. 点击 `加入生成队列 (Ctrl+Enter)`。如果图片还在上传，页面会提示等待上传完成；如果后端返回错误，会显示具体 detail。
5. `角色驱动 (R2V)`：如果没有 Motion Reference，点击 `采集视频` 自动采集几个参考视频，先填入角色槽位做连通性验证。

### 4.7 QA & Export 第 9 步

进入工作台第 9 步：

- 独立项目：`#/project/{projectId}/step/export`
- 系列单集：`#/series/{seriesId}/episode/{episodeId}/step/export`

页面会调用 `/film/pipeline/run` dry-run，把当前项目编译为 Film Core 九阶段结果：

1. Runtime
2. Director DSL
3. Shot Graph
4. Prompt Compiler
5. Character Registry
6. Scene Registry
7. QA Engine
8. Retry Engine
9. Film State Engine

你要重点看：

- Shot Graph 是否完整。
- QA 分数是否低于阈值。
- Retry 次数是否异常。
- Ledger 是否记录每个镜头的 prompt fingerprint 和 selected output。
- Final Edit 是否存在 unresolved shots。

第 9 步默认 dry-run，不消耗视频模型额度，适合在真实生成前做结构验收。

页面还会读取当前项目的 CineForge 工作流状态：

```bash
curl -sS http://localhost:17177/projects/{projectId}/workflow
```

工作流会显示 9 个生产阶段：Novel Engine、Asset Pipeline、Storyboard、Image Runtime、Video Runtime、Voice Runtime、Composition、QA & Retry、Export。每个阶段都有状态、阻塞项、下一步动作和模型建议。

### 4.8 合成导出

当每个镜头都有选中的视频候选：

1. 进入合成/导出步骤。
2. 检查镜头顺序、转场、配音和字幕。
3. 导出 mp4。
4. 保存镜头台账和 QA 结果。

如果 Final Edit 报 `unresolved_shots`，说明还有镜头没有 selected output，要回到视频候选选择步骤补齐。

现在第 9 步 `Start Render` 有两个结果：

- `mode=video`：所有分镜都有选中视频，后端用 FFmpeg 合成 mp4，页面显示 Download。
- `mode=render_package`：视频或音频还不完整，后端不再报 `failed to export project`，而是导出一个 JSON render package。里面包含 workflow state、阻塞项、模型建议、每个 frame 的图片/视频/音频引用，方便继续生产或交接给剪辑。

所以，缺素材时点击 `Start Render` 也能得到可恢复产物；真正成片仍需要先补齐每个镜头的 selected video。

### 4.9 推荐最快路径：从模板到 5 集样片

1. 打开 `http://localhost:3014`。
2. 在“AI 漫剧模板中心”点击 `创建 5 集系列`。
3. 进入 `Night Signal Season 1` 系列页，确认左侧有 EP01-EP05。
4. 打开 EP01，进入第 9 步 `QA & Export`，确认九阶段 dry-run 全部可见。
5. 回到 EP01 的剧本、资产、分镜步骤，按真实生产需要补参考图和细化镜头。
6. 逐集完成图片候选、视频候选、配音、字幕和合成。
7. 每集导出前先看 QA、Retry、Ledger 和 unresolved shots。
8. 五集导出后，把完播率、评论、收藏、转发写回复盘表，决定是否扩成下一季。

## 5. 用系列蓝图批量验证 5 集

本仓库提供一个可执行的 5 集模板：

```text
samples/series_production/vertical_suspense_5ep.yaml
```

它包含：

- 1 个主角。
- 5 个场景。
- 2 个关键道具。
- 2 套服装。
- 5 集剧本。
- continuity locks。
- retry policy。
- dry-run backend。

页面查看方式：

- 首页：`http://localhost:3014` 的“AI 漫剧模板中心”。
- API：`GET http://localhost:17177/film/templates`。
- 文件：`samples/series_production/vertical_suspense_5ep.yaml`。

用 Python 直接 dry-run：

```bash
python3 - <<'PY'
from pathlib import Path
from src.film_engine import SeriesProductionPlanner

planner = SeriesProductionPlanner()
blueprint = planner.load_file(Path("samples/series_production/vertical_suspense_5ep.yaml"))
run = planner.run_blueprint(blueprint)
print(run.summary())
PY
```

预期结果：

- `accepted_items` 为 5。
- `failed_items` 为 0。
- `total_shots` 为 15。
- `selected_outputs` 每集都有 dry-run URI。

这个流程不直接产出真实 mp4；它用于验证 5 集结构、资产引用、连续性、QA、Retry、Ledger 和 Batch Production 是否稳定。真实媒体仍在 UI 的图片/视频/配音/合成步骤执行。

## 6. 用 3 个样片模板选题

样片验证包：

```text
samples/pilot_samples/three_60_90s_pilots.yaml
```

包含 3 个方向：

| 样片 | 类型 | 验证点 |
|---|---|---|
| Night Signal | 都市悬疑 | 单角色、单道具、冷色走廊连续性 |
| Contract Bride Counterattack | 复仇甜宠 | 对话近景、服装一致性、反转爽点 |
| Midnight Delivery | 都市奇幻 | 场景连续性和地址反转 |

页面查看方式：

- 首页：`http://localhost:3014` 的“AI 漫剧模板中心”。
- API：`GET http://localhost:17177/film/templates`。
- 文件：`samples/pilot_samples/three_60_90s_pilots.yaml`。

操作建议：

1. 每个方向只做 60-90 秒。
2. 每个方向只保留 1 个主角、1 个主场景、1 个关键道具。
3. 发布到抖音、快手、B 站、小红书、YouTube Shorts。
4. 用完播率、评论、收藏、转发判断是否扩成 5 集。
5. 胜出的题材再进入系列蓝图和 UI 多集生产。

## 7. Film Core API 调用

浏览器直接打开：

```text
http://localhost:3014/film/pipeline/run
```

会看到 endpoint 说明和 sample payload。

模板目录：

```bash
curl -sS http://localhost:17177/film/templates
```

从样片模板创建独立项目：

```bash
curl -sS -X POST http://localhost:17177/film/templates/pilots/midnight_delivery_70s/instantiate
```

从 5 集蓝图创建系列：

```bash
curl -sS -X POST http://localhost:17177/film/templates/series/night_signal_s01/instantiate
```

命令行 dry-run 示例：

```bash
curl -sS -X POST http://localhost:17177/film/pipeline/run \
  -H 'Content-Type: application/json' \
  -d '{
    "script_text": "INT. NIGHT CORRIDOR\nMaya: The phone rang again. [character=maya]",
    "graph_id": "manual_pilot",
    "source_title": "Manual Pilot",
    "backend": "dry_run"
  }'
```

返回中重点看：

- `story_graph`
- `director_program`
- `film_run.shot_graph`
- `film_run.generation_ledger`
- `film_run.qa_reports`
- `final_edit`

工作流状态：

```bash
curl -sS http://localhost:17177/projects/{projectId}/workflow
```

自动采集 Web 素材：

```bash
curl -sS -X POST http://localhost:17177/projects/{projectId}/web_media/collect \
  -H 'Content-Type: application/json' \
  -d '{"media_type":"both","count":3}'
```

给缺图分镜自动挂载图片：

```bash
curl -sS -X POST http://localhost:17177/projects/{projectId}/web_media/collect \
  -H 'Content-Type: application/json' \
  -d '{"media_type":"image","count":3,"attach_to":"storyboard"}'
```

记录重生成意图：

```bash
curl -sS -X POST http://localhost:17177/projects/{projectId}/workflow/stages/video_runtime/regenerate \
  -H 'Content-Type: application/json' \
  -d '{"reason":"主角动作幅度太弱，重生成视频候选","dry_run":true}'
```

这一步只记录可恢复的编辑/重生成事件；具体生成仍从 UI 的资产、分镜、视频或配音步骤执行。

一键 Auto Drama：

```bash
curl -sS http://localhost:17177/film/auto-drama/run
curl -sS -X POST http://localhost:17177/film/auto-drama/run \
  -H 'Content-Type: application/json' \
  -d '{"title":"Auto Pilot","seed_text":"A courier receives a call from a dead customer.","target_chapters":3}'
```

工作流 prompt 开关：

```bash
curl -sS http://localhost:17177/film/workflow/prompts
```

## 8. 如何解决行业痛点

| 痛点 | 解决方式 |
|---|---|
| 角色漂移 | Character Bible、reference images、locked traits、Film State |
| 换衣漂移 | CostumeAsset、`[costume=...]` 标签、continuity locks |
| 道具变形 | PropAsset、signature details、Production Bible |
| 镜头不连贯 | Story Graph、Shot Graph、scene state、transition metadata |
| 抽卡不可复盘 | Generation Ledger 记录 prompt、attempt、QA、成本、selected output |
| 失败靠人工记忆 | QA Engine + Retry Engine 输出 finding 和 repair notes |
| 批量生产混乱 | BatchProductionPlan、优先级、失败隔离、批次 summary |
| 一上来烧钱 | dry-run、第 9 步结构验收、低清/短时长预检 |
| 导出前素材不全 | `Start Render` 兜底导出 render package，不再只显示泛化失败 |
| 分镜因模型格式异常卡死 | JSON 修复 + deterministic fallback，先产出可编辑分镜 |
| 没有首帧图或参考视频无法测试 Motion | `采集图片` / `采集视频` 从 Web 临时补素材，先验证链路 |
| 自动/人工 workflow 不透明 | `9. QA & Export` 的 `Workflow Switches` 面板显示每个模块开关 |

## 9. 团队分工建议

2 人团队：

- 程序/流程负责人：环境、模型、资产库、QA、台账、自动化。
- 导演/运营负责人：题材、剧本、分镜、审片、发布复盘。

3 人团队：

- 技术架构：模型接入、自动化、成本、稳定性。
- 导演剪辑：分镜、候选选择、配音、合成。
- 题材运营：选题、发布、数据复盘、客户沟通。

## 10. 每日 SOP

1. 上午：写或改 1 集剧本，明确钩子和反转。
2. 中午：生成/修正角色、服装、场景、道具参考。
3. 下午：做分镜图和低成本视频候选。
4. 晚上：第 9 步 QA & Export 检查，人工选择候选并合成。
5. 次日：发布数据复盘，把好镜头和坏镜头都写入台账。

## 11. 常见故障

页面打不开：

```bash
docker compose ps
curl -I http://localhost:3014/
```

后端不可用：

```bash
curl -sS http://localhost:17177/config/info
docker compose logs backend --tail=100
```

第 9 步没有结果：

- 检查项目是否有剧本文本或分镜。
- 检查 `/film/pipeline/run` 是否返回 JSON。
- 先用 `backend=dry_run`，不要一开始接真实视频模型。

生成失败：

- 检查 API Key。
- 降低分辨率、缩短时长。
- 每个镜头只改一个变量。
- 回看 Ledger 的 prompt fingerprint、QA finding 和 retry notes。

分镜生成失败：

- 先看 `4. Storyboard` 是否已经生成 fallback 分镜。
- 如果有 fallback 分镜，直接编辑角色、场景、道具和动作后继续。
- 如果没有图片，点 `采集图片` 临时补图，再进入 Motion。

Motion 润色或提交失败：

- `AI 润色` 后即使模型失败，也会出现本地兜底提示词；点击 `应用` 后继续。
- I2V 没有首帧时点 `采集图片`。
- R2V 没有参考视频时点 `采集视频`。
- 如果上传图片后马上提交，等上传遮罩消失再点 `加入生成队列 (Ctrl+Enter)`。
