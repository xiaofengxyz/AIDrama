from __future__ import annotations

import time
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RuntimeBackend(str, Enum):
    DRY_RUN = "dry_run"
    DASHSCOPE = "dashscope"
    KLING = "kling"
    SEEDANCE = "seedance"
    VEO = "veo"


class DirectorScene(BaseModel):
    id: str = "scene_default"
    location: str = "unspecified"
    mood: str = "neutral"
    pacing: str = "medium"
    lighting: Optional[str] = None
    weather: Optional[str] = None
    tone: Optional[str] = None
    camera_style: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DirectorShot(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    shot_type: str = Field("shot", alias="type")
    framing: Optional[str] = None
    movement: Optional[str] = None
    lens: Optional[str] = None
    target: Optional[str] = None
    duration: float = Field(4.0, gt=0)
    emotion: Optional[str] = None
    pacing: Optional[str] = None
    action: Optional[str] = None
    dialogue: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("shot id cannot be empty")
        return value


class ShotTransition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_shot: str = Field(alias="from")
    to_shot: str = Field(alias="to")
    transition_type: str = Field("cut", alias="type")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DirectorProgram(BaseModel):
    sequence_id: str = "sequence_default"
    scene: DirectorScene = Field(default_factory=DirectorScene)
    characters: List[str] = Field(default_factory=list)
    shots: List[DirectorShot] = Field(default_factory=list)
    transitions: List[ShotTransition] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ShotGraph(BaseModel):
    sequence_id: str
    scene: DirectorScene
    shots: List[DirectorShot]
    transitions: List[ShotTransition]
    adjacency: Dict[str, List[str]] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CharacterAsset(BaseModel):
    id: str
    name: str = ""
    description: str = ""
    base_model: Optional[str] = None
    lora: Optional[str] = None
    hairstyle: Optional[str] = None
    current_outfit: Optional[str] = None
    embeddings: List[str] = Field(default_factory=list)
    outfits: List[str] = Field(default_factory=list)
    voices: List[str] = Field(default_factory=list)
    reference_images: List[str] = Field(default_factory=list)
    locked_traits: List[str] = Field(default_factory=list)
    continuity_notes: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SceneAsset(BaseModel):
    id: str
    location: str = ""
    mood: str = ""
    lighting: Optional[str] = None
    weather: Optional[str] = None
    tone: Optional[str] = None
    camera_style: Optional[str] = None
    time_of_day: Optional[str] = None
    reference_images: List[str] = Field(default_factory=list)
    continuity_notes: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CharacterBible(BaseModel):
    id: str = "character_bible"
    version: str = "v1"
    characters: List[CharacterAsset] = Field(default_factory=list)
    continuity_locks: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SceneBible(BaseModel):
    id: str = "scene_bible"
    version: str = "v1"
    scenes: List[SceneAsset] = Field(default_factory=list)
    continuity_locks: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PromptCompileRequest(BaseModel):
    backend: RuntimeBackend
    scene: DirectorScene
    shot: DirectorShot
    characters: List[CharacterAsset] = Field(default_factory=list)
    scene_asset: Optional[SceneAsset] = None
    film_state: Dict[str, Any] = Field(default_factory=dict)
    repair_notes: List[str] = Field(default_factory=list)


class CompiledPrompt(BaseModel):
    backend: RuntimeBackend
    shot_id: str
    prompt: str
    negative_prompt: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RuntimeRequest(BaseModel):
    backend: RuntimeBackend
    shot_id: str
    compiled_prompt: CompiledPrompt
    duration: float
    attempt: int = 1
    seed: Optional[int] = None
    repair_notes: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RuntimeResult(BaseModel):
    backend: RuntimeBackend
    shot_id: str
    status: str
    output_uri: Optional[str] = None
    cost_estimate: float = 0.0
    elapsed_seconds: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QAFinding(BaseModel):
    code: str
    message: str
    severity: str = "minor"
    repair_hint: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QAReport(BaseModel):
    shot_id: str
    score: float = Field(1.0, ge=0.0, le=1.0)
    threshold: float = Field(0.82, ge=0.0, le=1.0)
    findings: List[QAFinding] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def passed(self) -> bool:
        has_blocker = any(item.severity == "blocker" for item in self.findings)
        return self.score >= self.threshold and not has_blocker


class RetryPolicy(BaseModel):
    max_attempts: int = Field(2, ge=1)
    min_score: float = Field(0.82, ge=0.0, le=1.0)
    repair_failed_prompts: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RetryDecision(BaseModel):
    shot_id: str
    action: str
    reason: str
    next_request: Optional[RuntimeRequest] = None
    repair_notes: List[str] = Field(default_factory=list)


class FilmState(BaseModel):
    active_scene_id: Optional[str] = None
    character_states: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    scene_states: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    timeline: List[Dict[str, Any]] = Field(default_factory=list)
    continuity_locks: Dict[str, Any] = Field(default_factory=dict)
    updated_at: float = Field(default_factory=time.time)


class FilmEngineRun(BaseModel):
    graph: ShotGraph
    runtime_results: List[RuntimeResult] = Field(default_factory=list)
    qa_reports: List[QAReport] = Field(default_factory=list)
    final_state: FilmState
    metadata: Dict[str, Any] = Field(default_factory=dict)
