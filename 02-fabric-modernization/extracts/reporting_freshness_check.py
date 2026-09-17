"""Evaluate whether a reporting dependency satisfies its freshness SLA.

Classification: sanitized_derivative
Evidence status: corrected synthetic control example
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class FreshnessResult:
    ready: bool
    observed_at: datetime | None
    required_after: datetime
    lag_minutes: float | None
    reason: str


@dataclass(frozen=True)
class ReportingDependency:
    name: str
    observed_at: datetime | None
    maximum_lag: timedelta


def evaluate_freshness(
    observed_at: datetime | None,
    now: datetime | None = None,
    maximum_lag: timedelta = timedelta(hours=2),
) -> FreshnessResult:
    """Return structured readiness instead of a brittle exact-hour comparison."""
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        raise ValueError("Current time must be timezone-aware")
    required_after = current - maximum_lag
    if observed_at is None:
        return FreshnessResult(False, None, required_after, None, "no_data")
    if observed_at.tzinfo is None:
        raise ValueError("Observed time must be timezone-aware")
    lag = (current - observed_at).total_seconds() / 60
    if lag < 0:
        return FreshnessResult(False, observed_at, required_after, lag, "future_timestamp")
    return FreshnessResult(
        ready=observed_at >= required_after,
        observed_at=observed_at,
        required_after=required_after,
        lag_minutes=round(lag, 2),
        reason="within_sla" if observed_at >= required_after else "stale_data",
    )


def evaluate_reporting_dependencies(
    dependencies: list[ReportingDependency], now: datetime | None = None
) -> tuple[bool, dict[str, FreshnessResult]]:
    """Require every declared WBR input to be ready; no dependency is implicit."""
    required = {
        "inventory_current", "inventory_movements", "container_events",
        "component_recovery_events", "business_calendar", "target_plan",
    }
    supplied = {dependency.name for dependency in dependencies}
    if supplied != required or len(dependencies) != len(required):
        raise ValueError(f"Dependency registry mismatch: {sorted(required ^ supplied)}")
    results = {
        dependency.name: evaluate_freshness(
            dependency.observed_at, now=now, maximum_lag=dependency.maximum_lag
        )
        for dependency in dependencies
    }
    return all(result.ready for result in results.values()), results
