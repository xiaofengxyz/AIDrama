---
workflow_switch:
  module_id: 00_global_rules
  stage_id: global_rules
  label: Global Rules
  auto_advance: true
  requires_human_review: false
  stop_after_stage: false
  description: Apply shared execution rules, then continue automatically.
---

THIS PROJECT IS A FORK OF JELLYFISH.
DO NOT CREATE A NEW PROJECT.
Extend existing architecture only.

Requirements:
- Persist workflow state
- Support edit/regenerate
- Integrate QA and Retry
- Reuse Jellyfish systems

Switch behavior:
- `auto_advance: true` means the runner can continue to the next module after this module finishes.
- Set `auto_advance: false` or `requires_human_review: true` to stop after this module and wait for user action.
