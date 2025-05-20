from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import TYPE_CHECKING, NewType
from uuid import UUID, uuid4

from shared.domain.models import Entity
from users import UserId

from .. import errors as domain_errs
from ..constants import MAX_VEHICLE_SEATS

if TYPE_CHECKING:
    from typing import Self

    from .params_spec import CreateRideParams

CityId = NewType('CityId', UUID)
OwnerId = NewType('OwnerId', UserId)
RideId = NewType('RideId', UUID)
PassengerId = NewType('PassengerId', UserId)


@dataclass(frozen=True, slots=True)
class City:
    """City data."""

    id: CityId
    name: str


@dataclass(frozen=True, slots=True)
class Passenger:
    """A passenger of a ride."""

    id: PassengerId
    seats_booked: int

    def __post_init__(self) -> None:
        if self.seats_booked <= 0:
            raise domain_errs.SeatsBookedError


class Currency(StrEnum):
    """Available currencies."""

    DKK_ORE = 'DKK_ore'  # Denmark
    EUR_CENT = 'EUR_cent'  # EU
    GBP_PENCE = 'GBP_pence'  # UK
    PLN_GROSZ = 'PLN_grosz'  # Poland
    RUB_KOPECK = 'RUB_kopeck'  # Russia


@dataclass(frozen=True, slots=True)
class PriceVO:
    """Ride departure and destination cities.

    Prices are integers presented in fractional units (cents, pence, etc.).
    """

    currency: Currency
    value: int

    def __post_init__(self) -> None:
        # In fact, it depends on acquirings and currency, and there has to be a mapping,
        # but for the sake of example, let's leave it as is
        if self.value < 100:  # noqa: PLR2004
            raise domain_errs.PriceError(min_value=100)


@dataclass(frozen=True, slots=True)
class RouteVO:
    """Ride departure and destination cities."""

    city_id_departure: CityId
    city_id_destination: CityId

    def __post_init__(self) -> None:
        if self.city_id_departure == self.city_id_destination:
            msg = 'Departure and destination cities must be different'
            raise ValueError(msg)


class Ride(Entity):
    """A ride.

    Field 'description' is important for domain logic.
    Its use can be implemented later for recommendations algorithm, censorship, etc.
    """

    __slots__ = (
        '_departure_time',
        '_description',
        '_id',
        '_is_cancelled',
        '_owner_id',
        '_passengers',
        '_price',
        '_route',
        '_seats_number',
    )

    def __init__(
        self,
        *,
        departure_time: datetime,
        description: str | None,
        id: RideId,
        is_cancelled: bool,
        owner_id: OwnerId,
        passengers: list[Passenger],
        price: PriceVO,
        route: RouteVO,
        seats_number: int,
        _for_creating: bool = False,
    ) -> None:
        self._description = description
        self._id = id
        self._is_cancelled = is_cancelled
        self._owner_id = owner_id
        self._passengers = passengers
        self._route = route

        if not _for_creating:  # i.e. just initializing, validation not required
            self._departure_time = departure_time
            self._price = price
            self._seats_number = seats_number
        else:
            self.departure_time = departure_time
            self.price = price
            self.seats_number = seats_number

        super().__init__()

    @classmethod
    def create(cls, params: CreateRideParams) -> Self:
        """Create a new ride.

        For new rides passengers are always empty.
        """
        id = RideId(uuid4())
        is_cancelled = False
        passengers: list[Passenger] = []

        return cls(
            departure_time=params.departure_time,
            description=params.description,
            id=id,
            is_cancelled=is_cancelled,
            owner_id=params.owner_id,
            passengers=passengers,
            price=params.price,
            route=params.route,
            seats_number=params.seats_number,
            _for_creating=True,
        )

    @property
    def departure_time(self) -> datetime:
        """Return departure_time."""
        return self._departure_time

    @departure_time.setter
    def departure_time(self, value: datetime) -> None:
        """Check the value.

        Raise:
            - DisallowedToChangeError, if there are passengers;
        """
        if self._passengers:
            raise domain_errs.DisallowedToChangeError

        if value < datetime.now(UTC) + timedelta(hours=1):
            msg = 'Departure time has to be at least an hour later than the current time'
            raise ValueError(msg)

        self._departure_time = value

    @property
    def description(self) -> str | None:
        """Return description."""
        return self._description

    @description.setter
    def description(self, value: str | None) -> None:
        """Check the value.

        Raise:
            - DisallowedToChangeError, if there are passengers;
        """
        if self._passengers:
            raise domain_errs.DisallowedToChangeError

        self._description = value

    @property
    def id(self) -> RideId:
        """Return id."""
        return self._id

    @property
    def is_cancelled(self) -> bool:
        """Return is_cancelled.

        Cancelled rides cannot be updated.
        """
        return self._is_cancelled

    @property
    def owner_id(self) -> OwnerId:
        """Return owner_id."""
        return self._owner_id

    @property
    def passengers(self) -> list[Passenger]:
        """Return passengers."""
        return self._passengers

    @property
    def price(self) -> PriceVO:
        """Return price."""
        return self._price

    @price.setter
    def price(self, value: PriceVO) -> None:
        """Check the value.

        Raise:
            - DisallowedToChangeError, if there are passengers;
        """
        if self._passengers:
            raise domain_errs.DisallowedToChangeError

        self._price = value

    @property
    def route(self) -> RouteVO:
        """Return route."""
        return self._route

    @property
    def seats_available(self) -> int:
        """Return the number of available for booking seats."""
        return self.seats_number - self.seats_booked

    @property
    def seats_booked(self) -> int:
        """Return the number of seats booked by passengers."""
        return sum(p.seats_booked for p in self._passengers)

    @property
    def seats_number(self) -> int:
        """Return seats_number."""
        return self._seats_number

    @seats_number.setter
    def seats_number(self, value: int) -> None:
        """Check the value.

        Raise:
            - SeatsNumberLessThanPassengersError, if the value is less than passengers;
        """
        if not (1 <= value <= MAX_VEHICLE_SEATS):
            msg = 'Invalid seats number'
            raise ValueError(msg)

        if value < self.seats_booked:
            raise domain_errs.SeatsNumberLessThanPassengersError

        self._seats_number = value

    def add_passenger(self, passenger: Passenger) -> None:
        """Add the passenger to the ride."""
        if passenger.seats_booked > self.seats_available:
            raise domain_errs.RideIsFullError

        for p in self._passengers:
            if p.id == passenger.id:
                raise domain_errs.UserAlreadyIsPassengerError

        self._passengers.append(passenger)

        self._changed_fields.add('passengers_added')

    def cancel(self) -> None:
        """Cancel the ride."""
        if self._passengers and self.departure_time < datetime.now(UTC) + timedelta(hours=1):
            raise domain_errs.RideCantBeCancelledError

        self._is_cancelled = True
        self._changed_fields.add('is_cancelled')

    def remove_passenger(self, id: PassengerId) -> None:
        """Remove the passenger from the ride."""
        for idx, p in enumerate(self._passengers):
            if p.id == id:
                del self._passengers[idx]
                break
        else:
            raise domain_errs.UserIsntPassengerError

        self._changed_fields.add('passengers_removed')
