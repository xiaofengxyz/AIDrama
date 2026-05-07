from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import yaml

from .models import CharacterAsset, CharacterBible, SceneAsset, SceneBible


def _load_mapping_file(path: str | Path) -> Dict[str, Any]:
    source = Path(path)
    text = source.read_text(encoding="utf-8")
    if source.suffix.lower() == ".json":
        data = json.loads(text)
    else:
        data = yaml.safe_load(text) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Registry file must contain a mapping: {source}")
    return data


class CharacterRegistry:
    """Entity registry for reusable character assets."""

    def __init__(
        self,
        characters: Optional[Iterable[CharacterAsset]] = None,
        bibles: Optional[Iterable[CharacterBible]] = None,
    ):
        self._items: Dict[str, CharacterAsset] = {}
        self._bibles: Dict[str, CharacterBible] = {}
        self.continuity_locks: Dict[str, Any] = {}
        for character in characters or []:
            self.add(character)
        for bible in bibles or []:
            self.add_bible(bible)

    def add(self, character: CharacterAsset) -> CharacterAsset:
        self._items[character.id] = character
        return character

    def add_bible(self, bible: CharacterBible) -> CharacterBible:
        self._bibles[bible.id] = bible
        self._merge_locks(bible.continuity_locks)
        for character in bible.characters:
            character.metadata.setdefault("bible_id", bible.id)
            character.metadata.setdefault("bible_version", bible.version)
            self.add(character)
        return bible

    def get(self, character_id: str) -> Optional[CharacterAsset]:
        return self._items.get(character_id)

    def require(self, character_id: str) -> CharacterAsset:
        character = self.get(character_id)
        if not character:
            raise KeyError(f"Unknown character asset: {character_id}")
        return character

    def resolve_many(self, character_ids: Iterable[str]) -> List[CharacterAsset]:
        return [self.require(character_id) for character_id in character_ids]

    @property
    def bible_ids(self) -> List[str]:
        return sorted(self._bibles)

    @classmethod
    def from_json_file(cls, path: str | Path) -> "CharacterRegistry":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        payload = data if isinstance(data, list) else [data]
        registry = cls()
        for item in payload:
            item = dict(item)
            item.setdefault("name", item.get("id", ""))
            registry.add(CharacterAsset(**item))
        return registry

    @classmethod
    def from_bible_file(cls, path: str | Path) -> "CharacterRegistry":
        data = _load_mapping_file(path)
        payload = data.get("character_bible", data)
        if not isinstance(payload, dict):
            raise ValueError("Character Bible must be a mapping")

        raw_characters = payload.get("characters")
        if raw_characters is None and payload.get("character"):
            raw_characters = [payload["character"]]
        raw_characters = raw_characters or []
        if not isinstance(raw_characters, list):
            raise ValueError("Character Bible characters must be a list")

        characters = []
        for item in raw_characters:
            if not isinstance(item, dict):
                raise ValueError("Character Bible entries must be mappings")
            character_data = dict(item)
            character_data.setdefault("name", character_data.get("id", ""))
            characters.append(CharacterAsset(**character_data))

        bible = CharacterBible(
            id=payload.get("id", "character_bible"),
            version=str(payload.get("version", "v1")),
            characters=characters,
            continuity_locks=dict(payload.get("continuity_locks") or {}),
            metadata=dict(payload.get("metadata") or {}),
        )
        return cls(bibles=[bible])

    def _merge_locks(self, locks: Dict[str, Any]) -> None:
        for key, value in locks.items():
            if (
                isinstance(value, dict)
                and isinstance(self.continuity_locks.get(key), dict)
            ):
                self.continuity_locks[key].update(value)
            else:
                self.continuity_locks[key] = value


class SceneRegistry:
    """Entity registry for reusable scene assets."""

    def __init__(
        self,
        scenes: Optional[Iterable[SceneAsset]] = None,
        bibles: Optional[Iterable[SceneBible]] = None,
    ):
        self._items: Dict[str, SceneAsset] = {}
        self._bibles: Dict[str, SceneBible] = {}
        self.continuity_locks: Dict[str, Any] = {}
        for scene in scenes or []:
            self.add(scene)
        for bible in bibles or []:
            self.add_bible(bible)

    def add(self, scene: SceneAsset) -> SceneAsset:
        self._items[scene.id] = scene
        return scene

    def add_bible(self, bible: SceneBible) -> SceneBible:
        self._bibles[bible.id] = bible
        self._merge_locks(bible.continuity_locks)
        for scene in bible.scenes:
            scene.metadata.setdefault("bible_id", bible.id)
            scene.metadata.setdefault("bible_version", bible.version)
            self.add(scene)
        return bible

    def get(self, scene_id: str) -> Optional[SceneAsset]:
        return self._items.get(scene_id)

    def require(self, scene_id: str) -> SceneAsset:
        scene = self.get(scene_id)
        if not scene:
            raise KeyError(f"Unknown scene asset: {scene_id}")
        return scene

    @property
    def bible_ids(self) -> List[str]:
        return sorted(self._bibles)

    @classmethod
    def from_yaml_file(cls, path: str | Path) -> "SceneRegistry":
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        scene_payload = data.get("scene", data)
        if isinstance(scene_payload, list):
            payload = scene_payload
        else:
            payload = [scene_payload]
        registry = cls()
        for item in payload:
            item = dict(item)
            item.setdefault("id", item.get("location", "scene_default"))
            registry.add(SceneAsset(**item))
        return registry

    @classmethod
    def from_bible_file(cls, path: str | Path) -> "SceneRegistry":
        data = _load_mapping_file(path)
        payload = data.get("scene_bible", data)
        if not isinstance(payload, dict):
            raise ValueError("Scene Bible must be a mapping")

        raw_scenes = payload.get("scenes")
        if raw_scenes is None and payload.get("scene"):
            raw_scenes = [payload["scene"]]
        raw_scenes = raw_scenes or []
        if not isinstance(raw_scenes, list):
            raise ValueError("Scene Bible scenes must be a list")

        scenes = []
        for item in raw_scenes:
            if not isinstance(item, dict):
                raise ValueError("Scene Bible entries must be mappings")
            scene_data = dict(item)
            scene_data.setdefault("id", scene_data.get("location", "scene_default"))
            scenes.append(SceneAsset(**scene_data))

        bible = SceneBible(
            id=payload.get("id", "scene_bible"),
            version=str(payload.get("version", "v1")),
            scenes=scenes,
            continuity_locks=dict(payload.get("continuity_locks") or {}),
            metadata=dict(payload.get("metadata") or {}),
        )
        return cls(bibles=[bible])

    def _merge_locks(self, locks: Dict[str, Any]) -> None:
        for key, value in locks.items():
            if (
                isinstance(value, dict)
                and isinstance(self.continuity_locks.get(key), dict)
            ):
                self.continuity_locks[key].update(value)
            else:
                self.continuity_locks[key] = value
