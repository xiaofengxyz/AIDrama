# AIDrama Project Notes

This project is an AI Film Engine workspace. The target platform base is Jellyfish, and the runnable product entry is AIDrama Studio for local production, verification, and migration.

Recommended local path:

```bash
make up
```

Then open:

- Frontend: http://localhost:3014
- Backend API: http://localhost:17177/docs

Secrets are read from `Doc/accounts` and written to local `.env.local` by `scripts/bootstrap_env.sh`. `Doc/accounts`, `.env.local`, and legacy `.env` are ignored by git.

Read these project-specific docs first:

- `docs/README.md`
- `docs/project-overview.md`
- `docs/local-setup.md`
- `docs/open-source-comparison.md`
- `docs/ai-drama-business-plan.md`
- `docs/task-progress.md`
- `agent.md`
