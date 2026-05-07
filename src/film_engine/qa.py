from __future__ import annotations

from .models import FilmState, QAFinding, QAReport, RuntimeRequest, RuntimeResult


class QAEngine:
    """Structural QA layer.

    This is not a replacement for visual QA. It provides the stable report and
    failure schema that later InsightFace, MediaPipe, OpenCV, and CLIP checks can
    fill with real visual findings.
    """

    def evaluate(
        self,
        result: RuntimeResult,
        request: RuntimeRequest,
        state: FilmState,
        threshold: float = 0.82,
    ) -> QAReport:
        findings = []
        score = 1.0

        if result.status != "completed":
            findings.append(
                QAFinding(
                    code="runtime_failed",
                    message=result.error or "Runtime did not complete",
                    severity="blocker",
                    repair_hint="retry with a narrower shot prompt",
                )
            )
            score = 0.0

        if result.status == "completed" and not result.output_uri:
            findings.append(
                QAFinding(
                    code="missing_output",
                    message="Runtime completed without an output URI",
                    severity="blocker",
                    repair_hint="rerun the runtime adapter and require persisted media",
                )
            )
            score = min(score, 0.2)

        metadata = request.compiled_prompt.metadata
        if metadata.get("character_ids") and metadata.get("reference_image_count", 0) == 0:
            findings.append(
                QAFinding(
                    code="missing_character_reference",
                    message="Shot has characters but no reference images",
                    severity="major",
                    repair_hint="attach character reference images before rendering",
                )
            )
            score -= 0.12

        scene_id = metadata.get("scene_id")
        if state.active_scene_id and scene_id and scene_id != state.active_scene_id:
            findings.append(
                QAFinding(
                    code="scene_continuity_shift",
                    message="Scene changed from active film state",
                    severity="minor",
                    repair_hint="make the transition explicit in the shot graph",
                )
            )
            score -= 0.04

        if len(request.compiled_prompt.prompt) < 32:
            findings.append(
                QAFinding(
                    code="undercompiled_prompt",
                    message="Compiled prompt is too short to preserve shot intent",
                    severity="major",
                    repair_hint="include scene, camera, character, and action fields",
                )
            )
            score -= 0.2

        return QAReport(
            shot_id=request.shot_id,
            score=max(score, 0.0),
            threshold=threshold,
            findings=findings,
            metadata={
                "backend": request.backend.value,
                "attempt": request.attempt,
                "output_uri": result.output_uri,
            },
        )
