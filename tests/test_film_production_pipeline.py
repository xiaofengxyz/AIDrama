from src.film_engine import (
    AssetRegistry,
    CharacterAsset,
    CharacterRegistry,
    CostumeAsset,
    DirectorPlanner,
    FilmProductionPipeline,
    FinalEditingAssembler,
    PropAsset,
    RuntimeBackend,
    SceneAsset,
    SceneRegistry,
    StoryGraphBuilder,
)


SCRIPT = """
INT. NIGHT CORRIDOR
Maya: We should not open that door.

Suddenly the lock clicks by itself, and the shadow behind the frosted glass moves.

Maya: Run.
The chase breaks into the stairwell before dawn.
"""


def _character_registry() -> CharacterRegistry:
    return CharacterRegistry(
        [
            CharacterAsset(
                id="maya",
                name="Maya",
                description="sharp eyes, nervous but brave",
                current_outfit="blue raincoat",
                reference_images=["refs/maya_full_body.png"],
                locked_traits=["face", "hair", "blue raincoat"],
            )
        ]
    )


def _scene_registry() -> SceneRegistry:
    return SceneRegistry(
        [
            SceneAsset(
                id="night_corridor",
                location="night_corridor",
                mood="suspense",
                lighting="flickering fluorescent",
                time_of_day="night",
                reference_images=["refs/night_corridor.png"],
            )
        ]
    )


def test_story_graph_builder_extracts_script_beats_and_edges():
    graph = StoryGraphBuilder().build_from_script(
        SCRIPT,
        graph_id="pilot_story",
        source_title="Door Pilot",
    )

    assert graph.graph_id == "pilot_story"
    assert len(graph.beats) == 3
    assert graph.beats[0].scene_hint == "night_corridor"
    assert graph.beats[0].characters == ["maya"]
    assert graph.beats[1].emotional_intent == "suspense"
    assert graph.adjacency == {"beat_001": ["beat_002"], "beat_002": ["beat_003"], "beat_003": []}


def test_director_planner_creates_shootable_program_from_story_graph():
    graph = StoryGraphBuilder().build_from_script(SCRIPT, graph_id="pilot_story")
    program = DirectorPlanner().plan(graph)

    assert program.sequence_id == "pilot_story"
    assert program.scene.id == "night_corridor"
    assert program.characters == ["maya"]
    assert [shot.id for shot in program.shots] == ["shot_001", "shot_002", "shot_003"]
    assert program.shots[0].metadata["story_beat_id"] == "beat_001"
    assert program.shots[1].emotion == "suspense"
    assert len(program.transitions) == 2


def test_pipeline_preserves_tagged_props_and_costumes_from_script():
    tagged_script = """
INT. SAFE HOUSE
Maya: Keep the proof hidden. [prop=evidence_phone] [costume=blue_raincoat]
"""
    asset_registry = AssetRegistry(
        props=[
            PropAsset(
                id="evidence_phone",
                name="Evidence Phone",
                reference_images=["refs/evidence_phone.png"],
                locked_traits=["cracked screen"],
            )
        ],
        costumes=[
            CostumeAsset(
                id="blue_raincoat",
                name="Blue Raincoat",
                reference_images=["refs/blue_raincoat.png"],
                palette=["cobalt_blue"],
                locked_traits=["reflective trim"],
            )
        ],
    )

    run = FilmProductionPipeline().run_script(
        tagged_script,
        graph_id="tagged_assets_story",
        backend=RuntimeBackend.DRY_RUN,
        character_registry=_character_registry(),
        asset_registry=asset_registry,
    )

    assert run.story_graph.beats[0].metadata["prop_ids"] == ["evidence_phone"]
    assert run.director_program.shots[0].prop_ids == ["evidence_phone"]
    assert run.director_program.shots[0].costume_ids == ["blue_raincoat"]
    assert run.final_edit.clips[0].prop_ids == ["evidence_phone"]
    assert run.final_edit.clips[0].costume_ids == ["blue_raincoat"]


def test_full_pipeline_runs_script_to_final_edit_timeline():
    run = FilmProductionPipeline().run_script(
        SCRIPT,
        graph_id="pilot_story",
        source_title="Door Pilot",
        backend=RuntimeBackend.DRY_RUN,
        character_registry=_character_registry(),
        scene_registry=_scene_registry(),
    )

    assert run.story_graph.metadata["beat_count"] == 3
    assert run.director_program.metadata["planner_version"] == "director_planner.v1"
    assert run.film_run.generation_ledger is not None
    assert run.film_run.generation_ledger.summary()["accepted_shots"] == 3
    assert len(run.final_edit.clips) == 3
    assert run.final_edit.unresolved_shots == []
    assert run.final_edit.total_duration == sum(shot.duration for shot in run.director_program.shots)
    assert run.final_edit.clips[0].output_uri.startswith("dry-run://")
    assert run.metadata["pipeline_version"] == "film_production_pipeline.v1"


def test_final_editor_reports_unresolved_shots_when_no_output_is_selected():
    pipeline_run = FilmProductionPipeline().run_script(
        "INT. ROOM\nA single lamp flickers.",
        graph_id="missing_output_story",
    )
    shot_ids = [shot.id for shot in pipeline_run.film_run.graph.shots]
    for shot_id in shot_ids:
        pipeline_run.film_run.generation_ledger.shot_runs[shot_id].selected_output_uri = None

    timeline = FinalEditingAssembler().assemble(pipeline_run.film_run)

    assert timeline.clips == []
    assert timeline.unresolved_shots == shot_ids
    assert timeline.qa_summary["unresolved_count"] == len(shot_ids)
