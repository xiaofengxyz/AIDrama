from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import yaml

from .batch import BatchProductionRunner
from .director_planner import DirectorPlanner
from .models import (
    BatchProductionItem,
    BatchProductionPlan,
    BatchProductionRun,
    CharacterBible,
    PilotSamplePack,
    PilotSampleTemplate,
    ProductionBible,
    SceneBible,
    SeriesEpisodeBlueprint,
    SeriesProductionBlueprint,
)
from .orchestrator import FilmEngine
from .registry import AssetRegistry, CharacterRegistry, SceneRegistry
from .story_graph import StoryGraphBuilder


class FilmTemplateCatalogLoader:
    """Load checked pilot and series templates from repository sample files."""

    DEFAULT_PILOT_PACK_PATH = Path("samples/pilot_samples/three_60_90s_pilots.yaml")
    DEFAULT_SERIES_BLUEPRINT_PATHS = (
        Path("samples/series_production/vertical_suspense_5ep.yaml"),
    )

    def __init__(self, project_root: str | Path):
        """Store the project root used to resolve relative sample paths."""
        self.project_root = Path(project_root)

    def load_pilot_pack(self, path: str | Path | None = None) -> PilotSamplePack:
        """Load and validate the 60-90 second pilot template pack."""
        source = self._resolve(path or self.DEFAULT_PILOT_PACK_PATH)
        data = self._load_mapping(source)
        payload = data.get("pilot_samples", data)
        if not isinstance(payload, dict):
            raise ValueError("pilot_samples payload must be a mapping")
        return PilotSamplePack(**payload)

    def load_series_blueprints(
        self,
        paths: Sequence[str | Path] | None = None,
    ) -> List[SeriesProductionBlueprint]:
        """Load every configured multi-episode series validation blueprint."""
        sources = paths or self.DEFAULT_SERIES_BLUEPRINT_PATHS
        return [SeriesProductionPlanner.load_file(self._resolve(path)) for path in sources]

    def build_catalog(self) -> Dict[str, Any]:
        """Build the API-ready template catalog used by the Studio home page."""
        pilot_pack = self.load_pilot_pack()
        series_blueprints = self.load_series_blueprints()
        return {
            "status": "ready",
            "source": "repository_samples",
            "pilot_samples": pilot_pack,
            "series_blueprints": series_blueprints,
            "summary": {
                "pilot_sample_count": len(pilot_pack.samples),
                "series_blueprint_count": len(series_blueprints),
                "episode_count": sum(
                    len(blueprint.episodes) for blueprint in series_blueprints
                ),
            },
        }

    def get_pilot_sample(self, sample_id: str) -> PilotSampleTemplate:
        """Find one pilot sample by stable template id."""
        pilot_pack = self.load_pilot_pack()
        for sample in pilot_pack.samples:
            if sample.sample_id == sample_id:
                return sample
        raise KeyError(f"Unknown pilot sample template: {sample_id}")

    def get_series_blueprint(self, blueprint_id: str) -> SeriesProductionBlueprint:
        """Find one series production blueprint by stable template id."""
        for blueprint in self.load_series_blueprints():
            if blueprint.id == blueprint_id:
                return blueprint
        raise KeyError(f"Unknown series template: {blueprint_id}")

    def _resolve(self, path: str | Path) -> Path:
        """Resolve a template path relative to the configured project root."""
        source = Path(path)
        if source.is_absolute():
            return source
        return self.project_root / source

    def _load_mapping(self, path: Path) -> Dict[str, Any]:
        """Read a JSON/YAML sample file and require a mapping at the top level."""
        if not path.exists():
            raise FileNotFoundError(f"Template file does not exist: {path}")
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".json":
            data = json.loads(text)
        else:
            data = yaml.safe_load(text) or {}
        if not isinstance(data, dict):
            raise ValueError(f"Template file must contain a mapping: {path}")
        return data


