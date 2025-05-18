from datetime import UTC, datetime

from sqlalchemy import TIMESTAMP, ForeignKey, Index, SmallInteger, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, joinedload, mapped_column, relationship

from shared.infrastructure.sqlalchemy import Base

from ...domain import models as domain_models
from ...errors import ActiveRideNotFoundError


class RideSQLAlchemyModel(Base):
    """Ride model for SQLAlchemy ORM."""

    _created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))  # used for presentation
    _has_available_seats: Mapped[bool]  # used for faster filtration
    city_id_departure: Mapped[domain_models.CityId]
    city_id_destination: Mapped[domain_models.CityId]
    departure_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    description: Mapped[str | None]
    id: Mapped[domain_models.RideId] = mapped_column(primary_key=True, index=True)
    is_cancelled: Mapped[bool]
    owner_id: Mapped[domain_models.OwnerId]
    passengers: Mapped[list['Passenger']] = relationship(back_populates='ride', passive_deletes=True)
    price_currency: Mapped[domain_models.Currency]
    price_value: Mapped[int]
    seats_number: Mapped[int] = mapped_column(SmallInteger)

    __tablename__ = 'rides'
    __table_args__ = (
        Index('ix_ride_city_from_to_departure', 'city_id_departure', 'city_id_destination', 'departure_time'),
    )


class Passenger(Base):
    """Passenger model for SQLAlchemy ORM."""

    id: Mapped[domain_models.PassengerId] = mapped_column(primary_key=True, index=True)
    ride: Mapped[domain_models.Ride] = relationship(back_populates='passengers')
    ride_id: Mapped[domain_models.RideId] = mapped_column(
        ForeignKey('rides.id', ondelete='CASCADE'), primary_key=True, index=True
    )
    seats_booked: Mapped[int] = mapped_column(SmallInteger)

    __tablename__ = 'passengers'


class SQLAlchemyRideRepository:
    """A ride repository based on SQLAlchemy.

    docs: https://www.sqlalchemy.org/
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, ride: domain_models.Ride) -> None:
        """Create a new ride."""
        db_ride = RideSQLAlchemyModel(
            _created_at=datetime.now(UTC),
            _has_available_seats=True,
            city_id_departure=ride.route.city_id_departure,
            city_id_destination=ride.route.city_id_destination,
            departure_time=ride.departure_time,
            description=ride.description,
            id=ride.id,
            is_cancelled=ride.is_cancelled,
            owner_id=ride.owner_id,
            passengers=ride.passengers,
            price_currency=ride.price.currency,
            price_value=ride.price.value,
            seats_number=ride.seats_number,
        )
        self._session.add(db_ride)

    async def get_if_active(self, id: domain_models.RideId) -> domain_models.Ride:
        """Obtain the ride if it's active.

        Raise:
            - ActiveRideNotFoundError, if ride isn't active or wasn't found at all;
        """
        q = (
            select(RideSQLAlchemyModel)
            .join(RideSQLAlchemyModel.passengers)
            .options(joinedload(RideSQLAlchemyModel.passengers, innerjoin=True))
            .where(
                RideSQLAlchemyModel.id == id,
                RideSQLAlchemyModel.is_cancelled == False,
                RideSQLAlchemyModel.departure_time < datetime.now(UTC),
            )
        )
        ride = await self._session.scalar(q)

        if not ride:
            raise ActiveRideNotFoundError

        passengers = [domain_models.Passenger(passenger_id=p.id, seats_booked=p.seats_booked) for p in ride.passengers]
        return domain_models.Ride(
            route=domain_models.RouteVO(
                city_id_departure=ride.city_id_departure, city_id_destination=ride.city_id_destination
            ),
            departure_time=ride.departure_time,
            description=ride.description,
            id=ride.id,
            is_cancelled=ride.is_cancelled,
            owner_id=ride.owner_id,
            passengers=passengers,
            price=domain_models.PriceVO(currency=ride.price_currency, value=ride.price_value),
            seats_number=ride.seats_number,
        )

    async def update(self, ride: domain_models.Ride) -> None:
        """Save the ride changes."""
        updates = {k: getattr(ride, k) for k in ride.get_changed_fields()}
        q = update(RideSQLAlchemyModel).where(RideSQLAlchemyModel.id == ride.id).values(**updates)
        await self._session.execute(q)

        ride.clear_changed_fields()
