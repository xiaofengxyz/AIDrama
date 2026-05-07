from __future__ import annotations

import time
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


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


class GenerationAttempt(BaseModel):
    attempt_id: str
    shot_id: str
    attempt: int = Field(1, ge=1)
    backend: RuntimeBackend
    status: str
    output_uri: Optional[str] = None
    seed: Optional[int] = None
    prompt_fingerprint: str
    prompt: str = ""
    negative_prompt: str = ""
    repair_notes: List[str] = Field(default_factory=list)
    qa_score: float = Field(0.0, ge=0.0, le=1.0)
    qa_passed: bool = False
    qa_findings: List[QAFinding] = Field(default_factory=list)
    decision_action: str = "unknown"
    decision_reason: str = ""
    cost_estimate: float = 0.0
    elapsed_seconds: float = 0.0
    request_metadata: Dict[str, Any] = Field(default_factory=dict)
    runtime_metadata: Dict[str, Any] = Field(default_factory=dict)
    qa_metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)


class ShotRun(BaseModel):
    shot_id: str
    scene_id: Optional[str] = None
    character_ids: List[str] = Field(default_factory=list)
    status: str = "pending"
    attempts: List[GenerationAttempt] = Field(default_factory=list)
    selected_attempt: Optional[int] = None
    selected_output_uri: Optional[str] = None
    manual_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    tags: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)
    total_cost_estimate: float = 0.0
    total_elapsed_seconds: float = 0.0
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)


class GenerationLedger(BaseModel):
    sequence_id: str = "sequence_default"
    shot_runs: Dict[str, ShotRun] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)

    def summary(self) -> Dict[str, Any]:
        runs = list(self.shot_runs.values())
        attempts = [attempt for run in runs for attempt in run.attempts]
        accepted = [run for run in runs if run.status == "accepted"]
        failed = [run for run in runs if run.status == "failed"]
        scores = [attempt.qa_score for attempt in attempts]
        return {
            "sequence_id": self.sequence_id,
            "total_shots": len(runs),
            "accepted_shots": len(accepted),
            "failed_shots": len(failed),
            "total_attempts": len(attempts),
            "retry_attempts": max(len(attempts) - len(runs), 0),
            "total_cost_estimate": round(
                sum(run.total_cost_estimate for run in runs),
                6,
            ),
            "total_elapsed_seconds": round(
                sum(run.total_elapsed_seconds for run in runs),
                6,
            ),
            "average_qa_score": round(sum(scores) / len(scores), 6) if scores else 0.0,
            "selected_outputs": {
                run.shot_id: run.selected_output_uri
                for run in runs
                if run.selected_output_uri
            },
        }


class BatchProductionItem(BaseModel):
    item_id: str
    program: DirectorProgram
    backend: Optional[RuntimeBackend] = None
    retry_policy: Optional[RetryPolicy] = None
    priority: int = 100
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("item_id")
    @classmethod
    def validate_item_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("batch item_id cannot be empty")
        return value


class BatchProductionPlan(BaseModel):
    id: str = "batch_default"
    backend: RuntimeBackend = RuntimeBackend.DRY_RUN
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)
    items: List[BatchProductionItem] = Field(default_factory=list)
    continue_on_error: bool = True
    max_items: Optional[int] = Field(default=None, ge=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_items(self) -> "BatchProductionPlan":
        if not self.items:
            raise ValueError("BatchProductionPlan requires at least one item")
        item_ids = [item.item_id for item in self.items]
        duplicate_ids = sorted(
            {item_id for item_id in item_ids if item_ids.count(item_id) > 1}
        )
        if duplicate_ids:
            raise ValueError(f"Duplicate batch item ids: {duplicate_ids}")
        return self


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
    generation_ledger: Optional[GenerationLedger] = None
    final_state: FilmState
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BatchProductionRun(BaseModel):
    plan_id: str
    planned_item_count: int = 0
    scheduled_item_count: int = 0
    item_order: List[str] = Field(default_factory=list)
    item_runs: Dict[str, FilmEngineRun] = Field(default_factory=dict)
    errors: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)

    def summary(self) -> Dict[str, Any]:
        accepted_item_ids = []
        failed_item_ids = set(self.errors)
        selected_outputs: Dict[str, Dict[str, str]] = {}
        scores = []
        total_shots = 0
        accepted_shots = 0
        failed_shots = 0
        total_attempts = 0
        retry_attempts = 0
        total_cost_estimate = 0.0
        total_elapsed_seconds = 0.0

        for item_id, run in self.item_runs.items():
            total_shots += len(run.graph.shots)
            scores.extend(report.score for report in run.qa_reports)
            ledger_summary = run.generation_ledger.summary() if run.generation_ledger else {}
            accepted_shots += int(ledger_summary.get("accepted_shots", 0))
            failed_shots += int(ledger_summary.get("failed_shots", 0))
            total_attempts += int(ledger_summary.get("total_attempts", 0))
            retry_attempts += int(ledger_summary.get("retry_attempts", 0))
            total_cost_estimate += float(ledger_summary.get("total_cost_estimate", 0.0))
            total_elapsed_seconds += float(ledger_summary.get("total_elapsed_seconds", 0.0))
            outputs = ledger_summary.get("selected_outputs") or {}
            if outputs:
                selected_outputs[item_id] = outputs
            if ledger_summary.get("accepted_shots", 0) == len(run.graph.shots):
                accepted_item_ids.append(item_id)
            else:
                failed_item_ids.add(item_id)

        return {
            "plan_id": self.plan_id,
            "total_plan_items": self.planned_item_count,
            "scheduled_items": self.scheduled_item_count,
            "completed_items": len(self.item_runs),
            "accepted_items": len(accepted_item_ids),
            "failed_items": len(failed_item_ids),
            "failed_item_ids": sorted(failed_item_ids),
            "total_shots": total_shots,
            "accepted_shots": accepted_shots,
            "failed_shots": failed_shots,
            "total_attempts": total_attempts,
            "retry_attempts": retry_attempts,
            "total_cost_estimate": round(total_cost_estimate, 6),
            "total_elapsed_seconds": round(total_elapsed_seconds, 6),
            "average_qa_score": round(sum(scores) / len(scores), 6) if scores else 0.0,
            "selected_outputs": selected_outputs,
            "item_order": list(self.item_order),
        }
