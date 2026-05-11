from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import yaml
from pydantic import BaseModel, Field


PROMPT_SWITCH_VERSION = "workflow_prompt_switch.v1"


class WorkflowPromptSwitch(BaseModel):
    """Machine-readable execution switch embedded in a prompt module file."""

    module_id: str
    stage_id: str
    label: str = ""
    auto_advance: bool = True
    requires_human_review: bool = False
    stop_after_stage: bool = False
    description: str = ""

    @property
    def should_wait_for_user(self) -> bool:
        """Return true when execution must pause after this module completes."""
        return bool(
            not self.auto_advance
            or self.requires_human_review
            or self.stop_after_stage
        )


class WorkflowPromptModule(BaseModel):
    """One markdown prompt module plus its parsed execution switch."""

    path: str
    filename: str
    order: int
    title: str
    switch: WorkflowPromptSwitch
    body_preview: str = ""


class WorkflowPromptExecutionStep(BaseModel):
    """Runtime execution state for one prompt module in the auto workflow."""

    module_id: str
    stage_id: str
    label: str
    order: int
    status: str = "pending"
    auto_advance: bool = True
    waits_for_user: bool = False
    reason: str = ""


class WorkflowPromptExecutionPlan(BaseModel):
    """Ordered execution plan derived from prompt switches."""

    version: str = PROMPT_SWITCH_VERSION
    status: str = "ready"
    first_waiting_stage: Optional[str] = None
    steps: List[WorkflowPromptExecutionStep] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)


_FRONTMATTER_RE = re.compile(r"\A---\s*\n(?P<body>.*?)\n---\s*\n?", re.DOTALL)


def _default_switch_for_file(path: Path) -> WorkflowPromptSwitch:
    """Provide a conservative auto switch for legacy prompt files."""
    stem = path.stem.lower()
    return WorkflowPromptSwitch(
        module_id=stem,
        stage_id=stem,
        label=stem.replace("_", " ").title(),
        auto_advance=True,
        description="Legacy prompt without explicit switch; defaulting to automatic execution.",
    )


def _module_order(path: Path) -> int:
    """Sort prompt modules by numeric filename prefix when present."""
    match = re.match(r"^(\d+)_", path.name)
    return int(match.group(1)) if match else 999


def _title_from_body(path: Path, body: str, switch: WorkflowPromptSwitch) -> str:
    """Resolve a display title from markdown, switch label, or filename."""
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return switch.label or path.stem.replace("_", " ").title()


def parse_workflow_prompt_module(path: Path) -> WorkflowPromptModule:
    """Parse one markdown prompt module and its optional YAML frontmatter."""
    text = path.read_text(encoding="utf-8")
    switch = _default_switch_for_file(path)
    body = text

    match = _FRONTMATTER_RE.match(text)
    if match:
        raw_frontmatter = match.group("body")
        body = text[match.end():]
        parsed = yaml.safe_load(raw_frontmatter) or {}
        switch_payload = parsed.get("workflow_switch") or parsed
        if isinstance(switch_payload, dict):
            switch = WorkflowPromptSwitch(**switch_payload)

    preview = " ".join(part.strip() for part in body.splitlines() if part.strip())[:240]
    return WorkflowPromptModule(
        path=str(path),
        filename=path.name,
        order=_module_order(path),
        title=_title_from_body(path, body, switch),
        switch=switch,
        body_preview=preview,
    )


def load_workflow_prompt_modules(root: str | Path) -> List[WorkflowPromptModule]:
    """Load all markdown workflow prompt modules in execution order."""
    prompt_root = Path(root)
    if not prompt_root.exists():
        raise FileNotFoundError(f"Workflow prompt directory not found: {prompt_root}")

    modules = [
        parse_workflow_prompt_module(path)
        for path in prompt_root.glob("*.md")
        if path.is_file() and re.match(r"^\d+_", path.name)
    ]
    return sorted(modules, key=lambda item: (item.order, item.filename))


def build_prompt_execution_plan(
    modules: Iterable[WorkflowPromptModule],
    *,
    completed_module_ids: Optional[Iterable[str]] = None,
) -> WorkflowPromptExecutionPlan:
    """Build an execution plan that pauses on the first manual-gated module."""
    completed = set(completed_module_ids or [])
    steps: List[WorkflowPromptExecutionStep] = []
    first_waiting_stage: Optional[str] = None

    for module in modules:
        switch = module.switch
        waits = switch.should_wait_for_user
        status = "completed" if switch.module_id in completed else "ready"
        reason = ""
        if waits and first_waiting_stage is None:
            status = "waiting_for_user" if switch.module_id in completed else "will_pause"
            first_waiting_stage = switch.stage_id
            reason = "Manual review switch is enabled for this module."
        elif waits:
            reason = "Manual review switch is enabled, but an earlier gate pauses first."

        steps.append(
            WorkflowPromptExecutionStep(
                module_id=switch.module_id,
                stage_id=switch.stage_id,
                label=switch.label or module.title,
                order=module.order,
                status=status,
                auto_advance=switch.auto_advance,
                waits_for_user=waits,
                reason=reason,
            )
        )

    status = "waiting_for_user" if first_waiting_stage else "ready"
    return WorkflowPromptExecutionPlan(
        status=status,
        first_waiting_stage=first_waiting_stage,
        steps=steps,
        summary={
            "module_count": len(steps),
            "auto_modules": sum(1 for step in steps if step.auto_advance),
            "manual_gates": sum(1 for step in steps if step.waits_for_user),
        },
    )
