from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

from .models import DirectorProgram, DirectorScene, DirectorShot, ShotTransition


class DirectorDSLParser:
    """Parse structured cinematic YAML into a stable AST."""

    def parse_file(self, path: str | Path) -> DirectorProgram:
        return self.parse_yaml(Path(path).read_text(encoding="utf-8"))

    def parse_yaml(self, text: str) -> DirectorProgram:
        data = yaml.safe_load(text) or {}
        if not isinstance(data, dict):
            raise ValueError("Director DSL must be a YAML mapping")
        return self.parse_dict(data)

    def parse_dict(self, data: Dict[str, Any]) -> DirectorProgram:
        scene_data = dict(data.get("scene") or {})
        sequence_id = data.get("sequence_id") or scene_data.get("id") or "sequence_default"
        scene_data.setdefault("id", scene_data.get("location") or sequence_id)
        scene = DirectorScene(**scene_data)

        shots = []
        for index, raw_shot in enumerate(data.get("shots") or [], start=1):
            if not isinstance(raw_shot, dict):
                raise ValueError(f"Shot #{index} must be a mapping")
            shot_data = dict(raw_shot)
            shot_data.setdefault("id", f"shot_{index:03d}")
            shot_data.setdefault("type", shot_data.get("framing") or "shot")
            shot_data.setdefault("duration", 4.0)
            shots.append(DirectorShot(**shot_data))

        transitions = []
        for raw_transition in data.get("transitions") or []:
            if not isinstance(raw_transition, dict):
                raise ValueError("Shot transition must be a mapping")
            transitions.append(ShotTransition(**raw_transition))

        program = DirectorProgram(
            sequence_id=sequence_id,
            scene=scene,
            characters=list(data.get("characters") or []),
            props=list(data.get("props") or []),
            costumes=list(data.get("costumes") or []),
            shots=shots,
            transitions=transitions,
            metadata=dict(data.get("metadata") or {}),
        )
        self._validate(program)
        return program

    def _validate(self, program: DirectorProgram) -> None:
        if not program.shots:
            raise ValueError("Director DSL requires at least one shot")

        shot_ids = [shot.id for shot in program.shots]
        duplicate_ids = {shot_id for shot_id in shot_ids if shot_ids.count(shot_id) > 1}
        if duplicate_ids:
            raise ValueError(f"Duplicate shot ids: {sorted(duplicate_ids)}")

        known_ids = set(shot_ids)
        for transition in program.transitions:
            if transition.from_shot not in known_ids or transition.to_shot not in known_ids:
                raise ValueError(
                    "Transition references unknown shot: "
                    f"{transition.from_shot} -> {transition.to_shot}"
                )
