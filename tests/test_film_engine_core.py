from pathlib import Path

import pytest

from src.film_engine import (
    CharacterAsset,
    CharacterRegistry,
    DirectorDSLParser,
    FilmEngine,
    GenerationLedgerRecorder,
    RetryPolicy,
    RuntimeBackend,
    RuntimeResult,
    RuntimeRouter,
    SceneAsset,
    SceneRegistry,
    ShotGraphBuilder,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_director_dsl_sample_builds_shot_graph():
    program = DirectorDSLParser().parse_file(
        PROJECT_ROOT / "samples/director_dsl/suspense_scene.yaml"
    )

    graph = ShotGraphBuilder().build(program)

    assert graph.scene.mood == "suspense"
    assert graph.shots[0].id == "shot_001"
    assert graph.shots[0].framing == "wide"
    assert graph.adjacency == {"shot_001": []}


def test_registries_load_existing_samples():
    characters = CharacterRegistry.from_json_file(
        PROJECT_ROOT / "samples/character_registry/heroine_001.json"
    )
    scenes = SceneRegistry.from_yaml_file(
        PROJECT_ROOT / "samples/scene_registry/cinematic_night_street.yaml"
    )

    assert characters.require("heroine_001").outfits == ["school_uniform"]
    assert scenes.require("cinematic_night_street_v1").lighting == "low_key_blue"


def test_bibles_seed_registries_and_film_state_locks():
    program = DirectorDSLParser().parse_file(
        PROJECT_ROOT / "samples/shot_graph/suspense_sequence.yaml"
    )
    characters = CharacterRegistry.from_bible_file(
        PROJECT_ROOT / "samples/character_bible/heroine_bible.yaml"
    )
    scenes = SceneRegistry.from_bible_file(
        PROJECT_ROOT / "samples/scene_bible/night_corridor_bible.yaml"
    )

    run = FilmEngine(character_registry=characters, scene_registry=scenes).run(program)

    heroine = characters.require("heroine_001")
    assert heroine.hairstyle == "black_long"
    assert characters.bible_ids == ["heroine_series_bible"]
    assert scenes.bible_ids == ["suspense_corridor_bible"]
    assert run.final_state.continuity_locks["character_bible"]["heroine_001"][
        "outfit"
    ] == "school_uniform"
    assert run.final_state.continuity_locks["scene_bible"]["dark_corridor"][
        "tone"
    ] == "cold_blue"
    assert "continuity:" in run.runtime_results[0].metadata["prompt"]
    assert "hairstyle=black_long" in run.runtime_results[0].metadata["prompt"]


def test_shot_graph_rejects_cycles():
    program = DirectorDSLParser().parse_yaml(
        """
scene:
  id: cycle_lab
shots:
  - id: shot_001
  - id: shot_002
transitions:
  - from: shot_001
    to: shot_002
  - from: shot_002
    to: shot_001
"""
    )

    with pytest.raises(ValueError, match="cycle"):
        ShotGraphBuilder().build(program)


def test_film_engine_runs_all_core_phases():
    program = DirectorDSLParser().parse_file(
        PROJECT_ROOT / "samples/shot_graph/suspense_sequence.yaml"
    )
    characters = CharacterRegistry(
        [
            CharacterAsset(
                id="heroine_001",
                name="Heroine",
                description="black long hair, determined expression",
                outfits=["school_uniform"],
                reference_images=["refs/heroine_full_body.png"],
                locked_traits=["face", "hair", "outfit"],
            )
        ]
    )
    scenes = SceneRegistry(
        [
            SceneAsset(
                id="dark_corridor",
                location="dark_corridor",
                mood="suspense",
                lighting="low_key",
                reference_images=["refs/dark_corridor.png"],
            )
        ]
    )

    run = FilmEngine(character_registry=characters, scene_registry=scenes).run(program)

    assert run.metadata["backend"] == "dry_run"
    assert len(run.graph.shots) == 4
    assert len(run.runtime_results) == 4
    assert all(report.passed for report in run.qa_reports)
    assert run.final_state.active_scene_id == "dark_corridor"
    assert len(run.final_state.timeline) == 4
    assert run.generation_ledger is not None
    assert run.generation_ledger.summary()["accepted_shots"] == 4
    assert run.generation_ledger.summary()["total_attempts"] == 4
    assert run.generation_ledger.shot_runs["shot_001"].selected_output_uri
    assert len(
        run.generation_ledger.shot_runs["shot_001"].attempts[0].prompt_fingerprint
    ) == 16
    assert "shot:" in run.runtime_results[0].metadata["prompt"]
    assert "characters:" in run.runtime_results[0].metadata["prompt"]


class FlakyRuntimeAdapter:
    backend = RuntimeBackend.DRY_RUN

    def __init__(self):
        self.calls = 0

    def generate(self, request):
        self.calls += 1
        if self.calls == 1:
            return RuntimeResult(
                backend=request.backend,
                shot_id=request.shot_id,
                status="failed",
                error="simulated transient runtime failure",
            )
        return RuntimeResult(
            backend=request.backend,
            shot_id=request.shot_id,
            status="completed",
            output_uri=f"dry-run://retry/{request.shot_id}",
            metadata={"prompt": request.compiled_prompt.prompt, "attempt": request.attempt},
        )


def test_retry_engine_repairs_failed_runtime_attempt():
    program = DirectorDSLParser().parse_yaml(
        """
scene:
  id: retry_lab
  location: retry_lab
  mood: tense
characters:
  - heroine_001
shots:
  - id: shot_001
    type: closeup
    target: heroine_001
    movement: dolly_in
    emotion: fear
"""
    )
    characters = CharacterRegistry(
        [
            CharacterAsset(
                id="heroine_001",
                reference_images=["refs/heroine.png"],
            )
        ]
    )
    router = RuntimeRouter()
    adapter = FlakyRuntimeAdapter()
    router.register(adapter)

    run = FilmEngine(character_registry=characters, runtime_router=router).run(
        program,
        retry_policy=RetryPolicy(max_attempts=2),
    )

    assert adapter.calls == 2
    assert [report.passed for report in run.qa_reports] == [False, True]
    assert run.runtime_results[1].metadata["attempt"] == 2
    assert "repair pass:" in run.runtime_results[1].metadata["prompt"]
    assert len(run.final_state.timeline) == 1
    assert run.generation_ledger is not None
    shot_run = run.generation_ledger.shot_runs["shot_001"]
    assert shot_run.status == "accepted"
    assert len(shot_run.attempts) == 2
    assert [attempt.decision_action for attempt in shot_run.attempts] == [
        "retry",
        "accept",
    ]
    assert run.metadata["generation_ledger"]["retry_attempts"] == 1


def test_generation_ledger_supports_manual_review_metadata():
    program = DirectorDSLParser().parse_yaml(
        """
scene:
  id: review_lab
  location: review_lab
shots:
  - id: shot_001
    action: heroine notices the door opening
"""
    )
    recorder = GenerationLedgerRecorder.for_sequence("review_sequence")

    run = FilmEngine(ledger_recorder=recorder).run(program)
    reviewed = recorder.mark_manual_review(
        "shot_001",
        manual_score=0.91,
        selected_attempt=1,
        tags=["usable", "needs_color_grade"],
        notes=["Keep this candidate for rough cut."],
    )

    assert run.generation_ledger is not None
    assert run.generation_ledger.sequence_id == "review_sequence"
    assert reviewed.manual_score == 0.91
    assert reviewed.selected_attempt == 1
    assert reviewed.tags == ["needs_color_grade", "usable"]
    assert reviewed.notes == ["Keep this candidate for rough cut."]
    assert recorder.summary()["selected_outputs"]["shot_001"].startswith("dry-run://")

    with pytest.raises(ValueError, match="manual_score"):
        recorder.mark_manual_review("shot_001", manual_score=1.5)

    with pytest.raises(ValueError, match="Unknown attempt"):
        recorder.mark_manual_review("shot_001", selected_attempt=99)
