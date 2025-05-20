from __future__ import annotations

from typing import TYPE_CHECKING

from shared.errors import ForbiddenError

from ...constants import RIDE_COMPLEX_CACHE_KEY, RIDE_FOR_LISTING_CACHE_KEY

if TYPE_CHECKING:
    from shared.application.cache import Cache

    from ...domain.models import OwnerId, Ride, RideId
    from ...domain.uow import RideUnitOfWork


class CancelRideUsecase:
    """A usecase for ride cancelling."""

    def __init__(self, uow: RideUnitOfWork, cache: Cache) -> None:
        self._cache = cache
        self._uow = uow

    async def execute(self, ride_id: RideId, owner_id: OwnerId) -> Ride:
        """Cancel the ride if possible.

        Raise:
            - ForbiddenError, if the user isn't an owner;
        """
        async with self._uow:
            ride = await self._uow.ride_repo.get_if_active(ride_id)

            if owner_id != ride.owner_id:
                raise ForbiddenError

            ride.cancel()

            await self._uow.ride_repo.update(ride)
            self._uow.commit()

        cache_keys = (
            RIDE_COMPLEX_CACHE_KEY.format(ride_id=ride_id),
            RIDE_FOR_LISTING_CACHE_KEY.format(ride_id=ride_id),
        )
        await self._cache.delete(*cache_keys)
        return ride
