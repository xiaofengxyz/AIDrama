# AIDrama Studio

AIDrama 是一个以 Jellyfish 为主平台基座口径的工业级 AI Film Engine 工作区，目标不是做玩具式视频生成器，而是稳定支撑真人真实效果 AI 漫剧/AI 电影的批量生产。

## 核心链路

```text
Novel / Script
-> Story Graph
-> Director Planner
-> Film Core
-> Prompt Compiler
-> Runtime Adapter
-> Render Runtime / Video Models
-> QA Engine
-> Retry Engine
-> Final Editing
```

## 当前状态

- 可运行入口：AIDrama Studio
- 主平台基座口径：Jellyfish
- 核心内核：`src/film_engine/`
- 前端：Next.js 工作台，端口 `39211`
- 后端：FastAPI，端口 `48217`
- 临时上游参考：`external/`，已被 `.gitignore` 忽略，不参与提交和构建

## 快速启动

```bash
make up
```

然后打开：

- Studio: http://localhost:39211
- Backend API: http://localhost:48217/docs

## 验证

```bash
python3 -m pytest tests/test_film_engine_core.py tests/test_film_engine_batch.py tests/test_film_production_pipeline.py -q -s
cd frontend && npm run test
docker compose config --quiet
```

## 文档入口

- [项目文档索引](docs/README.md)
- [任务进度索引](docs/task-progress.md)
- [本地运行说明](docs/local-setup.md)
- [产品与制作人 Review](docs/ai-drama-product-review.md)
- [架构与工程动作](docs/ai-drama-architecture-actions.md)
- [测试用例与问题清单](docs/ai-drama-test-analysis.md)
- [商业落地计划](docs/ai-drama-business-plan.md)

密钥与生成资产不入库：`Doc/accounts`、`.env.local`、`.env`、`output/`、`external/` 都保持忽略。
