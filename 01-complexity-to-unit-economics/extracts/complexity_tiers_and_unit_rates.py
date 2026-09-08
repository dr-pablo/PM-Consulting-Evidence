"""Assign transparent complexity bands and illustrative unit rates.

Classification: sanitized_derivative
Production status: generalized design pattern; all boundaries and rates synthetic
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ComplexityTier:
    name: str
    minimum_minutes: Decimal
    maximum_minutes: Decimal | None
    rates_by_form: dict[str, Decimal]

    def contains(self, minutes: Decimal) -> bool:
        return minutes >= self.minimum_minutes and (
            self.maximum_minutes is None or minutes < self.maximum_minutes
        )


# Illustrative only. These values have no relationship to a private rate card.
ILLUSTRATIVE_TIERS = (
    ComplexityTier("tier_1", Decimal("0"), Decimal("10"), {"form_a": Decimal("25"), "form_b": Decimal("18")}),
    ComplexityTier("tier_2", Decimal("10"), Decimal("20"), {"form_a": Decimal("40"), "form_b": Decimal("30")}),
    ComplexityTier("tier_3", Decimal("20"), Decimal("35"), {"form_a": Decimal("60"), "form_b": Decimal("45")}),
    ComplexityTier("tier_4", Decimal("35"), Decimal("55"), {"form_a": Decimal("85"), "form_b": Decimal("65")}),
    ComplexityTier("tier_5", Decimal("55"), None, {"form_a": Decimal("115"), "form_b": Decimal("90")}),
)


def select_tier(
    modeled_minutes: Decimal,
    equipment_form: str,
    tiers: tuple[ComplexityTier, ...] = ILLUSTRATIVE_TIERS,
) -> tuple[str, Decimal]:
    """Return one non-overlapping tier and its form-specific illustrative rate."""
    if modeled_minutes < 0:
        raise ValueError("Modeled minutes cannot be negative")
    matches = [tier for tier in tiers if tier.contains(modeled_minutes)]
    if len(matches) != 1:
        raise ValueError("Tier configuration must produce exactly one match")
    tier = matches[0]
    try:
        return tier.name, tier.rates_by_form[equipment_form]
    except KeyError as error:
        raise ValueError(f"Unknown equipment form: {equipment_form}") from error


def compare_modeled_to_observed(
    modeled_minutes: Decimal,
    observed_minutes: Decimal,
) -> dict[str, Decimal]:
    """Keep scenario comparison separate from recognized revenue."""
    return {
        "modeled_minutes": modeled_minutes,
        "observed_minutes": observed_minutes,
        "minute_variance": observed_minutes - modeled_minutes,
    }
