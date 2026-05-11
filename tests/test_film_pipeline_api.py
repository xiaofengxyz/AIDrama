import importlib.util

import pytest
from fastapi.testclient import TestClient

DASHSCOPE_AVAILABLE = importlib.util.find_spec("dashscope") is not None
pytestmark = pytest.mark.skipif(
    not DASHSCOPE_AVAILABLE,
    reason="dashscope is required to import the full FastAPI app",
)

if DASHSCOPE_AVAILABLE:
    from src.apps.comic_gen import api as api_module

    app = api_module.app
else:
    api_module = None
    app = None


@pytest.fixture
def isolated_client(monkeypatch, tmp_path):
    """Provide a TestClient backed by temporary project and series stores."""
    pipeline = api_module.ComicGenPipeline()
    pipeline.data_file = str(tmp_path / "projects.json")
    pipeline.series_data_file = str(tmp_path / "series.json")
    pipeline.scripts = {}
    pipeline.series_store = {}
    monkeypatch.setattr(api_module, "pipeline", pipeline)
    monkeypatch.setattr(
        api_module,
        "workflow_store",
        api_module.WorkflowStateStore(tmp_path / "workflow_state.json"),
    )
    monkeypatch.setattr(
        api_module,
        "render_package_exporter",
        api_module.RenderPackageExporter(tmp_path / "export"),
    )
    return TestClient(app)


def test_film_pipeline_api_get_returns_usage_contract():
    client = TestClient(app)
    response = client.get("/film/pipeline/run")

    assert response.status_code == 200
    data = response.json()
    assert data["method"] == "POST"
    assert data["default_backend"] == "dry_run"
    assert "script_text" in data["sample_payload"]
    assert data["fixed_stages"] == [
        "Runtime",
        "Director DSL",
        "Shot Graph",
        "Prompt Compiler",
        "Character Registry",
        "Scene Registry",
        "QA Engine",
        "Retry Engine",
        "Film State Engine",
    ]


