from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from pydantic import BaseModel, Field


WORKFLOW_VERSION = "cineforge_workflow.v1"


class RuntimeModelRecommendation(BaseModel):
    """Model recommendation attached to a production workflow stage."""

    provider: str
    model: str
    role: str
    use_when: str
    required_env: List[str] = Field(default_factory=list)
    integration_status: str = "recommended"
    notes: List[str] = Field(default_factory=list)


class WorkflowStageDefinition(BaseModel):
    """Static contract for one CineForge workflow stage."""

    id: str
    order: int
    label: str
    required_artifact: str
    ui_step: str
    industry_pain_point: str
    model_recommendations: List[RuntimeModelRecommendation] = Field(default_factory=list)


class WorkflowStageState(BaseModel):
    """Evaluated state for one project at one workflow stage."""

    id: str
    order: int
    label: str
    status: str = "blocked"
    progress: float = Field(0.0, ge=0.0, le=1.0)
    artifact_count: int = 0
    required_count: int = 0
    blockers: List[str] = Field(default_factory=list)
    next_action: str = ""
    ui_step: str = ""
    required_artifact: str = ""
    industry_pain_point: str = ""
    model_recommendations: List[RuntimeModelRecommendation] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    updated_at: float = Field(default_factory=time.time)


class WorkflowEditEvent(BaseModel):
    """Small durable event used to support edit/regenerate loops."""

    event_id: str
    stage_id: str
    action: str
    reason: str = ""
    scope: Dict[str, Any] = Field(default_factory=dict)
    status: str = "queued"
    dry_run: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)


class WorkflowState(BaseModel):
    """Persistable CineForge workflow snapshot for one editable project."""

    project_id: str
    title: str = ""
    version: str = WORKFLOW_VERSION
    stages: List[WorkflowStageState] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)
    edit_history: List[WorkflowEditEvent] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)

    def stage(self, stage_id: str) -> Optional[WorkflowStageState]:
        """Return a stage by id without forcing callers to know list positions."""
        return next((stage for stage in self.stages if stage.id == stage_id), None)


def _recommendations() -> Dict[str, List[RuntimeModelRecommendation]]:
    """Centralize model choices so UI, API and docs can stay aligned."""
    return {
        "novel_engine": [
            RuntimeModelRecommendation(
                provider="Alibaba Bailian / DashScope",
                model="qwen-plus",
                role="script analysis and rewrite",
                use_when="Low-cost novel parsing, chapter outline and dialogue cleanup.",
                required_env=["DASHSCOPE_API_KEY"],
                integration_status="available",
            )
        ],
        "asset_pipeline": [
            RuntimeModelRecommendation(
                provider="Alibaba Bailian / DashScope",
                model="wan2.7-image-pro",
                role="character, scene, prop and costume reference images",
                use_when="High-quality master assets and locked visual bible images.",
                required_env=["DASHSCOPE_API_KEY"],
                integration_status="recommended_next",
                notes=["Current Studio adapters can keep using wan2.6-image while wan2.7 adapters are added."],
            ),
            RuntimeModelRecommendation(
                provider="Alibaba Bailian / DashScope",
                model="wan2.6-image",
                role="current image generation adapter",
                use_when="Temporary Bailian-first image generation in the current code path.",
                required_env=["DASHSCOPE_API_KEY"],
                integration_status="available",
            ),
        ],
        "storyboard": [
            RuntimeModelRecommendation(
                provider="Alibaba Bailian / DashScope",
                model="wan2.6-image",
                role="storyboard image edit / img2img",
                use_when="Turn composition data and reference assets into storyboard key frames.",
                required_env=["DASHSCOPE_API_KEY"],
                integration_status="available",
            )
        ],
        "image_runtime": [
            RuntimeModelRecommendation(
                provider="Alibaba Bailian / DashScope",
                model="wan2.7-image",
                role="fast shot stills",
                use_when="Fast shot still generation before expensive video attempts.",
                required_env=["DASHSCOPE_API_KEY"],
                integration_status="recommended_next",
            ),
            RuntimeModelRecommendation(
                provider="ComfyUI",
                model="FLUX / SDXL",
                role="future local or private image runtime",
                use_when="Private deployment, LoRA-heavy characters or controllable batch rendering.",
                integration_status="future_adapter",
            ),
        ],
        "video_runtime": [
            RuntimeModelRecommendation(
                provider="Alibaba Bailian / DashScope",
                model="wan2.7-i2v-2026-04-25",
                role="first-frame / first-last-frame / continuation video",
                use_when="Primary Bailian video model for continuity-sensitive shots.",
                required_env=["DASHSCOPE_API_KEY"],
                integration_status="recommended_next",
                notes=["Current Studio adapters can keep using wan2.6-i2v / wan2.6-r2v until wan2.7 media-array support lands."],
            ),
            RuntimeModelRecommendation(
                provider="Alibaba Bailian / DashScope",
                model="wan2.6-i2v",
                role="current image-to-video adapter",
                use_when="Temporary production path already wired through the current Studio video generator.",
                required_env=["DASHSCOPE_API_KEY"],
                integration_status="available",
            ),
            RuntimeModelRecommendation(
                provider="Extensible vendor runtime",
                model="Kling / Vidu / Seedance / Veo / Sora",
                role="future premium or vendor-direct video backends",
                use_when="Key shots, regional availability or higher motion quality experiments.",
                integration_status="future_adapter",
            ),
        ],
        "voice_runtime": [
            RuntimeModelRecommendation(
                provider="Alibaba Bailian / DashScope",
                model="cosyvoice-v3-flash",
                role="fast dialogue and narrator TTS",
                use_when="Daily batch voice generation and iteration.",
                required_env=["DASHSCOPE_API_KEY"],
                integration_status="available",
            ),
            RuntimeModelRecommendation(
                provider="Alibaba Bailian / DashScope",
                model="cosyvoice-v3-plus / cosyvoice-v3.5-plus",
                role="premium final voices and cloned voices",
                use_when="Final character casting, emotional delivery or voice clone workflows.",
                required_env=["DASHSCOPE_API_KEY"],
                integration_status="recommended_next",
            ),
        ],
        "composition": [
            RuntimeModelRecommendation(
                provider="Local runtime",
                model="FFmpeg",
                role="stitch video, mix audio and export mp4",
                use_when="Deterministic local composition after all selected clips and audio are ready.",
                integration_status="available",
            )
        ],
        "qa_retry": [
            RuntimeModelRecommendation(
                provider="AIDrama Film Core",
                model="QAEngine + RetryEngine",
                role="automatic continuity QA and deterministic retry decisions",
                use_when="Run before spending on expensive regeneration or final export.",
                integration_status="available",
            )
        ],
        "export": [
            RuntimeModelRecommendation(
                provider="AIDrama Studio",
                model="video export / render package",
                role="mp4 output when clips exist, JSON render package when they do not",
                use_when="Keep production recoverable even before all media assets are generated.",
                integration_status="available",
            )
        ],
    }


