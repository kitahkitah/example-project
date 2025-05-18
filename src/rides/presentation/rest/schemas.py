from datetime import UTC, datetime, timedelta
from typing import Annotated, Self

from pydantic import AwareDatetime, BaseModel, Field, field_validator, model_validator

from ...constants import MAX_VEHICLE_SEATS
from ...domain.models import CityId, Currency, OwnerId, RideId


class PriceBaseSchema(BaseModel):
    """A base schema for price."""

    currency: Currency
    value: int


class RouteBaseSchema(BaseModel):
    """A base schema for route."""

    city_id_departure: CityId
    city_id_destination: CityId
    # We can add an approximate arrival time in the response model based on statistics


class PriceInputSchema(PriceBaseSchema):
    """An input schema for price."""

    value: Annotated[int, Field(gt=0, lt=10_000_000)]


class RouteInputSchema(RouteBaseSchema):
    """An input schema for route."""

    @model_validator(mode='after')
    def check_cities(self) -> Self:
        """Check if cities aren't same."""
        if self.city_id_departure == self.city_id_destination:
            msg = 'Cities must be different'
            raise ValueError(msg)

        return self


class CreateRideRequest(BaseModel):
    """Create user request schema."""

    departure_time: AwareDatetime
    description: Annotated[str | None, Field(max_length=500)] = None
    price: PriceInputSchema
    route: RouteInputSchema
    seats_number: Annotated[int, Field(ge=1, le=MAX_VEHICLE_SEATS)]

    @field_validator('departure_time', mode='after')
    @classmethod
    def check_departure_time(cls, value: datetime) -> datetime:
        """Departure time must be at least an hour later."""
        if value < datetime.now(UTC) + timedelta(hours=1):
            msg = 'Departure time must be at least an hour later than the current time'
            raise ValueError(msg)
        return value


class CreateRideResponse(BaseModel):
    """Create ride response schema."""

    departure_time: datetime
    description: str
    id: RideId
    owner_id: OwnerId
    price: PriceBaseSchema
    route: RouteBaseSchema
    seats_number: int


class UpdateRideRequest(BaseModel):
    """Update user request schema."""

    departure_time: AwareDatetime | None = None
    description: Annotated[str | None, Field(max_length=500)] = None
    price: PriceInputSchema | None = None
    seats_number: Annotated[int, Field(ge=1, le=MAX_VEHICLE_SEATS)] | None = None

    @field_validator('departure_time', mode='after')
    @classmethod
    def check_departure_time(cls, value: datetime) -> datetime:
        """Departure time must be at least an hour later."""
        if value < datetime.now(UTC) + timedelta(hours=1):
            msg = 'Departure time must be at least an hour later than the current time'
            raise ValueError(msg)
        return value

    @model_validator(mode='after')
    def require_one_field(self) -> Self:
        """Require at least one field."""
        if not any([self.departure_time, self.description, self.price, self.seats_number]):
            msg = 'At least one field required'
            raise ValueError(msg)
        return self


class UpdateRideResponse(BaseModel):
    """Update ride response schema."""

    departure_time: datetime
    description: str
    price: PriceBaseSchema
    seats_number: int
