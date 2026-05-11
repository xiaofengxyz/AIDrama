---
workflow_switch:
  module_id: 09_final_integration
  stage_id: final_integration
  label: Final Integration
  auto_advance: true
  requires_human_review: false
  stop_after_stage: false
  description: Connect all stages into an executable AI Drama OS.
---

Connect all workflow stages into one executable AI Drama Operating System.

Requirements:
- Persist workflow state
- Support edit/regenerate
- Integrate QA and Retry
- Reuse Jellyfish systems

Switch behavior:
- Automatic mode completes the run and emits final workflow artifacts.
- Manual mode stops after integration for final user acceptance before export or push.