def get_workflow_stage_definitions() -> List[WorkflowStageDefinition]:
    """Return the fixed workflow contracts in execution order."""
    models = _recommendations()
    return [
        WorkflowStageDefinition(
            id="novel_engine",
            order=1,
            label="Novel Engine",
            required_artifact="world bible, relationship graph, chapter outline",
            ui_step="Script",
            industry_pain_point="Long source text must become editable beats instead of one-off prompts.",
            model_recommendations=models["novel_engine"],
        ),
        WorkflowStageDefinition(
            id="asset_pipeline",
            order=2,
            label="Asset Pipeline",
            required_artifact="character, scene, prop and costume bibles",
            ui_step="Assets",
            industry_pain_point="Character faces, costumes and props drift when the asset bible is weak.",
            model_recommendations=models["asset_pipeline"],
        ),
        WorkflowStageDefinition(
            id="storyboard",
            order=3,
            label="Storyboard",
            required_artifact="editable shot graph and storyboard frames",
            ui_step="Storyboard",
            industry_pain_point="Shots become unshootable when action, framing and continuity are not separated.",
            model_recommendations=models["storyboard"],
        ),
        WorkflowStageDefinition(
            id="image_runtime",
            order=4,
            label="Image Runtime",
            required_artifact="selected rendered frame images",
            ui_step="Storyboard",
            industry_pain_point="Video attempts get expensive if still frames are not locked first.",
            model_recommendations=models["image_runtime"],
        ),
        WorkflowStageDefinition(
            id="video_runtime",
            order=5,
            label="Video Runtime",
            required_artifact="selected video clip for every storyboard frame",
            ui_step="Motion",
            industry_pain_point="Shot continuity fails when clips are generated without selected outputs.",
            model_recommendations=models["video_runtime"],
        ),
        WorkflowStageDefinition(
            id="voice_runtime",
            order=6,
            label="Voice Runtime",
            required_artifact="dialogue audio bound to character voices",
            ui_step="Voice",
            industry_pain_point="Uncast voices break character identity even when visuals are stable.",
            model_recommendations=models["voice_runtime"],
        ),
        WorkflowStageDefinition(
            id="composition",
            order=7,
            label="Composition",
            required_artifact="ordered clips, audio, subtitles and timeline",
            ui_step="Final Mix",
            industry_pain_point="Final assembly must be reproducible and not depend on manual memory.",
            model_recommendations=models["composition"],
        ),
        WorkflowStageDefinition(
            id="qa_retry",
            order=8,
            label="QA & Retry",
            required_artifact="QA report, retry decisions and generation ledger",
            ui_step="QA & Export",
            industry_pain_point="Failed shots need traceable repair notes instead of blind rerolls.",
            model_recommendations=models["qa_retry"],
        ),
        WorkflowStageDefinition(
            id="export",
            order=9,
            label="Export",
            required_artifact="mp4 final video or recoverable render package",
            ui_step="QA & Export",
            industry_pain_point="The project must export useful state even before every media clip exists.",
            model_recommendations=models["export"],
        ),
    ]


