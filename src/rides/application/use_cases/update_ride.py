from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from shared.errors import ForbiddenError

from ...constants import RIDE_COMPLEX_CACHE_KEY
from ...domain.models import PriceVO, Ride, RideId

if TYPE_CHECKING:
    from collections.abc import Iterable
    from datetime import datetime

    from shared.application.cache import Cache

    from ...domain.models import Currency, OwnerId
    from ...domain.uow import RideUnitOfWork


@dataclass(frozen=True, slots=True)
class PriceDTO:
    """A DTO for price."""

    currency: Currency
    value: int


@dataclass(frozen=True, slots=True)
class UpdateRideDTO:
    """A DTO for ride update."""

    fields_to_update: Iterable[str]

    departure_time: datetime | None = None
    description: str | None = None
    price: PriceDTO | None = None
    seats_number: int | None = None


class UpdateRideUsecase:
    """A usecase for ride update."""

    def __init__(self, uow: RideUnitOfWork, cache: Cache) -> None:
        self._cache = cache
        self._uow = uow

    async def execute(self, ride_id: RideId, owner_id: OwnerId, ride_data: UpdateRideDTO) -> Ride:
        """Update the ride if possible.

        Raise:
            - ForbiddenError, if the user isn't an owner;
        """
        async with self._uow:
            ride = await self._uow.ride_repo.get_if_active(ride_id)

            if owner_id != ride.owner_id:
                raise ForbiddenError

            for field in ride_data.fields_to_update:
                if field == 'price' and ride_data.price:
                    data_to_update = PriceVO(currency=ride_data.price.currency, value=ride_data.price.value)
                else:
                    data_to_update = getattr(ride_data, field)

                setattr(ride, field, data_to_update)

            await self._uow.ride_repo.update(ride)
            self._uow.commit()

        cache_key = RIDE_COMPLEX_CACHE_KEY.format(ride_id=ride_id)
        await self._cache.delete(cache_key)
        return ride
