from __future__ import annotations

import time
from typing import Callable, List, Tuple

from .models import BatchProductionItem, BatchProductionPlan, BatchProductionRun
from .orchestrator import FilmEngine


class BatchProductionRunner:
    """Deterministic batch runner for multi-sequence Film Core production."""

    def __init__(self, engine_factory: Callable[[], FilmEngine] | None = None):
        self.engine_factory = engine_factory or FilmEngine

    def run(self, plan: BatchProductionPlan) -> BatchProductionRun:
        started_at = time.time()
        item_runs = {}
        errors = {}
        scheduled_items = self._schedule_items(plan)
        item_order = [item.item_id for item in scheduled_items]

        for item in scheduled_items:
            try:
                engine = self.engine_factory()
                item_runs[item.item_id] = engine.run(
                    item.program,
                    backend=item.backend or plan.backend,
                    retry_policy=item.retry_policy or plan.retry_policy,
                )
            except Exception as exc:
                errors[item.item_id] = str(exc)
                if not plan.continue_on_error:
                    raise

        finished_at = time.time()
        return BatchProductionRun(
            plan_id=plan.id,
            planned_item_count=len(plan.items),
            scheduled_item_count=len(scheduled_items),
            item_order=item_order,
            item_runs=item_runs,
            errors=errors,
            metadata={
                "backend": plan.backend.value,
                "continue_on_error": plan.continue_on_error,
                "max_items": plan.max_items,
                "elapsed_seconds": round(finished_at - started_at, 6),
                **plan.metadata,
            },
            created_at=started_at,
            updated_at=finished_at,
        )

    def _schedule_items(self, plan: BatchProductionPlan) -> List[BatchProductionItem]:
        indexed_items: List[Tuple[int, int, BatchProductionItem]] = [
            (item.priority, index, item) for index, item in enumerate(plan.items)
        ]
        scheduled = [item for _, _, item in sorted(indexed_items)]
        if plan.max_items:
            scheduled = scheduled[: plan.max_items]
        return scheduled