def get_model_recommendation_catalog() -> Dict[str, Any]:
    """Expose model recommendations as a stable API-friendly catalog."""
    definitions = get_workflow_stage_definitions()
    return {
        "version": WORKFLOW_VERSION,
        "provider_strategy": "Bailian-first now, pluggable vendor/local adapters later.",
        "stages": [
            {
                "stage_id": definition.id,
                "label": definition.label,
                "ui_step": definition.ui_step,
                "model_recommendations": [
                    recommendation.model_dump(mode="json")
                    for recommendation in definition.model_recommendations
                ],
            }
            for definition in definitions
        ],
    }


def _as_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _has_selected_image(asset: Any) -> bool:
    """Return true when a legacy or v2 asset container has a selected image."""
    if not asset:
        return False
    if getattr(asset, "selected_id", None) and _as_list(getattr(asset, "variants", [])):
        return True
    if getattr(asset, "selected_image_id", None) and _as_list(getattr(asset, "image_variants", [])):
        return True
    return bool(_as_list(getattr(asset, "variants", [])) or _as_list(getattr(asset, "image_variants", [])))


def _asset_has_image(asset: Any, fields: Iterable[str]) -> bool:
    """Check common Studio asset image fields without coupling to one schema version."""
    if any(getattr(asset, field, None) for field in fields):
        return True
    return any(
        _has_selected_image(getattr(asset, field, None))
        for field in (
            "image_asset",
            "full_body_asset",
            "three_view_asset",
            "headshot_asset",
            "full_body",
            "three_views",
            "head_shot",
            "rendered_image_asset",
        )
    )


def _frame_has_video(project: Any, frame: Any) -> bool:
    """Resolve selected or completed video for one frame."""
    if getattr(frame, "video_url", None):
        return True
    selected_id = getattr(frame, "selected_video_id", None)
    video_tasks = _as_list(getattr(project, "video_tasks", []))
    if selected_id:
        return any(
            task.id == selected_id and task.video_url and task.status == "completed"
            for task in video_tasks
        )
    return any(
        getattr(task, "frame_id", None) == getattr(frame, "id", None)
        and getattr(task, "video_url", None)
        and getattr(task, "status", "") == "completed"
        for task in video_tasks
    )


