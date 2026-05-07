# AIDrama AI 协作指南

本文件给后续 AI 会话使用。进入仓库后先读：

1. `docs/task-progress.md`
2. `docs/README.md`
3. `docs/project-overview.md`
4. `docs/open-source-comparison.md`
5. `Doc/drama prd`

## 工作原则

- 默认使用单个 agent 连续推进；只有用户明确要求时才启动多 agent。
- 先看现有代码和文档，再改动。
- 不打印、复制、总结 `Doc/accounts`、`.env.local`、`.env` 或任何 API key/secret。
- 不提交 `external/`、`.research/`、`output/`、`.env.local`、`.env`、`Doc/accounts`。
- 根目录是唯一可运行工程；`external/` 只允许临时放只读参考 clone，不能参与构建或提交。
- 当前项目面向 2-3 人 AI 漫剧试制团队，优先降低试错成本、角色一致性成本和部署维护成本。

## 当前项目选择

主平台基座（最终架构）：Jellyfish

当前可运行兼容工作台：LumenX Studio

本项目已适配：

- WSL Ubuntu 22.04 + Docker
- 前端端口 `3014`
- 后端端口 `17177`
- `scripts/bootstrap_env.sh` 从 `Doc/accounts` 生成 `.env.local`
- DashScope-first provider 路由

说明：Starter Kit 明确把 Jellyfish 定为 AI Film Engine 的主平台基座。当前仓库仍保留 LumenX 可运行代码，是为了不中断本地试制、测试和迁移验证；后续架构判断不得再把 LumenX 写成最终主基座。

## 常用命令

```bash
make up
make ps
make logs
make down
make doctor
```

后端测试优先在容器里跑，避免宿主 Python 缺少 DashScope/OSS 依赖：

```bash
docker cp tests lumenx-backend:/app/tests
docker compose exec -T backend python -m pip install --no-cache-dir pytest
docker compose exec -T backend python -m pytest -q -s /app/tests
```

前端测试优先：

```bash
cd frontend && npm run test
```

如果本地没有 `frontend/node_modules`，用 Docker 构建里的 `npm ci && npm run build` 作为前端基础验证。

构建检查：

```bash
docker compose config --quiet
```

不要运行会打印完整 Compose 配置的 `docker compose config`，因为它会展开 `.env.local` 或旧 `.env` 中的密钥。

## 代码地图

- `src/apps/comic_gen/api.py`：FastAPI 入口。
- `src/apps/comic_gen/pipeline.py`：核心生产流程。
- `src/apps/comic_gen/models.py`：项目、角色、场景、分镜、任务等数据结构。
- `src/film_engine/`：工业 AI Film Engine 的最小核心闭环，包含 Runtime、Director DSL、Shot Graph、Prompt Compiler、Registry、QA、Retry、Film State。
- `src/models/`：模型供应商封装。
- `src/utils/provider_registry.py`：模型家族和 provider 后端路由。
- `frontend/src/components/modules/`：创作工作台主要页面组件。
- `frontend/src/lib/api.ts`：前端 API 客户端。
- `docs/`：项目文档与交接记录。

## 改动守则

- 密钥和生成媒体永远不入库。
- 改模型或 provider 时，同时检查后端路由、前端设置页、测试和文档。
- 改数据模型时，同时检查 Pydantic 模型、API 返回、前端 store 和旧项目数据兼容。
- 改 Docker/启动方式时，同时更新 `docs/local-setup.md` 和 `docs/task-progress.md`。
- 做完改动后清理工作区，提交必要修改并 push。
