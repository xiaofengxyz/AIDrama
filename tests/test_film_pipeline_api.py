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
