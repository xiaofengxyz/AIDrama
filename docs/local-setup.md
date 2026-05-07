# 本地环境与项目配置

日期：2026-05-07

## 当前选择

本项目采用 `LumenX Studio` 作为 AI 漫剧工作台基座。它覆盖“剧本分析 -> 角色/场景/道具资产 -> 分镜 -> 分镜视频 -> 配音与合成”的完整链路，并且天然贴合 DashScope/Qwen/Wanx。

当前环境是 WSL Ubuntu 22.04，已有 Docker。推荐直接使用 Docker 启动，容器内会补齐 Python 3.11 与 FFmpeg，宿主机无需另外安装。

## 上游参考源码

本轮已清理 `external/` 下的上游 clone，避免根目录和 external 同时存在一套 Docker、前端、后端配置。当前根目录是唯一可运行工程。

如果后续需要对比官方 LumenX，上游源码只能临时 clone 到 `external/` 这类忽略目录，用完保持只读参考，不参与构建、不提交、不作为主工程启动入口。

## 端口

- 前端：`http://localhost:3014`
- 后端：`http://localhost:17177`
- API 文档：`http://localhost:17177/docs`

这里避开常用 `3000`，把 LumenX 前端映射到 `3014`。

## 启动

```bash
make up
```

等镜像构建完成后检查：

```bash
docker compose ps
docker compose config --quiet
curl http://localhost:17177/config/info
```

## 密钥配置

密钥来源为 `Doc/accounts`。运行 `make up` 时会自动执行：

```bash
./scripts/bootstrap_env.sh
```

它会生成本地 `.env.local`，包含：

- `DASHSCOPE_API_KEY`
- `DASHSCOPE_BASE_URL`
- `LLM_PROVIDER=dashscope`
- `OPENAI_BASE_URL` 与 `OPENAI_API_KEY`，作为可选 OpenAI-compatible 备用配置

`.env.local`、旧版 `.env` 与 `Doc/accounts` 都被 `.gitignore` 忽略，`Doc/accounts` 也被 `.dockerignore` 忽略。

## 常用命令

```bash
make ps
make logs
make down
make doctor
```

## 生产建议

先用 DashScope-only 跑通本地试制。等出现稳定内容方向后，再按需补 OSS，用于持久化媒体文件、跨机器协作和外网可访问素材。
