from __future__ import annotations

from collections import Counter
from typing import Dict, List

from .models import DirectorProgram, DirectorScene, DirectorShot, ShotTransition, StoryBeat, StoryGraph


class DirectorPlanner:
    """Turn story beats into a shootable Director DSL program."""

    _SHOT_RULES: Dict[str, Dict[str, str]] = {
        "setup": {
            "type": "establishing",
            "framing": "wide",
            "movement": "slow_dolly_in",
            "lens": "24mm",
        },
        "development": {
            "type": "dialogue",
            "framing": "medium",
            "movement": "locked_off",
            "lens": "35mm",
        },
        "turning_point": {
            "type": "reaction",
            "framing": "closeup",
            "movement": "push_in",
            "lens": "50mm",
        },
        "climax": {
            "type": "action",
            "framing": "medium_wide",
            "movement": "tracking",
            "lens": "28mm",
        },
        "resolution": {
            "type": "release",
            "framing": "wide",
            "movement": "static",
            "lens": "35mm",
        },
    }

    _PACING_BY_EMOTION: Dict[str, str] = {
        "suspense": "slow_burn",
        "conflict": "urgent",
        "romance": "gentle",
        "grief": "held",
        "triumph": "rising",
        "neutral": "medium",
    }

    def plan(self, story_graph: StoryGraph, *, sequence_id: str | None = None) -> DirectorProgram:
        shot_list = [
            self._beat_to_shot(beat=beat, index=index)
            for index, beat in enumerate(story_graph.beats, start=1)
        ]
        transitions = [
            ShotTransition(
                from_shot=shot_list[index].id,
                to_shot=shot_list[index + 1].id,
                transition_type=self._transition_for_edge(index, story_graph),
                metadata={"story_edge": index},
            )
            for index in range(len(shot_list) - 1)
        ]
        scene = self._plan_scene(story_graph)
        characters = sorted({character for beat in story_graph.beats for character in beat.characters})
        props = sorted(
            {
                prop_id
                for beat in story_graph.beats
                for prop_id in beat.metadata.get("prop_ids", [])
            }
        )
        costumes = sorted(
            {
                costume_id
                for beat in story_graph.beats
                for costume_id in beat.metadata.get("costume_ids", [])
            }
        )
        return DirectorProgram(
            sequence_id=sequence_id or story_graph.graph_id,
            scene=scene,
            characters=characters,
            props=props,
            costumes=costumes,
            shots=shot_list,
            transitions=transitions,
            metadata={
                "story_graph_id": story_graph.graph_id,
                "planner_version": "director_planner.v1",
                "continuity_strategy": "inherit_story_graph_entities",
                "shot_count": len(shot_list),
            },
        )

    def _plan_scene(self, story_graph: StoryGraph) -> DirectorScene:
        first_scene_hint = story_graph.beats[0].scene_hint if story_graph.beats else "story_space"
        emotion_counts = Counter(beat.emotional_intent for beat in story_graph.beats)
        dominant_emotion = emotion_counts.most_common(1)[0][0] if emotion_counts else "neutral"
        return DirectorScene(
            id=first_scene_hint or story_graph.graph_id,
            location=first_scene_hint or "story_space",
            mood=dominant_emotion,
            pacing=self._PACING_BY_EMOTION.get(dominant_emotion, "medium"),
            camera_style="continuity_first_cinematic",
            metadata={
                "story_graph_id": story_graph.graph_id,
                "scene_source": "first_story_beat",
            },
        )

    def _beat_to_shot(self, *, beat: StoryBeat, index: int) -> DirectorShot:
        rule = self._SHOT_RULES.get(beat.narrative_function, self._SHOT_RULES["development"])
        target = beat.characters[0] if beat.characters else None
        return DirectorShot(
            id=f"shot_{index:03d}",
            type=rule["type"],
            framing=rule["framing"],
            movement=rule["movement"],
            lens=rule["lens"],
            target=target,
            duration=self._duration_for_beat(beat),
            emotion=beat.emotional_intent,
            pacing=self._PACING_BY_EMOTION.get(beat.emotional_intent, "medium"),
            action=beat.summary,
            dialogue=self._dialogue_hint(beat),
            prop_ids=list(beat.metadata.get("prop_ids", [])),
            costume_ids=list(beat.metadata.get("costume_ids", [])),
            metadata={
                "story_beat_id": beat.id,
                "narrative_function": beat.narrative_function,
                "scene_hint": beat.scene_hint,
            },
        )

    def _duration_for_beat(self, beat: StoryBeat) -> float:
        if beat.narrative_function in {"turning_point", "climax"}:
            return 5.0
        if beat.emotional_intent in {"grief", "romance"}:
            return 4.5
        return 4.0

    def _dialogue_hint(self, beat: StoryBeat) -> str | None:
        if not beat.metadata.get("has_dialogue"):
            return None
        return beat.source_text.splitlines()[0].strip()

    def _transition_for_edge(self, index: int, story_graph: StoryGraph) -> str:
        if index >= len(story_graph.edges):
            return "cut"
        edge = story_graph.edges[index]
        return "match_cut" if edge.metadata.get("continuity") == "sequential" else "cut"
