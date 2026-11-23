"""Exact currency values represented as integer minor units."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import StrEnum

from ledger_api.domain.errors import ValidationError


class Currency(StrEnum):
    INR = "INR"
    USD = "USD"

    @property
    def minor_unit_scale(self) -> int:
        # Both currencies have two decimal places in the project schema.
        return 100


@dataclass(frozen=True, slots=True)
class Money:
    """A non-negative monetary amount; ``minor`` is the persisted value."""

    minor: int
    currency: Currency

    def __post_init__(self) -> None:
        if isinstance(self.minor, bool) or not isinstance(self.minor, int):
            raise ValidationError("minor amount must be an integer")
        if self.minor < 0:
            raise ValidationError("money amount cannot be negative")
        if not isinstance(self.currency, Currency):
            try:
                object.__setattr__(self, "currency", Currency(self.currency))
            except ValueError as exc:
                raise ValidationError("unsupported currency") from exc

    @classmethod
    def from_major(cls, value: str | Decimal, currency: Currency) -> Money:
        """Parse an exact decimal string without accepting floats or rounding."""
        if isinstance(value, float):
            raise ValidationError("amount must be a decimal string or Decimal")
        try:
            amount = value if isinstance(value, Decimal) else Decimal(value)
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValidationError("invalid amount") from exc
        if not amount.is_finite() or amount < 0:
            raise ValidationError("amount must be finite and non-negative")

        scaled = amount * currency.minor_unit_scale
        if scaled != scaled.to_integral_value():
            raise ValidationError("amount has more precision than the currency allows")
        return cls(int(scaled), currency)

    @classmethod
    def from_minor(cls, minor: int, currency: Currency) -> Money:
        return cls(minor, currency)

    def to_major_string(self) -> str:
        return f"{Decimal(self.minor) / self.currency.minor_unit_scale:.2f}"

    def __add__(self, other: Money) -> Money:
        self._require_same_currency(other)
        return Money(self.minor + other.minor, self.currency)

    def __sub__(self, other: Money) -> Money:
        self._require_same_currency(other)
        if other.minor > self.minor:
            raise ValidationError("money result cannot be negative")
        return Money(self.minor - other.minor, self.currency)

    def _require_same_currency(self, other: Money) -> None:
        if not isinstance(other, Money) or self.currency != other.currency:
            raise ValidationError("cannot combine different currencies")
