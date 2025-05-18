from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..errors import PriceError


class Currency(StrEnum):
    """Available currencies."""

    DKK_ORE = 'DKK_ore'  # Denmark
    EUR_CENT = 'EUR_cent'  # EU
    GBP_PENCE = 'GBP_pence'  # UK
    PLN_GROSZ = 'PLN_grosz'  # Poland
    RUB_KOPECK = 'RUB_kopeck'  # Russia


@dataclass(frozen=True, slots=True)
class PriceVO:
    """Ride departure and destination cities.

    Prices are integers presented in fractional units (cents, pence, etc.).
    """

    currency: Currency
    value: int

    def __post_init__(self) -> None:
        # In fact, it depends on acquirings and currency, and there has to be a mapping,
        # but for the sake of example, let's leave it as is
        if self.value < 100:  # noqa: PLR2004
            raise PriceError(min_value=100)
