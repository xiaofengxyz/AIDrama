"""Industrial AI Film Engine core primitives.

The package is intentionally independent from the LumenX app pipeline. It gives
the project a small, testable Film Core that can later be wired into FastAPI,
queues, real video runtimes, and visual QA systems.
"""

from .director_dsl import DirectorDSLParser
from .models import (
    CharacterAsset,
    CharacterBible,
    CompiledPrompt,
    DirectorProgram,
    DirectorScene,
    DirectorShot,
    FilmEngineRun,
    FilmState,
    PromptCompileRequest,
    QAReport,
    RetryPolicy,
    RuntimeBackend,
    RuntimeRequest,
    RuntimeResult,
    SceneAsset,
    SceneBible,
    ShotGraph,
    ShotTransition,
)
from .orchestrator import FilmEngine
from .prompt_compiler import PromptCompiler
from .qa import QAEngine
from .registry import CharacterRegistry, SceneRegistry
from .retry import RetryEngine
from .runtime import DryRunRuntimeAdapter, RuntimeRouter
from .shot_graph import ShotGraphBuilder
from .state import FilmStateEngine

__all__ = [
    "CharacterAsset",
    "CharacterBible",
    "CharacterRegistry",
    "CompiledPrompt",
    "DirectorDSLParser",
    "DirectorProgram",
    "DirectorScene",
    "DirectorShot",
    "DryRunRuntimeAdapter",
    "FilmEngine",
    "FilmEngineRun",
    "FilmState",
    "FilmStateEngine",
    "PromptCompileRequest",
    "PromptCompiler",
    "QAEngine",
    "QAReport",
    "RetryEngine",
    "RetryPolicy",
    "RuntimeBackend",
    "RuntimeRequest",
    "RuntimeResult",
    "RuntimeRouter",
    "SceneAsset",
    "SceneBible",
    "SceneRegistry",
    "ShotGraph",
    "ShotGraphBuilder",
    "ShotTransition",
]
