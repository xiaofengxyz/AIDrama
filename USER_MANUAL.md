# AIDrama Studio 用户手册

## 启动

```bash
make up
```

访问：

- Studio: http://localhost:3014
- Backend API: http://localhost:17177/docs

桌面打包模式的数据目录：

| 系统 | 目录 |
|---|---|
| macOS / Linux | `~/.aidrama/` |
| Windows | `C:\Users\<用户名>\.aidrama\` |

## 工作流

1. 新建系列或独立项目。
2. 导入小说、剧本或章节文本。
3. 抽取角色、场景、道具、服装与对白。
4. 进入分镜与导演规划，确认镜头主体、动作、情绪和运镜。
5. 生成图片/视频候选，按镜头进行 QA、重试和人工选择。
6. 进入合成与导出，产出可复盘的成片和镜头台账。

## 配置

默认本地优先保存资产。需要云端镜像时再配置 OSS：

| 环境变量 | 说明 | 示例 |
|---|---|---|
| `DASHSCOPE_API_KEY` | DashScope API Key | `sk-xxx` |
| `OSS_BUCKET_NAME` | OSS Bucket | `my-aidrama-bucket` |
| `OSS_BASE_PATH` | OSS 路径前缀 | `aidrama` |

`scripts/bootstrap_env.sh` 可以从本地 `Doc/accounts` 生成 `.env.local`。不要提交 `Doc/accounts`、`.env.local` 或任何密钥。

## 常见问题

如果页面打不开，先检查：

```bash
docker compose ps
curl -I http://localhost:3014/
curl -sS http://localhost:17177/config/info
```

如果配置页显示路径异常，删除 `~/.aidrama/webview_storage` 后重启桌面应用。
