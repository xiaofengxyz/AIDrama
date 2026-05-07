# Batch Production Freeze

Frozen:
- `BatchProductionItem.item_id`
- `BatchProductionItem.program`
- `BatchProductionItem.backend`
- `BatchProductionItem.retry_policy`
- `BatchProductionItem.priority`
- `BatchProductionPlan.id`
- `BatchProductionPlan.backend`
- `BatchProductionPlan.retry_policy`
- `BatchProductionPlan.items`
- `BatchProductionPlan.continue_on_error`
- `BatchProductionPlan.max_items`
- `BatchProductionRun.plan_id`
- `BatchProductionRun.item_order`
- `BatchProductionRun.item_runs`
- `BatchProductionRun.errors`
- `BatchProductionRun.summary()`

Do not couple:
- batch execution to DashScope, Kling, Vidu, Veo, or any concrete provider
- batch summaries to frontend-only models
- item failure handling to process exit behavior unless `continue_on_error` is disabled
