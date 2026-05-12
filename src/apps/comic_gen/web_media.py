import os
import re
import time
import uuid
from dataclasses import asdict, dataclass
from typing import Dict, List
from urllib.parse import quote, urlparse

import requests

from ...utils import get_logger

logger = get_logger(__name__)


@dataclass
class WebMediaItem:
    """A downloaded or externally referenced media item ready for Studio use."""

    id: str
    type: str
    url: str
    remote_url: str
    title: str
    provider: str
    query: str
    license: str
    local_path: str = ""
    downloaded: bool = False


class WebMediaCollector:
    """Collect small public web images/videos for empty storyboard and motion stages."""

    DEFAULT_VIDEO_URLS = [
        "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4",
        "https://filesamples.com/samples/video/mp4/sample_640x360.mp4",
        "https://samplelib.com/lib/preview/mp4/sample-5s.mp4",
    ]

    def __init__(self, output_dir: str = "output/web_media"):
        self.output_dir = output_dir

    def collect(self, query: str, media_type: str = "image", count: int = 3) -> List[Dict[str, object]]:
        """Collect web media and return JSON-safe item dictionaries."""
        clean_type = media_type if media_type in {"image", "video", "both"} else "image"
        safe_count = max(1, min(int(count or 3), 8))
        clean_query = self._clean_query(query)
        requested_types = ["image", "video"] if clean_type == "both" else [clean_type]

        items: List[WebMediaItem] = []
        for item_type in requested_types:
            candidates = self._candidate_urls(item_type, clean_query, safe_count)
            for index, remote_url in enumerate(candidates[:safe_count]):
                items.append(self._collect_one(item_type, remote_url, clean_query, index))

        return [asdict(item) for item in items]

    def _candidate_urls(self, media_type: str, query: str, count: int) -> List[str]:
        """Resolve configurable provider URLs before using public defaults."""
        env_key = "AIDRAMA_WEB_IMAGE_URLS" if media_type == "image" else "AIDRAMA_WEB_VIDEO_URLS"
        configured = [
            value.strip()
            for value in os.getenv(env_key, "").split(",")
            if value.strip()
        ]
        if configured:
            return [self._format_provider_url(url, query, index) for index, url in enumerate(configured)]

        if media_type == "image":
            quoted = quote(query or "cinematic drama")
            return [
                f"https://picsum.photos/seed/aidrama-{quoted}-{index}/1280/720"
                for index in range(count)
            ]

        return [
            self.DEFAULT_VIDEO_URLS[index % len(self.DEFAULT_VIDEO_URLS)]
            for index in range(count)
        ]

    def _format_provider_url(self, template: str, query: str, index: int) -> str:
        """Support simple URL templates for private media providers."""
        return template.format(
            query=quote(query or "cinematic drama"),
            raw_query=query or "cinematic drama",
            index=index,
            seed=f"aidrama-{index}",
        )

    def _collect_one(self, media_type: str, remote_url: str, query: str, index: int) -> WebMediaItem:
        """Download a media item; keep the remote URL if the download fails."""
        item_id = f"web_{media_type}_{uuid.uuid4().hex[:10]}"
        provider = urlparse(remote_url).netloc or "web"
        try:
            local_url, local_path = self._download(remote_url, media_type, item_id)
            return WebMediaItem(
                id=item_id,
                type=media_type,
                url=local_url,
                remote_url=remote_url,
                local_path=local_path,
                title=f"{query} {media_type} {index + 1}",
                provider=provider,
                query=query,
                license="external web media; verify rights before publishing",
                downloaded=True,
            )
        except Exception as error:
            logger.warning("Web media download failed for %s: %s", remote_url, error)
            return WebMediaItem(
                id=item_id,
                type=media_type,
                url=remote_url,
                remote_url=remote_url,
                title=f"{query} {media_type} {index + 1}",
                provider=provider,
                query=query,
                license="external web media; verify rights before publishing",
                downloaded=False,
            )

    def _download(self, remote_url: str, media_type: str, item_id: str) -> tuple[str, str]:
        """Download with a small size cap so one click cannot fill the disk."""
        response = requests.get(
            remote_url,
            stream=True,
            allow_redirects=True,
            timeout=(5, 30),
            headers={"User-Agent": "AIDramaStudio/1.0"},
        )
        response.raise_for_status()

        content_type = response.headers.get("content-type", "").split(";")[0].lower()
        extension = self._extension_for(media_type, content_type, remote_url)
        sub_dir = "images" if media_type == "image" else "videos"
        output_dir = os.path.join(self.output_dir, sub_dir)
        os.makedirs(output_dir, exist_ok=True)

        filename = f"{item_id}{extension}"
        local_path = os.path.join(output_dir, filename)
        max_bytes = 12 * 1024 * 1024 if media_type == "image" else 48 * 1024 * 1024
        written = 0

        with open(local_path, "wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 64):
                if not chunk:
                    continue
                written += len(chunk)
                if written > max_bytes:
                    raise ValueError(f"{media_type} exceeds {max_bytes} byte limit")
                handle.write(chunk)

        if written == 0:
            raise ValueError("empty response body")

        relative = os.path.relpath(local_path, "output")
        return relative, local_path

    def _extension_for(self, media_type: str, content_type: str, remote_url: str) -> str:
        """Pick an extension from content type or URL path."""
        content_map = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
            "video/mp4": ".mp4",
            "video/webm": ".webm",
            "video/quicktime": ".mov",
        }
        if content_type in content_map:
            return content_map[content_type]

        suffix = os.path.splitext(urlparse(remote_url).path)[1].lower()
        if suffix in {".jpg", ".jpeg", ".png", ".webp", ".mp4", ".webm", ".mov"}:
            return ".jpg" if suffix == ".jpeg" else suffix
        return ".jpg" if media_type == "image" else ".mp4"

    def _clean_query(self, query: str) -> str:
        """Keep provider URLs readable and filesystem-neutral."""
        cleaned = re.sub(r"\s+", " ", (query or "cinematic drama").strip())
        return cleaned[:120] or f"cinematic drama {int(time.time())}"
