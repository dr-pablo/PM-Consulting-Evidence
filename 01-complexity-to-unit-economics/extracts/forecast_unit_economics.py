"""Convert forecast volume into direct workload and contribution margin.

Classification: sanitized_derivative
Production status: generalized prior implementation pattern, not a complete P&L
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable


@dataclass(frozen=True)
class ForecastLine:
    period: str
    model_family: str
    equipment_form: str
    quantity: int


@dataclass(frozen=True)
class ModelEconomics:
    model_family: str
    equipment_form: str
    modeled_minutes: Decimal
    unit_rate: Decimal


def calculate_forecast_economics(
    forecast: Iterable[ForecastLine],
    economics: Iterable[ModelEconomics],
    direct_labor_cost_per_hour: Decimal,
) -> list[dict[str, object]]:
    """Return auditable row-level economics before any portfolio summary."""
    economics_rows = list(economics)
    economics_by_model = {
        (row.model_family, row.equipment_form): row for row in economics_rows
    }
    if len(economics_by_model) != len(economics_rows):
        raise ValueError("Economics must be unique by model family and equipment form")
    results = []
    for line in forecast:
        if line.quantity < 0:
            raise ValueError("Forecast quantity cannot be negative")
        model = economics_by_model.get((line.model_family, line.equipment_form))
        if model is None:
            raise ValueError(
                f"Missing economics for model/form {line.model_family}/{line.equipment_form}"
            )

        quantity = Decimal(line.quantity)
        workload_hours = quantity * model.modeled_minutes / Decimal(60)
        revenue = (quantity * model.unit_rate).quantize(Decimal("0.01"))
        direct_labor_cost = (workload_hours * direct_labor_cost_per_hour).quantize(
            Decimal("0.01")
        )
        contribution_margin = revenue - direct_labor_cost
        results.append(
            {
                "period": line.period,
                "model_family": line.model_family,
                "equipment_form": line.equipment_form,
                "quantity": line.quantity,
                "workload_hours": workload_hours.quantize(Decimal("0.01")),
                "revenue": revenue,
                "direct_labor_cost": direct_labor_cost,
                "contribution_margin": contribution_margin,
            }
        )
    return results


def reconcile(results: Iterable[dict[str, object]]) -> dict[str, Decimal]:
    """Expose additive totals used to check downstream summaries."""
    rows = list(results)
    revenue = sum((row["revenue"] for row in rows), Decimal(0))
    labor = sum((row["direct_labor_cost"] for row in rows), Decimal(0))
    margin = sum((row["contribution_margin"] for row in rows), Decimal(0))
    if revenue - labor != margin:
        raise AssertionError("Contribution-margin reconciliation failed")
    return {"revenue": revenue, "direct_labor_cost": labor, "contribution_margin": margin}
