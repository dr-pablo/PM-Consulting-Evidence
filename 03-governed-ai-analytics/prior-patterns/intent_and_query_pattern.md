# Intent and Query Pattern

Classification: `sanitized_derivative`

Evidence status: recovered request-to-query pattern; execution unverified

## Recovered Prior Pattern

The prior material separated intent extraction from query execution and used
structured fields for entity, filters, measures, grouping, and limit. That is a
sound boundary, but the recovered example did not fully align requested metrics
with selected fields and did not make ambiguity or time grain explicit.

## Reconstructed Structured Intent

```json
{
  "schema_version": "1.0",
  "route": "semantic_query",
  "entity": "planning_inventory",
  "time": {"grain": "reporting_period", "periods": ["synthetic-period-02"]},
  "filters": [
    {"field": "is_ready", "operator": "equals", "value": true}
  ],
  "measures": ["inventory_count", "average_complexity_score"],
  "group_by": ["equipment_category"],
  "limit": 100
}
```

This example is invented contract data. It contains no recovered query,
identifier, physical table, or semantic-model artifact.

## Ambiguity Gate

Before query compilation, unresolved material terms produce a typed response:

```json
{
  "schema_version": "1.0",
  "route": "clarification_required",
  "missing": ["time.periods"],
  "question": "Which reporting period should be used?",
  "allowed_answers": ["current_reporting_period", "previous_reporting_period"]
}
```

Clarification is required for a missing/conflicting entity, period, time grain,
unit, comparison baseline, or requested metric. Defaults may be used only when
they are policy-owned, versioned, disclosed in the answer, and do not broaden
data access. Low confidence alone is not permission to issue a broad query.

## Safe Compilation Boundary

```text
validated intent
  -> resolve entity and measure metadata from allowlist
  -> type-check filter values and period keys
  -> intersect requested arguments with trusted authorization scope
  -> compile through the semantic adapter (never model-authored physical SQL)
  -> normalize rows, source version, measure references, and warnings
```

The allowlist permits `planning_inventory`; measures `inventory_count`,
`average_complexity_score`, and `workload_hours`; dimensions
`equipment_category`, `complexity_band`, and `reporting_period`; and filters
`is_ready`, those dimensions, and bounded period keys. `inventory_count` uses
distinct planning groups at the declared grain. `workload_hours` is descriptive
only when supplied as an approved measure; scenario arithmetic routes to the
deterministic calculation tool.

## Known Failure Modes

- Reject unknown fields/operators, duplicate measures, incompatible dimensions,
  malformed values, unbounded periods, and limits above policy maximum.
- Block incompatible grains instead of joining or averaging them implicitly.
- Preserve no-data, suppressed, truncated, stale-source, and partial-result
  states; none is equivalent to zero.
- Return no rows for denied requests and do not reveal whether restricted values exist.
- Do not fall back to generated SQL, a broader entity, or prose arithmetic.

## Implementation Still Absent

The parser, ambiguity threshold, metadata allowlist, semantic compiler, data
authorization, and query execution are reconstructed requirements. They were
not recovered as a complete implementation and have no verified runtime result.
