---
workflow_switch:
  module_id: 04_stage3_image_runtime
  stage_id: stage3_image_runtime
  label: Stage 3 Image Runtime
  auto_advance: true
  requires_human_review: false
  stop_after_stage: false
  description: Generate or validate image runtime outputs and continue automatically.
---

Implement Image Runtime pipeline using FLUX, SDXL, StoryDiffusion and ComfyUI adapters.

Requirements:
- Persist workflow state
- Support edit/regenerate
- Integrate QA and Retry
- Reuse Jellyfish systems

Switch behavior:
- Automatic mode continues after image runtime artifacts are ready.
- Manual mode stops here to review still frames before video generation.
