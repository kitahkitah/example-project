from datetime import datetime

from dacite import from_dict
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from shared.application.cache import Cache
from shared.errors import NotFoundError
from users import get_users_data

from ...application.queries.complex_ride import ComplexRideDTO as ComplexRideDTO
from ...constants import RIDE_COMPLEX_CACHE_KEY
from ...domain.models import CityId, Currency, OwnerId, PassengerId, RideId
from ...domain.repositories import CityRepository
from ..repositories.ride_sqlalchemy import RideSQLAlchemyModel


class CachedPassenger(BaseModel):
    """Cached passenger model."""

    id: PassengerId
    seats_booked: int


class CachedPrice(BaseModel):
    """Cached price model."""

    currency: Currency
    value: int


class CachedRoute(BaseModel):
    """Cached cities model."""

    city_id_departure: CityId
    city_id_destination: CityId


class CachedRide(BaseModel):
    """Cached ride model."""

    created_at: datetime
    departure_time: datetime
    description: str | None
    id: RideId
    is_cancelled: bool
    owner_id: OwnerId
    passengers: list[CachedPassenger]
    price: CachedPrice
    route: CachedRoute
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
        ride = await self._get_ride(ride_id)
        ride_dict = ride.model_dump()

        cities_data = self._city_repo.list([ride.route.city_id_departure, ride.route.city_id_destination])
        ride_dict['route']['city_name_departure'] = cities_data[ride.route.city_id_departure].name
        ride_dict['route']['city_name_destination'] = cities_data[ride.route.city_id_destination].name

        passengers_data = await get_users_data([p.id for p in ride.passengers], self._db_session)
        for p in ride_dict['passengers']:
            p.update(passengers_data[p['id']])

        return from_dict(ComplexRideDTO, ride_dict)

    async def _get_ride(self, ride_id: RideId) -> CachedRide:
        """Get the ride from cache or db."""
        cache_key = RIDE_COMPLEX_CACHE_KEY.format(ride_id=ride_id)
        if cached_data := await self._cache.get(cache_key):
            return CachedRide.model_validate_json(cached_data)

        q = (
            select(RideSQLAlchemyModel)
            .options(joinedload(RideSQLAlchemyModel.passengers))
            .where(RideSQLAlchemyModel.id == ride_id)
        )
        ride = await self._db_session.scalar(q)

        if not ride:
            raise NotFoundError

        cached_ride = CachedRide(
            created_at=ride.created_at,
            departure_time=ride.departure_time,
            description=ride.description,
            id=ride.id,
            is_cancelled=ride.is_cancelled,
            owner_id=ride.owner_id,
            passengers=[CachedPassenger(id=p.id, seats_booked=p.seats_booked) for p in ride.passengers],
            price=CachedPrice(currency=ride.price_currency, value=ride.price_value),
            route=CachedRoute(city_id_departure=ride.city_id_departure, city_id_destination=ride.city_id_destination),
            seats_available=ride.seats_available,
            seats_number=ride.seats_number,
        )
        await self._cache.set(cache_key, cached_ride.model_dump_json(), self.RIDE_CACHE_TIMEOUT)
        return cached_ride
