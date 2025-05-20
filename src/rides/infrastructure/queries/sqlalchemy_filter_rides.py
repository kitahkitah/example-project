from __future__ import annotations

from datetime import UTC, datetime, time, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import select

from ...application.queries.filter_rides import FilteredRidesDTO, PriceDTO
from ..repositories.ride_sqlalchemy import RideSQLAlchemyModel as Model

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from ...application.queries.filter_rides import FilterParamsDTO


class SQLAlchemyFilterRidesQuery:
    """A query for rides filtering."""

    def __init__(self, db_session: AsyncSession) -> None:
        self._db_session = db_session

    async def handle(self, params: FilterParamsDTO) -> list[FilteredRidesDTO]:
        """Handle the query."""
        from_ = datetime.combine(params.departure_date, time(0, 0, tzinfo=UTC))
        to = from_ + timedelta(days=1)

        q = select(
            Model.departure_time,
            Model.id,
            Model.price_currency,
            Model.price_value,
            Model.seats_available,
            Model.seats_number,
        ).where(
            Model.city_id_departure == params.city_id_departure,
            Model.city_id_destination == params.city_id_destination,
            Model.departure_time >= from_,
            Model.departure_time < to,
            Model.seats_available >= params.min_seats_available,
        )
        rides = (await self._db_session.execute(q)).all()

        return [
            FilteredRidesDTO(
                departure_time=time,
                id=id,
                price=PriceDTO(currency=p_cur, value=p_val),
                seats_available=seats_av,
                seats_number=seats_num,
            )
            for time, id, p_cur, p_val, seats_av, seats_num in rides
        ]
