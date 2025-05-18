from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from .models import OwnerId, PriceVO, RouteVO


@dataclass(frozen=True, slots=True)
class CreateRideParams:
    """Params for ride creating."""

    departure_time: datetime
    description: str | None
    owner_id: OwnerId
    price: PriceVO
    route: RouteVO
    seats_number: int
