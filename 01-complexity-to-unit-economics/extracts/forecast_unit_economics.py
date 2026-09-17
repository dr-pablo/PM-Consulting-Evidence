"""Convert forecast volume into direct workload and contribution margin.

Classification: sanitized_derivative
Evidence status: recovered forecast/economics pattern with corrected version
and join grain; synthetic assumptions, not a complete P&L
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable


@dataclass(frozen=True)
class ForecastLine:
    forecast_version: str
    period: str
    model_code: str
    recovery_form: str
    quantity: int


@dataclass(frozen=True)
class ModelEconomics:
    model_code: str
    recovery_form: str
    complexity_tier: str
    modeled_minutes: Decimal
    unit_rate: Decimal


def calculate_forecast_economics(
    forecast: Iterable[ForecastLine],
    economics: Iterable[ModelEconomics],
    direct_labor_cost_per_hour: Decimal,
) -> list[dict[str, object]]:
    """Return auditable row-level economics before any portfolio summary."""
    economics_rows = list(economics)
    economics_by_model_form = {
        (row.model_code, row.recovery_form): row for row in economics_rows
    }
    if len(economics_by_model_form) != len(economics_rows):
        raise ValueError("Economics must be unique by model and recovery form")
    if direct_labor_cost_per_hour < 0:
        raise ValueError("Direct labor cost cannot be negative")
    if any(row.modeled_minutes < 0 or row.unit_rate < 0 for row in economics_rows):
        raise ValueError("Modeled minutes and illustrative rates cannot be negative")
    forecast_rows = list(forecast)
    forecast_keys = {
        (row.forecast_version, row.period, row.model_code, row.recovery_form)
        for row in forecast_rows
    }
    if len(forecast_keys) != len(forecast_rows):
        raise ValueError("Forecast lines must be unique at versioned model/form grain")
    results = []
    for line in forecast_rows:
        if line.quantity < 0:
            raise ValueError("Forecast quantity cannot be negative")
        model = economics_by_model_form.get((line.model_code, line.recovery_form))
        if model is None:
            raise ValueError(
                f"Missing economics for model/form {line.model_code}/{line.recovery_form}"
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
                "forecast_version": line.forecast_version,
                "model_code": line.model_code,
                "recovery_form": line.recovery_form,
                "complexity_tier": model.complexity_tier,
                "quantity": line.quantity,
                "workload_hours": workload_hours.quantize(Decimal("0.01")),
                "revenue": revenue,
                "direct_labor_cost": direct_labor_cost,
                "contribution_margin": contribution_margin,
            }
        )
    if len(results) != len(forecast_rows):
        raise AssertionError("Forecast row conservation failed")
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
