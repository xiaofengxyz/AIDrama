import importlib.util

import pytest

from src.apps.comic_gen.web_media import WebMediaCollector


DASHSCOPE_AVAILABLE = importlib.util.find_spec("dashscope") is not None


class _FakeResponse:
    def __init__(self, body: bytes, content_type: str = "image/png"):
        self.body = body
        self.headers = {"content-type": content_type}

    def raise_for_status(self):
        return None

    def iter_content(self, chunk_size=65536):
        yield self.body


def test_web_media_collector_downloads_images_to_output(monkeypatch, tmp_path):
    """Collected images should become local /files-compatible output paths."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "src.apps.comic_gen.web_media.requests.get",
        lambda *_args, **_kwargs: _FakeResponse(b"fake-image"),
    )

    collector = WebMediaCollector()
    items = collector.collect("night corridor", "image", 1)

    assert items[0]["type"] == "image"
    assert items[0]["downloaded"] is True
    assert items[0]["url"].startswith("web_media/images/")


def test_web_media_collector_keeps_remote_url_when_download_fails(monkeypatch):
    """A provider outage should not make the UI button useless."""
    def fail_get(*_args, **_kwargs):
        raise RuntimeError("network unavailable")

    monkeypatch.setattr("src.apps.comic_gen.web_media.requests.get", fail_get)

    collector = WebMediaCollector()
    items = collector.collect("reference motion", "video", 1)

    assert items[0]["type"] == "video"
    assert items[0]["downloaded"] is False
    assert items[0]["url"].startswith("https://")


@pytest.mark.skipif(
    not DASHSCOPE_AVAILABLE,
    reason="dashscope is required to import the full ComicGenPipeline",
)
def test_pipeline_attaches_collected_images_to_missing_storyboard_frames(tmp_path):
    """Storyboard web collection should fill only frames that have no image yet."""
    from src.apps.comic_gen.pipeline import ComicGenPipeline

    pipeline = ComicGenPipeline()
    pipeline.data_file = str(tmp_path / "projects.json")
    pipeline.series_data_file = str(tmp_path / "series.json")
    pipeline.scripts = {}
    pipeline.series_store = {}

    project = pipeline.create_project("Web Fill", "Maya enters the corridor.", skip_analysis=True)
    project = pipeline.add_frame(project.id, action_description="Maya enters the corridor")

    updated = pipeline.attach_web_images_to_storyboard(
        project.id,
        [{"type": "image", "url": "web_media/images/frame.png"}],
    )

    assert updated.frames[0].image_url == "web_media/images/frame.png"
    assert updated.frames[0].rendered_image_asset.selected_id
