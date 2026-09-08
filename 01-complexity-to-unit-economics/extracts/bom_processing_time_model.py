"""Estimate processing effort from a one-level equipment bill of materials.

Classification: sanitized_derivative
Production status: design pattern derived from prior implementation evidence

Names and values are synthetic. The recovered source aggregated one BOM level;
this extract intentionally does not present recursive traversal as recovered code.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Component:
    assembly_id: str
    model_family: str
    component_type: str
    quantity: float


@dataclass(frozen=True)
class TimeStandard:
    component_type: str
    seconds_per_component: float


@dataclass(frozen=True)
class EffortEstimate:
    assembly_id: str
    model_family: str
    modeled_minutes: float
    quantity_coverage: float


def estimate_assembly_effort(
    components: Iterable[Component],
    standards: Iterable[TimeStandard],
) -> list[EffortEstimate]:
    """Roll component quantities and standards to one estimate per assembly."""
    standard_rows = list(standards)
    standard_by_type = {row.component_type: row.seconds_per_component for row in standard_rows}
    if len(standard_by_type) != len(standard_rows):
        raise ValueError("Each component type must have exactly one time standard")

    totals: dict[tuple[str, str], dict[str, float]] = defaultdict(
        lambda: {"quantity": 0.0, "covered_quantity": 0.0, "seconds": 0.0}
    )
    for component in components:
        if component.quantity < 0:
            raise ValueError("Component quantities cannot be negative")
        key = (component.assembly_id, component.model_family)
        totals[key]["quantity"] += component.quantity
        seconds = standard_by_type.get(component.component_type)
        if seconds is not None:
            totals[key]["covered_quantity"] += component.quantity
            totals[key]["seconds"] += component.quantity * seconds

    estimates = []
    for (assembly_id, model_family), total in totals.items():
        quantity = total["quantity"]
        estimates.append(
            EffortEstimate(
                assembly_id=assembly_id,
                model_family=model_family,
                modeled_minutes=round(total["seconds"] / 60, 2),
                quantity_coverage=round(total["covered_quantity"] / quantity, 4)
                if quantity
                else 0.0,
            )
        )
    return estimates


def volume_weighted_model_effort(
    estimates: Iterable[EffortEstimate], assembly_volume: dict[str, int]
) -> dict[str, float]:
    """Produce model-level minutes weighted by the selected forecast volume."""
    weighted_minutes: dict[str, float] = defaultdict(float)
    volumes: dict[str, int] = defaultdict(int)
    for estimate in estimates:
        volume = assembly_volume.get(estimate.assembly_id, 0)
        weighted_minutes[estimate.model_family] += estimate.modeled_minutes * volume
        volumes[estimate.model_family] += volume
    return {
        model: round(total / volumes[model], 2)
        for model, total in weighted_minutes.items()
        if volumes[model] > 0
    }
