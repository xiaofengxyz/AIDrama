---
workflow_switch:
  module_id: 02_stage1_novel_engine
  stage_id: stage1_novel_engine
  label: Stage 1 Novel Engine
  auto_advance: true
  requires_human_review: false
  stop_after_stage: false
  description: Expand source text into a novel plan and continue automatically.
---

Implement Novel Engine with world bible, relationship graph, chapter outline, cliffhanger engine and editable workflow.

Requirements:
- Persist workflow state
- Support edit/regenerate
- Integrate QA and Retry
- Reuse Jellyfish systems

Switch behavior:
- Automatic mode sends the generated novel artifacts to the asset pipeline.
- Manual mode stops after the novel plan so the user can revise world bible, chapter outline, and cliffhangers.
