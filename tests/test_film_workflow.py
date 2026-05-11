from pathlib import Path

from src.apps.comic_gen.models import (
    Character,
    Prop,
    Scene,
    Script,
    StoryboardFrame,
    VideoTask,
)
from src.film_engine.workflow import (
    RenderPackageExporter,
    WorkflowEditEvent,
    WorkflowStateStore,
    evaluate_project_workflow,
    get_model_recommendation_catalog,
)


def _script_with_frame() -> Script:
    """Build a small project fixture without importing the FastAPI app."""
    return Script(
        id="project_workflow",
        title="Workflow Story",
        original_text="INT. ROOM\nMaya: Keep the phone hidden. [prop=evidence_phone]",
        characters=[
            Character(
                id="maya",
                name="Maya",
                description="brave investigator",
                image_url="assets/maya.png",
                voice_id="longanyang",
                voice_name="Long Anyang",
            )
        ],
        scenes=[
            Scene(
                id="room",
                name="Room",
                description="cold apartment",
                image_url="assets/room.png",
            )
        ],
        props=[
            Prop(
                id="evidence_phone",
                name="Evidence Phone",
                description="cracked screen",
                image_url="assets/phone.png",
            )
        ],
        frames=[
            StoryboardFrame(
                id="frame_001",
                scene_id="room",
                character_ids=["maya"],
                prop_ids=["evidence_phone"],
                action_description="Maya hides the phone",
                dialogue="Keep the phone hidden.",
                image_url="frames/frame_001.png",
                audio_url="audio/frame_001.wav",
            )
        ],
        created_at=1.0,
        updated_at=1.0,
    )


def test_workflow_evaluator_tracks_media_readiness():
    project = _script_with_frame()

    state = evaluate_project_workflow(project)

    assert state.summary["recommended_render_mode"] == "render_package"
    assert state.stage("asset_pipeline").status == "passed"
    assert state.stage("video_runtime").status == "attention"
    assert state.stage("voice_runtime").status == "passed"
    assert state.stage("export").status == "attention"


def test_workflow_evaluator_marks_video_export_ready_with_selected_clip():
    project = _script_with_frame()
    project.video_tasks.append(
        VideoTask(
            id="video_001",
            project_id=project.id,
            frame_id="frame_001",
            image_url="frames/frame_001.png",
            prompt="Maya hides the phone",
            status="completed",
            video_url="videos/frame_001.mp4",
            created_at=2.0,
        )
    )
    project.frames[0].selected_video_id = "video_001"

    state = evaluate_project_workflow(project)

    assert state.summary["recommended_render_mode"] == "video"
    assert state.summary["can_export_video"] is True
    assert state.stage("video_runtime").status == "passed"
    assert state.stage("composition").status == "ready"


def test_workflow_store_preserves_edit_history(tmp_path: Path):
    project = _script_with_frame()
    store = WorkflowStateStore(tmp_path / "workflow_state.json")

    first = store.upsert(evaluate_project_workflow(project))
    first.edit_history.append(
        WorkflowEditEvent(
            event_id="event_1",
            stage_id="video_runtime",
            action="regenerate",
            reason="motion too weak",
        )
    )
    store.save_all({project.id: first})
    second = store.upsert(evaluate_project_workflow(project))

    assert second.edit_history[0].stage_id == "video_runtime"


def test_render_package_exporter_writes_recoverable_manifest(tmp_path: Path):
    project = _script_with_frame()
    state = evaluate_project_workflow(project)

    result = RenderPackageExporter(tmp_path).export(
        project,
        workflow_state=state,
        options={"resolution": "1080p"},
        reason="No videos selected to merge.",
    )

    manifest_path = tmp_path / result["url"].split("/", 1)[1]
    assert result["mode"] == "render_package"
    assert manifest_path.exists()
    assert "No final mp4 was created" in result["warnings"][0]


def test_model_recommendation_catalog_is_bailian_first():
    catalog = get_model_recommendation_catalog()
    stages = {stage["stage_id"]: stage for stage in catalog["stages"]}

    assert catalog["provider_strategy"].startswith("Bailian-first")
    assert stages["video_runtime"]["model_recommendations"][0]["provider"].startswith(
        "Alibaba Bailian"
    )
    assert stages["voice_runtime"]["model_recommendations"][0]["model"] == "cosyvoice-v3-flash"
