# Planning Grounding Rules

Classification: `sanitized_derivative`

Production status: generalized requirements evidence

## Analytical Rules

1. Declare the grain before aggregating, normally one row per `asset_group_id`.
2. Prefer validated attributes over raw inferred attributes when both exist.
3. Never add a raw value and its validated replacement together.
4. Surface blocked, not-ready, or exception states before optimization advice.
5. Keep quantity, processing time, labor rate, and unit cost at compatible grains.
6. State units, effective dates, currency, null behavior, and aggregation policy.
7. Separate descriptive facts from recommendations and unresolved assumptions.
8. Return source references and warnings with every decision-oriented answer.

## Response Shape

```text
finding
supporting measures
business implication
assumptions and data-quality warnings
source references
recommended next action
```

These rules consume precomputed measures. They are not a recovered complexity,
labor, scheduling, or financial calculation engine.
