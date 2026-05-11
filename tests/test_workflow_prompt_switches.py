from pathlib import Path

from src.film_engine.workflow_prompts import (
    build_prompt_execution_plan,
    load_workflow_prompt_modules,
)


def test_repository_workflow_prompts_expose_auto_switches():
    """Every Codex workflow prompt should be machine-readable and auto-runnable."""
    modules = load_workflow_prompt_modules(Path("docs/Codex_Workflow_Prompts"))

    assert len(modules) == 10
    assert modules[0].switch.module_id == "00_global_rules"
    assert modules[-1].switch.module_id == "09_final_integration"
    assert all(module.switch.auto_advance for module in modules)

    plan = build_prompt_execution_plan(modules)

    assert plan.status == "ready"
    assert plan.summary["manual_gates"] == 0
    assert plan.summary["auto_modules"] == 10


def test_workflow_prompt_plan_stops_after_manual_stage(tmp_path: Path):
    """A non-auto switch should complete its module and then wait for the user."""
    (tmp_path / "01_AUTO.md").write_text(
        """---
workflow_switch:
  module_id: first
  stage_id: first_stage
  label: First
  auto_advance: true
  requires_human_review: false
  stop_after_stage: false
---
First body.
""",
        encoding="utf-8",
    )
    (tmp_path / "02_MANUAL.md").write_text(
        """---
workflow_switch:
  module_id: second
  stage_id: manual_stage
  label: Manual
  auto_advance: false
  requires_human_review: true
  stop_after_stage: true
---
Manual body.
""",
        encoding="utf-8",
    )

    modules = load_workflow_prompt_modules(tmp_path)
    plan = build_prompt_execution_plan(modules, completed_module_ids=["second"])

    assert plan.status == "waiting_for_user"
    assert plan.first_waiting_stage == "manual_stage"
    assert plan.steps[1].status == "waiting_for_user"
    assert plan.steps[1].waits_for_user is True
