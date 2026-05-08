# Contributing to AIDrama Studio

Thanks for helping build AIDrama Studio, an industrial AI Film Engine workspace aligned with Jellyfish as the target platform base.

## Principles

- Keep workflow graph-driven.
- Keep Film Core independent from specific UI and model vendors.
- Prefer reusable systems over prompt hardcoding.
- Preserve character, costume, prop, scene, shot, and film state continuity.
- Add tests when touching shared contracts, runtime routing, QA, retry, or batch production.

## Local Setup

```bash
make up
```

Run focused checks:

```bash
python3 -m compileall -q src/film_engine
python3 -m pytest tests/test_film_engine_core.py tests/test_film_engine_batch.py tests/test_film_production_pipeline.py -q -s
cd frontend && npm run test
```

## Git Hygiene

- Do not commit secrets, generated media, `output/`, `.env.local`, `.env`, `Doc/accounts`, or `external/`.
- Keep changes scoped to the task.
- Update `docs/task-progress.md` whenever a session changes architecture, tests, startup, or rollout status.
- Before committing, run `git diff --check` and confirm `git ls-files -u` is empty.

## Architecture Notes

New engine work should fit the fixed chain:

```text
Novel / Script -> Story Graph -> Director Planner -> Film Core -> Prompt Compiler -> Runtime Adapter -> QA -> Retry -> Final Editing
```

Runtime integrations must go through adapters and provider registries. UI code should not depend directly on vendor-specific details.
