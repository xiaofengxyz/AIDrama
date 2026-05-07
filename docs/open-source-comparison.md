# AI 漫剧开源项目对比

日期：2026-05-07

## 结论

推荐主基座：`LumenX Studio`。

推荐备选：`LocalMiniDrama`。如果后续希望普通运营同事在 Windows 桌面上更轻量地使用，优先回看它。

本轮补充结论：`superpowers-zh` 是 AI 编程 skills，不是漫剧生产基座；`Toonflow-app` 强但复杂度更高；`BigBanana-AI-Director` 的流程理念值得借鉴但商业使用受限；`huobao-drama` 热度高但平台化和授权边界仍需确认。详见 `docs/ai-drama-product-review.md`。

暂不把高 star 项目作为主基座：

- `huobao-drama`：star 很高，TypeScript 全栈也完整，但 root 缺少明确 LICENSE 文件，且 Nuxt + Hono + Mastra + SQLite 的 Agent 平台化结构比当前试制团队需要的更重。
- `Toonflow-app`：star 和提交数很高，Apache-2.0 许可也友好，但无限画布、三层 Agent、可编程供应商系统更像重型创作系统，学习和改造成本高于 LumenX。
- `BigBanana-AI-Director`：产品理念很好，关键帧驱动也很值得借鉴，但公开仓库已经转为说明文档和 Docker 镜像入口，后续源码不再公开同步，且许可证限制商业使用。

## 为什么不是只选 star 多、更新频率高的

star 和提交频率只说明关注度和活跃度，不等于适合做二开基座。对 2-3 人 AI 漫剧团队，真正关键的是：

- 源码是否完整开放，能否自己改。
- 许可是否允许商业试制和后续变现。
- 是否覆盖从剧本到成片的关键链路，而不是只有剧本、只有前端或只有平台后台。
- 是否能用一套低成本 API 先跑通样片。
- 是否天然支持角色资产、参考图贯穿、分镜图、图生视频和候选选择。
- 部署和维护是否足够轻，避免小团队被平台工程消耗掉。

LumenX 的 star 不是最高，但它在“源码可控 + MIT + DashScope 友好 + 漫剧链路完整 + Docker 可跑 + 二开负担低”这几个维度综合最合适。

## 候选项目速览

GitHub star/fork/commit 数读取于 2026-05-06，后续会变化，以项目页面为准。

