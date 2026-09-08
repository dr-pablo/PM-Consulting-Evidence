"""Model additive staffing demand and compare a selected plan with actuals.

Classification: sanitized_derivative
Production status: corrected and generalized design extract
"""

from dataclasses import dataclass
from math import ceil
from typing import Iterable


@dataclass(frozen=True)
class LaborAssumption:
    process: str
    minutes_per_unit: float
    productive_minutes_per_person: float


def build_labor_plan(
    period: str,
    demand_by_process: dict[str, int],
    assumptions: Iterable[LaborAssumption],
) -> list[dict[str, object]]:
    """Emit additive staffing detail at one period-and-process grain."""
    assumption_rows = list(assumptions)
    if any(
        row.minutes_per_unit < 0 or row.productive_minutes_per_person <= 0
        for row in assumption_rows
    ):
        raise ValueError("Labor assumptions require nonnegative effort and positive capacity")
    assumptions_by_process = {row.process: row for row in assumption_rows}
    if len(assumptions_by_process) != len(assumption_rows):
        raise ValueError("Labor assumptions must be unique by process")
    detail = []
    for process, quantity in demand_by_process.items():
        if quantity < 0:
            raise ValueError("Demand cannot be negative")
        assumption = assumptions_by_process[process]
        workload_minutes = quantity * assumption.minutes_per_unit
        required_people = ceil(workload_minutes / assumption.productive_minutes_per_person)
        detail.append(
            {
                "period": period,
                "process": process,
                "quantity": quantity,
                "workload_minutes": workload_minutes,
                "required_people": required_people,
                "is_additive": True,
            }
        )
    return detail


def compare_plan_to_actual(
    plan_rows: Iterable[dict[str, object]],
    actual_by_period_process: dict[tuple[str, str], dict[str, float]],
) -> list[dict[str, object]]:
    """Compare matching process grain without multiplying scenarios or periods."""
    comparisons = []
    for plan in plan_rows:
        process = str(plan["process"])
        period = str(plan["period"])
        actual = actual_by_period_process.get((period, process))
        if actual is None:
            comparisons.append(
                {
                    "period": period,
                    "process": process,
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
                "period": period,
                "process": process,
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