def _stage_state(
    definition: WorkflowStageDefinition,
    *,
    status: str,
    artifact_count: int,
    required_count: int,
    blockers: Optional[List[str]] = None,
    next_action: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> WorkflowStageState:
    """Build a state object with consistent progress and shared metadata."""
    if required_count <= 0:
        progress = 1.0 if status in {"ready", "passed"} else 0.0
    else:
        progress = min(max(artifact_count / required_count, 0.0), 1.0)
    return WorkflowStageState(
        id=definition.id,
        order=definition.order,
        label=definition.label,
        status=status,
        progress=progress,
        artifact_count=artifact_count,
        required_count=max(required_count, 0),
        blockers=blockers or [],
        next_action=next_action,
        ui_step=definition.ui_step,
        required_artifact=definition.required_artifact,
        industry_pain_point=definition.industry_pain_point,
        model_recommendations=definition.model_recommendations,
        metadata=metadata or {},
    )


def evaluate_project_workflow(project: Any, film_summary: Optional[Dict[str, Any]] = None) -> WorkflowState:
    """Evaluate one Studio project into a persisted CineForge workflow snapshot."""
    definitions = {definition.id: definition for definition in get_workflow_stage_definitions()}
    characters = _as_list(getattr(project, "characters", []))
    scenes = _as_list(getattr(project, "scenes", []))
    props = _as_list(getattr(project, "props", []))
    frames = _as_list(getattr(project, "frames", []))
    dialogue_frames = [frame for frame in frames if getattr(frame, "dialogue", None)]

    script_text = (getattr(project, "original_text", "") or "").strip()
    asset_total = len(characters) + len(scenes) + len(props)
    generated_assets = sum(
        1
        for asset in characters
        if _asset_has_image(asset, ("image_url", "avatar_url", "full_body_image_url", "three_view_image_url", "headshot_image_url"))
    )
    generated_assets += sum(
        1 for asset in scenes if _asset_has_image(asset, ("image_url",))
    )
    generated_assets += sum(
        1 for asset in props if _asset_has_image(asset, ("image_url",))
    )
    image_frames = sum(
        1
        for frame in frames
        if _asset_has_image(frame, ("image_url", "rendered_image_url"))
    )
    video_frames = sum(1 for frame in frames if _frame_has_video(project, frame))
    audio_frames = sum(1 for frame in dialogue_frames if getattr(frame, "audio_url", None))
    merged_video_url = getattr(project, "merged_video_url", None)

    stages: List[WorkflowStageState] = []
    stages.append(
        _stage_state(
            definitions["novel_engine"],
            status="passed" if script_text else "blocked",
            artifact_count=1 if script_text else 0,
            required_count=1,
            blockers=[] if script_text else ["Add or import source script text."],
            next_action="Analyze or edit the source script into beats." if script_text else "Paste a script or instantiate a template.",
            metadata={"source_chars": len(script_text)},
        )
    )
    stages.append(
        _stage_state(
            definitions["asset_pipeline"],
            status="passed" if asset_total and generated_assets >= asset_total else ("attention" if asset_total else "blocked"),
            artifact_count=generated_assets,
            required_count=asset_total or 1,
            blockers=[] if asset_total else ["Create character, scene and prop assets."],
            next_action="Generate or upload locked reference images for all assets.",
            metadata={"asset_total": asset_total},
        )
    )
    stages.append(
        _stage_state(
            definitions["storyboard"],
            status="passed" if frames else "blocked",
            artifact_count=len(frames),
            required_count=max(len(frames), 1),
            blockers=[] if frames else ["Generate editable storyboard frames."],
            next_action="Create, edit and lock the storyboard shot list.",
        )
    )
    stages.append(
        _stage_state(
            definitions["image_runtime"],
            status="passed" if frames and image_frames >= len(frames) else ("attention" if frames else "blocked"),
            artifact_count=image_frames,
            required_count=max(len(frames), 1),
            blockers=[] if image_frames else ["Render or upload key frame images."],
            next_action="Render storyboard stills before video generation.",
        )
    )
    stages.append(
        _stage_state(
            definitions["video_runtime"],
            status="passed" if frames and video_frames >= len(frames) else ("attention" if frames else "blocked"),
            artifact_count=video_frames,
            required_count=max(len(frames), 1),
            blockers=[] if video_frames else ["Generate and select video clips for each frame."],
            next_action="Generate I2V/R2V candidates and select one clip per frame.",
        )
    )
    stages.append(
        _stage_state(
            definitions["voice_runtime"],
            status="passed" if not dialogue_frames or audio_frames >= len(dialogue_frames) else "attention",
            artifact_count=audio_frames,
            required_count=len(dialogue_frames),
            blockers=[] if not dialogue_frames or audio_frames else ["Bind voices and generate dialogue audio."],
            next_action="Assign CosyVoice voices to characters and generate dialogue lines.",
            metadata={"dialogue_frames": len(dialogue_frames)},
        )
    )
    stages.append(
        _stage_state(
            definitions["composition"],
            status="ready" if frames and video_frames >= len(frames) else ("attention" if frames else "blocked"),
            artifact_count=video_frames,
            required_count=max(len(frames), 1),
            blockers=[] if video_frames >= len(frames) and frames else ["Composition can export a package now; mp4 needs selected clips."],
            next_action="Use Start Render for mp4 when clips exist, or download a render package for handoff.",
        )
    )
    qa_total = int((film_summary or {}).get("total_shots") or len(frames) or 0)
    qa_accepted = int((film_summary or {}).get("accepted_shots") or 0)
    stages.append(
        _stage_state(
            definitions["qa_retry"],
            status="passed" if qa_total and qa_accepted >= qa_total else ("ready" if script_text else "blocked"),
            artifact_count=qa_accepted,
            required_count=max(qa_total, 1),
            blockers=[] if script_text else ["Run Film Core dry-run after script exists."],
            next_action="Run QA dry-run and inspect ledger, retry notes and unresolved shots.",
            metadata=film_summary or {},
        )
    )
    can_export_video = bool(frames and video_frames >= len(frames))
    stages.append(
        _stage_state(
            definitions["export"],
            status="passed" if merged_video_url else ("ready" if can_export_video else "attention"),
            artifact_count=1 if merged_video_url else (video_frames if can_export_video else 0),
            required_count=1 if merged_video_url else max(len(frames), 1),
            blockers=[] if can_export_video or merged_video_url else ["No selected clips yet; Start Render will produce a render package instead of mp4."],
            next_action="Export final mp4 or render package.",
            metadata={"merged_video_url": merged_video_url},
        )
    )

    summary = {
        "stage_count": len(stages),
        "passed_stages": sum(1 for stage in stages if stage.status == "passed"),
        "attention_stages": sum(1 for stage in stages if stage.status == "attention"),
        "blocked_stages": sum(1 for stage in stages if stage.status == "blocked"),
        "can_export_video": can_export_video,
        "can_export_package": bool(script_text or frames),
        "recommended_render_mode": "video" if can_export_video else "render_package",
        "asset_total": asset_total,
        "storyboard_frames": len(frames),
        "selected_video_frames": video_frames,
        "dialogue_frames": len(dialogue_frames),
        "audio_frames": audio_frames,
    }
    return WorkflowState(
        project_id=getattr(project, "id", ""),
        title=getattr(project, "title", ""),
        stages=stages,
        summary=summary,
        metadata={"film_summary_attached": bool(film_summary)},
    )


class WorkflowStateStore:
    """Small JSON store for recoverable workflow state outside project payloads."""

    def __init__(self, path: str | Path = "output/workflow_state.json"):
        self.path = Path(path)

    def load_all(self) -> Dict[str, WorkflowState]:
        if not self.path.exists():
            return {}
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return {
            project_id: WorkflowState(**payload)
            for project_id, payload in raw.items()
        }

    def save_all(self, states: Dict[str, WorkflowState]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            project_id: state.model_dump(mode="json")
            for project_id, state in states.items()
        }
        tmp_path = self.path.with_suffix(".tmp")
        tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp_path, self.path)

    def upsert(self, state: WorkflowState) -> WorkflowState:
        states = self.load_all()
        previous = states.get(state.project_id)
        if previous:
            state.created_at = previous.created_at
            state.edit_history = list(previous.edit_history)
        state.updated_at = time.time()
        states[state.project_id] = state
        self.save_all(states)
        return state

    def record_edit_event(self, project_id: str, event: WorkflowEditEvent) -> WorkflowState:
        states = self.load_all()
        state = states.get(project_id)
        if not state:
            state = WorkflowState(project_id=project_id)
        state.edit_history.append(event)
        state.updated_at = time.time()
        states[project_id] = state
        self.save_all(states)
        return state


