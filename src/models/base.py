from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple

from .runtime_config import ModelRuntimeEndpoint, resolve_model_runtime_endpoint

class VideoGenModel(ABC):
    """Abstract base class for video generation models."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config or {}

    def resolve_endpoint(self, provider: str, **kwargs: Any) -> ModelRuntimeEndpoint:
        """Resolve provider base URL and credentials through the shared adapter layer."""
        return resolve_model_runtime_endpoint(self.config, provider, **kwargs)

    @abstractmethod
    def generate(self, prompt: str, output_path: str, **kwargs) -> Tuple[str, float]:
        """
        Generates a video from a prompt.

        Args:
            prompt: The input text prompt.
            output_path: The path to save the generated video.
            **kwargs: Additional arguments.

        Returns:
            A tuple containing:
            - The path to the generated video file.
            - The duration of the API generation process in seconds (excluding download).
        """
        pass
