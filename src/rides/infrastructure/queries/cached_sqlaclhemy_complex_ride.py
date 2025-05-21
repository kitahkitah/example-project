from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, TypedDict
from uuid import UUID

import orjson
from dacite import from_dict
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from shared.errors import NotFoundError
from users import get_users_data

from ...application.queries.complex_ride import ComplexRideDTO
from ...constants import RIDE_COMPLEX_CACHE_KEY
from ...domain.models import CityId, Currency, OwnerId, PassengerId, RideId, UserId
from ..repositories.ride_sqlalchemy import RideSQLAlchemyModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from shared.application.cache import Cache

    from ...domain.repositories import CityRepository


class CachedPassengerDict(TypedDict):
    """Passengers dict."""

    id: PassengerId
    seats_booked: int


class CachedPriceDict(TypedDict):
    """Price dict."""

    currency: Currency
    value: int


class CachedRouteDict(TypedDict):
    """Cities dict."""

    city_id_departure: CityId
    city_id_destination: CityId


class CachedRideDict(TypedDict):
    """A dict for ride stored in cache."""

    created_at: datetime
    departure_time: datetime
    description: str | None
    id: RideId
    is_cancelled: bool
    owner_id: OwnerId
    passengers: list[CachedPassengerDict]
    price: CachedPriceDict
    route: CachedRouteDict
    seats_available: int
    seats_number: int


class CachedSQLAlchemyComplexRideQuery:
    """A query for full ride presentation."""

    RIDE_CACHE_TIMEOUT = 60 * 60 * 24 * 2  # 2 days

    def __init__(self, db_session: AsyncSession, cache: Cache, city_repo: CityRepository) -> None:
        self._cache = cache
        self._city_repo = city_repo
        self._db_session = db_session

    async def handle(self, ride_id: RideId) -> ComplexRideDTO:
        """Handle the query.

        Raise:
            - shared.errors.NotFoundError, if the ride wasn't found;
        """
        ride_data = await self._get_ride(ride_id)

        city_id_departure = ride_data['route']['city_id_departure']
        city_id_destination = ride_data['route']['city_id_destination']
        cities_data = self._city_repo.list([city_id_departure, city_id_destination])
        ride_data['route']['city_name_departure'] = cities_data[city_id_departure].name
        ride_data['route']['city_name_destination'] = cities_data[city_id_destination].name

        passengers_data = await get_users_data([p['id'] for p in ride_data['passengers']], self._db_session)
        for p in ride_data['passengers']:
            p.update(passengers_data[p['id']])

        return from_dict(ComplexRideDTO, ride_data)

    async def _get_ride(self, ride_id: RideId) -> dict:
        """Get the ride from cache or db."""
        cache_key = RIDE_COMPLEX_CACHE_KEY.format(ride_id=ride_id)
        if cached_data := await self._cache.get(cache_key):
            cached_ride_dict = orjson.loads(cached_data)

            cached_ride_dict['created_at'] = datetime.fromisoformat(cached_ride_dict['created_at'])
            cached_ride_dict['departure_time'] = datetime.fromisoformat(cached_ride_dict['departure_time'])
            cached_ride_dict['id'] = RideId(UUID(cached_ride_dict['id']))
            cached_ride_dict['owner_id'] = OwnerId(UserId(UUID(cached_ride_dict['owner_id'])))
            for p in cached_ride_dict['passengers']:
                p['id'] = PassengerId(UserId(UUID(p['id'])))
            cached_ride_dict['price']['currency'] = Currency(cached_ride_dict['price']['currency'])
            cached_ride_dict['route']['city_id_departure'] = CityId(
                UUID(cached_ride_dict['route']['city_id_departure'])
            )
            cached_ride_dict['route']['city_id_destination'] = CityId(
                UUID(cached_ride_dict['route']['city_id_destination'])
            )
            return cached_ride_dict

        q = (
            select(RideSQLAlchemyModel)
            .options(joinedload(RideSQLAlchemyModel.passengers))
            .where(RideSQLAlchemyModel.id == ride_id)
        )
        ride = await self._db_session.scalar(q)

        if not ride:
            raise NotFoundError

        ride_dict = CachedRideDict(
            created_at=ride.created_at,
            departure_time=ride.departure_time,
            description=ride.description,
            id=ride.id,
            is_cancelled=ride.is_cancelled,
            owner_id=ride.owner_id,
            passengers=[CachedPassengerDict(id=p.id, seats_booked=p.seats_booked) for p in ride.passengers],
            price=CachedPriceDict(currency=ride.price_currency, value=ride.price_value),
            route=CachedRouteDict(
                city_id_departure=ride.city_id_departure, city_id_destination=ride.city_id_destination
            ),
            seats_available=ride.seats_available,
            seats_number=ride.seats_number,
        )

        await self._cache.set(cache_key, orjson.dumps(ride_dict), self.RIDE_CACHE_TIMEOUT)
        return ride_dict  # type: ignore[return-value]
