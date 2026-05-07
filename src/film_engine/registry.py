from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import yaml

from .models import CharacterAsset, SceneAsset


class CharacterRegistry:
    """Entity registry for reusable character assets."""

    def __init__(self, characters: Optional[Iterable[CharacterAsset]] = None):
        self._items: Dict[str, CharacterAsset] = {}
        for character in characters or []:
            self.add(character)

    def add(self, character: CharacterAsset) -> CharacterAsset:
        self._items[character.id] = character
        return character

    def get(self, character_id: str) -> Optional[CharacterAsset]:
        return self._items.get(character_id)

    def require(self, character_id: str) -> CharacterAsset:
        character = self.get(character_id)
        if not character:
            raise KeyError(f"Unknown character asset: {character_id}")
        return character

    def resolve_many(self, character_ids: Iterable[str]) -> List[CharacterAsset]:
        return [self.require(character_id) for character_id in character_ids]

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


class SceneRegistry:
    """Entity registry for reusable scene assets."""

    def __init__(self, scenes: Optional[Iterable[SceneAsset]] = None):
        self._items: Dict[str, SceneAsset] = {}
        for scene in scenes or []:
            self.add(scene)

    def add(self, scene: SceneAsset) -> SceneAsset:
        self._items[scene.id] = scene
        return scene

    def get(self, scene_id: str) -> Optional[SceneAsset]:
        return self._items.get(scene_id)

    def require(self, scene_id: str) -> SceneAsset:
        scene = self.get(scene_id)
        if not scene:
            raise KeyError(f"Unknown scene asset: {scene_id}")
        return scene

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
