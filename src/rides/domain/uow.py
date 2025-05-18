from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from typing import Self

    from .repositories import CityRepository, RideRepository


class RideUnitOfWork(Protocol):
    """Unit of work for rides."""

    ride_repo: RideRepository

    async def __aenter__(self) -> Self: ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...  # type: ignore[no-untyped-def]  # noqa: ANN001

    def commit(self) -> None:
        """Commit changes."""


class RideCityUnitOfWork(Protocol):
    """Unit of work for rides with cities."""

    city_repo: CityRepository
    ride_repo: RideRepository

    async def __aenter__(self) -> Self: ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...  # type: ignore[no-untyped-def]  # noqa: ANN001

    def commit(self) -> None:
        """Commit changes."""
