from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from datetime import datetime

    from ...domain.models import Currency, RideId
    from ..use_cases.filter_rides import FilterParamsDTO


@dataclass(frozen=True, slots=True)
class PriceDTO:
    """Price representation."""

    currency: Currency
    value: int


@dataclass(frozen=True, slots=True)
class FilteredRidesDTO:
    """Ride brief info."""

    departure_time: datetime
    id: RideId
    price: PriceDTO
    seats_available: int
    seats_number: int


class FilterRidesQuery(Protocol):
    """A query for rides filtering."""

    async def handle(self, params: FilterParamsDTO) -> list[FilteredRidesDTO]:
        """Handle the query."""
