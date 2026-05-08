from __future__ import annotations

from .director_planner import DirectorPlanner
from .final_editing import FinalEditingAssembler
from .models import FilmProductionRun, RetryPolicy, RuntimeBackend
from .orchestrator import FilmEngine
from .registry import AssetRegistry, CharacterRegistry, SceneRegistry
from .story_graph import StoryGraphBuilder


class FilmProductionPipeline:
    """Run the full Script -> Story Graph -> Film Core -> Final Edit path."""

    def __init__(
        self,
        story_graph_builder: StoryGraphBuilder | None = None,
        director_planner: DirectorPlanner | None = None,
        final_editor: FinalEditingAssembler | None = None,
    ):
        self.story_graph_builder = story_graph_builder or StoryGraphBuilder()
        self.director_planner = director_planner or DirectorPlanner()
        self.final_editor = final_editor or FinalEditingAssembler()

    def run_script(
        self,
        script_text: str,
        *,
        graph_id: str = "story_default",
        source_title: str = "",
        backend: RuntimeBackend = RuntimeBackend.DRY_RUN,
        retry_policy: RetryPolicy | None = None,
        character_registry: CharacterRegistry | None = None,
        scene_registry: SceneRegistry | None = None,
        asset_registry: AssetRegistry | None = None,
    ) -> FilmProductionRun:
        story_graph = self.story_graph_builder.build_from_script(
            script_text,
            graph_id=graph_id,
            source_title=source_title,
        )
        director_program = self.director_planner.plan(
            story_graph,
            sequence_id=graph_id,
        )
        film_engine = FilmEngine(
            character_registry=character_registry,
            scene_registry=scene_registry,
            asset_registry=asset_registry,
        )
        film_run = film_engine.run(
            director_program,
            backend=backend,
            retry_policy=retry_policy,
        )
        final_edit = self.final_editor.assemble(film_run)
        return FilmProductionRun(
            story_graph=story_graph,
            director_program=director_program,
            film_run=film_run,
            final_edit=final_edit,
            metadata={
                "pipeline_version": "film_production_pipeline.v1",
                "backend": backend.value,
                "source_title": source_title,
            },
        )
