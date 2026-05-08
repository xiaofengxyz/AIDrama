import importlib.util

import pytest
from fastapi.testclient import TestClient

DASHSCOPE_AVAILABLE = importlib.util.find_spec("dashscope") is not None
pytestmark = pytest.mark.skipif(
    not DASHSCOPE_AVAILABLE,
    reason="dashscope is required to import the full FastAPI app",
)

if DASHSCOPE_AVAILABLE:
    from src.apps.comic_gen.api import app
else:
    app = None


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
