# 项目说明

日期：2026-05-07

## 本项目是什么

AIDrama 是面向工业化 AI 漫剧/AI Film Engine 的内容试制工作区。最终主平台基座采用 Starter Kit 指定的 Jellyfish；当前仓库保留 LumenX-compatible 可运行工作台，并针对本机环境补了 Docker 启动、端口映射、密钥引导和项目级文档。

项目的第一目标是帮助小团队把内容生产链路跑顺，同时把 Film Core 做成可迁移内核：少花时间在工具切换、手工记录、素材丢失和重复抽卡上，多花时间验证题材、角色、爽点和发布数据。

## 能做什么

- 从小说、梗概或短剧脚本创建项目。
- 用大模型提取角色、场景、道具等实体。
- 统一美术风格，生成角色全身图、三视图、头像、场景和道具资产。
- 用资产参考图生成分镜图，减少角色漂移和场景不连贯。
- 按分镜生成视频候选，支持批量抽卡后人工选择。
- 生成配音、音频素材，并用 FFmpeg 合成视频片段。
- 本地优先保存项目数据和媒体文件，后续可接 OSS 做跨机器协作和云备份。
- 通过 DashScope 优先接入 Qwen/Wanx，后续可按镜头引入 Kling、Vidu、PixVerse 等更贵或更强的视频模型。

## 暂时不做什么

- 不先做自有短剧 App、会员系统、支付系统、积分系统和买量后台。
- 不追求“一句话稳定出商业成片”。当前行业核心瓶颈仍是角色一致性、动作可控性和镜头废片率。
- 不把所有模型都一次性接满。先用 DashScope-only 跑通，再按结果补供应商。
- 不把上游源码克隆目录提交进主仓库。`external/` 只作为临时忽略区，需要对比上游时再 clone，用完保持与主工程隔离。

## 架构概览

平台基座：

- `Jellyfish`：最终主平台基座，承载 Studio OS、Workflow Core、Project System、Asset Management、Async Task System、Shot Management 和 Studio UI。
- `LumenX-compatible workbench`：当前仓库内可运行入口，用于本地试制、DashScope/Wanx 验证和迁移期回归测试，不再作为最终架构主基座。

前端：

- `frontend/`
- Next.js 14 + React 18 + TypeScript + Tailwind CSS
- 主要工作台组件在 `frontend/src/components/modules/`
- API 封装在 `frontend/src/lib/api.ts`

后端：

- `src/apps/comic_gen/`
- FastAPI + Python 3.11
- `api.py` 提供接口
- `pipeline.py` 串联剧本、资产、分镜、视频、音频和导出流程
- `models.py` 定义 Pydantic 数据模型
- `src/film_engine/` 提供工业化 Film Core 最小闭环：Runtime、Director DSL、Shot Graph、Prompt Compiler、Registry、QA、Retry、Film State

模型与媒体：

- `src/models/`：DashScope/Wanx/Kling/Vidu 等模型封装。
- `src/utils/provider_registry.py`：按模型家族做 provider 路由。
- `output/`：本地媒体和项目数据输出目录，已忽略提交。
- `.env.local`：由 `scripts/bootstrap_env.sh` 从 `Doc/accounts` 生成，已忽略提交；旧 `.env` 仍兼容读取。

## 推荐生产 SOP

1. 选 3 个题材方向，各做 60-90 秒样片。
2. 每个题材先做稳定角色资产，再做分镜图，再做短镜头视频。
3. 单镜头控制在 3-5 秒，复杂动作拆镜，不让模型一次承担太多。
4. 同一镜头生成 3-6 个候选，记录 prompt、参考图、模型、成本和人工评分。
5. 样片发布到抖音、快手、B 站、小红书或 YouTube Shorts，用完播和互动数据反推题材。
6. 胜出题材扩到 5 集，再找网文作者、MCN、小版权方做 B2B 试播集或联合制作。

## 成本原则

先用 `qwen-plus + DashScope/Wanx` 做低成本试错。只有在题材被数据验证后，才给关键镜头使用更贵的视频模型。成本必须按镜头拆账，而不是只看单集总额。