def test_film_pipeline_api_runs_dry_run_with_assets():
    client = TestClient(app)
    response = client.post(
        "/film/pipeline/run",
        json={
            "script_text": (
                "INT. SAFE HOUSE\n"
                "Maya: Keep the proof hidden. "
                "[prop=evidence_phone] [costume=blue_raincoat]"
            ),
            "graph_id": "api_story",
            "source_title": "API Story",
            "characters": [
                {
                    "id": "maya",
                    "name": "Maya",
                    "reference_images": ["refs/maya.png"],
                    "locked_traits": ["face"],
                }
            ],
            "props": [
                {
                    "id": "evidence_phone",
                    "name": "Evidence Phone",
                    "reference_images": ["refs/phone.png"],
                    "locked_traits": ["cracked screen"],
                }
            ],
            "costumes": [
                {
                    "id": "blue_raincoat",
                    "name": "Blue Raincoat",
                    "reference_images": ["refs/raincoat.png"],
                    "palette": ["cobalt_blue"],
                }
            ],
            "continuity_locks": {
                "evidence_phone": {"crack_pattern": "spiderweb_upper_left"},
                "blue_raincoat": {"color": "cobalt_blue"},
            },
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["story_graph"]["graph_id"] == "api_story"
    assert data["director_program"]["props"] == ["evidence_phone"]
    assert data["director_program"]["costumes"] == ["blue_raincoat"]
    assert data["film_run"]["shot_graph"]["sequence_id"] == "api_story"
    assert data["film_run"]["shot_graph"]["shots"][0]["prop_ids"] == ["evidence_phone"]
    assert data["film_run"]["summary"]["accepted_shots"] == 1
    assert data["final_edit"]["clips"][0]["prop_ids"] == ["evidence_phone"]
    assert data["final_edit"]["clips"][0]["costume_ids"] == ["blue_raincoat"]


def test_film_pipeline_api_rejects_unknown_tagged_asset():
    client = TestClient(app)
    response = client.post(
        "/film/pipeline/run",
        json={
            "script_text": "INT. ROOM\nMaya: Hide it. [prop=missing_phone]",
            "graph_id": "missing_asset_story",
        },
    )

    assert response.status_code == 400
    assert "Unknown prop asset" in response.json()["detail"]


def test_film_templates_api_returns_catalog():
    """The template catalog API should expose the homepage template inventory."""
    client = TestClient(app)

    response = client.get("/film/templates")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["summary"] == {
        "pilot_sample_count": 3,
        "series_blueprint_count": 1,
        "episode_count": 5,
    }
    assert data["pilot_samples"]["samples"][0]["target_duration_seconds"] == 75
    assert data["series_blueprints"][0]["id"] == "night_signal_s01"


def test_runtime_recommendations_api_is_bailian_first():
    """The model catalog should recommend Bailian runtimes before future adapters."""
    client = TestClient(app)

    response = client.get("/film/runtime/recommendations")

    assert response.status_code == 200
    data = response.json()
    assert data["provider_strategy"].startswith("Bailian-first")
    stages = {stage["stage_id"]: stage for stage in data["stages"]}
    assert stages["asset_pipeline"]["model_recommendations"][0]["model"] == "wan2.7-image-pro"
    assert stages["voice_runtime"]["model_recommendations"][0]["model"] == "cosyvoice-v3-flash"


def test_workflow_prompt_switch_api_exposes_auto_execution_plan():
    """Codex workflow prompts should expose auto/manual gates to the backend."""
    client = TestClient(app)

    response = client.get("/film/workflow/prompts")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["execution_plan"]["status"] == "ready"
    assert data["execution_plan"]["summary"]["module_count"] == 10
    assert data["modules"][1]["switch"]["module_id"] == "01_workflow_architecture"


def test_auto_drama_api_generates_novel_and_studio_project(isolated_client):
    """Text-only input should produce a novel plan, dry-run film package and draft project."""
    response = isolated_client.post(
        "/film/auto-drama/run",
        json={
            "title": "Auto Night Signal",
            "seed_text": "Maya: The dead customer's phone rings again. The courier follows the sound.",
            "target_chapters": 2,
            "persist_project": True,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert len(data["novel_plan"]["chapters"]) == 2
    assert data["film_run"]["summary"]["accepted_shots"] >= 1
    assert data["final_edit"]["clips"]
    assert data["project"]["title"] == "Auto Night Signal"
    assert data["next_hash"].endswith("/step/export")


def test_auto_drama_api_respects_manual_prompt_gate(isolated_client):
    """A non-auto stage should return waiting_for_user after completing that stage."""
    response = isolated_client.post(
        "/film/auto-drama/run",
        json={
            "title": "Manual Auto Drama",
            "seed_text": "Maya: The phone rings.",
            "target_chapters": 2,
            "persist_project": False,
            "auto_overrides": {"02_stage1_novel_engine": False},
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "waiting_for_user"
    assert data["waiting_for_stage"] == "stage1_novel_engine"
    assert data["novel_plan"]["chapters"]
    assert data["final_edit"] is None


def test_pilot_template_api_instantiates_draft_project(isolated_client):
    """A pilot template can be copied into an editable standalone draft project."""
    response = isolated_client.post(
        "/film/templates/pilots/midnight_delivery_70s/instantiate"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["created_type"] == "pilot_project"
    assert data["template_id"] == "midnight_delivery_70s"
    assert data["next_hash"].endswith("/step/export")
    assert data["project"]["title"] == "Midnight Delivery"
    assert "customer ordered this meal ten years ago" in data["project"]["original_text"]


def test_series_template_api_instantiates_five_episode_series(isolated_client):
    """A series template can be copied into a five-episode Studio series."""
    response = isolated_client.post(
        "/film/templates/series/night_signal_s01/instantiate"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["created_type"] == "series"
    assert data["template_id"] == "night_signal_s01"
    assert data["series"]["title"] == "Night Signal Season 1"
    assert len(data["series"]["episode_ids"]) == 5
    assert len(data["series"]["characters"]) == 1
    assert len(data["series"]["scenes"]) == 5
    assert len(data["series"]["props"]) == 2
    assert len(data["episodes"]) == 5
    assert data["episodes"][0]["episode_number"] == 1


def test_project_workflow_api_persists_stage_state(isolated_client):
    """A Studio project should expose a recoverable CineForge workflow state."""
    project = api_module.pipeline.create_project(
        "Workflow API",
        "INT. ROOM\nMaya: Keep it safe. [character=maya]",
        True,
    )

    response = isolated_client.get(f"/projects/{project.id}/workflow")

    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == project.id
    assert data["version"] == "cineforge_workflow.v1"
    assert len(data["stages"]) == 9
    assert data["summary"]["recommended_render_mode"] == "render_package"


def test_export_api_falls_back_to_render_package_without_selected_videos(isolated_client):
    """Start Render should not fail generically when the project has no selected clips."""
    project = api_module.pipeline.create_project(
        "Package Export",
        "INT. ROOM\nMaya: The phone rang.",
        True,
    )

    response = isolated_client.post(
        f"/projects/{project.id}/export",
        json={
            "resolution": "1080p",
            "format": "mp4",
            "subtitles": "burn-in",
            "allow_package_fallback": True,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "render_package"
    assert data["url"].startswith("export/")
    assert data["workflow_state"]["summary"]["recommended_render_mode"] == "render_package"
    assert any("No final mp4" in warning for warning in data["warnings"])
