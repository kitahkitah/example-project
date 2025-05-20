from __future__ import annotations

from typing import TYPE_CHECKING

from ...constants import RIDE_COMPLEX_CACHE_KEY

if TYPE_CHECKING:
    from shared.application.cache import Cache

    from ...domain.models import PassengerId, RideId
    from ...domain.uow import RideUnitOfWork


class LeaveRideUsecase:
    """A usecase for ride leaving by a passenger."""

    def __init__(self, uow: RideUnitOfWork, cache: Cache) -> None:
        self._cache = cache
        self._uow = uow

    async def execute(self, ride_id: RideId, passenger_id: PassengerId) -> None:
        """Leave the ride."""
        async with self._uow:
            ride = await self._uow.ride_repo.get_if_active(ride_id)

            ride.remove_passenger(passenger_id)

            await self._uow.ride_repo.update(ride)
            self._uow.commit()

        cache_key = RIDE_COMPLEX_CACHE_KEY.format(ride_id=ride_id)
        await self._cache.delete(cache_key)
