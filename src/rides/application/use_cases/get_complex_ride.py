from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.models import RideId
    from ..queries.complex_ride import ComplexRideDTO, ComplexRideQuery


class GetComplexRideUsecase:
    """A usecase for ride obtaining with passengers info."""

    def __init__(self, query: ComplexRideQuery) -> None:
        self._query = query

    async def execute(self, ride_id: RideId) -> ComplexRideDTO:
        """Get the specified ride for presentation."""
        return await self._query.handle(ride_id)