class RenderPackageExporter:
    """Export a recoverable render package when an mp4 cannot be composed yet."""

    def __init__(self, output_dir: str | Path = "output/export"):
        self.output_dir = Path(output_dir)

    def export(
        self,
        project: Any,
        *,
        workflow_state: WorkflowState,
        options: Dict[str, Any],
        reason: str,
    ) -> Dict[str, Any]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = int(time.time())
        project_id = getattr(project, "id", "project")
        filename = f"{project_id}_{timestamp}_render_package.json"
        output_path = self.output_dir / filename
        blockers = [
            blocker
            for stage in workflow_state.stages
            for blocker in stage.blockers
            if blocker
        ]
        package = {
            "version": WORKFLOW_VERSION,
            "project_id": project_id,
            "title": getattr(project, "title", ""),
            "created_at": timestamp,
            "render_mode": "render_package",
            "reason": reason,
            "options": options,
            "workflow_state": workflow_state.model_dump(mode="json"),
            "model_recommendation_catalog": get_model_recommendation_catalog(),
            "frames": [
                {
                    "frame_id": getattr(frame, "id", ""),
                    "scene_id": getattr(frame, "scene_id", ""),
                    "dialogue": getattr(frame, "dialogue", None),
                    "image_url": getattr(frame, "rendered_image_url", None) or getattr(frame, "image_url", None),
                    "video_url": getattr(frame, "video_url", None),
                    "audio_url": getattr(frame, "audio_url", None),
                    "selected_video_id": getattr(frame, "selected_video_id", None),
                }
                for frame in _as_list(getattr(project, "frames", []))
            ],
            "action_required": blockers or ["Select final video clips before mp4 composition."],
        }
        output_path.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "url": f"export/{filename}",
            "mode": "render_package",
            "warnings": [
                "No final mp4 was created because selected video clips are not complete.",
                reason,
            ],
            "action_required": package["action_required"],
            "workflow_state": workflow_state.model_dump(mode="json"),
        }
