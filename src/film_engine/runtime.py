from __future__ import annotations

import time
from typing import Dict, Protocol

from .models import RuntimeBackend, RuntimeRequest, RuntimeResult


class RuntimeAdapter(Protocol):
    backend: RuntimeBackend

    def generate(self, request: RuntimeRequest) -> RuntimeResult:
        ...


class DryRunRuntimeAdapter:
    """Deterministic adapter used for tests and graph validation."""

    backend = RuntimeBackend.DRY_RUN

    def generate(self, request: RuntimeRequest) -> RuntimeResult:
        started_at = time.time()
        output_uri = (
            f"dry-run://{request.backend.value}/{request.shot_id}"
            f"/attempt-{request.attempt}"
        )
        return RuntimeResult(
            backend=request.backend,
            shot_id=request.shot_id,
            status="completed",
            output_uri=output_uri,
            elapsed_seconds=max(time.time() - started_at, 0.0),
            metadata={
                "prompt": request.compiled_prompt.prompt,
                "negative_prompt": request.compiled_prompt.negative_prompt,
                "attempt": request.attempt,
                "seed": request.seed,
            },
        )


class RuntimeRouter:
    """Runtime abstraction layer keyed by backend, not provider internals."""

    def __init__(self):
        self._adapters: Dict[RuntimeBackend, RuntimeAdapter] = {}
        self.register(DryRunRuntimeAdapter())

    def register(self, adapter: RuntimeAdapter) -> None:
        self._adapters[adapter.backend] = adapter

    def generate(self, request: RuntimeRequest) -> RuntimeResult:
        adapter = self._adapters.get(request.backend)
        if not adapter:
            raise KeyError(f"No runtime adapter registered for {request.backend.value}")
        return adapter.generate(request)
