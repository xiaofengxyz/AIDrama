---
workflow_switch:
  module_id: 07_studio_ui
  stage_id: studio_ui
  label: Studio UI
  auto_advance: true
  requires_human_review: false
  stop_after_stage: false
  description: Sync workflow state into Studio UI surfaces and continue automatically.
---

Transform Jellyfish frontend into CineForge Studio workflow UI.

Requirements:
- Persist workflow state
- Support edit/regenerate
- Integrate QA and Retry
- Reuse Jellyfish systems

Switch behavior:
- Automatic mode continues after UI/API workflow state is visible.
- Manual mode stops here for product review before data schema hardening.
