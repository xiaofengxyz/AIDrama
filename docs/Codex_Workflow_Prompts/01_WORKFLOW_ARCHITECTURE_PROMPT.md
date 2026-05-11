---
workflow_switch:
  module_id: 01_workflow_architecture
  stage_id: workflow_architecture
  label: Workflow Architecture
  auto_advance: true
  requires_human_review: false
  stop_after_stage: false
  description: Build the workflow-first architecture and continue automatically.
---

Implement workflow-first CineForge architecture integrated into Jellyfish.

Requirements:
- Persist workflow state
- Support edit/regenerate
- Integrate QA and Retry
- Reuse Jellyfish systems

Switch behavior:
- Automatic mode continues to Stage 1 after workflow state contracts are in place.
- Manual mode stops here so the user can review architecture boundaries before implementation continues.
