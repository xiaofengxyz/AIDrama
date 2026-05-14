#!/usr/bin/env python3
"""Produce playable local mp4 episodes from one Auto Drama seed idea."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.film_engine import (  # noqa: E402
    AutoDramaPipeline,
    EpisodeVideoProducer,
    EpisodeVideoProductionSettings,
    RetryPolicy,
    RuntimeBackend,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the command line argument parser for local video production."""
    parser = argparse.ArgumentParser(
        description="Generate a multi-episode Auto Drama production and playable local mp4 files."
    )
    parser.add_argument("--title", default="Night Signal Direct Production")
    parser.add_argument(
        "--seed-text",
        default=(
            "A courier receives a phone call from a customer who died ten years ago, "
            "then follows the signal into a locked city archive."
        ),
    )
    parser.add_argument("--episodes", type=int, default=3)
    parser.add_argument("--frame-seconds", type=float, default=1.6)
    parser.add_argument("--width", type=int, default=720)
    parser.add_argument("--height", type=int, default=1280)
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--output-root", default="output/productions")
    parser.add_argument("--discard-intermediates", action="store_true")
    return parser


def main() -> int:
    """Run Auto Drama and emit a concise JSON summary for automation."""
    args = build_parser().parse_args()
    prompt_root = PROJECT_ROOT / "docs" / "Codex_Workflow_Prompts"
    auto_run = AutoDramaPipeline(prompt_root=prompt_root).run(
        args.seed_text,
        title=args.title,
        target_chapters=args.episodes,
        backend=RuntimeBackend.DRY_RUN,
        retry_policy=RetryPolicy(max_attempts=2, min_score=0.82),
    )
    settings = EpisodeVideoProductionSettings(
        output_root=args.output_root,
        width=args.width,
        height=args.height,
        fps=args.fps,
        frame_seconds=args.frame_seconds,
        keep_intermediate_clips=not args.discard_intermediates,
    )
    video_run = EpisodeVideoProducer().produce_auto_run(auto_run, settings)
    summary = {
        "status": video_run.status,
        "title": video_run.title,
        "run_id": video_run.run_id,
        "series_manifest_path": video_run.series_manifest_path,
        "series_manifest_url": video_run.series_manifest_url,
        "episodes": [
            {
                "order": episode.order,
                "title": episode.title,
                "video_path": episode.video_path,
                "video_url": episode.video_url,
                "duration_seconds": episode.duration_seconds,
            }
            for episode in video_run.episodes
        ],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
