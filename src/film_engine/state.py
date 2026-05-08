from __future__ import annotations

import time
from typing import Any, Dict, Iterable

from .models import (
    CharacterAsset,
    CostumeAsset,
    DirectorScene,
    DirectorShot,
    FilmState,
    PropAsset,
    QAReport,
    RuntimeResult,
    SceneAsset,
)


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
                    "current_outfit": character.current_outfit,
                    "hairstyle": character.hairstyle,
                    "locked_traits": list(character.locked_traits),
                    "continuity_notes": list(character.continuity_notes),
                    "last_seen_shot": None,
                },
            )
            if character.locked_traits or character.current_outfit or character.hairstyle:
                character_locks = self.state.continuity_locks.setdefault("characters", {})
                character_locks.setdefault(character.id, {})
                character_locks[character.id].update(
                    {
                        key: value
                        for key, value in {
                            "locked_traits": list(character.locked_traits),
                            "current_outfit": character.current_outfit,
                            "hairstyle": character.hairstyle,
                        }.items()
                        if value
                    }
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
                "tone": getattr(scene, "tone", None),
                "time_of_day": getattr(scene, "time_of_day", None),
                "continuity_notes": list(getattr(scene, "continuity_notes", []) or []),
            },
        )
        scene_locks = {
            key: value
            for key, value in {
                "lighting": getattr(scene, "lighting", None),
                "weather": getattr(scene, "weather", None),
                "tone": getattr(scene, "tone", None),
                "time_of_day": getattr(scene, "time_of_day", None),
            }.items()
            if value
        }
        if scene_locks:
            self.state.continuity_locks.setdefault("scenes", {}).setdefault(scene.id, {})
            self.state.continuity_locks["scenes"][scene.id].update(scene_locks)
        self._touch()

    def register_assets(
        self,
        props: Iterable[PropAsset] | None = None,
        costumes: Iterable[CostumeAsset] | None = None,
    ) -> None:
        for prop in props or []:
            self.state.prop_states.setdefault(
                prop.id,
                {
                    "name": prop.name or prop.id,
                    "category": prop.category,
                    "signature_details": list(prop.signature_details),
                    "locked_traits": list(prop.locked_traits),
                    "continuity_notes": list(prop.continuity_notes),
                    "last_seen_shot": None,
                },
            )
            if prop.locked_traits or prop.signature_details:
                prop_locks = self.state.continuity_locks.setdefault("props", {})
                prop_locks.setdefault(prop.id, {})
                prop_locks[prop.id].update(
                    {
                        key: value
                        for key, value in {
                            "locked_traits": list(prop.locked_traits),
                            "signature_details": list(prop.signature_details),
                        }.items()
                        if value
                    }
                )

        for costume in costumes or []:
            self.state.costume_states.setdefault(
                costume.id,
                {
                    "name": costume.name or costume.id,
                    "wardrobe_role": costume.wardrobe_role,
                    "palette": list(costume.palette),
                    "materials": list(costume.materials),
                    "silhouette": costume.silhouette,
                    "locked_traits": list(costume.locked_traits),
                    "continuity_notes": list(costume.continuity_notes),
                    "last_seen_shot": None,
                },
            )
            if costume.locked_traits or costume.palette or costume.silhouette:
                costume_locks = self.state.continuity_locks.setdefault("costumes", {})
                costume_locks.setdefault(costume.id, {})
                costume_locks[costume.id].update(
                    {
                        key: value
                        for key, value in {
                            "locked_traits": list(costume.locked_traits),
                            "palette": list(costume.palette),
                            "silhouette": costume.silhouette,
                        }.items()
                        if value
                    }
                )
        self._touch()

    def apply_continuity_locks(self, locks: Dict[str, Any]) -> None:
        self._deep_merge(self.state.continuity_locks, locks)
        self._touch()

    def snapshot(self) -> Dict[str, Any]:
        return self.state.model_dump()

    def apply_success(
        self,
        scene: DirectorScene,
        shot: DirectorShot,
        characters: Iterable[CharacterAsset],
        props: Iterable[PropAsset],
        costumes: Iterable[CostumeAsset],
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
                    "current_outfit": character.current_outfit,
                    "hairstyle": character.hairstyle,
                    "last_seen_shot": shot.id,
                    "last_emotion": shot.emotion,
                }
            )
        for prop in props:
            self.state.prop_states.setdefault(prop.id, {})
            self.state.prop_states[prop.id].update(
                {
                    "name": prop.name or prop.id,
                    "category": prop.category,
                    "last_seen_shot": shot.id,
                }
            )
        for costume in costumes:
            self.state.costume_states.setdefault(costume.id, {})
            self.state.costume_states[costume.id].update(
                {
                    "name": costume.name or costume.id,
                    "wardrobe_role": costume.wardrobe_role,
                    "palette": list(costume.palette),
                    "last_seen_shot": shot.id,
                }
            )
        self.state.timeline.append(
            {
                "shot_id": shot.id,
                "scene_id": scene.id,
                "character_ids": [character.id for character in characters],
                "prop_ids": [prop.id for prop in props],
                "costume_ids": [costume.id for costume in costumes],
                "output_uri": result.output_uri,
                "qa_score": report.score,
                "timestamp": time.time(),
            }
        )
        self._touch()

    def _touch(self) -> None:
        self.state.updated_at = time.time()

    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        for key, value in source.items():
            if isinstance(value, dict) and isinstance(target.get(key), dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
