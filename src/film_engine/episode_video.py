from __future__ import annotations

import json
import re
import shutil
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .auto_drama import AutoDramaRun
from .production_extraction import EpisodeProductionPackage, ExtractedStoryboardFrame


class EpisodeVideoProductionSettings(BaseModel):
    """Runtime settings for deterministic local episode video production."""

    output_root: str = Field(
        "output/productions",
        description="Directory where production runs should be written.",
    )
    width: int = Field(720, ge=320, le=3840, description="Output video width in pixels.")
    height: int = Field(1280, ge=320, le=3840, description="Output video height in pixels.")
    fps: int = Field(24, ge=12, le=60, description="Frames per second for generated mp4 clips.")
    frame_seconds: float = Field(
        1.6,
        ge=0.4,
        le=12.0,
        description="Duration of each storyboard frame clip in seconds.",
    )
    keep_intermediate_clips: bool = Field(
        True,
        description="Keep generated frame PNGs and per-frame clips for QA traceability.",
    )
    crf: int = Field(23, ge=16, le=35, description="H.264 quality level for FFmpeg encoding.")


class EpisodeVideoArtifact(BaseModel):
    """A generated video artifact and manifest for one episode."""

    episode_id: str
    order: int
    title: str
    video_url: str
    video_path: str
    manifest_url: str
    manifest_path: str
    frame_image_urls: List[str] = Field(default_factory=list)
    clip_urls: List[str] = Field(default_factory=list)
    duration_seconds: float
    frame_count: int
    asset_counts: Dict[str, int] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SeriesVideoProductionRun(BaseModel):
    """The manifest-level result for a multi-episode local video production run."""

    status: str = "completed"
    title: str
    run_id: str
    output_dir: str
    series_manifest_url: str
    series_manifest_path: str
    episodes: List[EpisodeVideoArtifact] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EpisodeVideoProducer:
    """Produce playable mp4 samples from Auto Drama episode production packages."""

    def __init__(self, ffmpeg_path: Optional[str] = None):
        """Initialize the producer with an optional explicit FFmpeg binary."""
        self.ffmpeg_path = ffmpeg_path or shutil.which("ffmpeg")
        self.ffprobe_path = shutil.which("ffprobe")

    def produce_auto_run(
        self,
        auto_run: AutoDramaRun,
        settings: Optional[EpisodeVideoProductionSettings] = None,
    ) -> SeriesVideoProductionRun:
        """Produce a local video run from a completed Auto Drama dry-run."""
        if not auto_run.episode_packages:
            raise ValueError("Auto Drama run does not contain episode production packages")
        return self.produce_packages(
            title=auto_run.title,
            packages=auto_run.episode_packages,
            settings=settings or EpisodeVideoProductionSettings(),
            metadata={
                "source": "auto_drama_pipeline",
                "auto_drama_status": auto_run.status,
                "prompt_execution_status": auto_run.prompt_execution_plan.status,
                "novel_title": auto_run.novel_plan.title if auto_run.novel_plan else auto_run.title,
            },
        )

    def produce_packages(
        self,
        *,
        title: str,
        packages: List[EpisodeProductionPackage],
        settings: EpisodeVideoProductionSettings,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SeriesVideoProductionRun:
        """Produce all episode mp4 files and a series-level manifest."""
        self._require_ffmpeg()
        if not packages:
            raise ValueError("At least one episode package is required for video production")

        run_id = self._build_run_id(title)
        output_dir = Path(settings.output_root) / run_id
        output_dir.mkdir(parents=True, exist_ok=True)

        episodes = [
            self._produce_episode(
                title=title,
                package=package,
                output_dir=output_dir,
                settings=settings,
            )
            for package in packages
        ]
        series_run = SeriesVideoProductionRun(
            title=title,
            run_id=run_id,
            output_dir=str(output_dir),
            series_manifest_url=self._url_for_path(output_dir / "series_manifest.json"),
            series_manifest_path=str(output_dir / "series_manifest.json"),
            episodes=episodes,
            metadata={
                "producer": "episode_video_producer.v1",
                "created_at": time.time(),
                "episode_count": len(episodes),
                "settings": settings.model_dump(mode="json"),
                **(metadata or {}),
            },
        )
        self._write_json(output_dir / "series_manifest.json", series_run.model_dump(mode="json"))
        return series_run

    def _produce_episode(
        self,
        *,
        title: str,
        package: EpisodeProductionPackage,
        output_dir: Path,
        settings: EpisodeVideoProductionSettings,
    ) -> EpisodeVideoArtifact:
        """Render frame slates, encode clips, merge them, and write one episode manifest."""
        episode_slug = (
            self._slug(f"ep{package.order:02d}_{package.title}") or f"ep{package.order:02d}"
        )
        episode_dir = output_dir / "episodes" / episode_slug
        frame_dir = episode_dir / "frames"
        clip_dir = episode_dir / "clips"
        frame_dir.mkdir(parents=True, exist_ok=True)
        clip_dir.mkdir(parents=True, exist_ok=True)

        frame_paths = []
        clip_paths = []
        frames = package.storyboard_frames or self._fallback_frames(package)
        for index, frame in enumerate(frames, start=1):
            frame_path = self._render_frame_image(
                series_title=title,
                package=package,
                frame=frame,
                frame_index=index,
                output_dir=frame_dir,
                settings=settings,
            )
            clip_path = clip_dir / f"clip_{index:02d}.mp4"
            self._encode_image_clip(frame_path, clip_path, settings)
            frame_paths.append(frame_path)
            clip_paths.append(clip_path)

        video_path = episode_dir / f"{episode_slug}.mp4"
        self._concat_clips(clip_paths, video_path, settings)

        frame_urls = [self._url_for_path(path) for path in frame_paths]
        clip_urls = [self._url_for_path(path) for path in clip_paths]
        if not settings.keep_intermediate_clips:
            self._cleanup_intermediates([*frame_paths, *clip_paths])
            frame_urls = []
            clip_urls = []

        artifact = EpisodeVideoArtifact(
            episode_id=package.episode_id,
            order=package.order,
            title=package.title,
            video_url=self._url_for_path(video_path),
            video_path=str(video_path),
            manifest_url=self._url_for_path(episode_dir / "episode_manifest.json"),
            manifest_path=str(episode_dir / "episode_manifest.json"),
            frame_image_urls=frame_urls,
            clip_urls=clip_urls,
            duration_seconds=self._probe_duration(video_path)
            or round(len(frames) * settings.frame_seconds, 3),
            frame_count=len(frames),
            asset_counts={
                "characters": len(package.characters),
                "scenes": len(package.scenes),
                "props": len(package.props),
                "costumes": len(package.costumes),
                "special_effects": len(package.special_effects),
            },
            metadata={
                "producer": "episode_video_producer.v1",
                "summary": package.summary,
                "script_text": package.script_text,
                "created_at": time.time(),
            },
        )
        self._write_json(episode_dir / "episode_manifest.json", artifact.model_dump(mode="json"))
        return artifact

    def _render_frame_image(
        self,
        *,
        series_title: str,
        package: EpisodeProductionPackage,
        frame: ExtractedStoryboardFrame,
        frame_index: int,
        output_dir: Path,
        settings: EpisodeVideoProductionSettings,
    ) -> Path:
        """Render one storyboard frame as a production slate PNG."""
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError as error:
            raise RuntimeError("Pillow is required to render local episode frame images") from error

        width = settings.width
        height = settings.height
        image = Image.new("RGB", (width, height), color=(14, 18, 24))
        draw = ImageDraw.Draw(image)
        self._draw_gradient_background(draw, width, height, frame_index)

        title_font = self._load_font(ImageFont, 42)
        subtitle_font = self._load_font(ImageFont, 28)
        body_font = self._load_font(ImageFont, 24)
        small_font = self._load_font(ImageFont, 18)

        margin = max(32, int(width * 0.07))
        top = max(42, int(height * 0.06))
        accent = self._accent_color(frame_index)

        draw.rounded_rectangle(
            (margin, top, width - margin, top + 72),
            radius=18,
            fill=(18, 26, 34),
            outline=accent,
            width=2,
        )
        self._draw_text(
            draw,
            (margin + 24, top + 14),
            f"EP{package.order:02d}  {package.title}",
            title_font,
        )

        y = top + 104
        y = self._draw_wrapped_block(
            draw,
            text=series_title,
            position=(margin, y),
            font=subtitle_font,
            max_width=width - margin * 2,
            fill=(235, 240, 245),
            line_spacing=8,
        )
        y += 22

        role = str(frame.metadata.get("story_role", "story beat")).upper()
        draw.rectangle((margin, y, margin + 10, y + 36), fill=accent)
        self._draw_text(
            draw,
            (margin + 22, y + 2),
            f"{role} / FRAME {frame_index:02d}",
            small_font,
            fill=accent,
        )
        y += 56

        y = self._draw_wrapped_block(
            draw,
            text=frame.action_description or package.summary,
            position=(margin, y),
            font=body_font,
            max_width=width - margin * 2,
            fill=(246, 248, 250),
            line_spacing=10,
        )
        y += 26

        detail_lines = [
            f"Camera: {frame.camera_angle} / {frame.camera_movement}",
            f"Atmosphere: {frame.visual_atmosphere}",
            f"Dialogue: {frame.dialogue}" if frame.dialogue else "",
        ]
        for line in [item for item in detail_lines if item]:
            y = self._draw_wrapped_block(
                draw,
                text=line,
                position=(margin, y),
                font=small_font,
                max_width=width - margin * 2,
                fill=(194, 205, 216),
                line_spacing=6,
            )
            y += 10

        footer = self._asset_footer(package)
        self._draw_wrapped_block(
            draw,
            text=footer,
            position=(margin, height - max(128, int(height * 0.12))),
            font=small_font,
            max_width=width - margin * 2,
            fill=(160, 174, 188),
            line_spacing=6,
        )

        output_path = output_dir / f"frame_{frame_index:02d}.png"
        image.save(output_path)
        return output_path

    def _draw_gradient_background(
        self,
        draw: Any,
        width: int,
        height: int,
        frame_index: int,
    ) -> None:
        """Paint a simple cinematic gradient without relying on external assets."""
        base_a = (12 + frame_index * 4, 17, 28)
        base_b = (34, 46 + frame_index * 3, 55)
        for y in range(height):
            ratio = y / max(height - 1, 1)
            color = tuple(
                int(base_a[channel] * (1 - ratio) + base_b[channel] * ratio)
                for channel in range(3)
            )
            draw.line((0, y, width, y), fill=color)

        for offset in range(0, width, max(80, width // 8)):
            alpha_color = self._accent_color((offset // max(width // 8, 1)) + frame_index)
            draw.line((offset, 0, max(0, offset - width // 3), height), fill=alpha_color, width=1)

    def _draw_wrapped_block(
        self,
        draw: Any,
        *,
        text: str,
        position: tuple[int, int],
        font: Any,
        max_width: int,
        fill: tuple[int, int, int],
        line_spacing: int,
    ) -> int:
        """Draw wrapped text and return the next y coordinate."""
        x, y = position
        for line in self._wrap_text(draw, text, font, max_width):
            self._draw_text(draw, (x, y), line, font, fill=fill)
            bbox = draw.textbbox((x, y), line, font=font)
            y += (bbox[3] - bbox[1]) + line_spacing
        return y

    def _draw_text(
        self,
        draw: Any,
        position: tuple[int, int],
        text: str,
        font: Any,
        fill: tuple[int, int, int] = (248, 250, 252),
    ) -> None:
        """Draw text while falling back to ASCII if the active font rejects glyphs."""
        try:
            draw.text(position, text, font=font, fill=fill)
        except UnicodeEncodeError:
            safe_text = text.encode("ascii", "ignore").decode("ascii") or "Production beat"
            draw.text(position, safe_text, font=font, fill=fill)

    def _wrap_text(self, draw: Any, text: str, font: Any, max_width: int) -> List[str]:
        """Wrap mixed Chinese/English text by measured pixel width."""
        cleaned = " ".join((text or "").split())
        if not cleaned:
            return [""]

        lines: List[str] = []
        current = ""
        for token in self._wrap_tokens(cleaned):
            candidate = (
                f"{current}{token}"
                if self._is_cjk_token(token)
                else f"{current} {token}".strip()
            )
            if draw.textlength(candidate, font=font) <= max_width:
                current = candidate
                continue
            if current:
                lines.append(current)
            current = token.strip()
        if current:
            lines.append(current)
        return lines

    def _wrap_tokens(self, text: str) -> List[str]:
        """Tokenize text into words while allowing CJK characters to wrap naturally."""
        tokens: List[str] = []
        buffer = ""
        for char in text:
            if "\u4e00" <= char <= "\u9fff":
                if buffer:
                    tokens.extend(buffer.split())
                    buffer = ""
                tokens.append(char)
            else:
                buffer += char
        if buffer:
            tokens.extend(buffer.split())
        return tokens

    def _is_cjk_token(self, token: str) -> bool:
        """Return whether a wrapping token is a CJK character."""
        return len(token) == 1 and "\u4e00" <= token <= "\u9fff"

    def _encode_image_clip(
        self,
        image_path: Path,
        clip_path: Path,
        settings: EpisodeVideoProductionSettings,
    ) -> None:
        """Encode a single image into a short playable H.264 mp4 clip."""
        cmd = [
            self.ffmpeg_path,
            "-y",
            "-loop",
            "1",
            "-framerate",
            str(settings.fps),
            "-t",
            f"{settings.frame_seconds:.3f}",
            "-i",
            str(image_path),
            "-vf",
            f"scale={settings.width}:{settings.height}:force_original_aspect_ratio=decrease,"
            f"pad={settings.width}:{settings.height}:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
            "-c:v",
            "libx264",
            "-crf",
            str(settings.crf),
            "-preset",
            "veryfast",
            "-r",
            str(settings.fps),
            "-an",
            str(clip_path),
        ]
        self._run_command(cmd, f"encode clip {clip_path.name}")

    def _concat_clips(
        self,
        clip_paths: List[Path],
        output_path: Path,
        settings: EpisodeVideoProductionSettings,
    ) -> None:
        """Merge encoded clips into the final episode mp4."""
        if not clip_paths:
            raise ValueError("No clips were generated for episode merge")

        list_path = output_path.with_suffix(".concat.txt")
        list_path.write_text(
            "\n".join(f"file '{self._escape_concat_path(path)}'" for path in clip_paths) + "\n",
            encoding="utf-8",
        )
        cmd = [
            self.ffmpeg_path,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_path),
            "-c:v",
            "libx264",
            "-crf",
            str(settings.crf),
            "-preset",
            "veryfast",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            "-an",
            str(output_path),
        ]
        self._run_command(cmd, f"merge episode {output_path.name}")
        list_path.unlink(missing_ok=True)

    def _run_command(self, cmd: List[str], label: str) -> None:
        """Run FFmpeg and raise an actionable error when it fails."""
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            detail = result.stderr.strip()[-1200:] or result.stdout.strip()[-1200:]
            raise RuntimeError(f"FFmpeg failed to {label}: {detail}")

    def _probe_duration(self, video_path: Path) -> Optional[float]:
        """Read the actual mp4 duration with ffprobe when available."""
        if not self.ffprobe_path or not video_path.exists():
            return None
        cmd = [
            self.ffprobe_path,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return None
        try:
            return round(float(result.stdout.strip()), 3)
        except ValueError:
            return None

    def _require_ffmpeg(self) -> None:
        """Fail early with a clear message when FFmpeg is unavailable."""
        if not self.ffmpeg_path:
            raise RuntimeError(
                "FFmpeg is required to produce local episode videos but was not found"
            )

    def _fallback_frames(self, package: EpisodeProductionPackage) -> List[ExtractedStoryboardFrame]:
        """Create one minimal storyboard frame when a package lacks frame data."""
        return [
            ExtractedStoryboardFrame(
                frame_id=f"{package.episode_id}_fallback_frame",
                order=1,
                scene_ref="fallback_scene",
                action_description=package.summary or package.script_text,
                image_prompt=package.summary,
                video_prompt=package.summary,
                metadata={"story_role": "fallback"},
            )
        ]

    def _asset_footer(self, package: EpisodeProductionPackage) -> str:
        """Summarize production assets for the episode slate footer."""
        parts = [
            f"Characters {len(package.characters)}",
            f"Scenes {len(package.scenes)}",
            f"Props {len(package.props)}",
            f"Costumes {len(package.costumes)}",
            f"FX {len(package.special_effects)}",
        ]
        return " / ".join(parts)

    def _load_font(self, image_font_module: Any, size: int) -> Any:
        """Load a readable system font with CJK fallback when present."""
        candidates = [
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        for candidate in candidates:
            if Path(candidate).exists():
                return image_font_module.truetype(candidate, size=size)
        return image_font_module.load_default()

    def _accent_color(self, index: int) -> tuple[int, int, int]:
        """Pick a restrained accent color for a storyboard slate."""
        palette = [
            (72, 199, 184),
            (250, 173, 92),
            (129, 161, 255),
            (236, 112, 99),
        ]
        return palette[(index - 1) % len(palette)]

    def _cleanup_intermediates(self, paths: List[Path]) -> None:
        """Remove intermediate files after the episode mp4 has been merged."""
        for path in paths:
            path.unlink(missing_ok=True)

    def _write_json(self, path: Path, payload: Dict[str, Any]) -> None:
        """Write UTF-8 JSON manifests with stable indentation."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _build_run_id(self, title: str) -> str:
        """Create a unique and human-readable production run id."""
        slug = self._slug(title) or "auto_drama"
        return f"{slug}_{int(time.time())}_{uuid.uuid4().hex[:8]}"

    def _slug(self, value: str) -> str:
        """Create a filesystem-safe slug for generated output directories."""
        cleaned = re.sub(r"[^\w\u4e00-\u9fff]+", "_", (value or "").strip().lower())
        cleaned = re.sub(r"_+", "_", cleaned).strip("_")
        return cleaned[:72]

    def _url_for_path(self, path: Path) -> str:
        """Return a frontend-friendly output-relative URL when possible."""
        resolved = path.resolve()
        output_root = Path("output").resolve()
        try:
            return resolved.relative_to(output_root).as_posix()
        except ValueError:
            return str(path)

    def _escape_concat_path(self, path: Path) -> str:
        """Escape single quotes for FFmpeg concat list syntax."""
        return str(path.resolve()).replace("'", "'\\''")
