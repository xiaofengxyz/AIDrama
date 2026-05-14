"""
LLM Adapter - Unified interface for DashScope and OpenAI-compatible APIs.

Supports two providers:
  - dashscope (default): Alibaba Cloud DashScope via OpenAI-compatible endpoint
  - openai: Any OpenAI-compatible API (OpenAI, DeepSeek, Ollama, etc.)

Configuration via environment variables:
  LLM_PROVIDER=dashscope|openai
  DASHSCOPE_API_KEY=...
  OPENAI_API_KEY=...
  OPENAI_BASE_URL=https://api.openai.com/v1
  OPENAI_MODEL=gpt-4o
"""
import os
import logging
from typing import Dict, List, Optional, Any

from ...models.runtime_config import resolve_model_runtime_endpoint

logger = logging.getLogger(__name__)


class LLMAdapter:
    """Unified LLM call interface supporting DashScope and OpenAI-compatible APIs."""

    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "dashscope").lower()
        self._client = None
        logger.info(f"LLM Adapter initialized with provider: {self.provider}")

    @property
    def is_configured(self) -> bool:
        if self.provider == "openai":
            return resolve_model_runtime_endpoint({}, "OPENAI").is_configured
        return resolve_model_runtime_endpoint({}, "DASHSCOPE").is_configured

    def _get_client(self):
        """Get or create the OpenAI-compatible client (lazy, cached)."""
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError:
                raise RuntimeError(
                    "openai package not installed. Run: pip install openai>=1.0.0"
                )

            if self.provider == "openai":
                endpoint = resolve_model_runtime_endpoint({}, "OPENAI")
                self._client = OpenAI(
                    api_key=endpoint.api_key,
                    base_url=endpoint.base_url,
                )
            else:
                # DashScope uses OpenAI-compatible endpoint
                endpoint = resolve_model_runtime_endpoint({}, "DASHSCOPE")
                compatible_base_url = (
                    os.getenv("DASHSCOPE_COMPATIBLE_BASE_URL")
                    or f"{endpoint.base_url}/compatible-mode/v1"
                )
                self._client = OpenAI(
                    api_key=endpoint.api_key,
                    base_url=compatible_base_url.rstrip("/"),
                )
        return self._client

    def _get_default_model(self) -> str:
        """Return the provider default text model for storyboard and script tasks."""
        if self.provider == "openai":
            return os.getenv("OPENAI_MODEL", "gpt-4o")
        return os.getenv("DASHSCOPE_MODEL", "qwen-plus")

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        response_format: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Send a chat completion request and return the response content.

        Args:
            messages: List of {"role": ..., "content": ...} dicts
            model: Model name override (uses provider default if None)
            response_format: Optional {"type": "json_object"} constraint

        Returns:
            The assistant's response content as a string.

        Raises:
            RuntimeError: If the API call fails.
        """
        client = self._get_client()
        model = model or self._get_default_model()

        kwargs: Dict[str, Any] = {
            "model": model,
            "messages": messages,
        }
        if response_format:
            kwargs["response_format"] = response_format

        try:
            response = client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            provider_label = "DashScope" if self.provider != "openai" else "OpenAI"
            raise RuntimeError(f"{provider_label} API error: {e}") from e
