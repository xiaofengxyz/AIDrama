---
workflow_switch:
  module_id: 03_stage2_asset_pipeline
  stage_id: stage2_asset_pipeline
  label: Stage 2 Asset Pipeline
  auto_advance: true
  requires_human_review: false
  stop_after_stage: false
  description: Build locked production assets and continue automatically.
---

Implement Drama Asset Pipeline including Character Bible, Scene Bible, Shot Graph and Storyboard systems.

Requirements:
- Persist workflow state
- Support edit/regenerate
- Integrate QA and Retry
- Reuse Jellyfish systems

Switch behavior:
- Automatic mode continues after asset bible and storyboard contracts are generated.
- Manual mode stops here for asset approval before image/runtime spending.
