from __future__ import annotations

from typing import Dict, Iterable, List

from pydantic import BaseModel, Field

from .models import CompiledPrompt, PromptCompileRequest, RuntimeBackend


class BackendProfile(BaseModel):
    backend: RuntimeBackend
    cinematic_prefix: str
    negative_terms: List[str] = Field(default_factory=list)
    supports_reference_images: bool = True


DEFAULT_BACKEND_PROFILES: Dict[RuntimeBackend, BackendProfile] = {
    RuntimeBackend.DRY_RUN: BackendProfile(
        backend=RuntimeBackend.DRY_RUN,
        cinematic_prefix="structured dry-run render",
        negative_terms=["identity drift", "shot discontinuity"],
    ),
    RuntimeBackend.DASHSCOPE: BackendProfile(
        backend=RuntimeBackend.DASHSCOPE,
        cinematic_prefix="cinematic short drama shot",
        negative_terms=["low quality", "identity drift", "broken anatomy"],
    ),
    RuntimeBackend.KLING: BackendProfile(
        backend=RuntimeBackend.KLING,
        cinematic_prefix="cinematic image-to-video shot",
        negative_terms=["face drift", "outfit mismatch", "unstable camera"],
    ),
    RuntimeBackend.SEEDANCE: BackendProfile(
        backend=RuntimeBackend.SEEDANCE,
        cinematic_prefix="controlled cinematic video shot",
        negative_terms=["temporal flicker", "identity drift"],
    ),
    RuntimeBackend.VEO: BackendProfile(
        backend=RuntimeBackend.VEO,
        cinematic_prefix="film-quality dramatic shot",
        negative_terms=["continuity error", "unmotivated camera motion"],
    ),
}


class PromptCompiler:
    """Compile structured film state into backend-specific prompt bundles."""

    def __init__(self, profiles: Dict[RuntimeBackend, BackendProfile] | None = None):
        self.profiles = profiles or DEFAULT_BACKEND_PROFILES

    def compile(self, request: PromptCompileRequest) -> CompiledPrompt:
        profile = self.profiles[request.backend]
        character_ids = [character.id for character in request.characters]
        reference_images = [
            ref
            for character in request.characters
            for ref in character.reference_images
        ]
        if request.scene_asset:
            reference_images.extend(request.scene_asset.reference_images)

        prompt = "; ".join(
            self._compact(
                [
                    profile.cinematic_prefix,
                    self._scene_segment(request),
                    self._character_segment(request),
                    self._shot_segment(request),
                    self._state_segment(request),
                    self._repair_segment(request.repair_notes),
                ]
            )
        )
        negative_prompt = ", ".join(profile.negative_terms)

        return CompiledPrompt(
            backend=request.backend,
            shot_id=request.shot.id,
            prompt=prompt,
            negative_prompt=negative_prompt,
            metadata={
                "scene_id": request.scene.id,
                "character_ids": character_ids,
                "reference_images": reference_images,
                "reference_image_count": len(reference_images),
                "shot_type": request.shot.shot_type,
                "movement": request.shot.movement,
                "duration": request.shot.duration,
            },
        )

    def _scene_segment(self, request: PromptCompileRequest) -> str:
        scene = request.scene
        asset = request.scene_asset
        location = asset.location if asset and asset.location else scene.location
        lighting = scene.lighting or (asset.lighting if asset else None)
        weather = scene.weather or (asset.weather if asset else None)
        return self._join_fields(
            "scene",
            {
                "location": location,
                "mood": scene.mood or (asset.mood if asset else None),
                "lighting": lighting,
                "weather": weather,
                "tone": scene.tone or (asset.tone if asset else None),
            },
        )

    def _character_segment(self, request: PromptCompileRequest) -> str:
        if not request.characters:
            return ""
        values = []
        for character in request.characters:
            traits = self._compact(
                [
                    character.name or character.id,
                    character.description,
                    f"outfit={','.join(character.outfits)}" if character.outfits else "",
                    f"locked={','.join(character.locked_traits)}" if character.locked_traits else "",
                ]
            )
            values.append(" ".join(traits))
        return "characters: " + " | ".join(values)

    def _shot_segment(self, request: PromptCompileRequest) -> str:
        shot = request.shot
        return self._join_fields(
            "shot",
            {
                "id": shot.id,
                "type": shot.shot_type,
                "framing": shot.framing,
                "movement": shot.movement,
                "lens": shot.lens,
                "target": shot.target,
                "emotion": shot.emotion,
                "pacing": shot.pacing,
                "action": shot.action,
                "dialogue": shot.dialogue,
            },
        )

    def _state_segment(self, request: PromptCompileRequest) -> str:
        locks = request.film_state.get("continuity_locks") or {}
        if not locks:
            return ""
        lock_pairs = [f"{key}={value}" for key, value in sorted(locks.items())]
        return "continuity: " + ", ".join(lock_pairs)

    def _repair_segment(self, repair_notes: List[str]) -> str:
        if not repair_notes:
            return ""
        return "repair: " + "; ".join(repair_notes)

    def _join_fields(self, label: str, values: Dict[str, object]) -> str:
        parts = [f"{key}={value}" for key, value in values.items() if value]
        if not parts:
            return ""
        return f"{label}: " + ", ".join(parts)

    def _compact(self, values: Iterable[str]) -> List[str]:
        return [value.strip() for value in values if value and value.strip()]
