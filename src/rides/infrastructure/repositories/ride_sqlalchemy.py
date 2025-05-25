from contextlib import suppress
from datetime import UTC, datetime

from sqlalchemy import TIMESTAMP, ForeignKey, Index, SmallInteger, delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from shared.infrastructure.sqlalchemy import Base

from ...domain import models as domain_models
from ...errors import ActiveRideNotFoundError


class RideSQLAlchemyModel(Base):
    """Ride model for SQLAlchemy ORM."""

    city_id_departure: Mapped[domain_models.CityId]
    city_id_destination: Mapped[domain_models.CityId]
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))  # used for presentation
    departure_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    description: Mapped[str | None]
    id: Mapped[domain_models.RideId] = mapped_column(primary_key=True, index=True)
    is_cancelled: Mapped[bool]
    owner_id: Mapped[domain_models.OwnerId]
    passengers: Mapped[list['PassengerSQLAlchemyModel']] = relationship(back_populates='ride', passive_deletes=True)
    price_currency: Mapped[domain_models.Currency]
    price_value: Mapped[int]
    seats_available: Mapped[int] = mapped_column(SmallInteger)  # used for faster filtration and presentation
    seats_number: Mapped[int] = mapped_column(SmallInteger)

    __tablename__ = 'rides'
    __table_args__ = (
        Index('ix_ride_city_from_to_departure', 'city_id_departure', 'city_id_destination', 'departure_time'),
    )


class PassengerSQLAlchemyModel(Base):
    """Passenger model for SQLAlchemy ORM."""

    id: Mapped[domain_models.PassengerId] = mapped_column(primary_key=True, index=True)
    ride: Mapped[RideSQLAlchemyModel] = relationship(back_populates='passengers')
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
            city_id_departure=ride.route.city_id_departure,
            city_id_destination=ride.route.city_id_destination,
            created_at=datetime.now(UTC),
            departure_time=ride.departure_time,
            description=ride.description,
            id=ride.id,
            is_cancelled=ride.is_cancelled,
            owner_id=ride.owner_id,
            passengers=ride.passengers,
            price_currency=ride.price.currency,
            price_value=ride.price.value,
            seats_available=ride.seats_available,
            seats_number=ride.seats_number,
        )
        self._session.add(db_ride)

    async def get_if_active(self, id: domain_models.RideId) -> domain_models.Ride:
        """Obtain the ride for the following update if it's active.
        WARNING: the method uses SELECT FOR UPDATE.

        Raise:
            - ActiveRideNotFoundError, if ride isn't active or wasn't found at all;
        """
        # selectinload is used instead of joinedload,
        # since SELECT FOR UPDATE isn't supported with JOIN by PostgreSQL
        q = (
            select(RideSQLAlchemyModel)
            .with_for_update()
            .options(selectinload(RideSQLAlchemyModel.passengers))
            .where(
                RideSQLAlchemyModel.id == id,
                RideSQLAlchemyModel.is_cancelled == False,
                RideSQLAlchemyModel.departure_time > datetime.now(UTC),
            )
        )
        ride = await self._session.scalar(q)

        if not ride:
            raise ActiveRideNotFoundError

        passengers = [domain_models.Passenger(id=p.id, seats_booked=p.seats_booked) for p in ride.passengers]
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
        changed_fields = ride.get_changed_fields()
        updates = {}

        with suppress(KeyError):
            changed_fields.remove('passengers_added')

            updates['seats_available'] = ride.seats_available

            insert_q = insert(PassengerSQLAlchemyModel).values(
                [{'id': p.id, 'ride_id': ride.id, 'seats_booked': p.seats_booked} for p in ride.passengers]
            )
            insert_q = insert_q.on_conflict_do_nothing(
                index_elements=(PassengerSQLAlchemyModel.id, PassengerSQLAlchemyModel.ride_id)
            )
            await self._session.execute(insert_q)

        with suppress(KeyError):
            changed_fields.remove('passengers_removed')

            updates['seats_available'] = ride.seats_available

            passenger_ids = [p.id for p in ride.passengers]
            delete_q = delete(PassengerSQLAlchemyModel).where(
                PassengerSQLAlchemyModel.ride_id == ride.id, PassengerSQLAlchemyModel.id.not_in(passenger_ids)
            )
            await self._session.execute(delete_q)

        with suppress(KeyError):
            changed_fields.remove('seats_number')

            updates['seats_available'] = ride.seats_available

        updates.update({k: getattr(ride, k) for k in changed_fields})

        q = update(RideSQLAlchemyModel).where(RideSQLAlchemyModel.id == ride.id).values(**updates)
        await self._session.execute(q)

        ride.clear_changed_fields()
