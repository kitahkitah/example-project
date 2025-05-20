from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

    from ...domain.models import CityId
    from ..queries.filter_rides import FilteredRidesDTO, FilterRidesQuery


@dataclass(frozen=True, slots=True)
class FilterParamsDTO:
    """Params."""

    city_id_departure: CityId
    city_id_destination: CityId
    departure_date: date
    min_seats_available: int


class FilterRidesUsecase:
    """A usecase for rides filtering."""

    def __init__(self, query: FilterRidesQuery) -> None:
        self._query = query

    async def execute(self, params: FilterParamsDTO) -> list[FilteredRidesDTO]:
        """Return rides based on filtering params."""
        return await self._query.handle(params)
