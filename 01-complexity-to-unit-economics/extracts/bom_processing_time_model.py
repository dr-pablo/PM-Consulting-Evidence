"""Estimate recovery effort from a one-level equipment bill of materials.

Classification: sanitized_derivative
Production status: design pattern derived from prior implementation evidence

Names and values are synthetic. Host/parent-item/component grain is a sanitized
recovered pattern; status and coverage controls are corrected public design.
Recursive traversal is intentionally outside the evidence claim.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Component:
    host_id: str
    parent_item: str
    model_code: str
    recovery_form: str
    component_type: str
    quantity: float


@dataclass(frozen=True)
class TimeStandard:
    component_type: str
    seconds_per_component: float


@dataclass(frozen=True)
class EffortEstimate:
    host_id: str
    parent_item: str
    model_code: str
    recovery_form: str
    modeled_minutes: float
    quantity_coverage: float
    model_status: str


def estimate_parent_item_effort(
    components: Iterable[Component],
    standards: Iterable[TimeStandard],
) -> list[EffortEstimate]:
    """Roll components to one host/parent-item recovery estimate."""
    standard_rows = list(standards)
    standard_by_type = {
        row.component_type: row.seconds_per_component for row in standard_rows
    }
    if len(standard_by_type) != len(standard_rows):
        raise ValueError("Each component type must have exactly one time standard")
    if any(row.seconds_per_component < 0 for row in standard_rows):
        raise ValueError("Time standards cannot be negative")

    totals: dict[tuple[str, str, str, str], dict[str, float]] = defaultdict(
        lambda: {"quantity": 0.0, "covered_quantity": 0.0, "seconds": 0.0}
    )
    for component in components:
        if component.quantity < 0:
            raise ValueError("Component quantities cannot be negative")
        if component.recovery_form not in {"rack", "container"}:
            raise ValueError(f"Unknown recovery form: {component.recovery_form}")
        key = (
            component.host_id,
            component.parent_item,
            component.model_code,
            component.recovery_form,
        )
        totals[key]["quantity"] += component.quantity
        seconds = standard_by_type.get(component.component_type)
        if seconds is not None:
            totals[key]["covered_quantity"] += component.quantity
            totals[key]["seconds"] += component.quantity * seconds

    estimates = []
    for (host_id, parent_item, model_code, recovery_form), total in totals.items():
        quantity = total["quantity"]
        coverage = total["covered_quantity"] / quantity if quantity else 0.0
        estimates.append(
            EffortEstimate(
                host_id=host_id,
                parent_item=parent_item,
                model_code=model_code,
                recovery_form=recovery_form,
                modeled_minutes=round(total["seconds"] / 60, 2),
                quantity_coverage=round(coverage, 4),
                model_status="complete" if coverage == 1 else "partial_standard_coverage",
            )
        )
    return estimates


def volume_weighted_model_effort(
    estimates: Iterable[EffortEstimate], recovery_volume: dict[tuple[str, str], int]
) -> dict[tuple[str, str], float]:
    """Weight complete parent items to model/form grain using synthetic volume."""
    weighted_minutes: dict[tuple[str, str], float] = defaultdict(float)
    volumes: dict[tuple[str, str], int] = defaultdict(int)
    for estimate in estimates:
        if estimate.model_status != "complete":
            continue
        volume = recovery_volume.get((estimate.host_id, estimate.parent_item), 0)
        if volume < 0:
            raise ValueError("Host volume cannot be negative")
        key = (estimate.model_code, estimate.recovery_form)
        weighted_minutes[key] += estimate.modeled_minutes * volume
        volumes[key] += volume
    return {
        key: round(total / volumes[key], 2)
        for key, total in weighted_minutes.items()
        if volumes[key] > 0
    }
