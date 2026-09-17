"""Route exceptions and schedule available work under explicit constraints.

Classification: sanitized_derivative
Evidence status: clean-room correction of recovered identifier/model routing
and scheduling concepts; identifiers and capacities are synthetic
"""

from dataclasses import dataclass
from datetime import date
from typing import Iterable


@dataclass(frozen=True)
class WorkItem:
    recovery_id: str
    item_identifier: str
    model_code: str
    recovery_form: str
    available_date: date
    processing_stage: str
    workstation: str
    labor_department: str
    host_units: int
    workload_minutes: float


@dataclass(frozen=True)
class RoutingRule:
    rule_id: str
    priority: int
    item_identifier: str | None
    model_code: str | None
    target_stage: str
    target_workstation: str
    target_labor_department: str
    exception_code: str | None = None
    exclude_from_plan: bool = False

    def matches(self, item: WorkItem) -> bool:
        identifier_matches = (
            self.item_identifier is None or self.item_identifier == item.item_identifier
        )
        model_matches = self.model_code is None or self.model_code == item.model_code
        return identifier_matches and model_matches


def apply_routing_rules(
    items: Iterable[WorkItem], rules: Iterable[RoutingRule]
) -> tuple[list[WorkItem], list[dict[str, object]]]:
    """Apply first-match precedence while retaining a row-level audit record."""
    rule_rows = list(rules)
    if len({rule.rule_id for rule in rule_rows}) != len(rule_rows):
        raise ValueError("Routing rule identifiers must be unique")
    if any(rule.item_identifier is None and rule.model_code is None for rule in rule_rows):
        raise ValueError("Each routing rule needs an identifier or model match")
    ordered_rules = sorted(rule_rows, key=lambda rule: (rule.priority, rule.rule_id))
    routed_items = []
    audit = []
    item_rows = list(items)
    if len({item.recovery_id for item in item_rows}) != len(item_rows):
        raise ValueError("Recovery identifiers must be unique")
    if any(item.recovery_form not in {"rack", "container"} for item in item_rows):
        raise ValueError("Recovery form must be rack or container")
    for item in item_rows:
        match = next((rule for rule in ordered_rules if rule.matches(item)), None)
        if match is None:
            routed_items.append(item)
            audit.append(
                {
                    "recovery_id": item.recovery_id,
                    "routing_status": "default_route",
                    "rule_id": None,
                    "exception_code": None,
                }
            )
            continue
        routing_status = "excluded_exception" if match.exclude_from_plan else "routed"
        audit.append(
            {
                "recovery_id": item.recovery_id,
                "routing_status": routing_status,
                "rule_id": match.rule_id,
                "exception_code": match.exception_code,
            }
        )
        if not match.exclude_from_plan:
            routed_items.append(
                WorkItem(
                    recovery_id=item.recovery_id,
                    item_identifier=item.item_identifier,
                    model_code=item.model_code,
                    recovery_form=item.recovery_form,
                    available_date=item.available_date,
                    processing_stage=match.target_stage,
                    workstation=match.target_workstation,
                    labor_department=match.target_labor_department,
                    host_units=item.host_units,
                    workload_minutes=item.workload_minutes,
                )
            )
    if len(audit) != len(item_rows):
        raise AssertionError("Routing audit conservation failed")
    return routed_items, audit


def schedule_capacity_aware(
    items: Iterable[WorkItem],
    workdays: Iterable[date],
    host_capacity: dict[tuple[date, str], int],
    minute_capacity: dict[tuple[date, str], float],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Schedule by workstation while preserving one result per routed input."""
    queue = sorted(items, key=lambda item: (item.available_date, item.recovery_id))
    if len({item.recovery_id for item in queue}) != len(queue):
        raise ValueError("Recovery identifiers must be unique")
    if any(item.host_units < 0 or item.workload_minutes < 0 for item in queue):
        raise ValueError("Work-item requirements cannot be negative")
    if any(value < 0 for value in host_capacity.values()):
        raise ValueError("Host capacity cannot be negative")
    if any(value < 0 for value in minute_capacity.values()):
        raise ValueError("Minute capacity cannot be negative")
    scheduled: list[dict[str, object]] = []
    remaining = queue
    unique_workdays = sorted(set(workdays))
    usage: dict[tuple[date, str], dict[str, float]] = {}
    for workday in unique_workdays:
        next_remaining = []
        for item in remaining:
            key = (workday, item.workstation)
            used = usage.setdefault(key, {"hosts": 0, "minutes": 0.0})
            fits = (
                item.available_date <= workday
                and used["hosts"] + item.host_units <= host_capacity.get(key, 0)
                and used["minutes"] + item.workload_minutes <= minute_capacity.get(key, 0)
            )
            if not fits:
                next_remaining.append(item)
                continue
            scheduled.append(
                {
                    "recovery_id": item.recovery_id,
                    "workday": workday,
                    "processing_stage": item.processing_stage,
                    "workstation": item.workstation,
                    "labor_department": item.labor_department,
                    "schedule_status": "scheduled",
                    "exception_code": None,
                }
            )
            used["hosts"] += item.host_units
            used["minutes"] += item.workload_minutes
        remaining = next_remaining

    last_workday = unique_workdays[-1] if unique_workdays else None
    unscheduled = []
    for item in remaining:
        exception_code = (
            "not_available_in_horizon"
            if last_workday is None or item.available_date > last_workday
            else "capacity_exceeded"
        )
        unscheduled.append(
            {
                "recovery_id": item.recovery_id,
                "processing_stage": item.processing_stage,
                "workstation": item.workstation,
                "labor_department": item.labor_department,
                "schedule_status": "unscheduled_exception",
                "exception_code": exception_code,
            }
        )
    if len({row["recovery_id"] for row in scheduled}) != len(scheduled):
        raise AssertionError("An item was scheduled more than once")
    if len(scheduled) + len(unscheduled) != len(queue):
        raise AssertionError("Input conservation failed")
    return scheduled, unscheduled
