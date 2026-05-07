from __future__ import annotations

import time
from typing import Any, Dict, Iterable

from .models import CharacterAsset, DirectorScene, DirectorShot, FilmState, QAReport, RuntimeResult, SceneAsset


class FilmStateEngine:
    """State-centric continuity tracker for the Film Core."""

    def __init__(self, initial_state: FilmState | None = None):
        self.state = initial_state or FilmState()

    def register_characters(self, characters: Iterable[CharacterAsset]) -> None:
        for character in characters:
            self.state.character_states.setdefault(
                character.id,
                {
                    "name": character.name or character.id,
                    "outfits": list(character.outfits),
                    "locked_traits": list(character.locked_traits),
                    "last_seen_shot": None,
                },
            )
        self._touch()

    def register_scene(self, scene: SceneAsset | DirectorScene) -> None:
        self.state.scene_states.setdefault(
            scene.id,
            {
                "location": getattr(scene, "location", ""),
                "mood": getattr(scene, "mood", ""),
                "lighting": getattr(scene, "lighting", None),
                "weather": getattr(scene, "weather", None),
            },
        )
        self._touch()

    def snapshot(self) -> Dict[str, Any]:
        return self.state.model_dump()

    def apply_success(
        self,
        scene: DirectorScene,
        shot: DirectorShot,
        characters: Iterable[CharacterAsset],
        result: RuntimeResult,
        report: QAReport,
    ) -> None:
        self.state.active_scene_id = scene.id
        self.register_scene(scene)
        for character in characters:
            self.state.character_states.setdefault(character.id, {})
            self.state.character_states[character.id].update(
                {
                    "name": character.name or character.id,
                    "outfits": list(character.outfits),
                    "last_seen_shot": shot.id,
                    "last_emotion": shot.emotion,
                }
            )
        self.state.timeline.append(
            {
                "shot_id": shot.id,
                "scene_id": scene.id,
                "character_ids": [character.id for character in characters],
                "output_uri": result.output_uri,
                "qa_score": report.score,
                "timestamp": time.time(),
            }
        )
        self._touch()

    def _touch(self) -> None:
        self.state.updated_at = time.time()
