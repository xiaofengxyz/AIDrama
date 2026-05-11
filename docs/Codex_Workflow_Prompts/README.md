# CineForge Codex Workflow Prompts

按顺序执行各阶段 Prompt。

每个数字前缀模块顶部都有 `workflow_switch`：

- `auto_advance: true`：完成该模块后自动进入下一模块。
- `auto_advance: false`：完成该模块后停下等待用户操作。
- `requires_human_review: true`：完成该模块后必须人工审核。
- `stop_after_stage: true`：显式要求停在该模块之后。

后端会通过 `GET /film/workflow/prompts` 读取这些开关。默认 00-09 全部为自动模式，适合一键 dry-run；制作人需要审核大纲、资产或视频候选时，把对应模块改成非自动即可。
