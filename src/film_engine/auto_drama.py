from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Optional

from pydantic import BaseModel, Field

from .models import FilmProductionRun, RetryPolicy, RuntimeBackend
from .novel import NovelEngine, NovelPlan
from .pipeline import FilmProductionPipeline
from .workflow_prompts import (
    WorkflowPromptExecutionPlan,
    WorkflowPromptModule,
    build_prompt_execution_plan,
    load_workflow_prompt_modules,
)


class AutoDramaRun(BaseModel):
    """End-to-end artifact for text -> novel -> AI drama dry-run production."""

    title: str
    status: str = "completed"
    waiting_for_stage: Optional[str] = None
    novel_plan: Optional[NovelPlan] = None
    screenplay_text: str = ""
    production_run: Optional[FilmProductionRun] = None
    prompt_execution_plan: WorkflowPromptExecutionPlan
    metadata: Dict[str, object] = Field(default_factory=dict)


class AutoDramaPipeline:
    """Executable workflow that respects prompt auto/manual switches."""

    def __init__(
        self,
        *,
        novel_engine: Optional[NovelEngine] = None,
        film_pipeline: Optional[FilmProductionPipeline] = None,
        prompt_root: str | Path = "docs/Codex_Workflow_Prompts",
    ):
        self.novel_engine = novel_engine or NovelEngine()
        self.film_pipeline = film_pipeline or FilmProductionPipeline()
        self.prompt_root = Path(prompt_root)

    def run(
        self,
        seed_text: str,
        *,
        title: str = "Untitled AI Drama",
        target_chapters: int = 3,
        backend: RuntimeBackend = RuntimeBackend.DRY_RUN,
        retry_policy: Optional[RetryPolicy] = None,
        auto_overrides: Optional[Dict[str, bool]] = None,
    ) -> AutoDramaRun:
        """Run all workflow modules until completion or a manual gate pauses."""
        modules = self._apply_auto_overrides(
            load_workflow_prompt_modules(self.prompt_root),
            auto_overrides or {},
        )
        completed_module_ids = []
        novel_plan: Optional[NovelPlan] = None
        screenplay_text = ""
        production_run: Optional[FilmProductionRun] = None

        for module in modules:
            switch = module.switch
            if switch.stage_id == "stage1_novel_engine" and novel_plan is None:
                novel_plan = self.novel_engine.expand(
                    seed_text,
                    title=title,
                    target_chapters=target_chapters,
                )
                screenplay_text = self.novel_engine.to_screenplay(novel_plan)

            if switch.stage_id == "final_integration":
                if novel_plan is None:
                    novel_plan = self.novel_engine.expand(
                        seed_text,
                        title=title,
                        target_chapters=target_chapters,
                    )
                    screenplay_text = self.novel_engine.to_screenplay(novel_plan)
                production_run = self.film_pipeline.run_script(
                    screenplay_text,
                    graph_id=self._safe_graph_id(title),
                    source_title=title,
                    backend=backend,
                    retry_policy=retry_policy or RetryPolicy(),
                )

            completed_module_ids.append(switch.module_id)
            if switch.should_wait_for_user:
                return AutoDramaRun(
                    title=title,
                    status="waiting_for_user",
                    waiting_for_stage=switch.stage_id,
                    novel_plan=novel_plan,
                    screenplay_text=screenplay_text,
                    production_run=production_run,
                    prompt_execution_plan=build_prompt_execution_plan(
                        modules,
                        completed_module_ids=completed_module_ids,
                    ),
                    metadata={
                        "pipeline_version": "auto_drama_pipeline.v1",
                        "backend": backend.value,
                    },
                )

        if novel_plan is None:
            novel_plan = self.novel_engine.expand(
                seed_text,
                title=title,
                target_chapters=target_chapters,
            )
            screenplay_text = self.novel_engine.to_screenplay(novel_plan)

        if production_run is None:
            production_run = self.film_pipeline.run_script(
                screenplay_text,
                graph_id=self._safe_graph_id(title),
                source_title=title,
                backend=backend,
                retry_policy=retry_policy or RetryPolicy(),
            )

        return AutoDramaRun(
            title=title,
            status="completed",
            novel_plan=novel_plan,
            screenplay_text=screenplay_text,
            production_run=production_run,
            prompt_execution_plan=build_prompt_execution_plan(
                modules,
                completed_module_ids=completed_module_ids,
            ),
            metadata={
                "pipeline_version": "auto_drama_pipeline.v1",
                "backend": backend.value,
                "target_chapters": target_chapters,
            },
        )

    def _apply_auto_overrides(
        self,
        modules: Iterable[WorkflowPromptModule],
        overrides: Dict[str, bool],
    ) -> list[WorkflowPromptModule]:
        """Apply request-time auto/manual switches without mutating prompt files."""
        updated = []
        for module in modules:
            switch = module.switch
            if switch.module_id in overrides:
                auto_advance = bool(overrides[switch.module_id])
                switch = switch.model_copy(
                    update={
                        "auto_advance": auto_advance,
                        "requires_human_review": not auto_advance,
                        "stop_after_stage": not auto_advance,
                    }
                )
                module = module.model_copy(update={"switch": switch})
            updated.append(module)
        return updated

    def _safe_graph_id(self, title: str) -> str:
        """Create a deterministic graph id from the requested title."""
        slug = "".join(ch.lower() if ch.isalnum() else "_" for ch in title).strip("_")
        return f"auto_{slug or 'drama'}"
