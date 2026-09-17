"""Model additive staffing demand and compare a selected plan with actuals.

Classification: sanitized_derivative
Evidence status: corrected and generalized design extract
"""

from collections import defaultdict
from dataclasses import dataclass
from math import ceil
from typing import Iterable


@dataclass(frozen=True)
class LaborAssumption:
    scenario: str
    processing_stage: str
    workstation: str
    labor_department: str
    minutes_per_unit: float
    productive_minutes_per_person: float


def build_labor_plan(
    plan_version: str,
    period: str,
    demand_by_model_form: dict[tuple[str, str], int],
    model_stage_share: dict[tuple[str, str, str], float],
    assumptions: Iterable[LaborAssumption],
) -> list[dict[str, object]]:
    """Emit additive staffing at scenario/stage/workstation/department grain."""
    assumption_rows = list(assumptions)
    if any(
        row.minutes_per_unit < 0 or row.productive_minutes_per_person <= 0
        for row in assumption_rows
    ):
        raise ValueError("Labor assumptions require nonnegative effort and positive capacity")
    assumption_keys = {(row.scenario, row.processing_stage) for row in assumption_rows}
    if len(assumption_keys) != len(assumption_rows):
        raise ValueError("Each scenario must route a stage to one workstation/department")
    if any(quantity < 0 for quantity in demand_by_model_form.values()):
        raise ValueError("Demand cannot be negative")
    if any(share < 0 or share > 1 for share in model_stage_share.values()):
        raise ValueError("Model stage shares must be between zero and one")
    shares_by_model_form: dict[tuple[str, str], float] = defaultdict(float)
    for (model_code, recovery_form, _), share in model_stage_share.items():
        shares_by_model_form[(model_code, recovery_form)] += share
    demand_keys = set(demand_by_model_form)
    if set(shares_by_model_form) != demand_keys:
        raise ValueError("Stage-share models must match the demand model/form set")
    if any(abs(total - 1) > 1e-9 for total in shares_by_model_form.values()):
        raise ValueError("Stage shares must conserve each model/form workload")
    detail = []
    for assumption in assumption_rows:
        workload_minutes = 0.0
        planned_quantity = 0
        for (model_code, recovery_form), quantity in demand_by_model_form.items():
            stage_share = model_stage_share.get(
                (model_code, recovery_form, assumption.processing_stage)
            )
            if stage_share is None:
                continue
            workload_minutes += quantity * stage_share * assumption.minutes_per_unit
            if stage_share > 0:
                planned_quantity += quantity
        required_people = ceil(workload_minutes / assumption.productive_minutes_per_person)
        detail.append(
            {
                "plan_version": plan_version,
                "period": period,
                "scenario": assumption.scenario,
                "processing_stage": assumption.processing_stage,
                "workstation": assumption.workstation,
                "labor_department": assumption.labor_department,
                "quantity": planned_quantity,
                "workload_minutes": workload_minutes,
                "required_people": required_people,
                "additive_within_scenario": True,
            }
        )
    return detail


def compare_plan_to_actual(
    plan_rows: Iterable[dict[str, object]],
    actual_by_plan_grain: dict[tuple[str, str, str, str, str], dict[str, float]],
) -> list[dict[str, object]]:
    """Compare a selected plan version and matching operating dimensions."""
    comparisons = []
    for plan in plan_rows:
        period = str(plan["period"])
        dimensions = {
            "scenario": str(plan["scenario"]),
            "processing_stage": str(plan["processing_stage"]),
            "workstation": str(plan["workstation"]),
            "labor_department": str(plan["labor_department"]),
        }
        key = (
            period,
            dimensions["scenario"],
            dimensions["processing_stage"],
            dimensions["workstation"],
            dimensions["labor_department"],
        )
        actual = actual_by_plan_grain.get(key)
        common = {"plan_version": plan["plan_version"], "period": period, **dimensions}
        if actual is None:
            comparisons.append(
                {
                    **common,
                    "comparison_status": "missing_actual",
                    "planned_people": int(plan["required_people"]),
                    "actual_people": None,
                    "headcount_variance": None,
                    "planned_quantity": int(plan["quantity"]),
                    "actual_quantity": None,
                    "quantity_variance": None,
                }
            )
            continue
        planned_people = int(plan["required_people"])
        actual_people = int(actual["people"])
        planned_quantity = int(plan["quantity"])
        actual_quantity = int(actual["quantity"])
        comparisons.append(
            {
                **common,
                "comparison_status": "complete",
                "planned_people": planned_people,
                "actual_people": actual_people,
                "headcount_variance": actual_people - planned_people,
                "planned_quantity": planned_quantity,
                "actual_quantity": actual_quantity,
                "quantity_variance": actual_quantity - planned_quantity,
            }
        )
    return comparisons
