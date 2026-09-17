# Planning Grounding Rules

Classification: `sanitized_derivative`

Evidence status: recovered domain rules; calculation implementation absent

## Recovered Prior Pattern

The source pattern emphasized declared grain, validated-over-raw precedence,
anti-double-counting, readiness exceptions, compatible units, and evidence-led
answers. The available material did not establish a complete semantic model or
calculation engine.

## Reconstructed Planning Vocabulary

| Entity or concept | Declared grain | Safe analytical use |
| --- | --- | --- |
| `planning_inventory` | One current planning record per `asset_group_id` and reporting period | Readiness, category, complexity, and approved descriptive workload measures |
| Capacity scenario | One scenario per forecast version, assumption version, and reporting period | Deterministic comparison of workload minutes with available productive minutes |
| Evidence result | One normalized tool invocation | Source version, measure references, warnings, status, and optional calculation trace |

Approved descriptive measures are `inventory_count` (distinct planning groups),
`average_complexity_score` (average of the effective score at planning-group
grain), and `workload_hours` (approved workload minutes divided by 60 after
compatible-grain aggregation). Scenario outputs are `workload_minutes`,
`available_capacity_minutes`, `required_people`, and `capacity_gap`; formulas,
rounding, and null behavior belong to a versioned deterministic tool rather than
the language model. The reconstructed contract defines available capacity as
people multiplied by productive minutes per person, required people as workload
minutes divided by productive minutes per person under an explicit rounding
policy, and a positive capacity gap as workload minutes above available minutes.

Supported analytical time grains are `reporting_period` for inventory snapshots
and capacity decisions, and `forecast_horizon` for a declared contiguous set of
reporting periods. Mixing snapshot values across periods is prohibited unless a
measure defines its cross-period aggregation. A period label without a calendar
mapping is unresolved, not inferred.

## Analytical Rules

1. Declare entity, measure grain, and time grain before aggregating, normally one
   row per `asset_group_id` and reporting period for planning inventory.
2. Prefer validated attributes over raw inferred attributes when both exist.
3. Never add a raw value and its validated replacement together.
4. Surface blocked, not-ready, or exception states before optimization advice.
5. Keep quantity, processing time, labor rate, and unit cost at compatible grains.
6. State units, effective dates, currency, null behavior, and aggregation policy.
7. Separate descriptive facts from recommendations and unresolved assumptions.
8. Return source references and warnings with every decision-oriented answer.
9. Treat missing, suppressed, stale, and not-applicable values distinctly; none
   may be silently converted to zero.
10. Ask for the reporting period, scenario, or unit when it materially changes
    the result, unless a disclosed versioned policy default applies.

## Response Shape

```text
finding
supporting measures, units, and time grain
business implication
assumptions and data-quality warnings
source and measure references
recommended next action
approval state when the action is consequential
```

## Known Risks And Missing Implementation

Many-to-many joins, repeated snapshot totals, averaging pre-aggregated values,
mixing validated and inferred fields, stale assumption versions, inconsistent
minutes/hours, and treating no-data as zero can all produce plausible but wrong
answers. These reconstructed rules mitigate those risks but are not a recovered
semantic-model file, complexity model, labor model, scheduling engine, financial
engine, or verified calculation implementation.
