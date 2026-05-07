# Batch Production Benchmark

Benchmark target:
- load `samples/batch_production/pilot_batch.yaml`
- run with `RuntimeBackend.DRY_RUN`
- preserve deterministic item order by priority
- complete two scheduled items
- produce three accepted shots
- produce three total attempts when QA passes without retry

Baseline command:

```bash
python3 -m pytest tests/test_film_engine_batch.py -q -s
```

Expected baseline:
- sample batch test passes
- batch summary reports `accepted_items == 2`
- batch summary reports `total_shots == 3`
- batch summary reports `total_attempts == 3`
