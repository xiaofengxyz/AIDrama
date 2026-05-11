---
workflow_switch:
  module_id: 08_data_schema
  stage_id: data_schema
  label: Data Schema
  auto_advance: true
  requires_human_review: false
  stop_after_stage: false
  description: Validate production-grade schemas and continue automatically.
---

Implement production-grade schemas for workflow assets, QA, runtime and retry systems.

Requirements:
- Persist workflow state
- Support edit/regenerate
- Integrate QA and Retry
- Reuse Jellyfish systems

Switch behavior:
- Automatic mode continues after schemas are stable and tests pass.
- Manual mode stops here when schema migration requires user approval.
