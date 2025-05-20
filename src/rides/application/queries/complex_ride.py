from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from datetime import datetime

    from ...domain.models import CityId, Currency, OwnerId, PassengerId, RideId


@dataclass(frozen=True, slots=True)
class PassengerDTO:
    """Passengers representation."""

    age: int
    email_confirmed: bool
    first_name: str
    id: PassengerId
    seats_booked: int


@dataclass(frozen=True, slots=True)
class PriceDTO:
    """Price representation."""

    currency: Currency
    value: int


@dataclass(frozen=True, slots=True)
class RouteDTO:
    """Cities representation."""

    city_id_departure: CityId
    city_name_departure: str
    city_id_destination: CityId
    city_name_destination: str


@dataclass(frozen=True, slots=True)
class ComplexRideDTO:
    """Full representation for ride."""

    created_at: datetime
    departure_time: datetime
    description: str | None
    id: RideId
    is_cancelled: bool
    owner_id: OwnerId
    passengers: list[PassengerDTO]
    price: PriceDTO
    route: RouteDTO
    seats_available: int
    seats_number: int


class ComplexRideQuery(Protocol):
    """A query for full ride presentation."""

    async def handle(self, ride_id: RideId) -> ComplexRideDTO:
        """Handle the query.

        Raise:
            - shared.errors.NotFoundError, if the ride wasn't found;
        """
