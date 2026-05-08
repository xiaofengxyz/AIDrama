from __future__ import annotations

from typing import List

from .ledger import GenerationLedgerRecorder
from .models import (
    CharacterAsset,
    CostumeAsset,
    DirectorProgram,
    DirectorShot,
    FilmEngineRun,
    PromptCompileRequest,
    RetryPolicy,
    RuntimeBackend,
    RuntimeRequest,
    RuntimeResult,
    QAReport,
    PropAsset,
    SceneAsset,
)
from .prompt_compiler import PromptCompiler
from .qa import QAEngine
from .registry import AssetRegistry, CharacterRegistry, SceneRegistry
from .retry import RetryEngine
from .runtime import RuntimeRouter
from .shot_graph import ShotGraphBuilder
from .state import FilmStateEngine


class FilmEngine:
    """Run the minimal industrial Film Core loop end to end."""

    def __init__(
        self,
        character_registry: CharacterRegistry | None = None,
        scene_registry: SceneRegistry | None = None,
        asset_registry: AssetRegistry | None = None,
        runtime_router: RuntimeRouter | None = None,
        prompt_compiler: PromptCompiler | None = None,
        qa_engine: QAEngine | None = None,
        retry_engine: RetryEngine | None = None,
        state_engine: FilmStateEngine | None = None,
        ledger_recorder: GenerationLedgerRecorder | None = None,
    ):
        self.character_registry = character_registry or CharacterRegistry()
        self.scene_registry = scene_registry or SceneRegistry()
        self.asset_registry = asset_registry or AssetRegistry()
        self.runtime_router = runtime_router or RuntimeRouter()
        self.prompt_compiler = prompt_compiler or PromptCompiler()
        self.qa_engine = qa_engine or QAEngine()
        self.retry_engine = retry_engine or RetryEngine()
        self.state_engine = state_engine or FilmStateEngine()
        self.ledger_recorder = ledger_recorder
        self.graph_builder = ShotGraphBuilder()

    def run(
        self,
        program: DirectorProgram,
        backend: RuntimeBackend = RuntimeBackend.DRY_RUN,
        retry_policy: RetryPolicy | None = None,
    ) -> FilmEngineRun:
        policy = retry_policy or RetryPolicy()
        graph = self.graph_builder.build(program)
        scene_asset = self._resolve_scene_asset(program)
        registry_locks = {}
        if self.character_registry.continuity_locks:
            registry_locks["character_bible"] = self.character_registry.continuity_locks
        if self.scene_registry.continuity_locks:
            registry_locks["scene_bible"] = self.scene_registry.continuity_locks
        if self.asset_registry.continuity_locks:
            registry_locks["production_bible"] = self.asset_registry.continuity_locks
        if registry_locks:
            self.state_engine.apply_continuity_locks(registry_locks)
        self.state_engine.register_scene(scene_asset or program.scene)

        runtime_results: List[RuntimeResult] = []
        qa_reports: List[QAReport] = []
        ledger_recorder = self.ledger_recorder or GenerationLedgerRecorder.for_sequence(
            graph.sequence_id
        )

        for shot in graph.shots:
            characters = self._resolve_characters(program.characters, shot.target)
            props, costumes = self._resolve_assets(program, shot)
            self.state_engine.register_characters(characters)
            self.state_engine.register_assets(props, costumes)
            compiled_prompt = self.prompt_compiler.compile(
                PromptCompileRequest(
                    backend=backend,
                    scene=program.scene,
                    shot=shot,
                    characters=characters,
                    props=props,
                    costumes=costumes,
                    scene_asset=scene_asset,
                    film_state=self.state_engine.snapshot(),
                )
            )
            request = RuntimeRequest(
                backend=backend,
                shot_id=shot.id,
                compiled_prompt=compiled_prompt,
                duration=shot.duration,
            )

            while True:
                result = self.runtime_router.generate(request)
                report = self.qa_engine.evaluate(
                    result,
                    request,
                    self.state_engine.state,
                    threshold=policy.min_score,
                )
                runtime_results.append(result)
                qa_reports.append(report)

                decision = self.retry_engine.decide(report, request, policy)
                ledger_recorder.record_attempt(
                    request,
                    result,
                    report,
                    decision,
                    scene_id=program.scene.id,
                    character_ids=[character.id for character in characters],
                    prop_ids=[prop.id for prop in props],
                    costume_ids=[costume.id for costume in costumes],
                )
                if decision.action == "accept":
                    self.state_engine.apply_success(
                        program.scene,
                        shot,
                        characters,
                        props,
                        costumes,
                        result,
                        report,
                    )
                    break
                if decision.action != "retry" or not decision.next_request:
                    break
                request = decision.next_request

        return FilmEngineRun(
            graph=graph,
            runtime_results=runtime_results,
            qa_reports=qa_reports,
            generation_ledger=ledger_recorder.ledger,
            final_state=self.state_engine.state,
            metadata={
                "backend": backend.value,
                "runtime_attempts": len(runtime_results),
                "accepted_shots": len(self.state_engine.state.timeline),
                "generation_ledger": ledger_recorder.summary(),
            },
        )

    def _resolve_scene_asset(self, program: DirectorProgram) -> SceneAsset | None:
        return (
            self.scene_registry.get(program.scene.id)
            or self.scene_registry.get(program.scene.location)
        )

    def _resolve_characters(
        self,
        program_character_ids: List[str],
        shot_target: str | None,
    ) -> List[CharacterAsset]:
        character_ids = []
        if shot_target and self.character_registry.get(shot_target):
            character_ids.append(shot_target)
        for character_id in program_character_ids:
            if character_id not in character_ids and self.character_registry.get(character_id):
                character_ids.append(character_id)
        return self.character_registry.resolve_many(character_ids)

    def _resolve_assets(
        self,
        program: DirectorProgram,
        shot: DirectorShot,
    ) -> tuple[list[PropAsset], list[CostumeAsset]]:
        prop_ids = self._unique_ids([*program.props, *shot.prop_ids])
        costume_ids = self._unique_ids([*program.costumes, *shot.costume_ids])
        return (
            self.asset_registry.resolve_props(prop_ids),
            self.asset_registry.resolve_costumes(costume_ids),
        )

    def _unique_ids(self, values: List[str]) -> List[str]:
        seen = set()
        unique_values = []
        for value in values:
            if value and value not in seen:
                seen.add(value)
                unique_values.append(value)
        return unique_values
