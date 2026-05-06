# 任务进度索引

日期：2026-05-06

这个文件用于跨会话交接。后续 AI 或人工进入仓库时，先读本文件，再读 `docs/README.md` 和 `agent.md`。

## 本轮任务状态

| 任务 | 状态 | 备注 |
|---|---|---|
| 先做计划再执行 | 已完成 | 已按计划推进，未启动子 agent |
| 阅读 PRD 和仓库结构 | 已完成 | PRD 在 `Doc/drama prd`，密钥在 `Doc/accounts`，不要打印密钥 |
| 遍历候选开源库并给出推荐 | 已完成 | 推荐 LumenX，详见 `docs/open-source-comparison.md` |
| 清理上轮 clone | 已完成 | `.research/` 已删除 |
| 克隆推荐上游仓库 | 已完成 | 官方 LumenX 已浅克隆到 `external/lumenx` |
| 建立文档系统 | 已完成 | 本文件、文档中心、项目说明、AI 协作指南已补齐 |
| 工作区清理、提交、push | 已完成 | Docker 启动和测试已通过，本轮修改已准备提交并 push |

## 当前技术选择

主基座：LumenX Studio

推荐原因：

- MIT 许可，源码开放，适合二开。
- 工作流正好覆盖 AI 漫剧：资产提取、风格定调、资产生成、分镜图、分镜视频、合成。
- 与 DashScope/Qwen/Wanx 贴合，适合先用一个账号跑通低成本样片。
- 对 2-3 人团队而言，部署和维护负担低于 huobao、Toonflow、FastMovieAI 等更重平台。

上游参考：

- 路径：`external/lumenx`
- 地址：`https://github.com/alibaba/lumenx.git`
- 当前浅克隆提交：`e3251638240bdf6378e778e48f14d64b2c6b370b`
- 提交日期：2026-05-04
- 提交说明：`Merge pull request #18 from alibaba/feat/model-catalog-onboarding-mvp`

## 已知注意事项

- 当前主仓库只有初始提交，项目主体文件本轮会作为首次完整工程提交。
- `Doc/accounts` 和 `.env` 必须保持忽略，任何输出都不要暴露密钥。
- `external/` 是本地参考 clone，不提交、不构建、不改动。
- 当前启动建议使用 Docker：宿主是 WSL Ubuntu 22.04，已有 Docker，无需另装 Python 3.11 或 FFmpeg。
- 前端端口使用 `3014`，后端端口使用 `17177`，避免常用 `3000` 冲突。
- 前端 `package-lock.json` 与 `yarn.lock` 已把残留内部 registry 地址改为公开 npm registry，避免 Docker 构建拉包失败。

## 本轮验证记录

- `docker compose config --quiet`：通过。
- `make up`：通过，已启动 `lumenx-backend` 和 `lumenx-frontend`。
- `curl http://localhost:17177/config/info`：HTTP 200。
- `curl http://localhost:3014/`：HTTP 200。
- 容器内完整后端测试：`117 passed, 41 warnings`。
- 宿主直接跑完整 pytest 会因未安装 `dashscope`/`oss2` 等运行依赖失败；以后优先在容器或虚拟环境中跑全量测试。

## 下一步建议

1. 执行 `make up`，确认容器能启动。
2. 创建 3 个 60-90 秒题材样片，优先验证角色一致性和镜头废片率。
3. 把抽卡结果记录成镜头级台账：prompt、模型、参考图、seed/参数、成本、人工评分、是否可用。
4. 若 LumenX 在非技术同事使用上阻力明显，再并行评估 LocalMiniDrama 作为桌面备选。
5. 后续可把 `external/lumenx` 的 model catalog/onboarding 更新有选择地同步进本项目。
