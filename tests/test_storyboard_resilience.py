import importlib.util

import pytest

from src.apps.comic_gen.llm import ScriptProcessor


DASHSCOPE_AVAILABLE = importlib.util.find_spec("dashscope") is not None


def test_storyboard_parser_accepts_top_level_array_and_missing_action():
    """Messy but useful LLM output should still become usable frames."""
    processor = ScriptProcessor()

    frames = processor._parse_storyboard_json(
        """
        [
          {
            "scene_ref_name": "天台",
            "character_ref_names": "林夏",
            "prop_ref_names": ["旧手机"],
            "character_acting": "林夏屏住呼吸看向屏幕",
            "key_action_physics": "旧手机在掌心持续震动",
            "shot_size": "特写"
          },
        ]
        """
    )

    assert frames is not None
    assert frames[0]["character_ref_names"] == ["林夏"]
    assert "旧手机" in frames[0]["action_description"]


@pytest.mark.skipif(
    not DASHSCOPE_AVAILABLE,
    reason="dashscope is required to import the full ComicGenPipeline",
)
def test_storyboard_analysis_creates_editable_entities_for_draft_project(tmp_path):
    """Draft projects without prior entity extraction should not block storyboard generation."""
    from src.apps.comic_gen.pipeline import ComicGenPipeline

    pipeline = ComicGenPipeline()
    pipeline.data_file = str(tmp_path / "projects.json")
    pipeline.series_data_file = str(tmp_path / "series.json")
    pipeline.scripts = {}
    pipeline.series_store = {}

    project = pipeline.create_project(
        "夜半信号",
        "林夏握着旧手机站在天台边缘，屏幕亮起十年前的来电。",
        skip_analysis=True,
    )
    pipeline.script_processor.analyze_to_storyboard = lambda *_args, **_kwargs: [
        {
            "scene_ref_name": "天台",
            "character_ref_names": ["林夏"],
            "prop_ref_names": ["旧手机"],
            "visual_atmosphere": "冷蓝色夜景，城市灯光在远处闪烁",
            "action_description": "林夏握着旧手机站在天台边缘，屏幕亮起十年前的来电",
            "shot_size": "中景",
            "camera_angle": "平视",
            "camera_movement": "缓慢推镜",
        }
    ]

    updated = pipeline.analyze_text_to_frames(project.id, project.original_text)

    assert updated.frames[0].action_description.startswith("林夏握着旧手机")
    assert updated.scenes[0].name == "天台"
    assert updated.characters[0].name == "林夏"
    assert updated.props[0].name == "旧手机"
    assert updated.frames[0].image_prompt
