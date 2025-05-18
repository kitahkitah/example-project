from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from ...domain.models import City, CityId
from ...errors import CityNotFoundError

if TYPE_CHECKING:
    from collections.abc import Iterable


class FakeCityRepository:
    """A repository with fake cities."""

    def __init__(self):
        self._cities = [
            City(id=CityId(UUID('00000000-0000-0000-0000-000000000000')), name='City A'),
            City(id=CityId(UUID('00000000-0000-0000-0000-000000000001')), name='City B'),
            City(id=CityId(UUID('00000000-0000-0000-0000-000000000002')), name='City 17'),
        ]

    async def list(self, ids: Iterable[CityId]) -> dict[CityId, City]:
        """Return cities mapping.

        Raise:
            - CityNotFoundError, if at least one of specified cities wasn't found;
        """
        if set(ids) - {city.id for city in self._cities}:
            raise CityNotFoundError

        data = {}
        for id_ in ids:
            for city in self._cities:
                if id_ == city.id:
                    data[id_] = city
        return data
