from __future__ import annotations

import re
from typing import Dict, Iterable, List

from .models import StoryBeat, StoryGraph, StoryGraphEdge


class StoryGraphBuilder:
    """Build a deterministic story graph from source script text."""

    _SPEAKER_PATTERN = re.compile(r"^\s*([\w\u4e00-\u9fff]{1,24})\s*[:：]", re.MULTILINE)
    _SCENE_PATTERN = re.compile(
        r"(?i)\b(?:int|ext)\.?\s+([^\n.]+)|(?:scene|location|setting)\s*[:：]\s*([^\n]+)"
    )
    _TAG_PATTERN = re.compile(r"\[(prop|costume)=([^\]]+)\]", flags=re.IGNORECASE)

    def build_from_script(
        self,
        text: str,
        *,
        graph_id: str = "story_default",
        source_title: str = "",
    ) -> StoryGraph:
        segments = self._split_into_beats(text)
        beats = [
            self._build_beat(index=index, segment=segment)
            for index, segment in enumerate(segments, start=1)
        ]
        edges = [
            StoryGraphEdge(
                from_beat=beats[index].id,
                to_beat=beats[index + 1].id,
                edge_type="next",
                metadata={"continuity": "sequential"},
            )
            for index in range(len(beats) - 1)
        ]
        adjacency = self._build_adjacency((beat.id for beat in beats), edges)
        self._validate_acyclic(adjacency)
        return StoryGraph(
            graph_id=graph_id,
            source_title=source_title,
            beats=beats,
            edges=edges,
            adjacency=adjacency,
            metadata={
                "source": "script",
                "beat_count": len(beats),
                "builder_version": "story_graph.v1",
            },
        )

    def _split_into_beats(self, text: str) -> List[str]:
        cleaned = text.strip()
        if not cleaned:
            raise ValueError("script text cannot be empty")

        paragraph_segments = [
            segment.strip()
            for segment in re.split(r"\n\s*\n+", cleaned)
            if segment.strip()
        ]
        if len(paragraph_segments) > 1:
            return paragraph_segments

        protected = re.sub(
            r"\b(INT|EXT)\.\s+",
            lambda match: f"{match.group(1)}__SCENE_DOT__ ",
            cleaned,
            flags=re.IGNORECASE,
        )
        sentence_segments = [
            segment.replace("__SCENE_DOT__", ".").strip()
            for segment in re.split(r"(?<=[.!?])\s+", protected)
            if segment.strip()
        ]
        return self._merge_asset_tag_segments(sentence_segments) or [cleaned]

    def _build_beat(self, *, index: int, segment: str) -> StoryBeat:
        characters = sorted(set(self._extract_characters(segment)))
        tagged_assets = self._extract_tagged_assets(segment)
        return StoryBeat(
            id=f"beat_{index:03d}",
            order=index,
            source_text=segment,
            summary=self._summarize(segment),
            scene_hint=self._extract_scene_hint(segment),
            characters=characters,
            emotional_intent=self._infer_emotion(segment),
            narrative_function=self._infer_narrative_function(index, segment),
            metadata={
                "source_length": len(segment),
                "has_dialogue": bool(characters),
                "prop_ids": tagged_assets["prop_ids"],
                "costume_ids": tagged_assets["costume_ids"],
            },
        )

    def _extract_characters(self, segment: str) -> List[str]:
        speaker_names = [match.strip() for match in self._SPEAKER_PATTERN.findall(segment)]
        tagged_names = re.findall(r"\[character=([^\]]+)\]", segment, flags=re.IGNORECASE)
        return [self._slugify(name) for name in [*speaker_names, *tagged_names] if name.strip()]

    def _extract_scene_hint(self, segment: str) -> str:
        match = self._SCENE_PATTERN.search(segment)
        if match:
            value = (match.group(1) or match.group(2) or "").strip()
            if value:
                return self._slugify(value)[:48]
        return "story_space"

    def _extract_tagged_assets(self, segment: str) -> Dict[str, List[str]]:
        props = []
        costumes = []
        for tag_type, raw_value in self._TAG_PATTERN.findall(segment):
            asset_id = self._slugify(raw_value)
            if tag_type.lower() == "prop":
                props.append(asset_id)
            else:
                costumes.append(asset_id)
        return {
            "prop_ids": sorted(set(props)),
            "costume_ids": sorted(set(costumes)),
        }

    def _merge_asset_tag_segments(self, segments: List[str]) -> List[str]:
        merged: List[str] = []
        for segment in segments:
            tagless = self._TAG_PATTERN.sub("", segment).strip()
            if not tagless and merged:
                merged[-1] = f"{merged[-1]} {segment}".strip()
            else:
                merged.append(segment)
        return merged

    def _infer_emotion(self, segment: str) -> str:
        lowered = segment.lower()
        buckets: Dict[str, tuple[str, ...]] = {
            "suspense": ("fear", "afraid", "shadow", "threat", "silence", "secret"),
            "conflict": ("argue", "fight", "chase", "betray", "gun", "knife"),
            "romance": ("love", "kiss", "promise", "heart", "tender"),
            "grief": ("cry", "loss", "funeral", "regret", "alone"),
            "triumph": ("win", "escape", "rescue", "victory", "reveal"),
        }
        for emotion, keywords in buckets.items():
            if any(keyword in lowered for keyword in keywords):
                return emotion
        return "neutral"

    def _infer_narrative_function(self, index: int, segment: str) -> str:
        lowered = segment.lower()
        if index == 1:
            return "setup"
        if any(token in lowered for token in ("but", "however", "suddenly", "then")):
            return "turning_point"
        if any(token in lowered for token in ("fight", "chase", "betray", "escape")):
            return "climax"
        if any(token in lowered for token in ("finally", "afterward", "dawn")):
            return "resolution"
        return "development"

    def _summarize(self, segment: str, *, limit: int = 120) -> str:
        compacted = " ".join(segment.split())
        if len(compacted) <= limit:
            return compacted
        return compacted[: limit - 3].rstrip() + "..."

    def _slugify(self, value: str) -> str:
        cleaned = re.sub(r"[^\w\u4e00-\u9fff]+", "_", value.strip().lower())
        cleaned = re.sub(r"_+", "_", cleaned).strip("_")
        return cleaned or "unknown"

    def _build_adjacency(
        self,
        beat_ids: Iterable[str],
        edges: Iterable[StoryGraphEdge],
    ) -> Dict[str, List[str]]:
        adjacency: Dict[str, List[str]] = {beat_id: [] for beat_id in beat_ids}
        for edge in edges:
            adjacency[edge.from_beat].append(edge.to_beat)
        return adjacency

    def _validate_acyclic(self, adjacency: Dict[str, List[str]]) -> None:
        visiting = set()
        visited = set()

        def visit(beat_id: str) -> None:
            if beat_id in visiting:
                raise ValueError(f"Story graph contains a cycle at {beat_id}")
            if beat_id in visited:
                return
            visiting.add(beat_id)
            for next_beat_id in adjacency.get(beat_id, []):
                visit(next_beat_id)
            visiting.remove(beat_id)
            visited.add(beat_id)

        for beat_id in adjacency:
            visit(beat_id)
