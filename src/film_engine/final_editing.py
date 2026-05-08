from __future__ import annotations

from typing import Dict

from .models import FilmEngineRun, FinalEditClip, FinalEditTimeline, ShotTransition


class FinalEditingAssembler:
    """Assemble accepted shot outputs into an edit decision timeline."""

    def assemble(self, run: FilmEngineRun) -> FinalEditTimeline:
        ledger = run.generation_ledger
        selected_outputs = ledger.summary().get("selected_outputs", {}) if ledger else {}
        transition_by_to_shot = self._transition_map(run.graph.transitions)
        clips = []
        unresolved_shots = []
        cursor = 0.0

        for shot in run.graph.shots:
            output_uri = selected_outputs.get(shot.id)
            if not output_uri:
                unresolved_shots.append(shot.id)
                continue

            shot_run = ledger.shot_runs.get(shot.id) if ledger else None
            qa_score = 0.0
            if shot_run and shot_run.selected_attempt is not None:
                for attempt in shot_run.attempts:
                    if attempt.attempt == shot_run.selected_attempt:
                        qa_score = attempt.qa_score
                        break

            clip = FinalEditClip(
                clip_id=f"clip_{len(clips) + 1:03d}",
                shot_id=shot.id,
                output_uri=output_uri,
                start_time=cursor,
                end_time=cursor + shot.duration,
                duration=shot.duration,
                scene_id=run.graph.scene.id,
                character_ids=shot_run.character_ids if shot_run else [],
                transition=transition_by_to_shot.get(shot.id, "cut"),
                qa_score=qa_score,
                metadata={
                    "shot_type": shot.shot_type,
                    "movement": shot.movement,
                    "emotion": shot.emotion,
                },
            )
            clips.append(clip)
            cursor = clip.end_time

        qa_scores = [clip.qa_score for clip in clips]
        return FinalEditTimeline(
            sequence_id=run.graph.sequence_id,
            clips=clips,
            total_duration=cursor,
            unresolved_shots=unresolved_shots,
            qa_summary={
                "clip_count": len(clips),
                "unresolved_count": len(unresolved_shots),
                "average_qa_score": round(sum(qa_scores) / len(qa_scores), 6)
                if qa_scores
                else 0.0,
            },
            metadata={
                "assembler_version": "final_editing.v1",
                "source": "generation_ledger",
            },
        )

    def _transition_map(self, transitions: list[ShotTransition]) -> Dict[str, str]:
        mapping: Dict[str, str] = {}
        for transition in transitions:
            mapping[transition.to_shot] = transition.transition_type
        return mapping
