"""Assign transparent complexity bands and illustrative unit rates.

Classification: sanitized_derivative
Production status: recovered band/form pattern with corrected explicit statuses;
all boundaries and rates are synthetic
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ComplexityTier:
    name: str
    minimum_minutes: Decimal
    maximum_minutes: Decimal | None
    rates_by_recovery_form: dict[str, Decimal]

    def contains(self, minutes: Decimal) -> bool:
        return minutes >= self.minimum_minutes and (
            self.maximum_minutes is None or minutes < self.maximum_minutes
        )


# Illustrative only. These values have no relationship to a private rate card.
ILLUSTRATIVE_TIERS = (
    ComplexityTier(
        "tier_1", Decimal("0"), Decimal("10"),
        {"rack": Decimal("25"), "container": Decimal("18")},
    ),
    ComplexityTier(
        "tier_2", Decimal("10"), Decimal("20"),
        {"rack": Decimal("40"), "container": Decimal("30")},
    ),
    ComplexityTier(
        "tier_3", Decimal("20"), Decimal("35"),
        {"rack": Decimal("60"), "container": Decimal("45")},
    ),
    ComplexityTier(
        "tier_4", Decimal("35"), Decimal("55"),
        {"rack": Decimal("85"), "container": Decimal("65")},
    ),
    ComplexityTier(
        "tier_5", Decimal("55"), None,
        {"rack": Decimal("115"), "container": Decimal("90")},
    ),
)


def select_tier(
    modeled_minutes: Decimal,
    recovery_form: str,
    recovery_status: str,
    tiers: tuple[ComplexityTier, ...] = ILLUSTRATIVE_TIERS,
) -> dict[str, object]:
    """Rate only a completed recovery, retaining an explicit result status."""
    if modeled_minutes < 0:
        raise ValueError("Modeled minutes cannot be negative")
    if recovery_status != "recovered":
        return {
            "complexity_tier": None,
            "unit_rate": None,
            "rating_status": "not_rated",
            "recovery_status": recovery_status,
        }
    matches = [tier for tier in tiers if tier.contains(modeled_minutes)]
    if len(matches) != 1:
        raise ValueError("Tier configuration must produce exactly one match")
    tier = matches[0]
    try:
        unit_rate = tier.rates_by_recovery_form[recovery_form]
    except KeyError as error:
        raise ValueError(f"Unknown recovery form: {recovery_form}") from error
    return {
        "complexity_tier": tier.name,
        "unit_rate": unit_rate,
        "rating_status": "rated",
        "recovery_status": recovery_status,
    }


def compare_modeled_to_observed(
    modeled_minutes: Decimal,
    observed_minutes: Decimal,
) -> dict[str, Decimal]:
    """Keep scenario comparison separate from recognized revenue."""
    if modeled_minutes < 0 or observed_minutes < 0:
        raise ValueError("Modeled and observed minutes cannot be negative")
    return {
        "modeled_minutes": modeled_minutes,
        "observed_minutes": observed_minutes,
        "minute_variance": observed_minutes - modeled_minutes,
    }
