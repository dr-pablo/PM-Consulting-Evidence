"""Evaluate whether a reporting dependency satisfies its freshness SLA.

Classification: sanitized_derivative
Production status: corrected synthetic control example
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
