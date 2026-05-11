from pathlib import Path

from src.film_engine import AutoDramaPipeline, NovelEngine


def test_novel_engine_expands_seed_text_into_chapters():
    """Novel Engine should create editable world, relationship and chapter artifacts."""
    plan = NovelEngine().expand(
        "Maya: The dead customer's phone rings again. The courier follows the sound.",
        title="Night Signal",
        target_chapters=3,
    )

    assert plan.title == "Night Signal"
    assert plan.world_bible["format"] == "vertical AI mini-drama"
    assert len(plan.relationship_graph["characters"]) >= 2
    assert len(plan.chapters) == 3
    assert plan.chapters[0].cliffhanger


def test_auto_drama_pipeline_runs_text_to_final_edit_dry_run():
    """A single idea should compile into novel, screenplay, shot graph and final edit."""
    run = AutoDramaPipeline(prompt_root=Path("docs/Codex_Workflow_Prompts")).run(
        "Maya: The dead customer's phone rings again. The courier follows the sound.",
        title="Night Signal",
        target_chapters=2,
    )

    assert run.status == "completed"
    assert run.novel_plan is not None
    assert run.production_run is not None
    assert run.production_run.story_graph.beats
    assert run.production_run.final_edit.clips
    assert run.prompt_execution_plan.status == "ready"


def test_auto_drama_pipeline_waits_after_non_auto_stage():
    """Request-time overrides should make the workflow stop after that module."""
    run = AutoDramaPipeline(prompt_root=Path("docs/Codex_Workflow_Prompts")).run(
        "Maya: The phone rings.",
        title="Manual Gate",
        target_chapters=2,
        auto_overrides={"02_stage1_novel_engine": False},
    )

    assert run.status == "waiting_for_user"
    assert run.waiting_for_stage == "stage1_novel_engine"
    assert run.novel_plan is not None
    assert run.production_run is None
