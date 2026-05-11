---
workflow_switch:
  module_id: 06_qa_retry_engine
  stage_id: qa_retry_engine
  label: QA and Retry Engine
  auto_advance: true
  requires_human_review: false
  stop_after_stage: false
  description: Run QA and retry policy, then continue automatically.
---

Implement QA and Retry Engine for all workflow stages.

Requirements:
- Persist workflow state
- Support edit/regenerate
- Integrate QA and Retry
- Reuse Jellyfish systems

Switch behavior:
- Automatic mode continues when QA passes or retry decisions are recorded.
- Manual mode stops after QA reports so the user can approve repair actions.
