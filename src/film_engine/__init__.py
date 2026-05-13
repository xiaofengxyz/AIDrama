"""Industrial AI Film Engine core primitives.

The package is intentionally independent from any UI scaffold. It gives the
project a small, testable Film Core that can later be wired into Jellyfish-style
Studio OS surfaces, queues, real video runtimes, and visual QA systems.
"""

from .batch import BatchProductionRunner
from .auto_drama import AutoDramaPipeline, AutoDramaRun
from .director_dsl import DirectorDSLParser
from .director_planner import DirectorPlanner
from .final_editing import FinalEditingAssembler
from .ledger import GenerationLedgerRecorder
from .models import (
    BatchProductionItem,
    BatchProductionPlan,
    BatchProductionRun,
    CharacterAsset,
    CharacterBible,
    CompiledPrompt,
    CostumeAsset,
    DirectorProgram,
    DirectorScene,
    DirectorShot,
    FilmEngineRun,
    FilmProductionRun,
    FilmState,
    FinalEditClip,
    FinalEditTimeline,
    GenerationAttempt,
    GenerationLedger,
    PilotSamplePack,
    PilotSampleTemplate,
    PromptCompileRequest,
    ProductionBible,
    PropAsset,
    QAReport,
    RetryPolicy,
    RuntimeBackend,
    RuntimeRequest,
    RuntimeResult,
    SceneAsset,
    SceneBible,
    SeriesEpisodeBlueprint,
    SeriesProductionBlueprint,
    ShotRun,
    ShotGraph,
    ShotTransition,
    StoryBeat,
    StoryGraph,
    StoryGraphEdge,
)
from .orchestrator import FilmEngine
from .novel import NovelChapter, NovelEngine, NovelPlan, NovelRelationship
from .pipeline import FilmProductionPipeline
from .production_extraction import (
    EpisodeProductionExtractor,
    EpisodeProductionPackage,
    ExtractedProductionAsset,
    ExtractedStoryboardFrame,
)
from .prompt_compiler import PromptCompiler
from .qa import QAEngine
from .registry import AssetRegistry, CharacterRegistry, SceneRegistry
from .retry import RetryEngine
from .runtime import DryRunRuntimeAdapter, RuntimeRouter
from .series import FilmTemplateCatalogLoader, SeriesProductionPlanner
from .shot_graph import ShotGraphBuilder
from .state import FilmStateEngine
from .story_graph import StoryGraphBuilder
from .workflow import (
    RenderPackageExporter,
    RuntimeModelRecommendation,
    WorkflowEditEvent,
    WorkflowStageDefinition,
    WorkflowStageState,
    WorkflowState,
    WorkflowStateStore,
    evaluate_project_workflow,
    get_model_recommendation_catalog,
    get_workflow_stage_definitions,
)
from .workflow_prompts import (
    WorkflowPromptExecutionPlan,
    WorkflowPromptExecutionStep,
    WorkflowPromptModule,
    WorkflowPromptSwitch,
    build_prompt_execution_plan,
    load_workflow_prompt_modules,
    parse_workflow_prompt_module,
)

__all__ = [
    "BatchProductionItem",
    "AutoDramaPipeline",
    "AutoDramaRun",
    "BatchProductionPlan",
    "BatchProductionRun",
    "BatchProductionRunner",
    "AssetRegistry",
    "CharacterAsset",
    "CharacterBible",
    "CharacterRegistry",
    "CompiledPrompt",
    "CostumeAsset",
    "DirectorDSLParser",
    "DirectorPlanner",
    "DirectorProgram",
    "DirectorScene",
    "DirectorShot",
    "DryRunRuntimeAdapter",
    "EpisodeProductionExtractor",
    "EpisodeProductionPackage",
    "ExtractedProductionAsset",
    "ExtractedStoryboardFrame",
    "FinalEditClip",
    "FinalEditTimeline",
    "FinalEditingAssembler",
    "FilmEngine",
    "FilmEngineRun",
    "FilmProductionPipeline",
    "FilmProductionRun",
    "FilmState",
    "FilmStateEngine",
    "FilmTemplateCatalogLoader",
    "GenerationAttempt",
    "GenerationLedger",
    "GenerationLedgerRecorder",
    "NovelChapter",
    "NovelEngine",
    "NovelPlan",
    "NovelRelationship",
    "PilotSamplePack",
    "PilotSampleTemplate",
    "PromptCompileRequest",
    "PromptCompiler",
    "ProductionBible",
    "PropAsset",
    "QAEngine",
    "QAReport",
    "RetryEngine",
    "RetryPolicy",
    "RuntimeBackend",
    "RuntimeRequest",
    "RuntimeResult",
    "RuntimeRouter",
    "RenderPackageExporter",
    "RuntimeModelRecommendation",
    "SceneAsset",
    "SceneBible",
    "SceneRegistry",
    "SeriesEpisodeBlueprint",
    "SeriesProductionBlueprint",
    "SeriesProductionPlanner",
    "ShotRun",
    "ShotGraph",
    "ShotGraphBuilder",
    "ShotTransition",
    "StoryBeat",
    "StoryGraph",
    "StoryGraphBuilder",
    "StoryGraphEdge",
    "WorkflowEditEvent",
    "WorkflowPromptExecutionPlan",
    "WorkflowPromptExecutionStep",
    "WorkflowPromptModule",
    "WorkflowPromptSwitch",
    "WorkflowStageDefinition",
    "WorkflowStageState",
    "WorkflowState",
    "WorkflowStateStore",
    "evaluate_project_workflow",
    "build_prompt_execution_plan",
    "get_model_recommendation_catalog",
    "get_workflow_stage_definitions",
    "load_workflow_prompt_modules",
    "parse_workflow_prompt_module",
]
