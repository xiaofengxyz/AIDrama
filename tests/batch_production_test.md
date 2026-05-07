# Batch Production Test

Validate:
- batch plan sample loading
- deterministic priority scheduling
- `max_items` scheduling limit
- per-item Film Core execution
- one failed item does not erase successful item outputs when `continue_on_error` is enabled
- batch summary includes QA, retry, ledger, cost, elapsed time, failed item ids, and selected outputs

Executable coverage:
- `tests/test_film_engine_batch.py`
