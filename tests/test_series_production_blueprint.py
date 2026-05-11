from pathlib import Path

import pytest
import yaml

from src.film_engine import (
    FilmTemplateCatalogLoader,
    PilotSamplePack,
    SeriesProductionBlueprint,
    SeriesProductionPlanner,
    StoryGraphBuilder,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_series_production_blueprint_loads_five_episode_template():
    blueprint = SeriesProductionPlanner.load_file(
        PROJECT_ROOT / "samples/series_production/vertical_suspense_5ep.yaml"
    )

    assert isinstance(blueprint, SeriesProductionBlueprint)
    assert blueprint.id == "night_signal_s01"
    assert blueprint.backend == "dry_run"
    assert len(blueprint.episodes) == 5
    assert {episode.episode_id for episode in blueprint.episodes} == {
        "ep01",
        "ep02",
        "ep03",
        "ep04",
        "ep05",
    }
    assert {character.id for character in blueprint.characters} == {"maya"}
    assert {prop.id for prop in blueprint.props} == {
        "evidence_phone",
        "red_thread_badge",
    }


def test_series_planner_compiles_blueprint_to_batch_plan():
    planner = SeriesProductionPlanner()
    blueprint = planner.load_file(
        PROJECT_ROOT / "samples/series_production/vertical_suspense_5ep.yaml"
    )

    plan = planner.to_batch_plan(blueprint)

    assert plan.id == "night_signal_s01_batch"
    assert len(plan.items) == 5
    assert [item.item_id for item in plan.items] == [
        "ep01",
        "ep02",
        "ep03",
        "ep04",
        "ep05",
    ]
    assert plan.items[0].program.characters == ["maya"]
    assert plan.items[0].program.props == ["evidence_phone"]
    assert plan.items[3].program.costumes == ["black_field_outfit"]
    assert plan.metadata["series_id"] == "night_signal_s01"


def test_series_blueprint_runs_with_shared_continuity_registries():
    planner = SeriesProductionPlanner()
    blueprint = planner.load_file(
        PROJECT_ROOT / "samples/series_production/vertical_suspense_5ep.yaml"
    )

    run = planner.run_blueprint(blueprint)
    summary = run.summary()

    assert run.item_order == ["ep01", "ep02", "ep03", "ep04", "ep05"]
    assert summary["accepted_items"] == 5
    assert summary["failed_items"] == 0
    assert summary["total_plan_items"] == 5
    assert summary["total_shots"] == 15
    assert summary["total_attempts"] == 15
    assert summary["selected_outputs"]["ep05"]["shot_003"].startswith("dry-run://")

    ep01_state = run.item_runs["ep01"].final_state
    assert "character_bible" in ep01_state.continuity_locks
    assert "production_bible" in ep01_state.continuity_locks
    assert ep01_state.character_states["maya"]["locked_traits"]


def test_series_blueprint_rejects_duplicate_episode_ids():
    blueprint_data = yaml.safe_load(
        (
            PROJECT_ROOT / "samples/series_production/vertical_suspense_5ep.yaml"
        ).read_text(encoding="utf-8")
    )["series_production"]
    blueprint_data["episodes"][1]["episode_id"] = "ep01"

    with pytest.raises(ValueError, match="Duplicate series episode ids"):
        SeriesProductionBlueprint(**blueprint_data)


def test_three_pilot_samples_are_story_graph_ready():
    data = yaml.safe_load(
        (
            PROJECT_ROOT / "samples/pilot_samples/three_60_90s_pilots.yaml"
        ).read_text(encoding="utf-8")
    )
    samples = data["pilot_samples"]["samples"]

    assert len(samples) == 3
    for sample in samples:
        assert 60 <= sample["target_duration_seconds"] <= 90
        graph = StoryGraphBuilder().build_from_script(
            sample["script_text"],
            graph_id=sample["sample_id"],
            source_title=sample["title"],
        )
        assert len(graph.beats) >= 3
        assert graph.metadata["builder_version"] == "story_graph.v1"


def test_template_catalog_loader_exposes_home_page_templates():
    """The catalog loader should expose exactly the templates shown on the home page."""
    loader = FilmTemplateCatalogLoader(PROJECT_ROOT)

    pilot_pack = loader.load_pilot_pack()
    catalog = loader.build_catalog()

    assert isinstance(pilot_pack, PilotSamplePack)
    assert catalog["status"] == "ready"
    assert catalog["summary"] == {
        "pilot_sample_count": 3,
        "series_blueprint_count": 1,
        "episode_count": 5,
    }
    assert loader.get_pilot_sample("midnight_delivery_70s").title == "Midnight Delivery"
    assert loader.get_series_blueprint("night_signal_s01").title == "Night Signal Season 1"
