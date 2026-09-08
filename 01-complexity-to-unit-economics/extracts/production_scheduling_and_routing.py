"""Route exceptions and schedule available work under explicit constraints.

Classification: sanitized_derivative
Production status: clean-room correction of recovered scheduling concepts
"""

from dataclasses import dataclass
from datetime import date
from typing import Iterable


@dataclass(frozen=True)
class WorkItem:
    item_id: str
    available_date: date
    route: str
    host_units: int
    workload_minutes: float


@dataclass(frozen=True)
class RoutingRule:
    rule_id: str
    priority: int
    matched_route: str
    target_route: str
    exclude_from_plan: bool = False


def apply_routing_rules(
    items: Iterable[WorkItem], rules: Iterable[RoutingRule]
) -> tuple[list[WorkItem], list[dict[str, object]]]:
    """Apply first-match precedence while retaining a row-level audit record."""
    ordered_rules = sorted(rules, key=lambda rule: (rule.priority, rule.rule_id))
    routed_items = []
    audit = []
    for item in items:
        match = next((rule for rule in ordered_rules if item.route == rule.matched_route), None)
        if match is None:
            routed_items.append(item)
            continue
        audit.append(
            {
                "item_id": item.item_id,
                "rule_id": match.rule_id,
                "original_route": item.route,
                "target_route": match.target_route,
                "excluded": match.exclude_from_plan,
            }
        )
        if not match.exclude_from_plan:
            routed_items.append(
                WorkItem(
                    item_id=item.item_id,
                    available_date=item.available_date,
                    route=match.target_route,
                    host_units=item.host_units,
                    workload_minutes=item.workload_minutes,
                )
            )
    return routed_items, audit


def schedule_capacity_aware(
    items: Iterable[WorkItem],
    workdays: Iterable[date],
    host_capacity_by_day: dict[date, int],
    minute_capacity_by_day: dict[date, float],
) -> tuple[list[dict[str, object]], list[WorkItem]]:
    """Pack an availability-ordered queue while honoring both capacity limits."""
    queue = sorted(items, key=lambda item: (item.available_date, item.item_id))
    if any(item.host_units < 0 or item.workload_minutes < 0 for item in queue):
        raise ValueError("Work-item requirements cannot be negative")
    if any(value < 0 for value in host_capacity_by_day.values()):
        raise ValueError("Host capacity cannot be negative")
    if any(value < 0 for value in minute_capacity_by_day.values()):
        raise ValueError("Minute capacity cannot be negative")
    scheduled: list[dict[str, object]] = []
    remaining = queue
    unique_workdays = sorted(set(workdays))
    for workday in unique_workdays:
        next_remaining = []
        hosts_used = 0
        minutes_used = 0.0
        for item in remaining:
            fits = (
                item.available_date <= workday
                and hosts_used + item.host_units <= host_capacity_by_day[workday]
                and minutes_used + item.workload_minutes <= minute_capacity_by_day[workday]
            )
            if not fits:
                next_remaining.append(item)
                continue
            scheduled.append({"item_id": item.item_id, "workday": workday, "route": item.route})
            hosts_used += item.host_units
            minutes_used += item.workload_minutes
        remaining = next_remaining

    if len({row["item_id"] for row in scheduled}) != len(scheduled):
        raise AssertionError("An item was scheduled more than once")
    if len(scheduled) + len(remaining) != len(queue):
        raise AssertionError("Input conservation failed")
    return scheduled, remaining
