from __future__ import annotations

from .models import CompiledPrompt, QAReport, RetryDecision, RetryPolicy, RuntimeRequest


class RetryEngine:
    """Turn QA failures into deterministic repair attempts."""

    def decide(
        self,
        report: QAReport,
        request: RuntimeRequest,
        policy: RetryPolicy,
    ) -> RetryDecision:
        if report.passed:
            return RetryDecision(
                shot_id=request.shot_id,
                action="accept",
                reason="QA passed",
            )

        repair_notes = [
            finding.repair_hint or finding.message
            for finding in report.findings
            if finding.repair_hint or finding.message
        ]

        if request.attempt >= policy.max_attempts:
            return RetryDecision(
                shot_id=request.shot_id,
                action="stop",
                reason="retry budget exhausted",
                repair_notes=repair_notes,
            )

        next_prompt = request.compiled_prompt
        if policy.repair_failed_prompts and repair_notes:
            repaired_text = (
                next_prompt.prompt
                + "; repair pass: "
                + "; ".join(repair_notes)
            )
            next_prompt = CompiledPrompt(
                backend=next_prompt.backend,
                shot_id=next_prompt.shot_id,
                prompt=repaired_text,
                negative_prompt=next_prompt.negative_prompt,
                metadata={
                    **next_prompt.metadata,
                    "repair_notes": repair_notes,
                },
            )

        return RetryDecision(
            shot_id=request.shot_id,
            action="retry",
            reason="QA failed below threshold",
            repair_notes=repair_notes,
            next_request=request.model_copy(
                update={
                    "attempt": request.attempt + 1,
                    "compiled_prompt": next_prompt,
                    "repair_notes": [*request.repair_notes, *repair_notes],
                }
            ),
        )
