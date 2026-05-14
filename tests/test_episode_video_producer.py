import importlib.util
import shutil
import subprocess
from pathlib import Path

import pytest

from src.film_engine import (
    EpisodeProductionExtractor,
    EpisodeVideoProducer,
    EpisodeVideoProductionSettings,
    NovelEngine,
)


def _build_episode_packages(target_chapters: int = 2):
    """Create deterministic episode packages without external model calls."""
    plan = NovelEngine().expand(
        "Maya receives a call from a dead customer and follows the signal into a hidden archive.",
        title="Night Signal Video Test",
        target_chapters=target_chapters,
    )
    return EpisodeProductionExtractor().extract(plan)


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg is required")
@pytest.mark.skipif(importlib.util.find_spec("PIL") is None, reason="pillow is required")
def test_episode_video_producer_writes_playable_multi_episode_mp4s(tmp_path):
    """Episode production packages should become real mp4 files and manifests."""
    settings = EpisodeVideoProductionSettings(
        output_root=str(tmp_path / "productions"),
        width=360,
        height=640,
        fps=12,
        frame_seconds=0.5,
    )
    run = EpisodeVideoProducer().produce_packages(
        title="Night Signal Video Test",
        packages=_build_episode_packages(2),
        settings=settings,
    )

    assert run.status == "completed"
    assert len(run.episodes) == 2
    assert Path(run.series_manifest_path).exists()

    for episode in run.episodes:
        video_path = Path(episode.video_path)
        manifest_path = Path(episode.manifest_path)
        assert video_path.exists()
        assert video_path.stat().st_size > 1000
        assert manifest_path.exists()
        assert episode.video_url.endswith(".mp4")
        assert episode.frame_count == 3
        assert episode.duration_seconds > 0

        if shutil.which("ffprobe"):
            probe = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-select_streams",
                    "v:0",
                    "-show_entries",
                    "stream=codec_name,width,height",
                    "-of",
                    "csv=p=0",
                    str(video_path),
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert probe.returncode == 0
            assert "h264" in probe.stdout


def test_episode_video_producer_rejects_empty_package_list(tmp_path):
    """The producer should fail fast when no episode packages are provided."""
    settings = EpisodeVideoProductionSettings(output_root=str(tmp_path / "productions"))

    with pytest.raises(ValueError, match="At least one episode package"):
        EpisodeVideoProducer(ffmpeg_path=shutil.which("ffmpeg") or "ffmpeg").produce_packages(
            title="Empty",
            packages=[],
            settings=settings,
        )
