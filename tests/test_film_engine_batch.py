from pathlib import Path

import yaml

from src.film_engine import (
    BatchProductionItem,
    BatchProductionPlan,
    BatchProductionRunner,
    DirectorDSLParser,
    DirectorProgram,
    DirectorScene,
    DirectorShot,
    RuntimeBackend,
    ShotTransition,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _one_shot_program(sequence_id: str) -> DirectorProgram:
    return DirectorDSLParser().parse_yaml(
        f"""
sequence_id: {sequence_id}
scene:
  id: {sequence_id}_scene
  location: test_stage
  mood: tense
shots:
  - id: shot_001
    type: closeup
    action: heroine studies the room
"""
    )


def test_batch_production_runner_summarizes_multiple_sequences():
    parser = DirectorDSLParser()
    suspense_program = parser.parse_file(
        PROJECT_ROOT / "samples/shot_graph/suspense_sequence.yaml"
    )
    one_shot_program = _one_shot_program("insert_sequence")
    plan = BatchProductionPlan(
        id="pilot_batch",
        items=[
            BatchProductionItem(
                item_id="insert_sequence",
                program=one_shot_program,
                priority=20,
            ),
            BatchProductionItem(
                item_id="suspense_sequence",
                program=suspense_program,
                priority=10,
            ),
        ],
    )

    run = BatchProductionRunner().run(plan)
    summary = run.summary()

    assert run.item_order == ["suspense_sequence", "insert_sequence"]
    assert set(run.item_runs) == {"suspense_sequence", "insert_sequence"}
    assert summary["total_plan_items"] == 2
    assert summary["scheduled_items"] == 2
    assert summary["accepted_items"] == 2
    assert summary["failed_items"] == 0
    assert summary["total_shots"] == 5
    assert summary["accepted_shots"] == 5
    assert summary["total_attempts"] == 5
    assert summary["selected_outputs"]["suspense_sequence"]["shot_001"].startswith(
        "dry-run://"
    )


def test_batch_production_runner_isolates_item_errors():
    good_program = _one_shot_program("good_sequence")
    bad_program = DirectorProgram(
        sequence_id="bad_sequence",
        scene=DirectorScene(id="bad_scene"),
        shots=[DirectorShot(id="shot_001")],
        transitions=[ShotTransition(from_shot="shot_001", to_shot="missing_shot")],
    )
    plan = BatchProductionPlan(
        id="error_isolation_batch",
        continue_on_error=True,
        items=[
            BatchProductionItem(item_id="bad_sequence", program=bad_program, priority=10),
            BatchProductionItem(item_id="good_sequence", program=good_program, priority=20),
        ],
    )

    run = BatchProductionRunner().run(plan)
    summary = run.summary()

    assert set(run.item_runs) == {"good_sequence"}
    assert "bad_sequence" in run.errors
    assert "unknown shot" in run.errors["bad_sequence"]
    assert summary["accepted_items"] == 1
    assert summary["failed_items"] == 1
    assert summary["failed_item_ids"] == ["bad_sequence"]


def test_batch_production_runner_honors_priority_and_max_items():
    plan = BatchProductionPlan(
        id="priority_batch",
        max_items=2,
        items=[
            BatchProductionItem(
                item_id="late_sequence",
                program=_one_shot_program("late_sequence"),
                priority=30,
            ),
            BatchProductionItem(
                item_id="first_sequence",
                program=_one_shot_program("first_sequence"),
                priority=10,
            ),
            BatchProductionItem(
                item_id="second_sequence",
                program=_one_shot_program("second_sequence"),
                priority=20,
            ),
        ],
    )

    run = BatchProductionRunner().run(plan)
    summary = run.summary()

    assert run.item_order == ["first_sequence", "second_sequence"]
    assert set(run.item_runs) == {"first_sequence", "second_sequence"}
    assert "late_sequence" not in run.item_runs
    assert summary["total_plan_items"] == 3
    assert summary["scheduled_items"] == 2
    assert summary["accepted_items"] == 2


def test_batch_production_plan_loads_sample_yaml():
    data = yaml.safe_load(
        (PROJECT_ROOT / "samples/batch_production/pilot_batch.yaml").read_text(
            encoding="utf-8"
        )
    )
    plan = BatchProductionPlan(**data)

    run = BatchProductionRunner().run(plan)
    summary = run.summary()

    assert plan.backend == RuntimeBackend.DRY_RUN
    assert run.item_order == ["corridor_opening", "door_reveal"]
    assert summary["total_plan_items"] == 2
    assert summary["scheduled_items"] == 2
    assert summary["accepted_items"] == 2
    assert summary["total_shots"] == 3
    assert summary["total_attempts"] == 3