class SeriesProductionPlanner:
    """Compile a multi-episode series blueprint into reusable Film Core jobs."""

    def __init__(
        self,
        story_graph_builder: StoryGraphBuilder | None = None,
        director_planner: DirectorPlanner | None = None,
    ):
        self.story_graph_builder = story_graph_builder or StoryGraphBuilder()
        self.director_planner = director_planner or DirectorPlanner()

    @classmethod
    def load_file(cls, path: str | Path) -> SeriesProductionBlueprint:
        source = Path(path)
        text = source.read_text(encoding="utf-8")
        if source.suffix.lower() == ".json":
            data = json.loads(text)
        else:
            data = yaml.safe_load(text) or {}
        if not isinstance(data, dict):
            raise ValueError(f"Series blueprint file must contain a mapping: {source}")
        payload = data.get("series_production", data)
        if not isinstance(payload, dict):
            raise ValueError("Series blueprint payload must be a mapping")
        return SeriesProductionBlueprint(**payload)

    def to_batch_plan(self, blueprint: SeriesProductionBlueprint) -> BatchProductionPlan:
        items = [
            self.compile_episode(blueprint, episode)
            for episode in blueprint.episodes
        ]
        return BatchProductionPlan(
            id=f"{blueprint.id}_batch",
            backend=blueprint.backend,
            retry_policy=blueprint.retry_policy,
            items=items,
            continue_on_error=True,
            metadata={
                "series_id": blueprint.id,
                "series_title": blueprint.title,
                "source": "series_production_blueprint",
                **blueprint.metadata,
            },
        )

    def compile_episode(
        self,
        blueprint: SeriesProductionBlueprint,
        episode: SeriesEpisodeBlueprint,
    ) -> BatchProductionItem:
        graph_id = episode.graph_id or f"{blueprint.id}_{episode.episode_id}"
        story_graph = self.story_graph_builder.build_from_script(
            episode.script_text,
            graph_id=graph_id,
            source_title=episode.title,
        )
        program = self.director_planner.plan(story_graph, sequence_id=graph_id)
        program.metadata.update(
            {
                "series_id": blueprint.id,
                "series_title": blueprint.title,
                "episode_id": episode.episode_id,
                "episode_title": episode.title,
            }
        )
        return BatchProductionItem(
            item_id=episode.episode_id,
            program=program,
            backend=blueprint.backend,
            retry_policy=blueprint.retry_policy,
            priority=episode.priority,
            tags=list(episode.tags),
            metadata={
                "series_id": blueprint.id,
                "episode_title": episode.title,
                "graph_id": graph_id,
                **episode.metadata,
            },
        )

    def build_registries(
        self,
        blueprint: SeriesProductionBlueprint,
    ) -> Tuple[CharacterRegistry, SceneRegistry, AssetRegistry]:
        character_bible = CharacterBible(
            id=f"{blueprint.id}_character_bible",
            version=str(blueprint.metadata.get("bible_version", "v1")),
            characters=blueprint.characters,
            continuity_locks=self._locks_for(blueprint, "character_bible"),
            metadata={"series_id": blueprint.id},
        )
        scene_bible = SceneBible(
            id=f"{blueprint.id}_scene_bible",
            version=str(blueprint.metadata.get("bible_version", "v1")),
            scenes=blueprint.scenes,
            continuity_locks=self._locks_for(blueprint, "scene_bible"),
            metadata={"series_id": blueprint.id},
        )
        production_bible = ProductionBible(
            id=f"{blueprint.id}_production_bible",
            version=str(blueprint.metadata.get("bible_version", "v1")),
            props=blueprint.props,
            costumes=blueprint.costumes,
            continuity_locks=self._locks_for(blueprint, "production_bible"),
            metadata={"series_id": blueprint.id},
        )
        return (
            CharacterRegistry(bibles=[character_bible]),
            SceneRegistry(bibles=[scene_bible]),
            AssetRegistry(bibles=[production_bible]),
        )

    def run_blueprint(self, blueprint: SeriesProductionBlueprint) -> BatchProductionRun:
        character_registry, scene_registry, asset_registry = self.build_registries(
            blueprint
        )
        runner = BatchProductionRunner(
            engine_factory=lambda: FilmEngine(
                character_registry=character_registry,
                scene_registry=scene_registry,
                asset_registry=asset_registry,
            )
        )
        return runner.run(self.to_batch_plan(blueprint))

    def _locks_for(
        self,
        blueprint: SeriesProductionBlueprint,
        lock_group: str,
    ) -> Dict[str, Any]:
        locks = blueprint.continuity_locks.get(lock_group, {})
        if not isinstance(locks, dict):
            raise ValueError(f"continuity_locks.{lock_group} must be a mapping")
        return dict(locks)
