from __future__ import annotations

import re
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class NovelRelationship(BaseModel):
    """A lightweight relationship edge extracted or inferred from source text."""

    source: str
    target: str
    relationship: str = "story_link"
    tension: str = "unknown"


class NovelChapter(BaseModel):
    """Editable novel chapter artifact used before storyboard compilation."""

    chapter_id: str
    order: int
    title: str
    summary: str
    prose: str
    cliffhanger: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NovelPlan(BaseModel):
    """World bible, relationship graph and chapter outline generated from seed text."""

    title: str
    seed_text: str
    premise: str
    world_bible: Dict[str, Any] = Field(default_factory=dict)
    relationship_graph: Dict[str, Any] = Field(default_factory=dict)
    chapters: List[NovelChapter] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NovelEngine:
    """Deterministic Novel Engine for text-to-drama bootstrapping."""

    _CHAPTER_ARCS = (
        ("Hook", "Open with the strongest visual disturbance."),
        ("Escalation", "Raise stakes through a choice, clue or confrontation."),
        ("Reversal", "Reveal that the first explanation was incomplete."),
        ("Crisis", "Force the protagonist to pay a price."),
        ("Cliffhanger", "Close with a concrete next-episode question."),
    )

    def expand(self, seed_text: str, *, title: str = "Untitled AI Drama", target_chapters: int = 3) -> NovelPlan:
        """Expand one source idea into an editable novel production plan."""
        cleaned = self._normalize_text(seed_text)
        if not cleaned:
            raise ValueError("seed_text cannot be empty")

        chapter_count = max(1, min(int(target_chapters or 3), 12))
        sentences = self._split_sentences(cleaned)
        characters = self._extract_characters(cleaned)
        chapters = self._build_chapters(cleaned, sentences, chapter_count)
        relationships = self._build_relationships(characters)

        return NovelPlan(
            title=title.strip() or "Untitled AI Drama",
            seed_text=cleaned,
            premise=self._summarize(cleaned, 160),
            world_bible={
                "genre": self._infer_genre(cleaned),
                "format": "vertical AI mini-drama",
                "visual_style": "cinematic, continuity-first, production-bible driven",
                "core_conflict": self._summarize(cleaned, 96),
                "continuity_rules": [
                    "Keep character identity stable across chapters and shots.",
                    "Lock any signature prop before image or video generation.",
                    "Preserve scene lighting and time-of-day unless the story explicitly changes it.",
                ],
            },
            relationship_graph={
                "characters": characters,
                "relationships": [edge.model_dump(mode="json") for edge in relationships],
            },
            chapters=chapters,
            metadata={
                "engine": "novel_engine.v1",
                "target_chapters": chapter_count,
                "source_chars": len(cleaned),
            },
        )

    def to_screenplay(self, plan: NovelPlan) -> str:
        """Compile a novel plan into screenplay text for FilmProductionPipeline."""
        lines: List[str] = []
        protagonist = (plan.relationship_graph.get("characters") or ["Protagonist"])[0]

        for chapter in plan.chapters:
            scene_id = f"INT. CHAPTER {chapter.order:02d} - CONTINUITY SPACE"
            dialogue_summary = self._strip_speaker_prefix(chapter.summary, protagonist)
            lines.extend(
                [
                    scene_id,
                    f"{protagonist}: {dialogue_summary}",
                    chapter.prose,
                    f"Narrator: {chapter.cliffhanger}",
                    "",
                ]
            )

        return "\n".join(lines).strip()

    def _normalize_text(self, text: str) -> str:
        """Normalize whitespace while preserving author intent."""
        return re.sub(r"\s+", " ", (text or "").strip())

    def _split_sentences(self, text: str) -> List[str]:
        """Split source text into reusable narrative fragments."""
        parts = re.split(r"(?<=[。！？.!?])\s+|\n+", text)
        return [part.strip(" -") for part in parts if part.strip(" -")]

    def _extract_characters(self, text: str) -> List[str]:
        """Extract likely character names from dialogue prefixes and fallback roles."""
        names = []
        for match in re.finditer(r"([A-Za-z][A-Za-z0-9_\-]{1,24}|[\u4e00-\u9fff]{2,6})[:：]", text):
            candidate = match.group(1).strip()
            if candidate not in names:
                names.append(candidate)

        if not names:
            names = ["Protagonist", "Antagonist"]
        elif len(names) == 1:
            names.append("Hidden Opponent")
        return names[:8]

    def _build_relationships(self, characters: List[str]) -> List[NovelRelationship]:
        """Create a simple graph so later systems have stable relationship nodes."""
        if len(characters) < 2:
            return []
        protagonist = characters[0]
        return [
            NovelRelationship(
                source=protagonist,
                target=target,
                relationship="conflict_or_secret",
                tension="rising",
            )
            for target in characters[1:]
        ]

    def _build_chapters(self, text: str, sentences: List[str], count: int) -> List[NovelChapter]:
        """Build chapter outlines from source fragments and dramatic arc slots."""
        fragments = sentences or [text]
        chapters: List[NovelChapter] = []
        for index in range(count):
            arc_name, arc_rule = self._CHAPTER_ARCS[min(index, len(self._CHAPTER_ARCS) - 1)]
            fragment = fragments[index % len(fragments)]
            summary = self._summarize(fragment, 90)
            chapters.append(
                NovelChapter(
                    chapter_id=f"chapter_{index + 1:02d}",
                    order=index + 1,
                    title=f"EP{index + 1:02d} {arc_name}",
                    summary=summary,
                    prose=(
                        f"{arc_rule} The scene develops from this source idea: {summary}. "
                        "Each beat should be staged as a short, shootable visual moment."
                    ),
                    cliffhanger=self._cliffhanger_for(index, count, summary),
                    metadata={"arc": arc_name, "source_fragment": fragment},
                )
            )
        return chapters

    def _summarize(self, text: str, limit: int) -> str:
        """Return a compact summary without calling an external model."""
        compact = self._normalize_text(text)
        return compact[:limit].rstrip() + ("..." if len(compact) > limit else "")

    def _strip_speaker_prefix(self, text: str, speaker: str) -> str:
        """Avoid duplicated `Speaker: Speaker:` dialogue in compiled scripts."""
        pattern = rf"^\s*{re.escape(speaker)}\s*[:：]\s*"
        return re.sub(pattern, "", text, flags=re.IGNORECASE).strip() or text

    def _infer_genre(self, text: str) -> str:
        """Infer a coarse genre label for downstream art direction defaults."""
        lowered = text.lower()
        if any(token in lowered for token in ("murder", "dead", "secret", "phone", "mystery")):
            return "urban suspense"
        if any(token in lowered for token in ("contract", "wedding", "love", "bride")):
            return "romance revenge"
        if any(token in lowered for token in ("magic", "ghost", "future", "dream")):
            return "urban fantasy"
        return "character-driven drama"

    def _cliffhanger_for(self, index: int, count: int, summary: str) -> str:
        """Create an episode-ending question that keeps the production editable."""
        if index + 1 >= count:
            return f"The immediate mystery resolves, but a larger question remains: what did '{summary}' really cost?"
        return f"End this chapter on a concrete unresolved image tied to: {summary}"
