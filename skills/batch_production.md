# Batch Production Skill

Goal:
Turn multiple Director DSL programs into a deterministic production batch.

Batch production must:
- keep each sequence isolated by default
- preserve QA, Retry, Film State, and Generation Ledger outputs per item
- continue the batch when one item fails, when configured
- summarize accepted items, failed items, shot counts, retry counts, selected outputs, cost, and elapsed time

Requirements:
- `BatchProductionPlan` is the stable input contract
- `BatchProductionRunner` is the execution boundary
- runtime backends stay behind `RuntimeRouter`
- no provider-specific prompt or media logic belongs in the batch layer
