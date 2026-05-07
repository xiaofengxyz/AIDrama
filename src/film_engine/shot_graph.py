from __future__ import annotations

from typing import Dict, List

from .models import DirectorProgram, ShotGraph, ShotTransition


class ShotGraphBuilder:
    """Build graph edges and adjacency from a Director DSL program."""

    def build(self, program: DirectorProgram) -> ShotGraph:
        transitions = list(program.transitions)
        if not transitions and len(program.shots) > 1:
            transitions = [
                ShotTransition(
                    from_shot=program.shots[index].id,
                    to_shot=program.shots[index + 1].id,
                    transition_type="cut",
                )
                for index in range(len(program.shots) - 1)
            ]

        adjacency: Dict[str, List[str]] = {shot.id: [] for shot in program.shots}
        known_ids = set(adjacency)
        for transition in transitions:
            if transition.from_shot not in known_ids or transition.to_shot not in known_ids:
                raise ValueError(
                    "Transition references unknown shot: "
                    f"{transition.from_shot} -> {transition.to_shot}"
                )
            if transition.from_shot == transition.to_shot:
                raise ValueError(f"Shot graph cannot self-loop on {transition.from_shot}")
            adjacency[transition.from_shot].append(transition.to_shot)

        self._validate_acyclic(adjacency)

        return ShotGraph(
            sequence_id=program.sequence_id,
            scene=program.scene,
            shots=program.shots,
            transitions=transitions,
            adjacency=adjacency,
            metadata={"graph_type": "directed_shot_sequence"},
        )

    def _validate_acyclic(self, adjacency: Dict[str, List[str]]) -> None:
        visiting = set()
        visited = set()

        def visit(shot_id: str) -> None:
            if shot_id in visiting:
                raise ValueError(f"Shot graph contains a cycle at {shot_id}")
            if shot_id in visited:
                return
            visiting.add(shot_id)
            for next_shot_id in adjacency.get(shot_id, []):
                visit(next_shot_id)
            visiting.remove(shot_id)
            visited.add(shot_id)

        for shot_id in adjacency:
            visit(shot_id)
