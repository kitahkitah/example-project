from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ...domain.models import PriceVO, Ride, RouteVO
from ...domain.params_spec import CreateRideParams

if TYPE_CHECKING:
    from datetime import datetime

    from ...domain.models import CityId, Currency, OwnerId, RideId
    from ...domain.uow import RideCityUnitOfWork


@dataclass(frozen=True, slots=True)
class PriceDTO:
    """A DTO for price."""

    currency: Currency
    value: int


@dataclass(frozen=True, slots=True)
class RouteDTO:
    """Route DTO."""

    city_id_departure: CityId
    city_id_destination: CityId


@dataclass(frozen=True, slots=True)
class CreateRideDTO:
    """A DTO for a ride creating."""

    departure_time: datetime
    description: str | None
    owner_id: OwnerId
    price: PriceDTO
    route: RouteDTO
    seats_number: int


@dataclass(frozen=True, slots=True)
class RouteReturnDTO(RouteDTO):
    """Route return DTO."""

    city_name_departure: str
    city_name_destination: str


@dataclass(frozen=True, slots=True)
class CreateRideReturnDTO:
    """A DTO for return."""

    departure_time: datetime
    description: str | None
    id: RideId
    owner_id: OwnerId
    price: PriceVO
    route: RouteReturnDTO
    seats_number: int


class CreateRideUsecase:
    """A usecase for a ride creating."""

    def __init__(self, uow: RideCityUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, ride_data: CreateRideDTO) -> CreateRideReturnDTO:
        """Create a new ride."""
        params = CreateRideParams(
            departure_time=ride_data.departure_time,
            description=ride_data.description,
            owner_id=ride_data.owner_id,
            price=PriceVO(currency=ride_data.price.currency, value=ride_data.price.value),
            route=RouteVO(
                city_id_departure=ride_data.route.city_id_departure,
                city_id_destination=ride_data.route.city_id_destination,
            ),
            seats_number=ride_data.seats_number,
        )
        ride = Ride.create(params)

        async with self._uow:
            cities_data = await self._uow.city_repo.list([ride.route.city_id_departure, ride.route.city_id_destination])
            await self._uow.ride_repo.create(ride)
            self._uow.commit()

            departure_city = cities_data[ride.route.city_id_departure]
            destination_city = cities_data[ride.route.city_id_destination]

        return CreateRideReturnDTO(
            departure_time=ride.departure_time,
            description=ride.description,
            id=ride.id,
            owner_id=ride.owner_id,
            price=ride.price,
            route=RouteReturnDTO(
                city_id_departure=ride.route.city_id_departure,
                city_id_destination=ride.route.city_id_destination,
                city_name_departure=departure_city.name,
                city_name_destination=destination_city.name,
            ),
            seats_number=ride.seats_number,
        )
