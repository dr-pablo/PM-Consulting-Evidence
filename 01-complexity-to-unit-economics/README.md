# Complexity to Unit Economics

Case study: [Turning hardware complexity into profitable unit economics](https://paulymurph.com/work/complexity-to-unit-economics)

This folder shows how heterogeneous recovery work can be translated into
modeled processing effort, complexity bands, direct labor, production plans,
and unit economics. The operational grain is explicit: BOM rows identify a
host, parent item, and component; recovery work distinguishes rack and container
forms; and planning rows retain forecast, scenario, stage, workstation, and
labor-department dimensions.

All displayed identifiers, values, rates, capacities, dates, and thresholds are
synthetic. The operational entities and control points are sanitized derivatives
of recovered patterns. Corrections for grain, additivity, routing precedence,
exception handling, and conservation are public-ready design improvements, not
claims about the original implementation or measured business outcomes.

## Extracts

| File | What it demonstrates |
| --- | --- |
| [`bom_processing_time_model.py`](extracts/bom_processing_time_model.py) | Rolls host/parent-item/component BOM rows into recovery effort with coverage and model status |
| [`complexity_tiers_and_unit_rates.py`](extracts/complexity_tiers_and_unit_rates.py) | Applies non-overlapping five-band intervals and synthetic rack/container rates only to recovered work |
| [`forecast_unit_economics.py`](extracts/forecast_unit_economics.py) | Preserves forecast version and model/form grain while deriving workload and illustrative contribution margin |
| [`labor_capacity_and_plan_actual.py`](extracts/labor_capacity_and_plan_actual.py) | Models scenario capacity by processing stage, workstation, and labor department, then compares a selected plan with actuals |
| [`production_scheduling_and_routing.py`](extracts/production_scheduling_and_routing.py) | Routes identifier/model exceptions with precedence and schedules work against workstation host/minute capacities |

## Operational Thread

1. One-level BOM rows are grouped at host, parent-item, model, and recovery-form grain; missing time standards remain visible through coverage and model status.
2. Successful rack or container recoveries receive one complexity band and a synthetic illustrative rate.
3. A versioned forecast joins to model/form economics without dropping or multiplying rows.
4. Labor scenarios convert volume into stage/workstation/department requirements that are additive only within a scenario; selected plan versions compare at the same dimensional grain as actuals.
5. Identifier- and model-based routing produces an audit row for every input, while scheduling distinguishes availability and capacity exceptions and checks input conservation.

## Coverage Boundary

The extracts support one-level BOM processing-time estimation, five complexity
bands, forecast unit economics, labor planning, constrained scheduling, routing
exceptions, and plan-versus-actual controls. They do not reproduce contractual
rates, real forecasts, operational records, proprietary identifiers, capacity
commitments, or a complete accounting P&L. The recovered BOM source used
one-level aggregation, so recursive BOM traversal is intentionally outside the
evidence claim.
