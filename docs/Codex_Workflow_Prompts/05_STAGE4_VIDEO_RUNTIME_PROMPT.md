---
workflow_switch:
  module_id: 05_stage4_video_runtime
  stage_id: stage4_video_runtime
  label: Stage 4 Video Runtime
  auto_advance: true
  requires_human_review: false
  stop_after_stage: false
  description: Generate or validate video runtime outputs and continue automatically.
---

Implement Video Runtime Engine for Seedance, Kling, Veo and Wan2.1, Sora and so on.

Requirements:
- Persist workflow state
- Support edit/regenerate
- Integrate QA and Retry
- Reuse Jellyfish systems

Switch behavior:
- Automatic mode continues after selected video outputs are present or dry-run outputs are available.
- Manual mode stops here so the user can inspect expensive video candidates.
