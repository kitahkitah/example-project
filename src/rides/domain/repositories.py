from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Iterable

    from .models import City, CityId, Ride, RideId


class RideRepository(Protocol):
    """A ride repository."""

    async def create(self, ride: Ride) -> None:
        """Create a new ride."""

    async def get_if_active(self, id: RideId) -> Ride:
        """Obtain the ride for the following update if it's active.

        Raise:
            - ActiveRideNotFoundError, if ride isn't active or wasn't found at all;
        """

    async def update(self, ride: Ride) -> None:
        """Save the ride changes."""


class CityRepository(Protocol):
    """A city repository."""

    def list(self, ids: Iterable[CityId]) -> dict[CityId, City]:
        """Return cities mapping.

        Raise:
            - CityNotFoundError, if at least one of specified cities wasn't found;
        """
