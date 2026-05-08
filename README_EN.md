# AIDrama Studio

AIDrama is an industrial AI Film Engine workspace aligned with Jellyfish as the target Studio OS base. It focuses on cinematic storytelling, character consistency, shot continuity, film state continuity, automated QA, automated retry, and batch production.

## Pipeline

```text
Novel / Script
-> Story Graph
-> Director Planner
-> Film Core
-> Prompt Compiler
-> Runtime Adapter
-> Render Runtime / Video Models
-> QA Engine
-> Retry Engine
-> Final Editing
```

## Run

```bash
make up
```

Open:

- Studio: http://localhost:3014
- Backend API: http://localhost:17177/docs

## Validate

```bash
python3 -m pytest tests/test_film_engine_core.py tests/test_film_engine_batch.py tests/test_film_production_pipeline.py -q -s
cd frontend && npm run test
docker compose config --quiet
```

## Project Notes

- Target platform base: Jellyfish
- Runnable product entry: AIDrama Studio
- Core engine package: `src/film_engine/`
- Temporary upstream clones live under ignored `external/`
- Secrets and generated media must never be committed

Start from [docs/README.md](docs/README.md) and [docs/task-progress.md](docs/task-progress.md) when continuing work.
