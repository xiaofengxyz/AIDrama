from __future__ import annotations

import hashlib
import json
import time
from typing import Iterable

from .models import (
    GenerationAttempt,
    GenerationLedger,
    QAReport,
    RetryDecision,
    RuntimeRequest,
    RuntimeResult,
    ShotRun,
)


class GenerationLedgerRecorder:
    """Append-only shot generation ledger for QA, retry, and cost analysis."""

    def __init__(self, ledger: GenerationLedger | None = None):
        self.ledger = ledger or GenerationLedger()

    @classmethod
    def for_sequence(cls, sequence_id: str) -> "GenerationLedgerRecorder":
        return cls(GenerationLedger(sequence_id=sequence_id))

    def record_attempt(
        self,
        request: RuntimeRequest,
        result: RuntimeResult,
        report: QAReport,
        decision: RetryDecision,
        scene_id: str | None = None,
        character_ids: Iterable[str] | None = None,
    ) -> GenerationAttempt:
        shot_run = self._ensure_shot_run(request.shot_id, scene_id, character_ids)
        attempt = GenerationAttempt(
            attempt_id=f"{request.shot_id}:attempt-{request.attempt}",
            shot_id=request.shot_id,
            attempt=request.attempt,
            backend=request.backend,
            status=result.status,
            output_uri=result.output_uri,
            seed=request.seed,
            prompt_fingerprint=self._prompt_fingerprint(request),
            prompt=request.compiled_prompt.prompt,
            negative_prompt=request.compiled_prompt.negative_prompt,
            repair_notes=list(request.repair_notes),
            qa_score=report.score,
            qa_passed=report.passed,
            qa_findings=list(report.findings),
            decision_action=decision.action,
            decision_reason=decision.reason,
            cost_estimate=result.cost_estimate,
            elapsed_seconds=result.elapsed_seconds,
            request_metadata=dict(request.metadata),
            runtime_metadata=dict(result.metadata),
            qa_metadata=dict(report.metadata),
        )
        shot_run.attempts.append(attempt)
        shot_run.total_cost_estimate += result.cost_estimate
        shot_run.total_elapsed_seconds += result.elapsed_seconds
        self._apply_decision(shot_run, attempt, decision)
        shot_run.updated_at = time.time()
        self.ledger.updated_at = shot_run.updated_at
        return attempt

    def mark_manual_review(
        self,
        shot_id: str,
        manual_score: float | None = None,
        selected_attempt: int | None = None,
        tags: Iterable[str] | None = None,
        notes: Iterable[str] | None = None,
    ) -> ShotRun:
        shot_run = self.ledger.shot_runs[shot_id]
        if manual_score is not None:
            if manual_score < 0.0 or manual_score > 1.0:
                raise ValueError("manual_score must be between 0.0 and 1.0")
            shot_run.manual_score = manual_score
        if selected_attempt is not None:
            shot_run.selected_attempt = selected_attempt
            matched = False
            for attempt in shot_run.attempts:
                if attempt.attempt == selected_attempt:
                    shot_run.selected_output_uri = attempt.output_uri
                    matched = True
                    break
            if not matched:
                raise ValueError(f"Unknown attempt {selected_attempt} for shot {shot_id}")
        if tags:
            shot_run.tags = sorted({*shot_run.tags, *tags})
        if notes:
            shot_run.notes.extend(notes)
        shot_run.updated_at = time.time()
        self.ledger.updated_at = shot_run.updated_at
        return shot_run

    def summary(self) -> dict:
        return self.ledger.summary()

    def _ensure_shot_run(
        self,
        shot_id: str,
        scene_id: str | None,
        character_ids: Iterable[str] | None,
    ) -> ShotRun:
        if shot_id not in self.ledger.shot_runs:
            self.ledger.shot_runs[shot_id] = ShotRun(
                shot_id=shot_id,
                scene_id=scene_id,
                character_ids=list(character_ids or []),
            )
        shot_run = self.ledger.shot_runs[shot_id]
        if scene_id and not shot_run.scene_id:
            shot_run.scene_id = scene_id
        if character_ids:
            shot_run.character_ids = sorted({*shot_run.character_ids, *character_ids})
        return shot_run

    def _apply_decision(
        self,
        shot_run: ShotRun,
        attempt: GenerationAttempt,
        decision: RetryDecision,
    ) -> None:
        if decision.action == "accept":
            shot_run.status = "accepted"
            shot_run.selected_attempt = attempt.attempt
            shot_run.selected_output_uri = attempt.output_uri
        elif decision.action == "retry":
            shot_run.status = "retrying"
        elif decision.action == "stop":
            shot_run.status = "failed"
        else:
            shot_run.status = "needs_review"

    def _prompt_fingerprint(self, request: RuntimeRequest) -> str:
        payload = {
            "backend": request.backend.value,
            "prompt": request.compiled_prompt.prompt,
            "negative_prompt": request.compiled_prompt.negative_prompt,
            "metadata": request.compiled_prompt.metadata,
        }
        raw = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