| 项目 | 当前热度 | 定位 | 技术栈/结构 | 优点 | 风险/不足 | 建议 |
|---|---:|---|---|---|---|---|
| [LumenX](https://github.com/alibaba/lumenx) | 465 stars / 118 forks / 123 commits | AI 短漫剧一站式生产 | FastAPI + Next.js + DashScope/Wanx | 链路完整、MIT、DashScope 亲和、测试较多、本地优先 | 星标低于 huobao/Toonflow，官方仍在快速变化 | 主推荐 |
| [LocalMiniDrama](https://github.com/xuanyustudio/LocalMiniDrama) | 321 stars / 79 forks / 185 commits | 本地短剧/漫剧助手 | Node.js + Vue + Electron + SQLite | MIT、本地化强、模型支持广、桌面友好、一键流水线清楚 | 更偏普通创作者桌面工具，深度二开架构不如 LumenX 清晰 | 强备选 |
| [huobao-drama](https://github.com/chatfire-AI/huobao-drama) | 11.6k stars / 2.2k forks / 274 commits | AI 短剧生成平台 | Nuxt + Hono + Drizzle + Mastra + SQLite | 热度高、Agent 技能结构明确、TTS/FFmpeg/视频链路完整 | root 无明确 LICENSE 文件，平台化和 Agent 栈更重 | 观察，不做当前主基座 |
| [Toonflow-app](https://github.com/HBAI-Ltd/Toonflow-app) | 7.7k stars / 1.3k forks / 838 commits | AI 短剧工厂 | TypeScript + Electron + 本地 Agent 记忆 | Apache-2.0、活跃、无限画布、供应商可编程 | 复杂度高，学习曲线和维护成本更大 | 观察/方法参考 |
| [BigBanana-AI-Director](https://github.com/shuyu-labs/BigBanana-AI-Director) | 1.2k stars / 223 forks / 433 commits | AI 漫剧工场 | 公开仓库主要是文档 + Docker 镜像 | Script-to-Asset-to-Keyframe 理念强，首尾帧/关键帧思路好 | 源码不再公开同步，非商业/商业授权限制明显 | 不做基座，借鉴方法 |
| [deep-printfilm](https://github.com/yuanzhongqiao/deep-printfilm) | 576 stars / 31 forks / 34 commits | AI 短剧/漫剧前端工作台 | React/Vite + IndexedDB | 轻、原型快、Script-to-Asset-to-Keyframe 概念可参考 | 缺完整自建后端，依赖外部 API/代理色彩较重 | 原型参考 |
| [FastMovieAI](https://github.com/xhadmincn/FastMovieAI) | 315 stars / 90 forks / 17 commits | 可商用短剧创作平台 | PHP/Webman + Vue + MySQL + Redis + 支付/插件 | Apache-2.0、商业模块完整 | 对内容试制团队太重，早期会被后台/支付/用户系统拖慢 | 后期平台化再看 |
| [drama-workshop](https://github.com/jinlei665/drama-workshop) | 23 stars / 14 forks / 492 commits | 短剧漫剧创作工坊 | Next.js + Supabase/Postgres + S3 | 工作流编辑器、首尾帧、FFmpeg 处理意识好 | Supabase/Postgres/S3 前置较重，热度小 | 不优先 |
| [novelvids](https://github.com/Anning01/novelvids) | 206 stars / 36 forks / 34 commits | 小说转短剧平台 | FastAPI + React + Tortoise ORM | 分层和测试意识好，章节级工作流明确 | Python 3.12、模型落地和生态仍需验证 | 观察 |
| [llm-script-factory](https://github.com/oidahdsah0/llm-script-factory) | 25 stars / 11 forks / 22 commits | 短剧剧本工厂 | FastAPI + Next.js | DTG 短剧理论和剧本阶段有价值 | 不覆盖视频生产 | 作为编剧辅助 |
| [aimanju](https://github.com/huangama666/aimanju) | 28 stars / 9 forks / 10 commits | AI 漫剧前端应用 | Vite + Supabase | 前端 UI 和 Supabase 函数可参考 | 生成链路与后端完整度不如 LumenX | 不优先 |
| [ai_story](https://github.com/xiaofengxyz/ai_story) | 本地 fork | 故事视频自动生成 | Django/Vue/Celery/Redis | Pipeline、队列、Docker 思路完整 | 部分 Agent/MCP 模块闭源或依赖较重 | 不优先 |
| [superpowers-zh](https://github.com/jnMetaCode/superpowers-zh) | 2.1k stars / 231 forks / 51 commits | AI 编程技能包 | 多 AI 编程工具 skills | 可改善 AI 协作方式 | 不是漫剧生产工具 | 不作为基座 |
| [codeywood](https://github.com/kaigani/codeywood) | 14 stars / 3 forks / 27 commits | AI 影视制作 skills | Claude/Codex skills + 脚本 | 角色一致性、制作 SOP 值得参考 | 不是开箱工作台 | 方法参考 |

## 额外搜索观察

额外搜索到 `TypeTale`、`VANTA`、`OpenMontage` 等视频/动画方向项目。它们有参考价值，但当前不替代 LumenX：

- `TypeTale` 更偏本地 AIGC 视频软件与 ComfyUI 节点生态，适合观察模型接入和本地算力路线。
- `VANTA` 和 `OpenMontage` 更偏通用视频引擎、Remotion 或素材剪辑工作流，不是 AI 漫剧从小说到角色资产再到分镜成片的直接基座。

## 关键维度评分

| 维度 | LumenX | LocalMiniDrama | huobao | Toonflow | BigBanana |
|---|---|---|---|---|---|
| 输出质量潜力 | 高：资产/分镜/视频链路完整 | 高：多模型和参考图传递做得细 | 中高：链路完整但需确认模型策略 | 中高：工作流强但复杂 | 高：理念强 |
| 出片速度 | 中高：Docker + DashScope 先跑 | 高：桌面/本地流水线友好 | 中：平台栈较重 | 中：学习曲线较高 | 高：镜像体验可能快 |
| 部署难易 | 中：Docker 稳 | 低：Node/Electron 轻 | 中：前后端 + Agent | 中高：桌面 + 内置 Agent 系统 | 低到中：Docker 但不可控 |
| 操作难易 | 中 | 高 | 中 | 中 | 中 |
| 成本控制 | 高：DashScope-only 先试 | 高：多供应商可选 | 中：多模型配置更复杂 | 中：供应商系统强但调试成本高 | 中：依赖推荐 API |
| 角色一致性 | 高：角色资产、三视图、头像、参考图 | 高：参考图传递、素材库和多图模式 | 中高 | 中高 | 高 |
| 动作与运镜控制 | 中高：分镜短镜头、i2v/r2v | 中高：景别/运镜/全能模式字段细 | 中高 | 中高 | 高：关键帧理念强 |
| 二开可控性 | 高 | 高 | 中：许可需确认 | 中高 | 低 |
| 小团队适配 | 高 | 高 | 中 | 中 | 低 |

## 推荐落地方案

1. 本项目继续用 LumenX 做主基座。
2. `external/` 不再常驻上游 clone，避免重复配置干扰；需要对比官方上游时临时 clone 到 ignored 目录，按需人工移植。
3. 第一阶段只跑 DashScope-only，不急着接满 Kling/Vidu/Seedance。
4. 建立镜头级抽卡台账，记录 prompt、参考图、模型、成本、候选评分和最终采用原因。
5. 如果非技术同事上手阻力大，再把 LocalMiniDrama 作为桌面工具备选进行一次短期试用。
