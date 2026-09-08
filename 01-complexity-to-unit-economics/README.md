# Complexity to Unit Economics

Case study: [Turning hardware complexity into profitable unit economics](https://paulymurph.com/work/complexity-to-unit-economics)

This folder shows how heterogeneous equipment can be translated into modeled
processing effort, complexity bands, direct labor, production plans, and unit
economics. Names, rates, capacities, and thresholds are synthetic.

## Extracts

| File | What it demonstrates |
| --- | --- |
| [`bom_processing_time_model.py`](extracts/bom_processing_time_model.py) | Rolls component quantities and time standards into assembly- and model-level effort estimates |
| [`complexity_tiers_and_unit_rates.py`](extracts/complexity_tiers_and_unit_rates.py) | Applies explicit five-band intervals and form-specific illustrative unit rates |
| [`forecast_unit_economics.py`](extracts/forecast_unit_economics.py) | Converts forecast volume and modeled effort into revenue, direct labor, and contribution margin |
| [`labor_capacity_and_plan_actual.py`](extracts/labor_capacity_and_plan_actual.py) | Produces additive staffing requirements and compares a selected plan with actual output |
| [`production_scheduling_and_routing.py`](extracts/production_scheduling_and_routing.py) | Applies ordered routing rules and schedules available work within host and minute constraints |

## Coverage Boundary

The extracts support BOM-based processing-time estimation, five complexity
bands, forecast unit economics, labor planning, constrained scheduling, and
plan-versus-actual controls. They do not reproduce contractual rates, real
forecasts, operational records, or a complete accounting P&L. The recovered BOM
source was one-level aggregation, so this folder does not present recursive BOM
traversal as recovered implementation evidence.
