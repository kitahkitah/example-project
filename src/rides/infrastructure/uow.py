from __future__ import annotations

from typing import TYPE_CHECKING

from .repositories.city_fake import FakeCityRepository
from .repositories.ride_sqlalchemy import SQLAlchemyRideRepository

if TYPE_CHECKING:
    from typing import Self

    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from ..domain.repositories import CityRepository, RideRepository


class RideSQLAlchemyUnitOfWork:
    """Unit of work for rides."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._to_commit = False

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        self._session.begin()
        self.ride_repo: RideRepository = SQLAlchemyRideRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]  # noqa: ANN001
        try:
            if exc_type or not self._to_commit:
                await self._session.rollback()
            else:
                await self._session.commit()
        finally:
            await self._session.aclose()

    def commit(self) -> None:
        """Commit changes."""
        self._to_commit = True


class RideSQLAlchemyCityFakeUnitOfWork:
    """Unit of work for rides with cities."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._to_commit = False

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        self._session.begin()
        self.city_repo: CityRepository = FakeCityRepository()
        self.ride_repo: RideRepository = SQLAlchemyRideRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]  # noqa: ANN001
        try:
            if exc_type or not self._to_commit:
                await self._session.rollback()
            else:
                await self._session.commit()
        finally:
            await self._session.aclose()

    def commit(self) -> None:
        """Commit changes."""
        self._to_commit = True
